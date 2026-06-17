from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models



class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, phone_number, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        if not phone_number:
            raise ValueError(_("The phone number must be set"))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


def phone_validator(value):
        if not value.startswith("09"):
            raise ValidationError("Error: Phone number must be started with 09. (Iran Format)")     
        if not value.isdigit():
            raise ValidationError("Error: You must enter digits.")
        
class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(
        help_text=_("username"),
        max_length=150,
        unique=True,
        null=True,
        blank=True
    )
    email = models.EmailField(_("email address"), unique=True)
    phone_number = models.CharField(max_length=11, validators=[phone_validator], unique=True, null=False, blank=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_vendor = models.BooleanField(default=False, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    objects = UserManager()
    

    def __str__(self):
        return self.email
    def clean(self):
        super().clean()
        # if self.phone_number and not self.phone_number.startswith("09"):
        #     raise ValidationError({
        #         'phone_number': "Phone number must start with 09. (Iran Format)"
        #     })
        

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profiles"
    )
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    biography = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to="profile_pictures/", default="img/profile-avatar.png")
    def __str__(self):
        return f"{self.user.email}"
    
##############################


