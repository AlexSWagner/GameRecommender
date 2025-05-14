import logging
import importlib
import sys
from django.core.management.base import BaseCommand
from django.utils import timezone
from scraper.models import ScrapingSource, ScrapingJob
from scrapy.crawler import CrawlerRunner
from scrapy.crawler import Crawler
from scrapy.settings import Settings
from scrapy import signals

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run game scrapers directly without Twisted dependency issues'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'source',
            type=str,
            help='Name of the source to scrape (e.g., "metacritic", "gamespot")'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Maximum number of games to scrape (default: 20)'
        )
    
    def handle(self, *args, **options):
        source_name = options.get('source')
        limit = options.get('limit')
        
        self.stdout.write(self.style.SUCCESS(f'Starting scraping for {source_name} with limit {limit}'))
        
        try:
            # Create a job record in the database
            source, created = ScrapingSource.objects.get_or_create(
                name=source_name.capitalize(),
                spider_name=source_name,
                defaults={'is_active': True}
            )
            
            job = ScrapingJob.objects.create(
                source=source,
                status='running',
            )
            
            # Dynamically import the spider class based on name
            if source_name == 'metacritic':
                from scraper.spiders.metacritic_spider import MetacriticSpider as SpiderClass
            elif source_name == 'gamespot':
                from scraper.spiders.gamespot_spider import GameSpotSpider as SpiderClass
            else:
                self.stdout.write(self.style.ERROR(f'Spider {source_name} not found'))
                return
                
            # Create a spider instance
            spider = SpiderClass(job_id=job.id, limit=limit)
            
            # Set up a simple logger for the spider
            spider.logger = logger
            
            # Use our own simple crawler
            items = []
            
            # Define a callback for collected items
            def process_item(item, spider):
                items.append(dict(item))
                return item
            
            # Set up the spider to collect items
            spider.items = items
            
            # Run the spider's parse method on start_urls
            for url in spider.start_urls:
                self.stdout.write(self.style.SUCCESS(f'Crawling URL: {url}'))
                
                # Create a fresh request
                import requests
                headers = {'User-Agent': spider.custom_settings.get('USER_AGENT')}
                response = requests.get(url, headers=headers)
                
                if response.status_code == 200:
                    # Convert to scrapy response
                    from scrapy.http import HtmlResponse
                    scrapy_response = HtmlResponse(
                        url=url,
                        body=response.content,
                        encoding='utf-8',
                        request=None
                    )
                    
                    # Run the spider's parse method
                    for result in spider.parse(scrapy_response):
                        # Handle Request objects by following them
                        if hasattr(result, 'callback'):
                            callback = result.callback
                            meta = result.meta
                            
                            # Make the request and get the response
                            follow_url = result.url
                            self.stdout.write(self.style.SUCCESS(f'Following URL: {follow_url}'))
                            follow_response = requests.get(follow_url, headers=headers)
                            
                            if follow_response.status_code == 200:
                                # Convert to scrapy response
                                follow_scrapy_response = HtmlResponse(
                                    url=follow_url,
                                    body=follow_response.content,
                                    encoding='utf-8',
                                    request=None
                                )
                                follow_scrapy_response.meta = meta
                                
                                # Call the callback
                                for item in callback(follow_scrapy_response):
                                    if not hasattr(item, 'callback'):  # It's an item, not a request
                                        items.append(dict(item))
                                        self.stdout.write(self.style.SUCCESS(f'Found game: {item.get("title")}'))
                            else:
                                self.stdout.write(self.style.ERROR(f'Error fetching {follow_url}: {follow_response.status_code}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Error fetching {url}: {response.status_code}'))
            
            # Process the collected items by passing them to the pipeline
            from scraper.pipelines import GameDataPipeline
            pipeline = GameDataPipeline()
            
            # Process each item through the pipeline
            self.stdout.write(self.style.SUCCESS(f'Processing {len(items)} items through pipeline'))
            for item in items:
                try:
                    pipeline.process_item(item, spider)
                    self.stdout.write(self.style.SUCCESS(f'Saved game: {item.get("title")}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error saving game {item.get("title")}: {str(e)}'))
            
            # Update the job status
            job.status = 'completed'
            job.items_scraped = len(items)
            job.items_saved = len(items)
            job.completed_at = timezone.now()
            job.save()
            
            # Update source last_scraped timestamp
            source.last_scraped = timezone.now()
            source.save()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully scraped {len(items)} items from {source_name}'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error running {source_name} scraper: {str(e)}'))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc())) 