from django.db import models

# Create your models here.

class Genre(models.Model):
    """Genre model for game categorization."""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class Platform(models.Model):
    """Platform model for game availability."""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name


class GameImage(models.Model):
    """Model for caching game cover images."""
    # A unique identifier for the image (game_title, etc.)
    identifier = models.CharField(max_length=255, unique=True, db_index=True)
    
    # Primary image URL - this is the working URL we've verified
    primary_url = models.URLField(blank=True)
    
    # Backup image URLs in case primary fails
    backup_url1 = models.URLField(blank=True)
    backup_url2 = models.URLField(blank=True)
    
    # Fallback image URL if everything else fails
    fallback_url = models.URLField(blank=True)
    
    # Track when image URLs were last verified
    last_verified = models.DateTimeField(null=True, blank=True)
    
    # Track if this has been verified as working
    is_verified = models.BooleanField(default=False)
    
    # Track image source
    source = models.CharField(max_length=50, blank=True)  # e.g., "RAWG", "IGDB", "local"
    
    # Creation and update timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Image for {self.identifier}"
    
    def get_best_url(self):
        """Returns the best available URL, falling back as needed."""
        if self.is_verified and self.primary_url:
            return self.primary_url
        elif self.backup_url1:
            return self.backup_url1
        elif self.backup_url2:
            return self.backup_url2
        elif self.fallback_url:
            return self.fallback_url
        else:
            # Return a default placeholder if nothing else is available
            return "https://via.placeholder.com/300x400?text=No+Game+Image"


class Game(models.Model):
    """Game model for storing game information."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    developer = models.CharField(max_length=255, blank=True)
    genres = models.ManyToManyField(Genre, related_name='games')
    platforms = models.ManyToManyField(Platform, related_name='games')
    
    # Game metrics
    rating = models.FloatField(null=True, blank=True)  # Overall rating (e.g., 0-10)
    metacritic_score = models.IntegerField(null=True, blank=True)
    user_score = models.FloatField(null=True, blank=True)
    
    # Game characteristics
    is_multiplayer = models.BooleanField(default=False)
    has_in_app_purchases = models.BooleanField(default=False)
    is_free_to_play = models.BooleanField(default=False)
    age_rating = models.CharField(max_length=10, blank=True)  # e.g., "E", "T", "M"
    
    # Game media
    image_url = models.URLField(blank=True)
    cached_image = models.ForeignKey(GameImage, null=True, blank=True, on_delete=models.SET_NULL, related_name='games')
    trailer_url = models.URLField(blank=True)
    
    # Scraping metadata
    source_url = models.URLField(blank=True)  # URL where data was scraped from
    source_name = models.CharField(max_length=100, blank=True)  # Name of the source (e.g., "Steam", "IGN")
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-release_date', 'title']
    
    def get_image_url(self):
        """Get the best available image URL."""
        if self.cached_image:
            return self.cached_image.get_best_url()
        return self.image_url or "https://via.placeholder.com/300x400?text=No+Game+Image"


class GameReview(models.Model):
    """Model for storing game reviews from external sources."""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    source = models.CharField(max_length=100)  # e.g., "IGN", "GameSpot"
    author = models.CharField(max_length=100, blank=True)
    rating = models.FloatField(null=True, blank=True)
    content = models.TextField(blank=True)
    review_date = models.DateField(null=True, blank=True)
    url = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.source} review for {self.game.title}"
