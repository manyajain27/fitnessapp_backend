from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from django.utils import timezone
from users.models import CustomUser

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        
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