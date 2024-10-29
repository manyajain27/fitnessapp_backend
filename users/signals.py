from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import random
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def generate_otp(sender, instance, created, **kwargs):
    if created and not instance.is_active:  # Only generate OTP for new inactive users
        instance.otp = f"{random.randint(100000, 999999)}"  # Generate a 6-digit OTP
        instance.otp_expiration = timezone.now() + timedelta(minutes=10)  # OTP valid for 10 minutes
        instance.save()

        # Send OTP to the user's email
        subject = "Your OTP Code for Verification"
        message = f"Hello {instance.first_name},\nYour OTP code for account verification is {instance.otp}. This code is valid for 10 minutes.\nHope you stay healthy and strong.\nThankyou,\nFitcut Fitness"
        
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [instance.email],
            fail_silently=False,
        )
