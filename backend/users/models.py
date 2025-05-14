from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from games.models import Genre, Platform, Game


class UserProfile(models.Model):
    """Extended user profile with additional information."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Basic demographics
    birth_year = models.IntegerField(null=True, blank=True)
    
    # Gaming habits
    hours_per_week = models.IntegerField(null=True, blank=True)
    
    # Platform preferences (ranked by preference)
    preferred_platforms = models.ManyToManyField(Platform, through='PlatformPreference')
    
    # Genre preferences (ranked by preference)
    preferred_genres = models.ManyToManyField(Genre, through='GenrePreference')
    
    # Favorite games
    favorite_games = models.ManyToManyField(Game, related_name='favorited_by', blank=True)
    
    # Games the user has played/rated
    rated_games = models.ManyToManyField(Game, through='GameRating', related_name='ratings')
    
    # Survey completion status
    survey_completed = models.BooleanField(default=False)
    
    # Profile creation and last update times
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"


class PlatformPreference(models.Model):
    """User platform preferences with ranking."""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['rank']
        unique_together = ('user_profile', 'platform')


class GenrePreference(models.Model):
    """User genre preferences with ranking."""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['rank']
        unique_together = ('user_profile', 'genre')


class GameRating(models.Model):
    """User ratings for games they have played."""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # 1-10 scale
    has_played = models.BooleanField(default=True)
    playtime_hours = models.PositiveIntegerField(null=True, blank=True)
    comments = models.TextField(blank=True)
    
    class Meta:
        unique_together = ('user_profile', 'game')
    
    def __str__(self):
        return f"{self.user_profile.user.username}'s rating for {self.game.title}"


class UserGamePreferences(models.Model):
    """Specific user preferences collected through the survey."""
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='game_preferences')
    
    # Game style preferences
    prefers_multiplayer = models.BooleanField(null=True, blank=True)
    prefers_competitive = models.BooleanField(null=True, blank=True)
    prefers_cooperative = models.BooleanField(null=True, blank=True)
    
    # Content preferences
    prefers_story_driven = models.BooleanField(null=True, blank=True)
    prefers_open_world = models.BooleanField(null=True, blank=True)
    prefers_linear = models.BooleanField(null=True, blank=True)
    
    # Gameplay preferences
    difficulty_preference = models.CharField(
        max_length=10,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
            ('variable', 'Variable'),
        ],
        blank=True
    )
    
    # Purchase preferences
    willing_to_pay = models.CharField(
        max_length=20,
        choices=[
            ('free_only', 'Free Only'),
            ('under_20', 'Under $20'),
            ('under_60', 'Under $60'),
            ('any_price', 'Any Price'),
        ],
        blank=True
    )
    
    accepts_in_app_purchases = models.BooleanField(null=True, blank=True)
    
    # Additional preferences as free-form text
    additional_preferences = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user_profile.user.username}'s game preferences"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved."""
    instance.profile.save()
