import requests
import re
import time
import logging
from django.core.management.base import BaseCommand
from games.models import Game
from django.db.models import Q

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Populate image URLs for games from online sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of games to process'
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        
        # Find games without images
        games_without_images = Game.objects.filter(
            Q(image_url__isnull=True) | Q(image_url='')
        ).order_by('-metacritic_score')[:limit]
        
        self.stdout.write(self.style.SUCCESS(f'Found {games_without_images.count()} games without images'))
        
        # Update sources dictionary with reliable image sources
        image_sources = {
            "The Legend of Zelda: Breath of the Wild": "https://upload.wikimedia.org/wikipedia/en/c/c6/The_Legend_of_Zelda_Breath_of_the_Wild.jpg",
            "Red Dead Redemption 2": "https://upload.wikimedia.org/wikipedia/en/4/44/Red_Dead_Redemption_II.jpg",
            "The Witcher 3: Wild Hunt": "https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg",
            "God of War": "https://upload.wikimedia.org/wikipedia/en/a/a7/God_of_War_4_cover.jpg",
            "Elden Ring": "https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg",
            "Persona 5 Royal": "https://upload.wikimedia.org/wikipedia/en/b/b0/Persona_5_Royal_cover_art.jpg",
            "The Last of Us Part II": "https://upload.wikimedia.org/wikipedia/en/4/4f/TLOU_P2_Box_Art_2.png",
            "Sekiro: Shadows Die Twice": "https://upload.wikimedia.org/wikipedia/en/6/6e/Sekiro_art.jpg",
            "Hades": "https://upload.wikimedia.org/wikipedia/en/c/cc/Hades_cover_art.jpg",
            "Disco Elysium: The Final Cut": "https://upload.wikimedia.org/wikipedia/en/0/01/Disco_Elysium.jpg",
            "Mass Effect Legendary Edition": "https://upload.wikimedia.org/wikipedia/en/9/93/Mass_Effect_Legendary_Edition.jpeg",
            "Ghost of Tsushima": "https://upload.wikimedia.org/wikipedia/en/b/b6/Ghost_of_Tsushima.jpg",
            "Baldur's Gate 3": "https://upload.wikimedia.org/wikipedia/en/0/0e/Baldurs_Gate_3_cover_art.jpg",
            "Hollow Knight": "https://upload.wikimedia.org/wikipedia/en/c/c0/Hollow_Knight_cover.jpg",
            "Celeste": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Celeste_box_art_full.png",
            "Stardew Valley": "https://upload.wikimedia.org/wikipedia/en/f/fd/Logo_of_Stardew_Valley.png",
        }
        
        # Update games with images from our reliable sources
        for game in games_without_images:
            if game.title in image_sources:
                self.stdout.write(f'Found known image for: {game.title}')
                game.image_url = image_sources[game.title]
                game.save()
                continue
                
            # For other games, try to find images online
            # Strategy 1: Search Wikipedia
            try:
                self.stdout.write(f'Searching for image for: {game.title}')
                clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', game.title)
                search_query = f"{clean_title} video game cover art wikipedia"
                
                # Try to find on Wikipedia through Google search
                self.search_and_update_wikipedia_image(game)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error searching for {game.title}: {str(e)}'))
            
            # Avoid hitting rate limits
            time.sleep(0.5)
        
        # Count how many still need images
        remaining_without_images = Game.objects.filter(
            Q(image_url__isnull=True) | Q(image_url='')
        ).count()
        
        self.stdout.write(self.style.SUCCESS(
            f'Finished populating images. {games_without_images.count() - remaining_without_images} '
            f'games updated, {remaining_without_images} still need images.'
        ))
    
    def search_and_update_wikipedia_image(self, game):
        """Search for game cover art on Wikipedia and update the game if found"""
        clean_title = re.sub(r'[^a-zA-Z0-9\s]', '', game.title)
        
        # Try different search patterns to find the image
        search_patterns = [
            f"https://en.wikipedia.org/wiki/{clean_title.replace(' ', '_')}",
            f"https://en.wikipedia.org/wiki/{clean_title.replace(' ', '_')}_(video_game)",
        ]
        
        for url in search_patterns:
            try:
                # Try to fetch the Wikipedia page
                self.stdout.write(f'Trying URL: {url}')
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'}
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    # Look for image file in the content
                    image_pattern = r'(https://upload\.wikimedia\.org/wikipedia/(?:en|commons)/[a-zA-Z0-9/_\-.%]+\.(jpg|png|jpeg))'
                    matches = re.findall(image_pattern, response.text)
                    
                    if matches and len(matches) > 0:
                        # Use the first image found (likely to be the cover art)
                        image_url = matches[0][0]  # Extract the URL from the tuple
                        self.stdout.write(self.style.SUCCESS(f'Found image for {game.title}: {image_url}'))
                        
                        # Update the game
                        game.image_url = image_url
                        game.save()
                        return True
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error fetching {url}: {str(e)}'))
                continue
        
        # If no image was found on Wikipedia, try a more general approach
        # This could be expanded with other sources or APIs
        self.stdout.write(self.style.WARNING(f'No image found for {game.title} on Wikipedia'))
        return False 