from django.db import models
from core import settings
# Create your models here.
from django.contrib.auth.models  import (PermissionsMixin, BaseUserManager, AbstractBaseUser)  


class MyUserManager(BaseUserManager):
    def create_user(self, email,password,name=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a  password')

        
        user = self.model(
            email=email.lower(),
            password=password,
            name=name
            )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, name='admin'):
        user = self.create_user(
            email=email.lower(),
            password=password,
            name=name
        )
        user.is_staff = True
        user.is_superuser = True
        user.is_pro = True
        
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    name = models.CharField(verbose_name='name', max_length=80,blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_customer=models.BooleanField(default=False)
    is_vendor=models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    objects = MyUserManager()        
    def __str__(self):
        return self.email
    
    
# class User(AbstractUser):
#     is_customer=models.BooleanField(default=False)
#     is_vendor=models.BooleanField(default=False)
#     email = models.EmailField('email address', unique=True)
    
#     objects = CustomUserManager()

#     def __str__(self):
#         return self.username

class Customer(models.Model):
    user=models.OneToOneField( 'User', related_name="customer_user", on_delete=models.CASCADE,primary_key=True)
    phone=models.TextField(default="",blank=True)
    country = models.CharField(max_length=100,blank=True)

    
    def __str__(self):
        return self.user.email
    
class Vendor(models.Model):
    user=models.OneToOneField('User', related_name="vendor_user", on_delete=models.CASCADE,primary_key=True)
    rating=models.IntegerField(default=0)
    area = models.CharField(max_length=100,blank=True)
    address = models.CharField(max_length=100,blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.user.email
    
    
# class Orders(models.Model):
# 	STATUS_CHOICES = (("Accepted",'Accepted'),("Packed",'Packed'),("On The Way",'On The Way'),("Delivered",'Delivered'),("Cancel",'Cancel'))
# 	order_id = models.CharField(max_length=50,default='')
# 	saler = models.CharField(max_length=100,default='wrappers@admin',)
# 	user = models.ForeignKey(User, default='', on_delete=models.CASCADE)
# 	products = models.CharField(max_length=50)
# 	size = models.CharField(max_length=50,default='',null=True)
# 	status = models.CharField(max_length=15,choices=STATUS_CHOICES,default='')
    