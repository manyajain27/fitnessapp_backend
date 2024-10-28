from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from users.models import CustomUser, HealthData
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password', 'date_of_birth', 'gender', 'profile_image']
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        
        # Check for existing user with the same email
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({"email": "User account already exists."})

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
            date_of_birth=validated_data.get('date_of_birth'),
            gender=validated_data.get('gender'),
            profile_image=validated_data.get('profile_image'),
            is_active=False 
        )
        
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'date_of_birth', 'gender', 'profile_image', 'is_active', 'is_staff', 'created_at']
        read_only_fields = ['is_active', 'is_staff', 'created_at']


class HealthDataSerializer(serializers.ModelSerializer):
    # This will use the user ID by default but can include the full user serializer if needed
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    class Meta:
        model = HealthData
        fields = ['id', 'user', 'height', 'weight', 'age', 'fitness_goal', 'bmi', 'created_at', 'updated_at']
        read_only_fields = ['bmi', 'created_at', 'updated_at']

    def validate(self, data):
        """Optional: Add custom validation logic for HealthData fields."""
        height = data.get('height')
        weight = data.get('weight')
        if height and height <= 0:
            raise serializers.ValidationError("Height must be greater than zero.")
        if weight and weight <= 0:
            raise serializers.ValidationError("Weight must be greater than zero.")
        return data

    def create(self, validated_data):
        """Automatically calculate BMI on create."""
        instance = super().create(validated_data)
        instance.calculate_bmi()
        instance.save()
        return instance

    def update(self, instance, validated_data):
        """Recalculate BMI on update if height or weight are changed."""
        instance = super().update(instance, validated_data)
        if 'height' in validated_data or 'weight' in validated_data:
            instance.calculate_bmi()
            instance.save()
        return instance



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # token['username'] = user.username
        token['email'] = user.email
        return token