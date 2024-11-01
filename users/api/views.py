from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer,CustomUserSerializer, HealthDataSerializer,ProfileImageSerializer
from django.utils import timezone
from users.models import CustomUser, HealthData


class UserProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        health_data = HealthData.objects.filter(user=user).first()  # Get user's health data

        user_data = {
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "profile_image": user.profile_image.url if user.profile_image else None,
            "bio":user.bio
        }

        health_data_serialized = HealthDataSerializer(health_data).data if health_data else None

        return Response({
            "user": user_data,
            "health_data": health_data_serialized
        })

class ProfileImageUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = ProfileImageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the currently authenticated user
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class HealthDataCreateView(generics.CreateAPIView):
    queryset = HealthData.objects.all()
    serializer_class = HealthDataSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Associate the HealthData with the logged-in user
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class HealthDataRetrieveView(generics.RetrieveAPIView):
    serializer_class = HealthDataSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return HealthData.objects.get(user=self.request.user)
        except HealthData.DoesNotExist:
            return None  # Handle the case where health data might not exist for the user


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # delete existing user if inactive incase of failed registration
            email = serializer.validated_data['email']
            existing_user = CustomUser.objects.filter(email=email, is_active=False).first()
            if existing_user:
                existing_user.delete()
            serializer.save()
            return Response({"message": "OTP sent successfully to verify registration"}, status=status.HTTP_201_CREATED)
        
        # If the serializer is not valid, we return the errors.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        
        try:
            user = CustomUser.objects.get(email=email)
            # Check if OTP matches and hasn't expired
            if user.otp == otp and user.otp_expiration > timezone.now():
                user.is_active = True  # Activate user after OTP verification
                user.otp = None  # Clear OTP after successful verification
                user.otp_expiration = None
                user.save()
                return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class= MyTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        # Call the original post method to get the token
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # If valid, return the token
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        
        # Handle incorrect login attempts
        if serializer.errors.get('non_field_errors'):
            return Response(
                {"error": "Invalid credentials. Please check your email and password."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)