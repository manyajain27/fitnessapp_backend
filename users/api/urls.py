from django.urls import path
from . import views 
from . import gemini_api
from .views import MyTokenObtainPairView, RegisterView,VerifyOTPView, HealthDataCreateView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('health-data/', HealthDataCreateView.as_view(), name='health-data-create'),
    path('health-data/retrieve/', views.HealthDataRetrieveView.as_view(), name='health-data-retrieve'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),  # Add this line
    path('chatbot/', gemini_api.chatbot_view, name='chatbot'),
]