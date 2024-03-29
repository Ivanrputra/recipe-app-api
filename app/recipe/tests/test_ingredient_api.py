from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

class PublicIngredientApiTests(TestCase):
	# test the publicy available ingredients API

	def setUp(self):
		self.client = APIClient()

	def test_login_required(self):
		# test that login is required to access the endpoint
		res = self.client.get(INGREDIENTS_URL)
		self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientApiTests(TestCase):
	# test the privare ingredients API

	def setUp(self):
		self.client = APIClient()
		self.user = get_user_model().objects.create_user(
			'ivanrputra@gmail.com','12345789')
		self.client.force_authenticate(self.user)

	def test_retrieve_ingredient_list(self):
		# test retrieving a alist og ingredient
		Ingredient.objects.create(user=self.user,name="haha")
		Ingredient.objects.create(user=self.user,name="asdasd")

		res = self.client.get(INGREDIENTS_URL)

		ingredients = Ingredient.objects.all().order_by('-name')
		serializers = IngredientSerializer(ingredients,many=True)
		self.assertEqual(res.status_code,status.HTTP_200_OK)
		self.assertEqual(res.data,serializers.data)

	def test_ingredient_limited_to_user(self):
		# test that ingredients for the authenticated user are returned
		user2 = get_user_model().objects.create_user("haha@gmail.com",'1234567890')
		Ingredient.objects.create(user=user2,name="Vinegar")

		ingredient = Ingredient.objects.create(user=self.user,name="Tumeric")

		res = self.client.get(INGREDIENTS_URL)

		self.assertEqual(res.status_code,status.HTTP_200_OK)
		self.assertEqual(len(res.data),1)
		self.assertEqual(res.data[0]['name'],ingredient.name)

	def test_create_ingredient_successful(self):
		# test create a new ingredient
		payload = {'name': "Cabbage"}
		self.client.post(INGREDIENTS_URL,payload)

		exists = Ingredient.objects.filter(
			user = self.user,
			name = payload['name'],
			).exists()

		self.assertTrue(exists)

	def test_create_ingredient_invalid(self):
		# test creating invalid ingredient fails
		payload = {'name':''}
		res = self.client.post(INGREDIENTS_URL,payload)

		self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)