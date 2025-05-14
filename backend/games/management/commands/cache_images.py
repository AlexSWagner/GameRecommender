from django.core.management.base import BaseCommand
from games.utils.image_cache import verify_all_game_images
import time

class Command(BaseCommand):
    help = 'Cache images for games to improve loading times and reliability'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of games to process',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of games to process in each batch',
        )
        parser.add_argument(
            '--delay',
            type=float,
            default=0.5,
            help='Delay in seconds between batches to avoid rate limiting',
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        batch_size = options.get('batch_size', 10)
        delay = options.get('delay', 0.5)
        
        self.stdout.write(self.style.SUCCESS('Starting image caching process...'))
        
        # If a limit is specified, process in one go
        if limit:
            success, failure = verify_all_game_images(limit)
            self.stdout.write(self.style.SUCCESS(
                f'Completed image caching. Success: {success}, Failure: {failure}'
            ))
            return
            
        # Otherwise, process in batches with a delay to avoid rate limiting
        from games.models import Game
        
        # Get count of games with no cached image
        games_without_cache_count = Game.objects.filter(cached_image__isnull=True).count()
        
        if games_without_cache_count > 0:
            self.stdout.write(self.style.WARNING(
                f'Found {games_without_cache_count} games with no cached image'
            ))
            
            processed = 0
            while processed < games_without_cache_count:
                batch_limit = min(batch_size, games_without_cache_count - processed)
                success, failure = verify_all_game_images(batch_limit)
                processed += success + failure
                
                self.stdout.write(self.style.SUCCESS(
                    f'Processed batch of {batch_limit} games. '
                    f'Success: {success}, Failure: {failure}, '
                    f'Total: {processed}/{games_without_cache_count}'
                ))
                
                # Sleep to avoid rate limiting
                if processed < games_without_cache_count:
                    time.sleep(delay)
        
        self.stdout.write(self.style.SUCCESS('Image caching completed successfully!')) 