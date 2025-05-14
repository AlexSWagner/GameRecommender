#!/usr/bin/env python
"""
Script to fix database issues including duplicate games and image URLs
"""
import os
import sys
import re
from collections import defaultdict

# Add the project path to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from games.models import Game
from django.db.models import Q, Count

def normalize_title(title):
    """Normalize game title to help identify duplicates"""
    # Remove special characters, convert to lowercase
    normalized = re.sub(r'[^\w\s]', '', title.lower())
    # Remove common words/prefixes like "the", "a", etc.
    normalized = re.sub(r'^(the|a|an)\s+', '', normalized)
    return normalized.strip()

def fix_duplicate_games():
    """
    Fix all duplicate games in the database by identifying similar titles
    and removing duplicates, keeping the entry with more complete information.
    """
    print("Checking for duplicate games...")
    
    # Get all games and group by normalized title
    all_games = Game.objects.all()
    games_by_title = defaultdict(list)
    
    for game in all_games:
        normalized = normalize_title(game.title)
        games_by_title[normalized].append(game)
    
    # Process each group of potential duplicates
    for normalized_title, games in games_by_title.items():
        if len(games) > 1:
            print(f"Found {len(games)} potential duplicates for '{normalized_title}':")
            for g in games:
                print(f"  - ID: {g.id}, Title: '{g.title}', MetaScore: {g.metacritic_score}")
            
            # Keep the game with the highest metacritic score, or most complete data
            keep_game = sorted(games, key=lambda g: (
                g.metacritic_score is not None,             # Games with metacritic score first
                g.metacritic_score if g.metacritic_score else 0,  # Higher score preferred
                g.image_url is not None and g.image_url != '',     # Games with image URLs
                g.description is not None and g.description != '',  # Games with descriptions
                g.release_date is not None,                 # Games with release dates
                len(g.title)                               # Prefer longer titles assuming more complete
            ), reverse=True)[0]
            
            print(f"Keeping game: '{keep_game.title}' (ID: {keep_game.id})")
            
            # Delete the duplicates
            for game in games:
                if game.id != keep_game.id:
                    print(f"Deleting duplicate: '{game.title}' (ID: {game.id})")
                    game.delete()
    
    # Fix the specific Zelda case that we know about
    zelda_games = Game.objects.filter(
        Q(title="Breath of the Wild") | 
        Q(title="The Legend of Zelda: Breath of the Wild")
    )
    
    if zelda_games.count() >= 2:
        print(f"Found {zelda_games.count()} Zelda Breath of the Wild games")
        
        # Keep the one with more complete data, or the "The Legend of Zelda: Breath of the Wild"
        keep_game = None
        delete_games = []
        
        for game in zelda_games:
            if game.title == "The Legend of Zelda: Breath of the Wild":
                keep_game = game
        
        # If we didn't find the full title, pick the first one
        if not keep_game and zelda_games:
            keep_game = zelda_games.first()
            # Update its title to the full version
            keep_game.title = "The Legend of Zelda: Breath of the Wild"
            keep_game.save()
            
        # Mark other games for deletion
        for game in zelda_games:
            if game.id != keep_game.id:
                delete_games.append(game)
        
        # Delete the duplicates
        for game in delete_games:
            print(f"Deleting duplicate Zelda game: {game.title} (ID: {game.id})")
            game.delete()
            
        print(f"Kept Zelda game: {keep_game.title} (ID: {keep_game.id})")
    else:
        print("No duplicate Zelda games found")

def fix_missing_cover_art():
    """Fix missing cover art for all games"""
    
    # Popular game covers from Wikipedia or other reliable sources
    # This is a larger set of cover art for popular games
    cover_fixes = {
        "Baldur's Gate 3": "https://upload.wikimedia.org/wikipedia/en/0/0e/Baldurs_Gate_3_cover_art.jpg",
        "Disco Elysium: The Final Cut": "https://upload.wikimedia.org/wikipedia/en/0/01/Disco_Elysium.jpg",
        "The Witcher 3: Wild Hunt": "https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg",
        "Elden Ring": "https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg",
        "God of War": "https://upload.wikimedia.org/wikipedia/en/a/a7/God_of_War_4_cover.jpg",
        "Red Dead Redemption 2": "https://upload.wikimedia.org/wikipedia/en/4/44/Red_Dead_Redemption_II.jpg",
        "Cyberpunk 2077": "https://upload.wikimedia.org/wikipedia/en/9/9f/Cyberpunk_2077_box_art.jpg",
        "Grand Theft Auto V": "https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png",
        "The Last of Us Part II": "https://upload.wikimedia.org/wikipedia/en/4/4f/TLOU_P2_Box_Art_2.png",
        "Ghost of Tsushima": "https://upload.wikimedia.org/wikipedia/en/b/b6/Ghost_of_Tsushima.jpg",
        "Hades": "https://upload.wikimedia.org/wikipedia/en/c/cc/Hades_cover_art.jpg",
        "Skyrim": "https://upload.wikimedia.org/wikipedia/en/1/15/The_Elder_Scrolls_V_Skyrim_cover.png",
        "The Elder Scrolls V: Skyrim": "https://upload.wikimedia.org/wikipedia/en/1/15/The_Elder_Scrolls_V_Skyrim_cover.png",
        "Mass Effect Legendary Edition": "https://upload.wikimedia.org/wikipedia/en/9/93/Mass_Effect_Legendary_Edition.jpeg",
        "Horizon Zero Dawn": "https://upload.wikimedia.org/wikipedia/en/9/93/Horizon_Zero_Dawn.jpg",
        "Half-Life: Alyx": "https://upload.wikimedia.org/wikipedia/en/1/15/Half-Life_Alyx_Cover_Art.jpg",
        "Death Stranding": "https://upload.wikimedia.org/wikipedia/en/2/22/Death_Stranding.jpg",
        "Control": "https://upload.wikimedia.org/wikipedia/en/a/a3/Control_game_cover_art.jpg",
        "Sekiro: Shadows Die Twice": "https://upload.wikimedia.org/wikipedia/en/6/6e/Sekiro_art.jpg",
        "Doom Eternal": "https://upload.wikimedia.org/wikipedia/en/9/9d/Cover_Art_of_Doom_Eternal.png",
        "Final Fantasy VII Remake": "https://upload.wikimedia.org/wikipedia/en/c/ce/FFVIIRemake.png",
        "Hellblade: Senua's Sacrifice": "https://upload.wikimedia.org/wikipedia/en/f/f1/Hellblade_-_Senua%27s_Sacrifice.jpg",
        "Stardew Valley": "https://upload.wikimedia.org/wikipedia/en/f/fd/Logo_of_Stardew_Valley.png",
        "Marvel's Spider-Man": "https://upload.wikimedia.org/wikipedia/en/e/e1/Spider-Man_PS4_cover.jpg",
        "Hollow Knight": "https://upload.wikimedia.org/wikipedia/en/c/c0/Hollow_Knight_cover.jpg",
        "Portal 2": "https://upload.wikimedia.org/wikipedia/en/f/f9/Portal2cover.jpg",
        "Celeste": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Celeste_box_art_full.png",
        "Dark Souls III": "https://upload.wikimedia.org/wikipedia/en/b/bb/Dark_Souls_III_cover_art.jpg",
        "Bloodborne": "https://upload.wikimedia.org/wikipedia/en/6/68/Bloodborne_Cover_Artwork.jpg",
        "Monster Hunter: World": "https://upload.wikimedia.org/wikipedia/en/1/1b/Monster_Hunter_World_cover_art.jpg",
        "NieR: Automata": "https://upload.wikimedia.org/wikipedia/en/2/21/Nier_Automata_cover_art.jpg",
        "Resident Evil 2": "https://upload.wikimedia.org/wikipedia/en/f/fd/Resident_Evil_2_Remake.jpg",
        "Resident Evil Village": "https://upload.wikimedia.org/wikipedia/en/2/2c/Resident_Evil_Village.png",
        "Ori and the Will of the Wisps": "https://upload.wikimedia.org/wikipedia/en/9/94/Ori_and_the_Will_of_the_Wisps.jpg",
        "Ori and the Blind Forest": "https://upload.wikimedia.org/wikipedia/en/b/b2/Ori_and_the_Blind_Forest_Logo.jpg",
        "Persona 5 Royal": "https://upload.wikimedia.org/wikipedia/en/b/b0/Persona_5_Royal_cover_art.jpg",
        "Persona 5": "https://upload.wikimedia.org/wikipedia/en/b/b0/Persona_5_cover_art.jpg",
        "Halo Infinite": "https://upload.wikimedia.org/wikipedia/en/1/14/Halo_Infinite.png",
        "Among Us": "https://upload.wikimedia.org/wikipedia/en/9/9a/Among_Us_cover_art.jpg",
        "Death's Door": "https://upload.wikimedia.org/wikipedia/en/8/8a/Death%27s_Door_cover_art.jpg"
    }
    
    # First, apply specific fixes
    for title, image_url in cover_fixes.items():
        games = Game.objects.filter(title=title)
        if games:
            for game in games:
                if not game.image_url or game.image_url.strip() == '':
                    game.image_url = image_url
                    game.save()
                    print(f"Fixed cover art for {game.title}")
        else:
            print(f"Game not found: {title}")
    
    # Next, find all games with missing cover art
    games_without_art = Game.objects.filter(Q(image_url__isnull=True) | Q(image_url=''))
    
    if games_without_art:
        print(f"Found {games_without_art.count()} games without cover art")
        print("These games need manual cover art assignments:")
        for game in games_without_art:
            print(f"  - {game.title}")
    else:
        print("All games have cover art!")

def ensure_quality_data():
    """Ensure a minimum number of high-quality games with complete data"""
    
    # Find games with metacritic scores sorted by highest score
    top_rated_games = Game.objects.exclude(metacritic_score__isnull=True).order_by('-metacritic_score')
    
    if top_rated_games.count() < 50:
        print(f"WARNING: Only {top_rated_games.count()} games with metacritic scores in database")
        print("Database should have at least 50 high-quality games with scores and cover art")
    else:
        print(f"Database has {top_rated_games.count()} games with metacritic scores")
    
    # Check that top 50 games all have cover art
    # First get the top 50 ids, then filter those games for missing art
    if top_rated_games.count() > 0:
        top_ids = list(top_rated_games.values_list('id', flat=True)[:50])
        missing_art_count = Game.objects.filter(id__in=top_ids).filter(Q(image_url__isnull=True) | Q(image_url='')).count()
        if missing_art_count > 0:
            print(f"WARNING: {missing_art_count} of top 50 rated games are missing cover art")
        else:
            print("All top 50 rated games have cover art - good!")

if __name__ == "__main__":
    fix_duplicate_games()
    fix_missing_cover_art()
    ensure_quality_data()
    print("Database fixes completed") 