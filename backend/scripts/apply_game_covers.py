#!/usr/bin/env python
"""
Script to apply hand-picked game cover images directly to games in the database
"""
import os
import sys

# Add the project path to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from games.models import Game

# Hand-picked game cover images for popular titles
GAME_COVERS = {
    "Starfield": "https://upload.wikimedia.org/wikipedia/en/7/74/Starfield_game_cover.jpg",
    "Baldur's Gate 3": "https://upload.wikimedia.org/wikipedia/en/0/0e/Baldurs_Gate_3_cover_art.jpg",
    "Elden Ring": "https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg",
    "God of War": "https://upload.wikimedia.org/wikipedia/en/a/a7/God_of_War_4_cover.jpg",
    "Disco Elysium": "https://upload.wikimedia.org/wikipedia/en/0/01/Disco_Elysium.jpg",
    "Cyberpunk 2077": "https://upload.wikimedia.org/wikipedia/en/9/9f/Cyberpunk_2077_box_art.jpg",
    "Hades": "https://upload.wikimedia.org/wikipedia/en/c/cc/Hades_cover_art.jpg",
    "Half-Life: Alyx": "https://upload.wikimedia.org/wikipedia/en/7/77/Half-Life_Alyx_Cover_Art.jpg",
    "Sekiro": "https://upload.wikimedia.org/wikipedia/en/6/6e/Sekiro_art.jpg",
    "Red Dead Redemption 2": "https://upload.wikimedia.org/wikipedia/en/4/44/Red_Dead_Redemption_II.jpg",
    "Breath of the Wild": "https://upload.wikimedia.org/wikipedia/en/c/c6/The_Legend_of_Zelda_Breath_of_the_Wild.jpg",
    "Hollow Knight": "https://upload.wikimedia.org/wikipedia/en/c/c0/Hollow_Knight_cover.jpg",
    "The Witcher 3": "https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg",
    "Minecraft": "https://upload.wikimedia.org/wikipedia/en/5/51/Minecraft_cover.png",
    "Portal 2": "https://upload.wikimedia.org/wikipedia/en/f/f9/Portal2cover.jpg",
    "The Last of Us": "https://upload.wikimedia.org/wikipedia/en/4/46/Video_Game_Cover_-_The_Last_of_Us.jpg",
    "Horizon Zero Dawn": "https://upload.wikimedia.org/wikipedia/en/9/93/Horizon_Zero_Dawn.jpg",
    "Control": "https://upload.wikimedia.org/wikipedia/en/8/88/Control_cover_art.jpg",
    "Doom Eternal": "https://upload.wikimedia.org/wikipedia/en/9/9d/Cover_Art_of_Doom_Eternal.png",
    "Death Stranding": "https://upload.wikimedia.org/wikipedia/en/2/22/Death_Stranding.jpg",
    "Dark Souls": "https://upload.wikimedia.org/wikipedia/en/8/8d/Dark_Souls_Cover_Art.jpg",
    "Bloodborne": "https://upload.wikimedia.org/wikipedia/en/6/68/Bloodborne_Cover_Wallpaper.jpg",
    "Ghost of Tsushima": "https://upload.wikimedia.org/wikipedia/en/b/b6/Ghost_of_Tsushima.jpg"
}

def apply_game_covers():
    """Apply hand-picked game cover images to games in the database"""
    # Get all games
    games = Game.objects.all()
    updated_count = 0
    
    print(f"Found {games.count()} games in database")
    
    for game in games:
        # Try exact title match first
        if game.title in GAME_COVERS:
            game.image_url = GAME_COVERS[game.title]
            game.save()
            print(f"Updated cover for {game.title}")
            updated_count += 1
            continue
        
        # Try partial matches
        for title, url in GAME_COVERS.items():
            if (title.lower() in game.title.lower() or 
                game.title.lower() in title.lower()):
                game.image_url = url
                game.save()
                print(f"Updated cover for {game.title} (matched with {title})")
                updated_count += 1
                break
    
    print(f"Updated {updated_count} games with hand-picked covers")

if __name__ == "__main__":
    apply_game_covers() 