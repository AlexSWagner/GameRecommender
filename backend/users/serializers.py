from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, UserGamePreferences, PlatformPreference, GenrePreference, GameRating
from games.serializers import GameListSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class PlatformPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlatformPreference
        fields = ['id', 'platform', 'rank']


class GenrePreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenrePreference
        fields = ['id', 'genre', 'rank']


class GameRatingSerializer(serializers.ModelSerializer):
    game = GameListSerializer(read_only=True)
    game_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = GameRating
        fields = ['id', 'game', 'game_id', 'rating', 'has_played', 'playtime_hours', 'comments']
        read_only_fields = ['id']


class UserGamePreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGamePreferences
        fields = [
            'id', 'prefers_multiplayer', 'prefers_competitive', 'prefers_cooperative',
            'prefers_story_driven', 'prefers_open_world', 'prefers_linear',
            'difficulty_preference', 'willing_to_pay', 'accepts_in_app_purchases',
            'additional_preferences'
        ]
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    preferred_platforms = PlatformPreferenceSerializer(source='platformpreference_set', many=True, read_only=True)
    preferred_genres = GenrePreferenceSerializer(source='genrepreference_set', many=True, read_only=True)
    game_preferences = UserGamePreferencesSerializer(read_only=True)
    rated_games = GameRatingSerializer(source='gamerating_set', many=True, read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'birth_year', 'hours_per_week', 
            'preferred_platforms', 'preferred_genres', 'game_preferences',
            'rated_games', 'survey_completed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class GamePreferenceSurveySerializer(serializers.Serializer):
    """
    Serializer for handling the complete game preference survey.
    This combines multiple models for a single form submission.
    """
    # Basic demographic info
    birth_year = serializers.IntegerField(required=False, allow_null=True)
    hours_per_week = serializers.IntegerField(required=False, allow_null=True)
    
    # Platform preferences (array of platform IDs in order of preference)
    platform_preferences = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    # Genre preferences (array of genre IDs in order of preference)
    genre_preferences = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    # Game style preferences
    prefers_multiplayer = serializers.BooleanField(required=False, allow_null=True)
    prefers_competitive = serializers.BooleanField(required=False, allow_null=True)
    prefers_cooperative = serializers.BooleanField(required=False, allow_null=True)
    
    # Content preferences
    prefers_story_driven = serializers.BooleanField(required=False, allow_null=True)
    prefers_open_world = serializers.BooleanField(required=False, allow_null=True)
    prefers_linear = serializers.BooleanField(required=False, allow_null=True)
    
    # Gameplay preferences
    difficulty_preference = serializers.ChoiceField(
        choices=['easy', 'medium', 'hard', 'variable'],
        required=False,
        allow_blank=True
    )
    
    # Purchase preferences
    willing_to_pay = serializers.ChoiceField(
        choices=['free_only', 'under_20', 'under_60', 'any_price'],
        required=False,
        allow_blank=True
    )
    
    accepts_in_app_purchases = serializers.BooleanField(required=False, allow_null=True)
    
    # Additional preferences
    additional_preferences = serializers.CharField(required=False, allow_blank=True) 