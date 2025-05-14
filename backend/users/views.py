from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from games.models import Platform, Genre
from .models import (
    UserProfile, UserGamePreferences, 
    PlatformPreference, GenrePreference,
    GameRating
)
from .serializers import (
    UserProfileSerializer, GamePreferenceSurveySerializer,
    GameRatingSerializer
)
from recommendations.tasks import generate_recommendations_for_user


class UserProfileViewSet(viewsets.ModelViewSet):
    """API endpoint for user profiles."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only see their own profile
        return UserProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        # Return the user's profile directly
        return self.get_queryset().first()
    
    @action(detail=False, methods=['get', 'post'])
    def survey(self, request):
        """
        GET: Retrieve the user's current survey data
        POST: Submit survey data to create/update user preferences
        """
        user_profile = self.get_object()
        
        if request.method == 'GET':
            # Prepare data for survey view
            data = {
                'birth_year': user_profile.birth_year,
                'hours_per_week': user_profile.hours_per_week,
                
                # Get platform preferences
                'platform_preferences': [
                    pref.platform_id for pref in 
                    PlatformPreference.objects.filter(user_profile=user_profile).order_by('rank')
                ],
                
                # Get genre preferences
                'genre_preferences': [
                    pref.genre_id for pref in 
                    GenrePreference.objects.filter(user_profile=user_profile).order_by('rank')
                ],
            }
            
            # Add game preferences if they exist
            game_prefs = getattr(user_profile, 'game_preferences', None)
            if game_prefs:
                data.update({
                    'prefers_multiplayer': game_prefs.prefers_multiplayer,
                    'prefers_competitive': game_prefs.prefers_competitive,
                    'prefers_cooperative': game_prefs.prefers_cooperative,
                    'prefers_story_driven': game_prefs.prefers_story_driven,
                    'prefers_open_world': game_prefs.prefers_open_world,
                    'prefers_linear': game_prefs.prefers_linear,
                    'difficulty_preference': game_prefs.difficulty_preference,
                    'willing_to_pay': game_prefs.willing_to_pay,
                    'accepts_in_app_purchases': game_prefs.accepts_in_app_purchases,
                    'additional_preferences': game_prefs.additional_preferences,
                })
            
            return Response(data)
        
        elif request.method == 'POST':
            serializer = GamePreferenceSurveySerializer(data=request.data)
            
            if serializer.is_valid():
                with transaction.atomic():
                    # Update basic profile info
                    user_profile.birth_year = serializer.validated_data.get('birth_year', user_profile.birth_year)
                    user_profile.hours_per_week = serializer.validated_data.get('hours_per_week', user_profile.hours_per_week)
                    
                    # Create or update platform preferences
                    platform_ids = serializer.validated_data.get('platform_preferences', [])
                    if platform_ids:
                        # Clear existing preferences
                        PlatformPreference.objects.filter(user_profile=user_profile).delete()
                        
                        # Create new preferences with ranking
                        for rank, platform_id in enumerate(platform_ids):
                            platform = get_object_or_404(Platform, id=platform_id)
                            PlatformPreference.objects.create(
                                user_profile=user_profile,
                                platform=platform,
                                rank=rank
                            )
                    
                    # Create or update genre preferences
                    genre_ids = serializer.validated_data.get('genre_preferences', [])
                    if genre_ids:
                        # Clear existing preferences
                        GenrePreference.objects.filter(user_profile=user_profile).delete()
                        
                        # Create new preferences with ranking
                        for rank, genre_id in enumerate(genre_ids):
                            genre = get_object_or_404(Genre, id=genre_id)
                            GenrePreference.objects.create(
                                user_profile=user_profile,
                                genre=genre,
                                rank=rank
                            )
                    
                    # Create or update game preferences
                    game_prefs, created = UserGamePreferences.objects.get_or_create(user_profile=user_profile)
                    
                    # Update game style preferences
                    if 'prefers_multiplayer' in serializer.validated_data:
                        game_prefs.prefers_multiplayer = serializer.validated_data['prefers_multiplayer']
                    
                    if 'prefers_competitive' in serializer.validated_data:
                        game_prefs.prefers_competitive = serializer.validated_data['prefers_competitive']
                    
                    if 'prefers_cooperative' in serializer.validated_data:
                        game_prefs.prefers_cooperative = serializer.validated_data['prefers_cooperative']
                    
                    # Update content preferences
                    if 'prefers_story_driven' in serializer.validated_data:
                        game_prefs.prefers_story_driven = serializer.validated_data['prefers_story_driven']
                    
                    if 'prefers_open_world' in serializer.validated_data:
                        game_prefs.prefers_open_world = serializer.validated_data['prefers_open_world']
                    
                    if 'prefers_linear' in serializer.validated_data:
                        game_prefs.prefers_linear = serializer.validated_data['prefers_linear']
                    
                    # Update gameplay preferences
                    if 'difficulty_preference' in serializer.validated_data:
                        game_prefs.difficulty_preference = serializer.validated_data['difficulty_preference']
                    
                    # Update purchase preferences
                    if 'willing_to_pay' in serializer.validated_data:
                        game_prefs.willing_to_pay = serializer.validated_data['willing_to_pay']
                    
                    if 'accepts_in_app_purchases' in serializer.validated_data:
                        game_prefs.accepts_in_app_purchases = serializer.validated_data['accepts_in_app_purchases']
                    
                    # Update additional preferences
                    if 'additional_preferences' in serializer.validated_data:
                        game_prefs.additional_preferences = serializer.validated_data['additional_preferences']
                    
                    game_prefs.save()
                    
                    # Mark survey as completed
                    user_profile.survey_completed = True
                    user_profile.save()
                
                # Generate recommendations asynchronously
                generate_recommendations_for_user.delay(user_profile.id)
                
                return Response({
                    'status': 'success',
                    'message': 'Survey data saved successfully'
                })
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get', 'post', 'put', 'delete'])
    def game_ratings(self, request):
        """Manage user game ratings."""
        user_profile = self.get_object()
        
        if request.method == 'GET':
            # Get all ratings for this user
            ratings = GameRating.objects.filter(user_profile=user_profile)
            serializer = GameRatingSerializer(ratings, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            # Create a new rating
            serializer = GameRatingSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user_profile=user_profile)
                
                # Generate new recommendations
                generate_recommendations_for_user.delay(user_profile.id)
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method in ['PUT', 'DELETE']:
            # Get the rating to update or delete
            if 'id' not in request.data:
                return Response({'error': 'Rating ID is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            rating_id = request.data.get('id')
            rating = get_object_or_404(GameRating, id=rating_id, user_profile=user_profile)
            
            if request.method == 'PUT':
                serializer = GameRatingSerializer(rating, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    
                    # Generate new recommendations
                    generate_recommendations_for_user.delay(user_profile.id)
                    
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            elif request.method == 'DELETE':
                rating.delete()
                
                # Generate new recommendations
                generate_recommendations_for_user.delay(user_profile.id)
                
                return Response(status=status.HTTP_204_NO_CONTENT)
