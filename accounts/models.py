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
        user.is_admin=True
        
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    name = models.CharField(verbose_name='name', max_length=80,blank=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_customer=models.BooleanField(default=False)
    is_vendor=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    updated_at = models.DateTimeField(auto_now=True,null=True)
    
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
    phone=models.CharField(max_length=100,default="",blank=True)
    country = models.CharField(max_length=100,blank=True)

    def delete(self):
        if self.user:
            self.user.delete()
        super(Customer, self).delete()
    
    def save(self, *args, **kwargs):
        self.user.is_customer=True
        self.user.save()
        # Call the original save method
        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.email
    
class Vendor(models.Model):
    user=models.OneToOneField('User', related_name="vendor_user", on_delete=models.CASCADE,primary_key=True)
    rating=models.IntegerField(default=5)
    area = models.CharField(max_length=100,blank=True)
    address = models.CharField(max_length=100,blank=True)
    description = models.CharField(max_length=500,blank=True)
    
    def delete(self):
        if self.user:
            self.user.delete()
        super(Vendor, self).delete()

    def save(self, *args, **kwargs):
        
        self.user.is_vendor=True
        self.user.save()
        # Call the original save method
        super(Vendor, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.email
    
    