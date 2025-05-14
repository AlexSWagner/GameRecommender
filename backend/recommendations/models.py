from django.db import models
from games.models import Game
from users.models import UserProfile


class GameRecommendation(models.Model):
    """Model for storing personalized game recommendations for users."""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='recommendations')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='recommended_to')
    score = models.FloatField()  # Recommendation score/confidence (higher = more confident)
    reason = models.TextField(blank=True)  # Explanation for why this game was recommended
    
    # Recommendation timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    # User interactions with recommendation
    viewed = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)
    saved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-score']
        unique_together = ('user_profile', 'game')
    
    def __str__(self):
        return f"Recommendation of {self.game.title} for {self.user_profile.user.username}"


class RecommendationFeedback(models.Model):
    """User feedback on game recommendations."""
    recommendation = models.OneToOneField(GameRecommendation, on_delete=models.CASCADE, related_name='feedback')
    
    # Rating of the recommendation itself (not the game)
    RATING_CHOICES = [
        ('very_bad', 'Very Bad Recommendation'),
        ('bad', 'Bad Recommendation'),
        ('neutral', 'Neutral'),
        ('good', 'Good Recommendation'),
        ('very_good', 'Very Good Recommendation'),
    ]
    rating = models.CharField(max_length=10, choices=RATING_CHOICES)
    
    # Feedback details
    has_played = models.BooleanField(null=True, blank=True)  # Has the user already played this game?
    interested = models.BooleanField(null=True, blank=True)  # Is the user interested in this game?
    comments = models.TextField(blank=True)  # User comments about the recommendation
    
    # Feedback timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback on {self.recommendation}"
