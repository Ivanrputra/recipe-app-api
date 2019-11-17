from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL		= reverse('user:token')

def create_user(**params):
	return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
	# Test the users api public
	def setUp(self):
		self.client = APIClient()

	def test_create_valid_user_success(self):
		# test creating user with valid payload is succesfull
		payload = {'email': 'ivanrputra@gmail.com','name': 'ivanrputra','password': '1234578',}
		res = self.client.post(CREATE_USER_URL,payload)

		self.assertEqual(res.status_code,status.HTTP_201_CREATED)
		user = get_user_model().objects.get(**res.data)
		self.assertTrue(user.check_password(payload['password']))
		self.assertNotIn('password',res.data)

	def test_user_exists(self):
		# test creatings user that already exist must fails
		payload = {'email': 'ivanrputra@gmail.com','name': 'ivanrputra','password': '12345678',}
		create_user(**payload)
		res = self.client.post(CREATE_USER_URL,payload)

		self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

	def test_password_too_short(self):
		# test password must be more than 5 character
		payload = {'email': 'ivanrputra@gmail.com','name': 'ivanrputra','password': '1234',}
		res = self.client.post(CREATE_USER_URL,payload)
		self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
		user_exists = get_user_model().objects.filter(email=payload['email'])
		self.assertFalse(user_exists)

	def test_create_token_for_user(self):
		# Test that a token is created for the user
		payload = {'email': 'ivanrputra@gmail.com','name': 'ivanrputra','password': '12345678',}
		create_user(**payload)
		res = self.client.post(TOKEN_URL,payload)
		self.assertIn('token',res.data)
		self.assertEqual(res.status_code,status.HTTP_200_OK)

	def test_create_token_invalid_credential(self):
		# Test that token is not created if invalid credential are given
		create_user(email="ivanrputra@gmail.com",password="1234578")
		payload = {'email': "ivanrputra@gmail.com",'password': "wrongpass"}
		res = self.client.post(TOKEN_URL,payload)

		self.assertNotIn('token',res.data)
		self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

	def test_create_token_no_user(self):
		# Test that token is not created ig user doenst exist
		payload = {'email': 'ivanrputra@gmail.com','name': 'ivanrputra','password': '12345678',}
		res = self.client.post(TOKEN_URL,payload)

		self.assertNotIn('token',res.data)
		self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

	def test_create_token_missing_field(self):
		# test that email and password are required
		res = self.client.post(TOKEN_URL,{'email':'','password':''})
		self.assertNotIn('token',res.data)
		self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)