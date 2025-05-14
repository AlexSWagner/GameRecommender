import os
import requests
import logging
import time
from django.utils import timezone
from games.models import Game, GameImage
from .image_fetcher import get_image_from_rawg, get_game_cover_image

logger = logging.getLogger(__name__)

def verify_url(url, timeout=3):
    """
    Verify if a URL is accessible.
    
    Args:
        url: The URL to verify
        timeout: Timeout in seconds
        
    Returns:
        bool: True if the URL is valid and accessible, False otherwise
    """
    if not url:
        return False
        
    try:
        # Use head request to avoid downloading the entire image
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        
        # Check if the response is successful and the content type is an image
        if response.status_code == 200 and 'image' in response.headers.get('Content-Type', ''):
            return True
        
        # If head request doesn't return content type, try a small get request
        if response.status_code == 200 and 'Content-Type' not in response.headers:
            img_response = requests.get(url, timeout=timeout, stream=True)
            # Just get the first few bytes to check content type
            for chunk in img_response.iter_content(chunk_size=1024):
                content_type = img_response.headers.get('Content-Type', '')
                return 'image' in content_type
                
        return False
    except Exception as e:
        logger.warning(f"Error verifying URL {url}: {str(e)}")
        return False

def cache_game_image(game):
    """
    Cache the image for a game.
    
    Args:
        game: The Game model instance
        
    Returns:
        GameImage: The cached image instance
    """
    # If the game already has a cached image, use that
    if game.cached_image:
        cached_image = game.cached_image
        
        # If the primary URL is verified and not too old, just return it
        if cached_image.is_verified and cached_image.last_verified:
            # Only reverify if it's been more than 7 days
            age = timezone.now() - cached_image.last_verified
            if age.days < 7:
                return cached_image
    else:
        # Create a new cached image
        identifier = f"{game.title}_{game.id}"
        cached_image, _ = GameImage.objects.get_or_create(
            identifier=identifier
        )
        game.cached_image = cached_image
        game.save(update_fields=['cached_image'])
    
    # If we're here, we need to verify and potentially update the image URLs
    
    # Start with the existing image_url from the game
    if game.image_url and verify_url(game.image_url):
        cached_image.primary_url = game.image_url
        cached_image.is_verified = True
        cached_image.source = "existing"
    else:
        # Try to get an image from RAWG
        rawg_url = get_image_from_rawg(
            game.title, 
            game.release_date.year if game.release_date else None
        )
        
        if rawg_url and verify_url(rawg_url):
            cached_image.primary_url = rawg_url
            cached_image.is_verified = True
            cached_image.source = "RAWG"
        else:
            # Try the generic game cover image fetcher
            cover_url = get_game_cover_image(
                game.title,
                game.release_date.year if game.release_date else None
            )
            
            if cover_url and verify_url(cover_url):
                cached_image.primary_url = cover_url
                cached_image.is_verified = True
                cached_image.source = "fetcher"
    
    # Set sensible fallbacks
    if not cached_image.fallback_url:
        # Wikipedia URLs for popular games
        title_slug = game.title.replace(' ', '_').replace(':', '')
        cached_image.fallback_url = f"https://upload.wikimedia.org/wikipedia/en/c/c6/{title_slug}.jpg"
    
    # Set backup URLs from known good sources for popular games
    known_games = {
        "The Legend of Zelda: Breath of the Wild": "https://upload.wikimedia.org/wikipedia/en/c/c6/The_Legend_of_Zelda_Breath_of_the_Wild.jpg",
        "Red Dead Redemption 2": "https://upload.wikimedia.org/wikipedia/en/4/44/Red_Dead_Redemption_II.jpg",
        "The Witcher 3": "https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg",
        "God of War": "https://upload.wikimedia.org/wikipedia/en/a/a7/God_of_War_4_cover.jpg",
        "Elden Ring": "https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg",
    }
    
    # Check if the game title matches or contains any of the known game titles
    for known_title, known_url in known_games.items():
        if known_title.lower() in game.title.lower() or game.title.lower() in known_title.lower():
            if not cached_image.primary_url:
                cached_image.primary_url = known_url
                cached_image.is_verified = True
                cached_image.source = "known"
            elif not cached_image.backup_url1:
                cached_image.backup_url1 = known_url
            elif not cached_image.backup_url2:
                cached_image.backup_url2 = known_url
    
    # Always update the verification timestamp
    cached_image.last_verified = timezone.now()
    cached_image.save()
    
    return cached_image

def verify_all_game_images(limit=None):
    """
    Verify and cache images for all games.
    
    Args:
        limit: Optional limit to the number of games to process
        
    Returns:
        tuple: (success_count, failure_count)
    """
    # Start with games that have no cached image
    games_without_cache = Game.objects.filter(cached_image__isnull=True)
    if limit:
        games_without_cache = games_without_cache[:limit]
    
    success_count = 0
    failure_count = 0
    
    for game in games_without_cache:
        try:
            cached_image = cache_game_image(game)
            if cached_image and cached_image.is_verified:
                success_count += 1
            else:
                failure_count += 1
        except Exception as e:
            logger.error(f"Error caching image for game {game.title}: {str(e)}")
            failure_count += 1
    
    # Then update older cached images that need verification
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)
    games_with_outdated_cache = Game.objects.filter(
        cached_image__isnull=False,
        cached_image__last_verified__lt=seven_days_ago
    )
    
    remaining = limit - success_count - failure_count if limit else None
    if remaining and remaining > 0:
        games_with_outdated_cache = games_with_outdated_cache[:remaining]
    
    for game in games_with_outdated_cache:
        try:
            cached_image = cache_game_image(game)
            if cached_image and cached_image.is_verified:
                success_count += 1
            else:
                failure_count += 1
        except Exception as e:
            logger.error(f"Error updating cache for game {game.title}: {str(e)}")
            failure_count += 1
    
    return success_count, failure_count 