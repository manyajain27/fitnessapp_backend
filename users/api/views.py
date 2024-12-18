from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer,CustomUserSerializer, HealthDataSerializer,ProfileImageSerializer
from django.utils import timezone
from users.models import CustomUser, HealthData
import google.generativeai as genai
from django.conf import settings
import json

genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiFitnessPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        health_data = HealthData.objects.filter(user=user).first()
        
        if not health_data:
            return Response({"error": "Health data not found for this user"}, status=404)

        # Serialize health data into JSON format
        health_data_json = json.dumps(HealthDataSerializer(health_data).data)

        # Prepare the prompt with user health data
        prompt = (
            f"""Based on the following user health data, create a 7-day meal and workout plan:
{health_data_json}

Structure your response exactly as follows with no additional explanations or titles:

MEAL PLAN:

Day 1:
Breakfast: (include dish name, portions, and calories)
Morning Snack: (include dish name, portions, and calories)
Lunch: (include dish name, portions, and calories)
Evening Snack: (include dish name, portions, and calories)
Dinner: (include dish name, portions, and calories)
Total Calories:

[Repeat the same structure for Days 2-7, with completely different meals each day]

WORKOUT PLAN:
Day 1: Provide a detailed workout plan that includes:
- Type and duration of exercises
- Number of sets and reps where applicable
- Recommended rest periods
- Low-impact alternatives if needed
[Repeat the same structure for Days 2-7 with new workouts which target every muscle over the week]

Remember to:
- Make each day's meals completely different from other days
- Account for user's dietary preferences and restrictions
- Include portion sizes and calories for each meal
- Consider health conditions: {health_data.selectedConditions if health_data.selectedConditions else 'No specific condition'}

Respond only with the plan itself, without any introductions, explanations, or conclusions."""
        )

        try:
            # Initialize the model
            model = genai.GenerativeModel('gemini-pro')
            
            # Generate content
            response = model.generate_content(prompt)
            
            # Check if we got a response and it has text
            if response and response.text:
                return Response({"fitness_plan": response.text})
            
            return Response({"error": "No content generated by Gemini AI"}, status=503)
        
        except Exception as e:
            return Response(
                {"error": "Failed to generate content with Gemini AI", "details": str(e)},
                status=503
            )

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