#!/usr/bin/env python
"""
Script to add high-quality top-rated games to the database
"""
import os
import sys

# Add the project path to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from games.models import Game, Genre
from django.db.models import Q

def add_or_update_genre(name):
    """Add a genre if it doesn't exist, or get the existing one"""
    genre, created = Genre.objects.get_or_create(name=name)
    return genre

def add_top_rated_games():
    """Add or update top-rated games in the database"""
    
    # List of top-rated games with complete information
    top_games = [
        {
            "title": "The Legend of Zelda: Breath of the Wild",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/c/c6/The_Legend_of_Zelda_Breath_of_the_Wild.jpg",
            "release_date": "2017-03-03",
            "metacritic_score": 97,
            "description": "An open-world action-adventure game where Link awakens from a 100-year slumber to defeat Calamity Ganon.",
            "publisher": "Nintendo",
            "developer": "Nintendo EPD",
            "genres": ["Action", "Adventure", "RPG"],
        },
        {
            "title": "Red Dead Redemption 2",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/4/44/Red_Dead_Redemption_II.jpg",
            "release_date": "2018-10-26",
            "metacritic_score": 97,
            "description": "An epic tale of life in America's unforgiving heartland, following outlaw Arthur Morgan and the Van der Linde gang.",
            "publisher": "Rockstar Games",
            "developer": "Rockstar Games",
            "genres": ["Action", "Adventure", "Open World"],
        },
        {
            "title": "The Witcher 3: Wild Hunt",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/0/0c/Witcher_3_cover_art.jpg",
            "release_date": "2015-05-19",
            "metacritic_score": 93,
            "description": "A story-driven, open world RPG set in a visually stunning fantasy universe full of meaningful choices and impactful consequences.",
            "publisher": "CD Projekt",
            "developer": "CD Projekt Red",
            "genres": ["Action", "RPG", "Open World"],
        },
        {
            "title": "God of War",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/a/a7/God_of_War_4_cover.jpg",
            "release_date": "2018-04-20",
            "metacritic_score": 94,
            "description": "A third-person action-adventure game that follows Kratos and his son Atreus on a journey through Norse realms.",
            "publisher": "Sony Interactive Entertainment",
            "developer": "Santa Monica Studio",
            "genres": ["Action", "Adventure"],
        },
        {
            "title": "Elden Ring",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg",
            "release_date": "2022-02-25",
            "metacritic_score": 96,
            "description": "An action RPG set in a vast, interconnected world designed by Hidetaka Miyazaki and George R.R. Martin.",
            "publisher": "Bandai Namco Entertainment",
            "developer": "FromSoftware",
            "genres": ["Action", "RPG", "Open World"],
        },
        {
            "title": "Persona 5 Royal",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/b/b0/Persona_5_Royal_cover_art.jpg",
            "release_date": "2020-03-31",
            "metacritic_score": 95,
            "description": "A JRPG where players take on the role of a high school student who leads a group of vigilantes called the Phantom Thieves.",
            "publisher": "Atlus",
            "developer": "P-Studio",
            "genres": ["RPG", "JRPG", "Turn-based Strategy"],
        },
        {
            "title": "The Last of Us Part II",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/4/4f/TLOU_P2_Box_Art_2.png",
            "release_date": "2020-06-19",
            "metacritic_score": 93,
            "description": "A story of vengeance and the consequences of violence in a post-apocalyptic United States.",
            "publisher": "Sony Interactive Entertainment",
            "developer": "Naughty Dog",
            "genres": ["Action", "Adventure", "Survival Horror"],
        },
        {
            "title": "Sekiro: Shadows Die Twice",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/6/6e/Sekiro_art.jpg",
            "release_date": "2019-03-22",
            "metacritic_score": 90,
            "description": "An action-adventure game set in Sengoku period Japan, following a shinobi seeking revenge against a samurai clan.",
            "publisher": "Activision",
            "developer": "FromSoftware",
            "genres": ["Action", "Adventure"],
        },
        {
            "title": "Hades",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/c/cc/Hades_cover_art.jpg",
            "release_date": "2020-09-17",
            "metacritic_score": 93,
            "description": "A rogue-like dungeon crawler where you defy the god of the dead as you hack and slash out of the Underworld.",
            "publisher": "Supergiant Games",
            "developer": "Supergiant Games",
            "genres": ["Action", "Rogue-like"],
        },
        {
            "title": "Disco Elysium: The Final Cut",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/0/01/Disco_Elysium.jpg",
            "release_date": "2021-03-30",
            "metacritic_score": 97,
            "description": "A groundbreaking role-playing game where you play as a detective with a unique skill system and a world that reacts to your choices.",
            "publisher": "ZA/UM",
            "developer": "ZA/UM",
            "genres": ["RPG", "Adventure"],
        },
        {
            "title": "Mass Effect Legendary Edition",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/9/93/Mass_Effect_Legendary_Edition.jpeg",
            "release_date": "2021-05-14",
            "metacritic_score": 90,
            "description": "A remastered collection of the Mass Effect trilogy, with improved visuals and gameplay adjustments.",
            "publisher": "Electronic Arts",
            "developer": "BioWare",
            "genres": ["Action", "RPG", "Third-person Shooter"],
        },
        {
            "title": "Ghost of Tsushima",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/b/b6/Ghost_of_Tsushima.jpg",
            "release_date": "2020-07-17",
            "metacritic_score": 83,
            "description": "An action-adventure game following a samurai on a quest to protect Tsushima Island during the first Mongol invasion of Japan.",
            "publisher": "Sony Interactive Entertainment",
            "developer": "Sucker Punch Productions",
            "genres": ["Action", "Adventure", "Open World"],
        },
        {
            "title": "Baldur's Gate 3",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/0/0e/Baldurs_Gate_3_cover_art.jpg",
            "release_date": "2023-08-03",
            "metacritic_score": 97,
            "description": "A role-playing game based on the Dungeons & Dragons tabletop RPG, featuring turn-based combat and rich storytelling.",
            "publisher": "Larian Studios",
            "developer": "Larian Studios",
            "genres": ["RPG", "Turn-based Strategy"],
        },
        {
            "title": "Hollow Knight",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/c/c0/Hollow_Knight_cover.jpg",
            "release_date": "2017-02-24",
            "metacritic_score": 87,
            "description": "A challenging 2D action-adventure game with a beautiful, ruined world of insects and heroes.",
            "publisher": "Team Cherry",
            "developer": "Team Cherry",
            "genres": ["Metroidvania", "Platformer", "Action"],
        },
        {
            "title": "Celeste",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0f/Celeste_box_art_full.png",
            "release_date": "2018-01-25",
            "metacritic_score": 94,
            "description": "A platform game about climbing a mountain, overcoming challenges, and facing inner demons.",
            "publisher": "Matt Makes Games",
            "developer": "Extremely OK Games",
            "genres": ["Platformer", "Indie"],
        },
        {
            "title": "Stardew Valley",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/f/fd/Logo_of_Stardew_Valley.png",
            "release_date": "2016-02-26",
            "metacritic_score": 89,
            "description": "A farming simulation game where players take over their grandfather's farm and build a thriving agricultural business.",
            "publisher": "ConcernedApe",
            "developer": "ConcernedApe",
            "genres": ["Simulation", "RPG"],
        },
        {
            "title": "Resident Evil 4 Remake",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/d/df/Resident_Evil_4_remake_cover_art.jpg",
            "release_date": "2023-03-24",
            "metacritic_score": 93,
            "description": "A remake of the survival horror classic, following Leon S. Kennedy on a mission to rescue the president's daughter.",
            "publisher": "Capcom",
            "developer": "Capcom",
            "genres": ["Survival Horror", "Action"],
        },
        {
            "title": "Final Fantasy VII Remake",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/c/ce/FFVIIRemake.png",
            "release_date": "2020-04-10",
            "metacritic_score": 87,
            "description": "A reimagining of the iconic JRPG, following Cloud Strife and eco-terrorist group AVALANCHE as they fight against the Shinra Electric Power Company.",
            "publisher": "Square Enix",
            "developer": "Square Enix",
            "genres": ["JRPG", "Action"],
        },
        {
            "title": "Death Stranding",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/2/22/Death_Stranding.jpg",
            "release_date": "2019-11-08",
            "metacritic_score": 82,
            "description": "An action game set in a post-apocalyptic United States, where players must reconnect isolated colonies.",
            "publisher": "Sony Interactive Entertainment",
            "developer": "Kojima Productions",
            "genres": ["Action", "Adventure"],
        },
        {
            "title": "Divinity: Original Sin 2",
            "image_url": "https://upload.wikimedia.org/wikipedia/en/0/06/Divinity_Original_Sin_II_cover_art.jpg",
            "release_date": "2017-09-14",
            "metacritic_score": 93,
            "description": "A critically acclaimed RPG with deep tactical combat and rich storytelling in a fantasy world.",
            "publisher": "Larian Studios",
            "developer": "Larian Studios",
            "genres": ["RPG", "Turn-based Strategy"],
        },
    ]
    
    # Count how many games have been added or updated
    games_added = 0
    games_updated = 0
    
    # Add or update each game
    for game_data in top_games:
        # Try to find existing game by title
        game = Game.objects.filter(title=game_data["title"]).first()
        
        if game:
            # Update existing game
            for field, value in game_data.items():
                if field != "genres":  # Handle genres separately
                    setattr(game, field, value)
            
            game.save()
            games_updated += 1
            print(f"Updated game: {game.title}")
        else:
            # Create new game
            genres_data = game_data.pop("genres")
            game = Game.objects.create(**game_data)
            
            # Add genres
            for genre_name in genres_data:
                genre = add_or_update_genre(genre_name)
                game.genres.add(genre)
            
            games_added += 1
            print(f"Added new game: {game.title}")
    
    print(f"Added {games_added} new games and updated {games_updated} existing games")

def check_database_status():
    """Check the status of the games database"""
    total_games = Game.objects.count()
    games_with_score = Game.objects.exclude(metacritic_score__isnull=True).count()
    games_with_images = Game.objects.exclude(Q(image_url__isnull=True) | Q(image_url='')).count()
    
    print(f"Database status:")
    print(f"- Total games: {total_games}")
    print(f"- Games with metacritic scores: {games_with_score}")
    print(f"- Games with cover images: {games_with_images}")
    
    # List games without cover images
    games_missing_images = Game.objects.filter(Q(image_url__isnull=True) | Q(image_url=''))
    if games_missing_images:
        print(f"Games missing cover images ({games_missing_images.count()}):")
        for game in games_missing_images:
            print(f"- {game.title}")

if __name__ == "__main__":
    # Check database status before
    print("Database status before updates:")
    check_database_status()
    
    # Add top rated games
    add_top_rated_games()
    
    # Check database status after
    print("\nDatabase status after updates:")
    check_database_status() 