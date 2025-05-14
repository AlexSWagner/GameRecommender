from django.core.management.base import BaseCommand
from scraper.models import ScrapingSource


class Command(BaseCommand):
    help = 'Verify and set up scraper sources if not already configured'

    def handle(self, *args, **options):
        # Default sources that should exist
        default_sources = [
            {
                'name': 'Metacritic',
                'slug': 'metacritic',
                'spider_name': 'metacritic',
                'url': 'https://www.metacritic.com/browse/games/score/metascore/all/pc/filtered',
                'is_active': True,
                'scraping_interval': 24 * 7  # Weekly
            },
            {
                'name': 'GameSpot',
                'slug': 'gamespot',
                'spider_name': 'gamespot',
                'url': 'https://www.gamespot.com/games/reviews/',
                'is_active': True,
                'scraping_interval': 24 * 7  # Weekly
            },
            {
                'name': 'OpenCritic',
                'slug': 'opencritic',
                'spider_name': 'opencritic',
                'url': 'https://opencritic.com/browse/all',
                'is_active': True,
                'scraping_interval': 24 * 7  # Weekly
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for source_data in default_sources:
            source, created = ScrapingSource.objects.get_or_create(
                slug=source_data['slug'],
                defaults=source_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created new source: {source.name}"))
            else:
                # Update existing source to ensure it's active
                if not source.is_active:
                    source.is_active = True
                    source.save()
                    updated_count += 1
                    self.stdout.write(self.style.SUCCESS(f"Activated existing source: {source.name}"))
                else:
                    self.stdout.write(f"Source already exists and is active: {source.name}")
        
        # Summary
        total_active = ScrapingSource.objects.filter(is_active=True).count()
        self.stdout.write(self.style.SUCCESS(
            f"Setup complete. Created {created_count} sources, updated {updated_count} sources. "
            f"Total active sources: {total_active}"
        ))
        
        if total_active == 0:
            self.stdout.write(self.style.WARNING(
                "No active sources found. This may prevent game data from being scraped."
            ))
        
        # Instructions for running scrapers
        self.stdout.write("\nTo run scrapers and populate game images, use:")
        self.stdout.write(self.style.SUCCESS("python manage.py run_all_scrapers --limit 50")) 