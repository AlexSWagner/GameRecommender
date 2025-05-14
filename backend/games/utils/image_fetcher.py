import os
import requests
import logging
import time
from django.conf import settings
import urllib.parse

logger = logging.getLogger(__name__)

class IGDBImageFetcher:
    """
    Utility class to fetch game cover images from IGDB API
    """
    
    BASE_URL = "https://api.igdb.com/v4"
    COVER_URL_TEMPLATE = "https://images.igdb.com/igdb/image/upload/t_cover_big/{}.jpg"
    
    def __init__(self):
        # IGDB credentials
        self.client_id = os.environ.get('IGDB_CLIENT_ID', '')
        self.client_secret = os.environ.get('IGDB_CLIENT_SECRET', '')
        self.access_token = None
        self.token_expires = 0
        
        # Check if credentials are set
        if not self.client_id or not self.client_secret:
            logger.warning("IGDB credentials not set. Set IGDB_CLIENT_ID and IGDB_CLIENT_SECRET environment variables.")
    
    def _authenticate(self):
        """Get access token from Twitch/IGDB API"""
        if self.access_token and time.time() < self.token_expires:
            return True
            
        url = f"https://id.twitch.tv/oauth2/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            data = response.json()
            
            self.access_token = data.get('access_token')
            # Set expiry time (usually 60 days, but we'll use a bit less to be safe)
            self.token_expires = time.time() + (data.get('expires_in', 86400) - 100)
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with IGDB: {str(e)}")
            return False
    
    def search_game(self, game_title, release_year=None):
        """
        Search for a game by title and optionally release year
        
        Args:
            game_title: Title of the game
            release_year: Optional release year to narrow search
            
        Returns:
            Dict containing game data if found, None otherwise
        """
        if not self._authenticate():
            logger.error("Authentication failed, cannot search for game")
            return None
            
        # Build the search query
        query = f'search "{game_title}"; fields name,cover,first_release_date;'
        if release_year:
            # IGDB timestamps are in Unix epoch seconds
            # Create a range from start to end of the year
            year_start = f"{release_year}-01-01"
            year_end = f"{release_year}-12-31"
            timestamp_start = int(time.mktime(time.strptime(year_start, "%Y-%m-%d")))
            timestamp_end = int(time.mktime(time.strptime(year_end, "%Y-%m-%d")))
            query = f'search "{game_title}"; fields name,cover,first_release_date; where first_release_date >= {timestamp_start} & first_release_date <= {timestamp_end};'
        
        # Make the API request
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        try:
            response = requests.post(f"{self.BASE_URL}/games", headers=headers, data=query)
            response.raise_for_status()
            games = response.json()
            
            # Return the first result if any
            if games and len(games) > 0:
                return games[0]
            return None
        except Exception as e:
            logger.error(f"Error searching for game '{game_title}': {str(e)}")
            return None
    
    def get_cover_url(self, game_title, release_year=None):
        """
        Get the cover image URL for a game
        
        Args:
            game_title: Title of the game
            release_year: Optional release year
            
        Returns:
            Cover image URL if found, None otherwise
        """
        # Search for the game
        game = self.search_game(game_title, release_year)
        if not game or 'cover' not in game:
            return None
            
        # Get cover ID
        cover_id = game['cover']
        
        # Get cover details
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        try:
            query = f'fields image_id; where id = {cover_id};'
            response = requests.post(f"{self.BASE_URL}/covers", headers=headers, data=query)
            response.raise_for_status()
            covers = response.json()
            
            if covers and len(covers) > 0 and 'image_id' in covers[0]:
                image_id = covers[0]['image_id']
                return self.COVER_URL_TEMPLATE.format(image_id)
            return None
        except Exception as e:
            logger.error(f"Error fetching cover details for game '{game_title}': {str(e)}")
            return None

    def fallback_search(self, game_title):
        """
        Fallback method to search for a game image using a generic API
        
        Args:
            game_title: Title of the game
            
        Returns:
            Image URL if found, None otherwise
        """
        # Try with Wikipedia first - most reliable source
        try:
            # Use basic URL patterns for popular games on Wikipedia
            # This is more reliable than complex API parsing
            sanitized_title = game_title.replace(' ', '_').replace(':', '')
            potential_urls = [
                f"https://upload.wikimedia.org/wikipedia/en/c/c6/{sanitized_title}.jpg",
                f"https://upload.wikimedia.org/wikipedia/en/0/0c/{sanitized_title}.jpg",
                f"https://upload.wikimedia.org/wikipedia/en/4/44/{sanitized_title}.jpg",
                f"https://upload.wikimedia.org/wikipedia/en/a/a7/{sanitized_title}.jpg",
                f"https://upload.wikimedia.org/wikipedia/en/b/b9/{sanitized_title}.jpg"
            ]
            
            for url in potential_urls:
                # Check if image exists
                response = requests.head(url)
                if response.status_code == 200:
                    return url
        except Exception as e:
            logger.error(f"Error in Wikipedia fallback for '{game_title}': {str(e)}")
        
        # If Wikipedia approach doesn't work, try with SERP API
        try:
            search_term = f"{game_title} game cover"
            serp_api_key = os.environ.get('SERP_API_KEY', '')
            
            if serp_api_key:
                url = f"https://serpapi.com/search.json?q={urllib.parse.quote(search_term)}&tbm=isch&ijn=0&api_key={serp_api_key}"
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if 'images_results' in data and len(data['images_results']) > 0:
                        return data['images_results'][0]['original']
        except Exception as e:
            logger.error(f"Error in SERP API fallback for '{game_title}': {str(e)}")
        
        # Last resort: try with hard-coded common game covers
        common_games = {
            "The Legend of Zelda: Breath of the Wild": "https://upload.wikimedia.org/wikipedia/en/c/c6/The_Legend_of_Zelda_Breath_of_the_Wild.jpg",
            "Red Dead Redemption 2": "https://upload.wikimedia.org/wikipedia/en/4/44/Red_Dead_Redemption_II.jpg",
            "The Witcher 3: Wild Hunt": "https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg",
            "God of War": "https://upload.wikimedia.org/wikipedia/en/a/a7/God_of_War_4_cover.jpg",
            "Elden Ring": "https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg",
            "Horizon Zero Dawn": "https://upload.wikimedia.org/wikipedia/en/9/93/Horizon_Zero_Dawn.jpg",
            "Cyberpunk 2077": "https://upload.wikimedia.org/wikipedia/en/9/9f/Cyberpunk_2077_box_art.jpg"
        }
        
        # Check if title is in our common games dictionary
        for common_title, image_url in common_games.items():
            if game_title.lower() in common_title.lower() or common_title.lower() in game_title.lower():
                return image_url
        
        # We've tried everything and found nothing
        return None


def get_image_from_rawg(game_title, release_year=None):
    """
    Get a game cover image from RAWG.io API
    This doesn't require API keys for basic usage and has a good database of games
    
    Args:
        game_title: Title of the game
        release_year: Optional release year
        
    Returns:
        Image URL if found, None otherwise
    """
    try:
        # Get API key from environment
        api_key = os.environ.get('RAWG_API_KEY', '')
        if not api_key:
            logger.warning("RAWG API key not set. Set RAWG_API_KEY environment variable.")
            return None
            
        # Encode the game title for URL
        encoded_title = urllib.parse.quote(game_title)
        
        # Build query parameters
        params = f"?key={api_key}&search={encoded_title}&page_size=5"
        if release_year:
            params += f"&dates={release_year}-01-01,{release_year}-12-31"
            
        # Make request to RAWG API
        url = f"https://api.rawg.io/api/games{params}"
        headers = {
            'User-Agent': 'GameRecommenderApp/1.0'
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Look for matching games
        if data and 'results' in data and len(data['results']) > 0:
            for game in data['results']:
                # Try to find a close match
                if game_title.lower() in game['name'].lower() or game['name'].lower() in game_title.lower():
                    # Return the background image or screenshot
                    if game.get('background_image'):
                        # Verify image URL is accessible
                        try:
                            img_response = requests.head(game['background_image'], timeout=3)
                            if img_response.status_code == 200:
                                return game['background_image']
                        except Exception as e:
                            logger.warning(f"Image URL check failed: {str(e)}")
            
            # If no close match found, just return the first result's image
            if data['results'][0].get('background_image'):
                # Verify image URL is accessible
                try:
                    img_response = requests.head(data['results'][0]['background_image'], timeout=3)
                    if img_response.status_code == 200:
                        return data['results'][0]['background_image']
                except Exception as e:
                    logger.warning(f"Image URL check failed: {str(e)}")
                
        return None
    except Exception as e:
        logger.error(f"Error fetching image from RAWG for '{game_title}': {str(e)}")
        return None


# Helper function to get cover image for a game
def get_game_cover_image(game_title, release_year=None):
    """
    Get a cover image URL for a game
    
    Args:
        game_title: Title of the game
        release_year: Optional release year
        
    Returns:
        Image URL if found, None otherwise
    """
    # Try RAWG.io first (no API key needed)
    rawg_image = get_image_from_rawg(game_title, release_year)
    if rawg_image:
        return rawg_image
    
    # Then try IGDB
    fetcher = IGDBImageFetcher()
    cover_url = fetcher.get_cover_url(game_title, release_year)
    if cover_url:
        return cover_url
    
    # Last fallback to other search
    return fetcher.fallback_search(game_title) 