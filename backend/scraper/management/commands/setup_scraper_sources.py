from django.core.management.base import BaseCommand
from scraper.models import ScrapingSource


class Command(BaseCommand):
    help = 'Set up initial scraping sources for game data'
    
    def handle(self, *args, **options):
        sources = [
            {
                'name': 'Metacritic',
                'base_url': 'https://www.metacritic.com/browse/game/pc/',
                'description': 'Metacritic aggregates game reviews from various publications.',
                'spider_name': 'metacritic',
                'is_active': True,
                'requires_javascript': False,
                'requires_login': False,
                'requests_per_minute': 10
            },
            {
                'name': 'GameSpot',
                'base_url': 'https://www.gamespot.com/gallery/best-pc-games/2900-4143/',
                'description': 'GameSpot provides game reviews, news, videos, and more.',
                'spider_name': 'gamespot',
                'is_active': True,
                'requires_javascript': False,
                'requires_login': False,
                'requests_per_minute': 10
            },
            {
                'name': 'OpenCritic',
                'base_url': 'https://opencritic.com/browse/pc',
                'description': 'OpenCritic is a review aggregator for video games, designed to be free from publisher influence.',
                'spider_name': 'opencritic',
                'is_active': True,
                'requires_javascript': False,
                'requires_login': False,
                'requests_per_minute': 10
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for source_data in sources:
            source, created = ScrapingSource.objects.update_or_create(
                name=source_data['name'],
                defaults=source_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created source: {source.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f'Updated source: {source.name}'))
        
        self.stdout.write(self.style.SUCCESS(
            f'Finished setting up scraping sources. Created: {created_count}, Updated: {updated_count}'
        )) 