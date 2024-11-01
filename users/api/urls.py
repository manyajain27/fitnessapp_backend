from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static
from . import gemini_api
from .views import MyTokenObtainPairView, RegisterView,VerifyOTPView, HealthDataCreateView,UserProfileView, ProfileImageUpdateView
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
    path('profile/', UserProfileView.as_view(), name='user-profile'),  
    path('profile/profile_image/', ProfileImageUpdateView.as_view(), name='profile-image-update'),
    path('chatbot/', gemini_api.chatbot_view, name='chatbot'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)