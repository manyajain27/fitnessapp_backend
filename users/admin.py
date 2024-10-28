from django.contrib import admin
from .models import CustomUser, HealthData
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(HealthData)
