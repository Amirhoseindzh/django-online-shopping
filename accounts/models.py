from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from time import gmtime, strftime
from shop.models import States
from shop.models import DEFAULt_IMAGE_ADDRESS
from .validators import phone_validator
import os
from uuid import uuid4
from PIL import Image


class CustomUserManager(UserManager):
    """
    Custom manager for User model where email is the unique identifier
    and users are inactive by default, except for superusers.
    """

    def create_user(self, email, username=None, password=None, **extra_fields):
        """
        Create and return a regular user with is_active=False.
        """
        if not email:
            raise ValueError("The Email field must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.is_active = extra_fields.get("is_active", False)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        """
        Create and return a superuser with is_active=True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        
        return self.create_user(
            email, username=username, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(
        _("email address"), unique=True, max_length=30, blank=True, null=True
    )
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, validators=[phone_validator], blank=True)
    date_joined = models.DateField(auto_now_add=True)
    last_login = models.DateField(auto_now=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    class Meta:
        verbose_name_plural = "User"
        
    def get_full_name(self):
        return self.username
    
    def __str__(self):
        return self.email
    

def user_directory_path(instance, filename):
    # Extract the file extension
    ext = filename.split('.')[-1]
    # Use the user's ID if available, otherwise generate a unique identifier
    user_id = instance.user.id if instance.user and instance.user.id else uuid4().hex[:8]
    # Generate a unique filename using a UUID and timestamp
    unique_filename = f"user_{user_id}_{strftime('%Y%m%d-%H%M%S', gmtime())}_{uuid4().hex[:8]}.{ext}"
    # Construct the path, grouping by user ID for organization if available
    return os.path.join('static', 'images', 'profile', f"user_{user_id}", unique_filename)


class Profile(models.Model):
    class GenderChoice(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        UNSET = "FM", "Unset"

    class NewsChoice(models.TextChoices):
        TRUE = "T", "مشترک خبرنامه"
        FALSE = "F", "عدم اشتراک در خبرنامه"

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=20, null=True, blank=True)
    last_name = models.CharField(max_length=20, null=True, blank=True)
    age = models.IntegerField(blank=True, null=True)
    gender = models.CharField(
        max_length=2, choices=GenderChoice.choices, default=GenderChoice.UNSET
    )
    description = models.TextField(blank=True, null=True)
    newsletter = models.CharField(
        max_length=5,
        choices=NewsChoice.choices,
        default=NewsChoice.FALSE,
        blank=True,
    )
    avatar = models.ImageField(
        upload_to=user_directory_path,
        default=DEFAULt_IMAGE_ADDRESS,
        width_field="image_width",
        height_field="image_height",
    )

    image_width = models.PositiveIntegerField(editable=False, default=65)
    image_height = models.PositiveIntegerField(editable=False, default=65)

    class Meta:
        verbose_name_plural = 'Profile'
        
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        # save the profile first
        super().save(*args, **kwargs)

        # resize the image
        img = Image.open(self.avatar.path)
        if img.height > 80 or img.width > 80:
            output_size = (80, 80)
            # create a thumbnail
            img.thumbnail(output_size)
            # overwrite the larger image
            img.save(self.avatar.path)
    
    def __str__(self):
        return self.user.username
    
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    postal_address = models.TextField(max_length=50, help_text="Your exact address")
    full_name = models.CharField(max_length=100, help_text="Recipient's full name")
    phone_number = models.CharField(max_length=15)
    neighborhood = models.CharField(max_length=1000, help_text="Street address, P.O. box, company name, etc.")
    city = models.CharField(max_length=100)
    state = models.ForeignKey(States, on_delete=models.CASCADE)
    postal_code = models.PositiveIntegerField()
    license_plate = models.PositiveIntegerField()
    unit = models.CharField(max_length=15, help_text="Apartment or house unit")
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.postal_address} - {self.user.username}"

    class Meta:
        ordering = ['-is_default', 'id']  # Default address appears first
    