import os
import sys
import django
import requests
import time
import json

# Add the parent directory to the Python path so we can import Django settings
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from games.models import Game

# RAWG API key
RAWG_API_KEY = os.environ.get('RAWG_API_KEY', '')
print(f"Using RAWG API key: {RAWG_API_KEY[:5]}...")

# Hardcoded reliable image URLs as fallback
GAME_COVER_URLS = {
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
    "Final Fantasy VII Remake": "https://upload.wikimedia.org/wikipedia/en/c/ce/FFVIIRemake.png",
    "Cyberpunk 2077": "https://upload.wikimedia.org/wikipedia/en/9/9f/Cyberpunk_2077_box_art.jpg",
    "Death Stranding": "https://upload.wikimedia.org/wikipedia/en/2/22/Death_Stranding.jpg",
    "Portal 2": "https://upload.wikimedia.org/wikipedia/en/f/f9/Portal2cover.jpg"
}

def update_game_cover(game):
    """Update game cover image directly from RAWG API or fallback to hardcoded URLs"""
    print(f"Updating cover for: {game.title}")
    
    # First check our hardcoded fallback list
    if game.title in GAME_COVER_URLS:
        game.image_url = GAME_COVER_URLS[game.title]
        game.save()
        print(f"✅ Updated with hardcoded image for: {game.title}")
        return True
    
    # Otherwise try RAWG API
    if not RAWG_API_KEY:
        print("No RAWG API key found. Please set RAWG_API_KEY environment variable.")
        return False
        
    # Prepare search URL for RAWG API
    url = f"https://api.rawg.io/api/games"
    params = {
        'key': RAWG_API_KEY,
        'search': game.title,
        'page_size': 5
    }
    
    try:
        print(f"Making request to: {url} with params: search={game.title}")
        response = requests.get(url, params=params)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Debug response
            print(f"Found {len(data.get('results', []))} results")
            
            if 'results' in data and data['results']:
                # Look for best match
                for result in data['results']:
                    if game.title.lower() in result['name'].lower() or result['name'].lower() in game.title.lower():
                        if result.get('background_image'):
                            game.image_url = result['background_image']
                            game.save()
                            print(f"✅ Updated image for: {game.title}")
                            return True
                
                # If no good match, use first result
                if data['results'][0].get('background_image'):
                    game.image_url = data['results'][0]['background_image']
                    game.save()
                    print(f"✅ Used first result for: {game.title}")
                    return True
        else:
            print(f"Error response: {response.text}")
                    
        print(f"❌ No image found for: {game.title}")
        return False
    except Exception as e:
        print(f"❌ Error updating {game.title}: {str(e)}")
        return False

def main():
    # Get all games
    games = Game.objects.all()
    print(f"Found {games.count()} games in database")
    
    # Try to update all games
    updated = 0
    failed = 0
    
    for game in games:
        if update_game_cover(game):
            updated += 1
        else:
            failed += 1
        # Be nice to the API
        time.sleep(0.5)
    
    print(f"Update complete: {updated} updated, {failed} failed")
    
    # Check database status
    games_with_images = Game.objects.exclude(image_url__isnull=True).exclude(image_url='').count()
    print(f"Database status: {games.count()} total games, {games_with_images} with images")

if __name__ == "__main__":
    main() 