from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import serializers
from users.models import CustomUser, HealthData, FitnessGoal, HealthCondition
from django.contrib.auth.password_validation import validate_password

class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = FitnessGoal
        fields = ['id', 'name']

class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCondition
        fields = ['id', 'name']

class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['profile_image']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password']
    
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
            is_active=False 
        )
        
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'bio', 'is_active', 'is_staff', 'created_at']
        read_only_fields = ['is_active', 'is_staff', 'created_at']


class HealthDataSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    selectedGoals = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=FitnessGoal.objects.all()
    )
    selectedConditions = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=HealthCondition.objects.all()
    )

    class Meta:
        model = HealthData
        fields = ['id', 'user', 'birthdate', 'heightCm','gender', 'currentWeightKg', 'targetWeight', 'age', 'selectedGoals', 'selectedActivity', 'selectedDiet', 'selectedConditions', 'bmi', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        # Pop the selected goals and conditions before creating HealthData
        goals_data = validated_data.pop('selectedGoals', [])
        conditions_data = validated_data.pop('selectedConditions', [])
        
        # Check if HealthData already exists for this user
        user = validated_data.get('user')
        if HealthData.objects.filter(user=user).exists():
            raise serializers.ValidationError("Health data for this user already exists.")

        # Create HealthData instance
        health_data = HealthData.objects.create(**validated_data)

        # Add selected goals and conditions
        for goal in goals_data:
            health_data.selectedGoals.add(goal)
        for condition in conditions_data:
            health_data.selectedConditions.add(condition)

        return health_data

    def to_representation(self, instance):
        """Customize the output format for selectedGoals and selectedConditions."""
        representation = super().to_representation(instance)
        representation['selectedGoals'] = [goal.name for goal in instance.selectedGoals.all()]
        representation['selectedConditions'] = [condition.name for condition in instance.selectedConditions.all()]
        return representation

    
    def validate(self, data):
        """Optional: Add custom validation logic for HealthData fields."""
        height = data.get('heightCm')
        weight = data.get('currentWeightKg')
        if height and height <= 0:
            raise serializers.ValidationError("Height must be greater than zero.")
        if weight and weight <= 0:
            raise serializers.ValidationError("Weight must be greater than zero.")
        return data




class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # token['username'] = user.username
        token['email'] = user.email
        token['id'] = user.id
        return token