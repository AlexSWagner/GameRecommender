import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.models import ScrapingSource, ScrapingJob


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Run game data scrapers for top games'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            help='Name of the source to scrape (e.g., "metacritic", "gamespot"). Scrapes all sources if not specified.'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of games to scrape per source (default: 100)'
        )
    
    def handle(self, *args, **options):
        source_name = options.get('source')
        limit = options.get('limit')
        
        if source_name:
            # Scrape specific source
            sources = ScrapingSource.objects.filter(
                spider_name=source_name,
                is_active=True
            )
            if not sources.exists():
                self.stdout.write(self.style.ERROR(f'No active source found with name "{source_name}"'))
                return
        else:
            # Scrape all active sources
            sources = ScrapingSource.objects.filter(is_active=True)
            if not sources.exists():
                self.stdout.write(self.style.ERROR('No active sources found'))
                return
        
        for source in sources:
            spider_name = source.spider_name
            self.stdout.write(self.style.SUCCESS(f'Starting scraping job for {source.name}'))
            
            # Create a job record
            job = ScrapingJob.objects.create(
                source=source,
                status='running',
            )
            
            # Run the spider directly
            settings = get_project_settings()
            process = CrawlerProcess(settings)
            
            try:
                # Import the appropriate spider
                if spider_name == 'metacritic':
                    from scraper.spiders.metacritic_spider import MetacriticSpider
                    spider = MetacriticSpider
                elif spider_name == 'gamespot':
                    from scraper.spiders.gamespot_spider import GameSpotSpider
                    spider = GameSpotSpider
                else:
                    self.stdout.write(self.style.ERROR(f'Spider {spider_name} not found'))
                    continue
                
                # Run the spider
                process.crawl(spider, job_id=job.id, limit=limit)
                process.start()
                
                self.stdout.write(self.style.SUCCESS(f'Successfully completed scraping for {source.name}'))
                # Update source last scraped timestamp
                source.last_scraped = timezone.now()
                source.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to scrape {source.name}: {str(e)}'))
                # Update job status
                job.status = 'failed'
                job.errors = str(e)
                job.completed_at = timezone.now()
                job.save() 