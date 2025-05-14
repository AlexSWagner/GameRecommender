from rest_framework import serializers
from .models import GameRecommendation, RecommendationFeedback
from games.serializers import GameListSerializer, GameDetailSerializer


class GameRecommendationListSerializer(serializers.ModelSerializer):
    """Serializer for recommendation list views."""
    game = GameListSerializer(read_only=True)
    
    class Meta:
        model = GameRecommendation
        fields = [
            'id', 'game', 'score', 'reason', 'created_at',
            'viewed', 'clicked', 'dismissed', 'saved'
        ]
        read_only_fields = ['id', 'game', 'score', 'reason', 'created_at']


class GameRecommendationDetailSerializer(serializers.ModelSerializer):
    """Serializer for recommendation detail views."""
    game = GameDetailSerializer(read_only=True)
    
    class Meta:
        model = GameRecommendation
        fields = [
            'id', 'game', 'score', 'reason', 'created_at',
            'viewed', 'clicked', 'dismissed', 'saved'
        ]
        read_only_fields = ['id', 'game', 'score', 'reason', 'created_at']


class RecommendationFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for recommendation feedback."""
    
    class Meta:
        model = RecommendationFeedback
        fields = [
            'id', 'recommendation', 'rating', 'has_played',
            'interested', 'comments', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RecommendationInteractionSerializer(serializers.ModelSerializer):
    """
    Serializer for tracking user interactions with recommendations.
    This is used to update viewed, clicked, dismissed, saved states.
    """
    
    class Meta:
        model = GameRecommendation
        fields = ['id', 'viewed', 'clicked', 'dismissed', 'saved']
        read_only_fields = ['id'] 