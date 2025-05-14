from django.shortcuts import render
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from users.models import UserProfile
from .models import GameRecommendation, RecommendationFeedback
from .serializers import (
    GameRecommendationListSerializer, GameRecommendationDetailSerializer,
    RecommendationFeedbackSerializer, RecommendationInteractionSerializer
)
from .tasks import generate_recommendations_for_user


class RecommendationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for game recommendations."""
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['score', 'created_at']
    
    def get_queryset(self):
        # Only return recommendations for the current user
        user_profile = UserProfile.objects.get(user=self.request.user)
        return GameRecommendation.objects.filter(user_profile=user_profile)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GameRecommendationDetailSerializer
        return GameRecommendationListSerializer
    
    @action(detail=True, methods=['post'])
    def interaction(self, request, pk=None):
        """Update user interaction with a recommendation."""
        recommendation = self.get_object()
        serializer = RecommendationInteractionSerializer(recommendation, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def feedback(self, request, pk=None):
        """Submit feedback for a recommendation."""
        recommendation = self.get_object()
        
        # Check if feedback already exists
        existing_feedback = RecommendationFeedback.objects.filter(recommendation=recommendation).first()
        
        if existing_feedback:
            # Update existing feedback
            serializer = RecommendationFeedbackSerializer(existing_feedback, data=request.data, partial=True)
        else:
            # Create new feedback
            serializer = RecommendationFeedbackSerializer(data=request.data)
        
        if serializer.is_valid():
            if not existing_feedback:
                serializer.save(recommendation=recommendation)
            else:
                serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """Manually trigger recommendation refresh for the current user."""
        user_profile = UserProfile.objects.get(user=self.request.user)
        
        # Check if survey is completed
        if not user_profile.survey_completed:
            return Response(
                {'error': 'Please complete the survey first to get recommendations.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Trigger async task to generate recommendations
        task = generate_recommendations_for_user.delay(user_profile.id)
        
        return Response({
            'status': 'success',
            'message': 'Recommendation refresh has been triggered.',
            'task_id': task.id
        })
