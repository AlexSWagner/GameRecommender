import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from django.db.models import Count, Avg, Q

from games.models import Game, Genre, Platform
from users.models import UserProfile, GenrePreference, PlatformPreference, GameRating
from .models import GameRecommendation


class RecommendationEngine:
    """Engine for generating personalized game recommendations."""
    
    def __init__(self):
        self.scaler = MinMaxScaler()
    
    def generate_recommendations(self, user_profile, limit=20):
        """
        Generate recommendations for a user profile.
        
        Args:
            user_profile: UserProfile object
            limit: Maximum number of recommendations to generate
            
        Returns:
            List of (game, score, reason) tuples
        """
        # Delete existing recommendations
        GameRecommendation.objects.filter(user_profile=user_profile).delete()
        
        # Get user preferences
        genre_prefs = list(GenrePreference.objects.filter(user_profile=user_profile).order_by('rank'))
        platform_prefs = list(PlatformPreference.objects.filter(user_profile=user_profile).order_by('rank'))
        
        # Get game preferences if they exist
        game_prefs = getattr(user_profile, 'game_preferences', None)
        
        # If user has no preferences yet, return empty list
        if not genre_prefs and not platform_prefs and not game_prefs:
            return []
        
        # Get games rated by the user
        rated_game_ids = GameRating.objects.filter(user_profile=user_profile).values_list('game_id', flat=True)
        
        # Get candidate games (games not yet rated by the user)
        candidate_games = Game.objects.exclude(id__in=rated_game_ids)
        
        # Apply platform filter if user has platform preferences
        if platform_prefs:
            platform_ids = [p.platform_id for p in platform_prefs]
            candidate_games = candidate_games.filter(platforms__id__in=platform_ids).distinct()
        
        # Apply multiplayer filter if set
        if game_prefs and game_prefs.prefers_multiplayer is not None:
            candidate_games = candidate_games.filter(is_multiplayer=game_prefs.prefers_multiplayer)
        
        # Apply price filter if set
        if game_prefs and game_prefs.willing_to_pay:
            if game_prefs.willing_to_pay == 'free_only':
                candidate_games = candidate_games.filter(is_free_to_play=True)
            
            # Note: In a real implementation, you would have a price field to filter on
        
        # Apply in-app purchases filter if set
        if game_prefs and game_prefs.accepts_in_app_purchases is not None:
            candidate_games = candidate_games.filter(has_in_app_purchases=game_prefs.accepts_in_app_purchases)
        
        # Convert to DataFrame for easier processing
        game_data = []
        for game in candidate_games:
            game_genres = set(game.genres.values_list('id', flat=True))
            game_platforms = set(game.platforms.values_list('id', flat=True))
            
            game_data.append({
                'id': game.id,
                'title': game.title,
                'genres': game_genres,
                'platforms': game_platforms,
                'rating': game.rating if game.rating else 0,
                'metacritic_score': game.metacritic_score if game.metacritic_score else 0,
                'user_score': game.user_score if game.user_score else 0,
                'release_date': game.release_date,
                'is_multiplayer': game.is_multiplayer,
                'is_free_to_play': game.is_free_to_play,
                'has_in_app_purchases': game.has_in_app_purchases,
            })
        
        if not game_data:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame(game_data)
        
        # Calculate scores based on user preferences
        scores = []
        reasons = []
        
        for idx, row in df.iterrows():
            score = 0
            reason_parts = []
            
            # Score based on genre preferences
            genre_score = 0
            for i, genre_pref in enumerate(genre_prefs):
                if genre_pref.genre_id in row['genres']:
                    # Weighted by rank (first preferences get higher score)
                    weight = 1.0 / (i + 1)
                    genre_score += weight
                    reason_parts.append(f"Matches your {genre_pref.genre.name} genre preference")
            
            # Normalize genre score (0-1)
            if genre_prefs:
                max_genre_score = sum(1.0 / (i + 1) for i in range(len(genre_prefs)))
                genre_score = genre_score / max_genre_score if max_genre_score > 0 else 0
            
            # Score based on platform preferences
            platform_score = 0
            for i, platform_pref in enumerate(platform_prefs):
                if platform_pref.platform_id in row['platforms']:
                    # Weighted by rank
                    weight = 1.0 / (i + 1)
                    platform_score += weight
                    reason_parts.append(f"Available on your preferred platform ({platform_pref.platform.name})")
            
            # Normalize platform score (0-1)
            if platform_prefs:
                max_platform_score = sum(1.0 / (i + 1) for i in range(len(platform_prefs)))
                platform_score = platform_score / max_platform_score if max_platform_score > 0 else 0
            
            # Score based on game quality
            quality_score = 0
            if row['metacritic_score'] > 0:
                # Normalize Metacritic score (0-100) to 0-1
                quality_score += row['metacritic_score'] / 100
                if row['metacritic_score'] >= 90:
                    reason_parts.append(f"Critically acclaimed (Metacritic score: {row['metacritic_score']})")
            
            if row['user_score'] > 0:
                # Normalize user score (0-10) to 0-1
                quality_score += row['user_score'] / 10
                if row['user_score'] >= 8:
                    reason_parts.append(f"Highly rated by players (User score: {row['user_score']})")
            
            # Normalize quality score (average of available scores)
            num_scores = (row['metacritic_score'] > 0) + (row['user_score'] > 0)
            quality_score = quality_score / num_scores if num_scores > 0 else 0
            
            # Calculate final score (weighted average)
            score = 0.5 * genre_score + 0.3 * platform_score + 0.2 * quality_score
            
            scores.append(score)
            reasons.append(" • ".join(reason_parts[:3]))  # Limit to top 3 reasons
        
        # Add scores and reasons to DataFrame
        df['score'] = scores
        df['reason'] = reasons
        
        # Sort by score in descending order
        df = df.sort_values('score', ascending=False)
        
        # Get top N recommendations
        top_recommendations = df.head(limit)
        
        # Create recommendation objects
        recommendation_results = []
        
        for _, row in top_recommendations.iterrows():
            game = Game.objects.get(id=row['id'])
            
            # Create recommendation in database
            recommendation = GameRecommendation.objects.create(
                user_profile=user_profile,
                game=game,
                score=row['score'],
                reason=row['reason']
            )
            
            recommendation_results.append((game, row['score'], row['reason']))
        
        return recommendation_results 