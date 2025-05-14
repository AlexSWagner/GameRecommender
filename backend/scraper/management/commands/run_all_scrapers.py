from django.core.management.base import BaseCommand
from scraper.models import ScrapingSource
from scraper.tasks import scrape_source


class Command(BaseCommand):
    help = 'Run all active scraper sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of games to scrape per source'
        )

    def handle(self, *args, **options):
        limit = options.get('limit')
        
        sources = ScrapingSource.objects.filter(is_active=True)
        
        if not sources:
            self.stdout.write(self.style.WARNING('No active scraping sources found!'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'Running {sources.count()} active scrapers with limit {limit} per source'))
        
        for source in sources:
            self.stdout.write(f'Starting scraper for {source.name}...')
            try:
                # Run the scraper synchronously
                result = scrape_source(source.id, limit)
                self.stdout.write(self.style.SUCCESS(f'Result: {result}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error running scraper for {source.name}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('All scrapers have been run')) 