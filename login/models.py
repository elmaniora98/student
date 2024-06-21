

from django.db import models
from django.contrib.auth.models import User, AbstractBaseUser , BaseUserManager
from django.conf import settings
from django.utils.translation import gettext_lazy as _


from phonenumber_field.modelfields import PhoneNumberField

# Own models

class UserAccountManager(BaseUserManager):
	def create_user(self , email , last_name , first_name, contact, password = None):
		if not email or len(email) <= 0 :
			raise ValueError("Email field is required !")
			
		if not password :
			raise ValueError("Password is must !")
		
		user = self.model(
			email      = self.normalize_email(email) ,
			last_name  = last_name,
			first_name = first_name,
			contact    = contact,
		)
		user.set_password(password)
		
		user.is_staff = True
		user.save(using = self._db)
		return user
	
	def create_superuser(self , email, password):
		user = self.create_user(
			email = self.normalize_email(email) ,
			password = password,
			last_name = '',
			first_name = '',
			contact    = '',
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using = self._db)
		return user
	
class UserAccount(AbstractBaseUser):

	contact = PhoneNumberField()

	email = models.EmailField(max_length=200, unique=True)
	first_name = models.CharField(max_length=30 )
	last_name = models.CharField(max_length=150)

	is_active     = models.BooleanField(default = True)
	is_admin      = models.BooleanField(default = False)
	is_staff      = models.BooleanField(default = False)
	is_superuser  = models.BooleanField(default = False)
	
	USERNAME_FIELD = "email"
	#USERNAME_FIELD = "first_name"
	
	# defining the manager for the UserAccount model
	objects = UserAccountManager()
	
	def __str__(self):
		return str(self.email)
	
	def has_perm(self , perm, obj = None):
		return self.is_admin
	
	def has_module_perms(self , app_label):
		return True
	
	def save(self , *args , **kwargs):
		return super().save(*args , **kwargs)

