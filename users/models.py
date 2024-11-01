from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
import random

# models.py

FITNESS_GOALS = {
    "Lose weight",
    "Gain weight",
    "Maintain weight",
    "Gain Muscle",
    "Modify Diet",
    "Gain stamina",
    "Improve mental health",
}

HEALTH_CONDITIONS = {
    "Cardiovascular Issues",
    "Joint or Mobility Problems",
    "Respiratory Conditions",
    "Chronic Pain or Injury",
    "None",
    
}


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    bio=models.TextField(default="This is your bio section! You can edit it to share a little about yourself, your interests, or anything you'd like others to know.",blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiration = models.DateTimeField(blank=True, null=True)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    

    def __str__(self):
        return self.email

class FitnessGoal(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class HealthCondition(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class HealthData(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='health_data')
    birthdate = models.DateField(null=True, blank=True)
    heightCm = models.DecimalField(max_digits=5, decimal_places=2,null=True, blank=True, help_text="Height in cm")
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True,null=True)
    currentWeightKg = models.DecimalField(max_digits=5, decimal_places=2,null=True, blank=True, help_text="Current Weight in kg")
    targetWeight = models.DecimalField(max_digits=5, decimal_places=2,null=True, blank=True, help_text="Target Weight in kg")
    age = models.PositiveIntegerField()
    bmi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    selectedGoals = models.ManyToManyField(FitnessGoal)
    selectedActivity = models.CharField(max_length=50, default='Sedentary', choices=[
        ('sedentary', 'Sedentary'),
        ('lightly_active', 'Lightly Active'),
        ('moderately_active', 'Moderately Active'),
        ('very_active', 'Very Active')
    ])
    selectedDiet = models.CharField(max_length=50, default='Vegetarian', choices=[
        ('vegetarian', 'Vegetarian'),
        ('non_vegetarian', 'Non-Vegetarian'),
        ('vegan','Vegan'),
        ('jain', 'Jain')
    ])
    selectedConditions = models.ManyToManyField(HealthCondition)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}'s Health Data"