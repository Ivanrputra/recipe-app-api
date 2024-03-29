from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer,RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')

def detail_url(recipe_id):
	# return recipe detail id
	return reverse('recipe:recipe-detail',args=[recipe_id])

def sample_recipe(user,**params):
	# create and return a sample recipe
	defaults = {
		'title': "Sample recipe",
		'time_minutes': 10,
		'price': 5.00
	}
	defaults.update(params)

	return Recipe.objects.create(user=user,**defaults)

def sample_tag(user,name="Main Course"):
	# create and return a sample tag
	return Tag.objects.create(user=user,name=name)

def sample_ingredient(user,name="Cinamon"):
	# create and return a sample ingredient
	return Ingredient.objects.create(user=user,name=name)


class PublicRecipeApitTests(TestCase):
	# Test unauthorized recipe API access
	def setUp(self):
		self.client = APIClient()

	def test_auth_required(self):
		# test that authentication is required
		res = self.client.get(RECIPE_URL)

		self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
	# test authenticated recipe API access

	def setUp(self):
		self.client = APIClient()
		self.user = get_user_model().objects.create_user(
			'ivanr@gmail.com','123567574654'
			)
		self.client.force_authenticate(self.user)

	def test_retrieve_recipes(self):
		# test retrieving a alist of recipes
		sample_recipe(user=self.user)
		sample_recipe(user=self.user)

		res = self.client.get(RECIPE_URL)

		recipes = Recipe.objects.all().order_by('-id')
		serializers = RecipeSerializer(recipes,many=True)
		self.assertEqual(res.status_code,status.HTTP_200_OK)
		self.assertEqual(res.data,serializers.data)

	def test_recipe_limited_to_user(self):
		# test retrieveing recipes for user
		user2 = get_user_model().objects.create_user(
			'ivanrputra2@gmail.com',
			'123457789'
			)
		sample_recipe(user=user2)
		sample_recipe(user=self.user)

		res = self.client.get(RECIPE_URL)

		recipes = Recipe.objects.filter(user=self.user)
		serializer = RecipeSerializer(recipes,many=True)

		self.assertEqual(res.status_code,status.HTTP_200_OK)
		self.assertEqual(len(res.data),1)
		self.assertEqual(res.data,serializer.data)

	def test_view_recipe_detail(self):
		# test viewing a recipe detail

		recipe = sample_recipe(user=self.user)
		recipe.tags.add(sample_tag(user=self.user))
		recipe.ingredients.add(sample_ingredient(user=self.user))

		url = detail_url(recipe.id)
		res = self.client.get(url)

		serializer = RecipeDetailSerializer(recipe)

		self.assertEqual(res.data,serializer.data)

	def test_create_basic_recipe(self):
		# test creating recipe
		payload = {
			'title': "Chocolate cheescake",
			'time_minutes': 30,
			'price': 5.00
		}
		res = self.client.post(RECIPE_URL,payload)

		self.assertEqual(res.status_code,status.HTTP_201_CREATED)

		recipe = Recipe.objects.get(id=res.data['id'])

		for key in payload.keys():
			self.assertEqual(payload[key],getattr(recipe,key))

	def test_create_recipe_with_tag(self):
		# test creating recipe with tags
		tag1 = sample_tag(user=self.user,name="Vegan")
		tag2 = sample_tag(user=self.user,name="Dessert")

		payload = {
			'title': "Avocado lime cheescake",
			'tags': [tag1.id,tag2.id],
			'time_minutes': 60,
			'price': 20.00
		}

		res = self.client.post(RECIPE_URL,payload)

		self.assertEqual(res.status_code,status.HTTP_201_CREATED)
		recipe = Recipe.objects.get(id=res.data['id'])
		tags = recipe.tags.all()
		self.assertEqual(tags.count(),2)
		self.assertIn(tag1,tags)
		self.assertIn(tag2,tags)

	def test_create_recipe_with_ingredient(self):
		# test creating reccipe with ingredient
		ingredient1 = sample_ingredient(user=self.user,name="Prawns")
		ingredient2 = sample_ingredient(user=self.user,name="Ginger")

		payload = {
			'title': "Avocado lime cheescake",
			'ingredients': [ingredient1.id,ingredient2.id],
			'time_minutes': 20,
			'price': 70.00
		}

		res = self.client.post(RECIPE_URL,payload)

		self.assertEqual(res.status_code,status.HTTP_201_CREATED)
		recipe = Recipe.objects.get(id=res.data['id'])
		ingredients = recipe.ingredients.all()
		self.assertEqual(ingredients.count(),2)
		self.assertIn(ingredient1,ingredients)
		self.assertIn(ingredient2,ingredients)