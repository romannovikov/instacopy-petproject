from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from unixtimestampfield import UnixTimeStampField


def profile_photo_directory(instance, filename):
    return f'users/{instance.user}/profile/{filename}'


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, full_name, password, **extra_fields):
        """
        Create and save a user with the given username, email,
        full_name, and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        if not username:
            raise ValueError('The given username must be set')
        if not full_name:
            raise ValueError('The given full name must be set')

        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(
            email=email, username=username, full_name=full_name, **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(
            email, username, full_name, password, **extra_fields
        )

    def create_superuser(self, email, username, full_name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(
            email, username, full_name, password, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()

    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150, unique=True, validators=[username_validator]
    )
    full_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'full_name']

    objects = UserManager()

    def __str__(self):
        return self.username

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return self.full_name

    def get_blog_page_url(self):
        return reverse('blog_page', args=[self.username])

    def get_follow_url(self):
        return reverse('follow_toggle', args=[self.username])

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(
            subject, message, from_email, [self.email], **kwargs
        )


class Profile(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    CUSTOM = 'C'
    PREFER_NOT_TO_SAY = 'P'

    GENDER_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
        (CUSTOM, 'Custom'),
        (PREFER_NOT_TO_SAY, 'Prefer Not To Say'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )

    photo = models.ImageField(upload_to=profile_photo_directory, verbose_name='Profile photo', blank=True)
    bio = models.CharField(
        max_length=160, default='', blank=True
    )
    website = models.URLField(default='', blank=True)
    phone_number = PhoneNumberField(default='', blank=True)
    gender = models.CharField(
        max_length=2,
        choices=GENDER_CHOICES,
        default=CUSTOM,
    )

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('blog_page', kwargs={'username': self.user.username})
