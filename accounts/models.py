from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser): # Add this class for custom user model
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
class UserProfile(models.Model): # Add this class for user profile model
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    address_line_1 = models.CharField(null= True, blank=True, max_length=100)
    address_line_2 = models.CharField(null= True, blank=True, max_length=100)
    profile_picture = models.ImageField(null= True, blank=True, upload_to='userprofile')
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    mobile = models.CharField(null=True, blank=True, max_length=15) 

    def __str__(self):
        return self.user.username

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'