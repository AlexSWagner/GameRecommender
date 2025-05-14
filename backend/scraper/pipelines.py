from django.utils import timezone
from games.models import Game, Genre, Platform


class GameDataPipeline:
    """Pipeline to process and save game data to database."""
    
    def process_item(self, item, spider):
        # Get or create genre objects
        genres = []
        for genre_name in item.get('genres', []):
            genre, created = Genre.objects.get_or_create(name=genre_name)
            genres.append(genre)
        
        # Get or create platform object
        platform = None
        if item.get('platform'):
            platform, created = Platform.objects.get_or_create(name=item['platform'])
        
        # Try to find existing game by title and platform
        games = Game.objects.filter(title=item['title'])
        if platform:
            games = games.filter(platforms=platform)
        
        if games.exists():
            # Update existing game
            game = games.first()
            game.description = item.get('description', game.description)
            game.publisher = item.get('publisher', game.publisher)
            game.developer = item.get('developer', game.developer)
            game.metacritic_score = item.get('metascore', game.metacritic_score)
            game.user_score = item.get('user_score', game.user_score)
            game.image_url = item.get('image_url', game.image_url)
            game.source_url = item.get('source_url', game.source_url)
            game.source_name = item.get('source_name', game.source_name)
            game.last_updated = timezone.now()
            
            # Only update release date if it was previously None
            if game.release_date is None and item.get('release_date'):
                game.release_date = item['release_date']
            
            game.save()
        else:
            # Create new game
            game = Game.objects.create(
                title=item['title'],
                description=item.get('description', ''),
                release_date=item.get('release_date'),
                publisher=item.get('publisher', ''),
                developer=item.get('developer', ''),
                metacritic_score=item.get('metascore'),
                user_score=item.get('user_score'),
                image_url=item.get('image_url', ''),
                source_url=item.get('source_url', ''),
                source_name=item.get('source_name', '')
            )
        
        # Add platform if exists
        if platform:
            game.platforms.add(platform)
        
        # Add genres
        for genre in genres:
            game.genres.add(genre)
        
        spider.logger.info(f"Saved game: {game.title}")
        return item 