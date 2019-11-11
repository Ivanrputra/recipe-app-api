from django.db import models
from django.contrib.auth.models import AbstractBaseUser, \
										BaseUserManager,PermissionsMixin
class UserManager(BaseUserManager):
	def create_user(self,email,password=None,**extra_fields):
		# create and save a new user
		if not email:
			raise ValueError("User must have an email address")

		user 	= self.model(email=self.normalize_email(email),**extra_fields)
		user.set_password(password)
		user.save(using=self._db)

		return user

	def create_superuser(self,email,password):
		# create and save a new superuser
		user 	= self.create_user(email,password)
		user.is_staff 		= True
		user.is_superuser	= True
		user.save(using=self._db)

		return user


class User(AbstractBaseUser,PermissionsMixin):
	# Custom user model that support using email instead username
	email		= models.EmailField(max_length=256,unique=True)
	name 		= models.CharField(max_length=256,default='')
	password	= models.CharField(max_length=256)
	is_active	= models.BooleanField(default=True) 
	is_staff	= models.BooleanField(default=False)

	objects		= UserManager()

	USERNAME_FIELD = 'email'