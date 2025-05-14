from rest_framework import serializers
from .models import Game, Genre, Platform, GameReview, GameImage


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ['id', 'name']


class GameReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameReview
        fields = ['id', 'source', 'author', 'rating', 'content', 'review_date', 'url']


class GameImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameImage
        fields = ['primary_url', 'backup_url1', 'backup_url2', 'fallback_url', 'is_verified']


class GameListSerializer(serializers.ModelSerializer):
    """Serializer for list views with reduced fields."""
    genres = GenreSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)
    cached_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = [
            'id', 'title', 'release_date', 'publisher', 
            'developer', 'genres', 'platforms', 'rating',
            'metacritic_score', 'user_score', 'image_url', 'cached_image_url'
        ]
    
    def get_cached_image_url(self, obj):
        """Get the best available image URL."""
        return obj.get_image_url()


class GameDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed game information."""
    genres = GenreSerializer(many=True, read_only=True)
    platforms = PlatformSerializer(many=True, read_only=True)
    reviews = GameReviewSerializer(many=True, read_only=True)
    cached_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = [
            'id', 'title', 'description', 'release_date', 
            'publisher', 'developer', 'genres', 'platforms',
            'rating', 'metacritic_score', 'user_score',
            'is_multiplayer', 'has_in_app_purchases', 'is_free_to_play',
            'age_rating', 'image_url', 'cached_image_url', 'trailer_url', 
            'source_url', 'source_name', 'reviews'
        ]
        
    def get_cached_image_url(self, obj):
        """Get the best available image URL."""
        return obj.get_image_url() 