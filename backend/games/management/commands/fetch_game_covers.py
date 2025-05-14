import requests
import time
import logging
from django.core.management.base import BaseCommand
from games.models import Game
from django.db.models import Q
from django.conf import settings
import os

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Fetch cover images for games using the RAWG.io API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--api-key',
            type=str,
            help='RAWG API key (can also be set as RAWG_API_KEY environment variable)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of games to process'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Process all games, even those that already have images'
        )

    def handle(self, *args, **options):
        # Get API key from command line, environment, or settings
        api_key = options.get('api_key') or os.environ.get('RAWG_API_KEY') or getattr(settings, 'RAWG_API_KEY', None)
        
        if not api_key:
            self.stdout.write(self.style.ERROR('RAWG API key is required. Set it with --api-key, RAWG_API_KEY environment variable, or in settings.py'))
            return
            
        limit = options.get('limit')
        all_games = options.get('all')
        
        # Get games without images first
        if all_games:
            games_to_process = Game.objects.all().order_by('-metacritic_score')[:limit]
            self.stdout.write(self.style.SUCCESS(f'Processing all games (limit: {limit})'))
        else:
            games_to_process = Game.objects.filter(
                Q(image_url__isnull=True) | Q(image_url='')
            ).order_by('-metacritic_score')[:limit]
            self.stdout.write(self.style.SUCCESS(f'Found {games_to_process.count()} games without images'))
        
        # Process each game
        games_updated = 0
        games_failed = 0
        
        for game in games_to_process:
            self.stdout.write(f'Processing: {game.title}')
            
            try:
                # First try RAWG API
                image_url = self.fetch_from_rawg(game.title, api_key)
                
                if not image_url:
                    # Fallback to IGDB
                    image_url = self.fetch_from_igdb(game.title)
                
                if image_url:
                    game.image_url = image_url
                    game.save()
                    games_updated += 1
                    self.stdout.write(self.style.SUCCESS(f'Updated image for: {game.title}'))
                else:
                    games_failed += 1
                    self.stdout.write(self.style.WARNING(f'No image found for: {game.title}'))
            except Exception as e:
                games_failed += 1
                self.stdout.write(self.style.ERROR(f'Error processing {game.title}: {str(e)}'))
            
            # Respect API rate limits
            time.sleep(0.25)  # 4 requests per second should be safe
        
        # Report results
        self.stdout.write(self.style.SUCCESS(
            f'Finished processing {games_to_process.count()} games. '
            f'Updated: {games_updated}, Failed: {games_failed}'
        ))
        
        # Verify we have enough games with images for display
        games_with_images = Game.objects.exclude(
            Q(image_url__isnull=True) | Q(image_url='')
        ).count()
        
        games_with_scores = Game.objects.exclude(
            metacritic_score__isnull=True
        ).count()
        
        self.stdout.write(self.style.SUCCESS(
            f'Database status: {Game.objects.count()} total games, '
            f'{games_with_images} with images, {games_with_scores} with metacritic scores'
        ))
    
    def fetch_from_rawg(self, game_title, api_key):
        """Fetch game cover from RAWG.io API"""
        try:
            # Make sure we have an API key
            if not api_key:
                self.stdout.write(self.style.ERROR('No RAWG API key provided'))
                return None
                
            self.stdout.write(f"Searching RAWG for '{game_title}'")
            
            base_url = 'https://api.rawg.io/api/games'
            params = {
                'key': api_key,
                'search': game_title,
                'page_size': 5  # We'll check the top 5 results
            }
            
            self.stdout.write(f"Making request to RAWG API with key: {api_key[:5]}...")
            response = requests.get(base_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' in data and len(data['results']) > 0:
                    # Check each result to find the best match
                    for result in data['results']:
                        if result['name'].lower() == game_title.lower() or game_title.lower() in result['name'].lower():
                            # Found a match
                            if result.get('background_image'):
                                self.stdout.write(f'Found match in RAWG: {result["name"]}')
                                return result['background_image']
                    
                    # If no exact match, use the first result
                    if data['results'][0].get('background_image'):
                        self.stdout.write(f'Using first RAWG result: {data["results"][0]["name"]}')
                        return data['results'][0]['background_image']
                
                self.stdout.write(self.style.WARNING(f'No suitable results found in RAWG API for "{game_title}"'))
            else:
                self.stdout.write(self.style.ERROR(f'RAWG API returned {response.status_code}: {response.text}'))
            
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'RAWG API error: {str(e)}'))
            return None
    
    def fetch_from_igdb(self, game_title):
        """Fallback method to get game cover from other sources like searching the web"""
        try:
            # Simple method: search using DuckDuckGo API
            search_url = "https://api.duckduckgo.com/"
            params = {
                'q': f"{game_title} game cover box art",
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1,
                't': 'gamerecommender'
            }
            
            response = requests.get(search_url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for image in the main response
                if 'Image' in data and data['Image']:
                    return data['Image']
                
                # Check results
                if 'Results' in data and data['Results']:
                    for result in data['Results']:
                        if 'Icon' in result and result['Icon'].get('URL'):
                            return result['Icon']['URL']
            
            return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'IGDB fallback error: {str(e)}'))
            return None 