from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers

class BaseRecipeAttrViewSet(viewsets.GenericViewSet,
				mixins.ListModelMixin,
				mixins.CreateModelMixin):
	# Base viewset for user owned recipe attributes
	authentication_classes 	= (TokenAuthentication,)
	permission_classes		= (IsAuthenticated,)

	def get_queryset(self):
		# Return objects for the current authentiated user only
		return self.queryset.filter(user=self.request.user).order_by('-name')

	def perform_create(self,serializers):
		# create a new tag
		serializers.save(user=self.request.user)

class TagViewSet(BaseRecipeAttrViewSet):
	# Manage tags in the database
	queryset				= Tag.objects.all()
	serializer_class		= serializers.TagSerializer

class IngredientViewSet(BaseRecipeAttrViewSet):
	# Manage Ingredients in the database

	queryset				= Ingredient.objects.all()
	serializer_class		= serializers.IngredientSerializer

class RecipeViewSet(viewsets.ModelViewSet):
	# Manage recipes in the database
	serializer_class 		= serializers.RecipeSerializer
	queryset				= Recipe.objects.all()
	authentication_classes 	= (TokenAuthentication,)
	permission_classes		= (IsAuthenticated,)

	def get_queryset(self):
		# Return objects for the current authentiated user only
		return self.queryset.filter(user=self.request.user)

	def get_serializer_class(self):
		# return appropriate serializer class
		if self.action == 'retrieve':
			return serializers.RecipeDetailSerializer

		return self.serializer_class

	def perform_create(self,serializers):
		# create a new recipe
		serializers.save(user=self.request.user)