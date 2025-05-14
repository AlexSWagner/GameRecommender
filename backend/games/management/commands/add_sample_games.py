import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from games.models import Game, Genre, Platform

class Command(BaseCommand):
    help = 'Add sample game data for testing'
    
    def handle(self, *args, **options):
        # Create genres
        genres = [
            "Action", "Adventure", "RPG", "Strategy", "Simulation", 
            "Sports", "Racing", "Puzzle", "Shooter", "Platform"
        ]
        
        genre_objects = []
        for genre_name in genres:
            genre, created = Genre.objects.get_or_create(name=genre_name)
            genre_objects.append(genre)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created genre: {genre_name}'))
        
        # Create platforms
        platforms = ["PC", "PlayStation 5", "Xbox Series X", "Nintendo Switch", "Mobile"]
        platform_objects = []
        for platform_name in platforms:
            platform, created = Platform.objects.get_or_create(name=platform_name)
            platform_objects.append(platform)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created platform: {platform_name}'))
        
        # Sample games
        games = [
            {
                "title": "Elden Ring",
                "description": "An action RPG with a vast open world and challenging combat.",
                "release_date": "2022-02-25",
                "publisher": "Bandai Namco",
                "developer": "FromSoftware",
                "metacritic_score": 96,
                "user_score": 8.7,
                "is_multiplayer": True,
                "has_in_app_purchases": False,
                "is_free_to_play": False,
                "age_rating": "M",
                "image_url": "https://assets-prd.ignimgs.com/2022/02/23/elden-ring-button-fin-1645631123435.jpg",
                "source_name": "Metacritic"
            },
            {
                "title": "The Witcher 3: Wild Hunt",
                "description": "An open-world RPG with a deep narrative and memorable characters.",
                "release_date": "2015-05-19",
                "publisher": "CD Projekt",
                "developer": "CD Projekt Red",
                "metacritic_score": 93,
                "user_score": 9.1,
                "is_multiplayer": False,
                "has_in_app_purchases": False,
                "is_free_to_play": False,
                "age_rating": "M",
                "image_url": "https://assets-prd.ignimgs.com/2020/07/22/the-witcher-3-wild-hunt-complete-edition-button-2020-1595435335097.jpg",
                "source_name": "Metacritic"
            },
            {
                "title": "Red Dead Redemption 2",
                "description": "An epic tale of life in America's unforgiving heartland.",
                "release_date": "2018-10-26",
                "publisher": "Rockstar Games",
                "developer": "Rockstar Games",
                "metacritic_score": 97,
                "user_score": 8.5,
                "is_multiplayer": True,
                "has_in_app_purchases": True,
                "is_free_to_play": False,
                "age_rating": "M",
                "image_url": "https://assets-prd.ignimgs.com/2018/10/24/rdr2-button-01-1540427618211.jpg",
                "source_name": "Metacritic"
            },
            {
                "title": "Hades",
                "description": "A god-like rogue-like dungeon crawler that combines the best aspects of Supergiant's critically acclaimed titles.",
                "release_date": "2020-09-17",
                "publisher": "Supergiant Games",
                "developer": "Supergiant Games",
                "metacritic_score": 93,
                "user_score": 8.8,
                "is_multiplayer": False,
                "has_in_app_purchases": False,
                "is_free_to_play": False,
                "age_rating": "T",
                "image_url": "https://assets-prd.ignimgs.com/2020/09/27/hades-button-fin-1601175814926.jpg",
                "source_name": "Metacritic"
            },
            {
                "title": "God of War",
                "description": "A third-person action-adventure game that follows the journey of Kratos and his son Atreus.",
                "release_date": "2018-04-20",
                "publisher": "Sony Interactive Entertainment",
                "developer": "Santa Monica Studio",
                "metacritic_score": 94,
                "user_score": 9.1,
                "is_multiplayer": False,
                "has_in_app_purchases": False,
                "is_free_to_play": False,
                "age_rating": "M",
                "image_url": "https://assets-prd.ignimgs.com/2020/07/22/god-of-war-ps4-button-01-1595435673370.jpg",
                "source_name": "Metacritic"
            },
            {
                "title": "Cyberpunk 2077",
                "description": "An open-world, action-adventure story set in Night City, a megalopolis obsessed with power, glamour and body modification.",
                "release_date": "2020-12-10",
                "publisher": "CD Projekt",
                "developer": "CD Projekt Red",
                "metacritic_score": 86,
                "user_score": 7.4,
                "is_multiplayer": False,
                "has_in_app_purchases": False,
                "is_free_to_play": False,
                "age_rating": "M",
                "image_url": "https://assets-prd.ignimgs.com/2020/12/04/cyberpunk-2077-button-fin-1607088809489.jpg",
                "source_name": "Metacritic"
            },
            {
                "title": "Breath of the Wild",
                "description": "Step into a world of discovery, exploration, and adventure in The Legend of Zelda: Breath of the Wild.",
                "release_date": "2017-03-03",
                "publisher": "Nintendo",
                "developer": "Nintendo",
                "metacritic_score": 97,
                "user_score": 8.7,
                "is_multiplayer": False,
                "has_in_app_purchases": False,
                "is_free_to_play": False,
                "age_rating": "E10+",
                "image_url": "https://assets-prd.ignimgs.com/2020/07/22/legend-of-zelda-breath-of-the-wild-switch-button-1595435578505.jpg",
                "source_name": "Metacritic"
            },
            {
                "title": "Minecraft",
                "description": "A game about placing blocks and going on adventures.",
                "release_date": "2011-11-18",
                "publisher": "Mojang",
                "developer": "Mojang",
                "metacritic_score": 93,
                "user_score": 8.2,
                "is_multiplayer": True,
                "has_in_app_purchases": True,
                "is_free_to_play": False,
                "age_rating": "E10+",
                "image_url": "https://assets-prd.ignimgs.com/2020/07/21/minecraft-button-fin-1595374026322.jpg",
                "source_name": "Metacritic"
            },
            {
                "title": "Portal 2",
                "description": "The sequel to the acclaimed portal puzzle game with new characters, puzzles, and challenges.",
                "release_date": "2011-04-19",
                "publisher": "Valve",
                "developer": "Valve",
                "metacritic_score": 95,
                "user_score": 9.0,
                "is_multiplayer": True,
                "has_in_app_purchases": False,
                "is_free_to_play": False,
                "age_rating": "E10+",
                "image_url": "https://assets-prd.ignimgs.com/2020/07/24/portal-2-button-1595616952728.jpg",
                "source_name": "Metacritic"
            },
            {
                "title": "Hollow Knight",
                "description": "A challenging 2D action-adventure set in a vast interconnected world.",
                "release_date": "2017-02-24",
                "publisher": "Team Cherry",
                "developer": "Team Cherry",
                "metacritic_score": 90,
                "user_score": 8.9,
                "is_multiplayer": False,
                "has_in_app_purchases": False,
                "is_free_to_play": False,
                "age_rating": "E10+",
                "image_url": "https://assets-prd.ignimgs.com/2020/07/24/hollow-knight-button-1595617094541.jpg",
                "source_name": "Metacritic"
            }
        ]
        
        # Save games and assign genres/platforms
        for game_data in games:
            # Convert date string to datetime object
            if "release_date" in game_data and game_data["release_date"]:
                game_data["release_date"] = datetime.strptime(game_data["release_date"], "%Y-%m-%d").date()
            
            # Check if game already exists
            existing_game = Game.objects.filter(title=game_data["title"]).first()
            if existing_game:
                self.stdout.write(self.style.WARNING(f'Game already exists: {game_data["title"]}'))
                continue
            
            # Create new game
            game = Game.objects.create(**game_data)
            
            # Assign random genres (2-4 per game)
            num_genres = random.randint(2, 4)
            selected_genres = random.sample(genre_objects, num_genres)
            for genre in selected_genres:
                game.genres.add(genre)
            
            # Assign random platforms (1-3 per game)
            num_platforms = random.randint(1, 3)
            selected_platforms = random.sample(platform_objects, num_platforms)
            for platform in selected_platforms:
                game.platforms.add(platform)
            
            self.stdout.write(self.style.SUCCESS(f'Created game: {game.title}'))
        
        self.stdout.write(self.style.SUCCESS('Sample games added successfully!')) 