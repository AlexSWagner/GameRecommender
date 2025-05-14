import logging
import datetime
import os
import tempfile
from celery import shared_task
from django.utils import timezone
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.settings import Settings
from twisted.internet import reactor
from multiprocessing import Process, Queue
from billiard.context import Process as BilliardProcess

from .models import ScrapingSource, ScrapingJob


logger = logging.getLogger(__name__)


def run_spider_process(spider_name, job_id, limit=100):
    """
    Run a spider in a separate process.
    
    Args:
        spider_name: Name of the spider to run
        job_id: ID of the ScrapingJob to associate with this run
        limit: Maximum number of items to scrape
    """
    def _crawl_in_process(spider_name, job_id, limit, results_queue=None):
        try:
            # Initialize Django
            import django
            django.setup()
            
            # Get the project settings
            settings = get_project_settings()
            
            # Set up the crawler process
            process = CrawlerProcess(settings=settings)
            
            # Import spiders only after Django setup
            if spider_name == 'metacritic':
                from scraper.spiders.metacritic_spider import MetacriticSpider
                process.crawl(MetacriticSpider, job_id=job_id, limit=limit)
            elif spider_name == 'gamespot':
                from scraper.spiders.gamespot_spider import GameSpotSpider
                process.crawl(GameSpotSpider, job_id=job_id, limit=limit)
            elif spider_name == 'opencritic':
                from scraper.spiders.opencritic_spider import OpenCriticSpider
                process.crawl(OpenCriticSpider, job_id=job_id, limit=limit)
            else:
                if results_queue:
                    results_queue.put((False, f"Spider {spider_name} not found"))
                return
            
            # Start the crawler
            process.start()
            
            # If we have a results queue, put the success result
            if results_queue:
                results_queue.put((True, "Spider completed successfully"))
                
        except Exception as e:
            logger.exception(f"Error running spider {spider_name}: {str(e)}")
            if results_queue:
                results_queue.put((False, str(e)))
    
    # Create a queue for the process to communicate back results
    results_queue = Queue()
    
    # Start the process
    process = BilliardProcess(
        target=_crawl_in_process,
        args=(spider_name, job_id, limit, results_queue)
    )
    process.start()
    process.join()
    
    # Get the results from the queue
    success, result = results_queue.get()
    
    if success:
        # Success
        logger.info(f"Spider {spider_name} completed successfully")
        return True
    else:
        # Failure with error message
        logger.error(f"Spider {spider_name} failed: {result}")
        return False


@shared_task
def scrape_game_data(limit=100):
    """
    Main task to scrape game data from all active sources.
    This task is scheduled by Celery Beat to run periodically.
    
    Args:
        limit: Maximum number of games to scrape per source
    """
    logger.info("Starting scheduled game data scraping")
    
    # Get all active scraping sources
    sources = ScrapingSource.objects.filter(is_active=True)
    
    for source in sources:
        # Launch a task for each source
        scrape_source.delay(source.id, limit)
    
    return f"Initiated scraping for {sources.count()} sources"


@shared_task
def scrape_source(source_id, limit=100):
    """
    Task to scrape data from a specific source.
    
    Args:
        source_id: ID of the ScrapingSource to scrape
        limit: Maximum number of games to scrape
    """
    try:
        source = ScrapingSource.objects.get(id=source_id)
        
        # Create a job record
        task_id = getattr(scrape_source, 'request', None)
        job = ScrapingJob.objects.create(
            source=source,
            status='running',
            task_id=task_id.id if task_id else "manual_run"  # Use "manual_run" if not in a Celery task
        )
        
        logger.info(f"Starting scraping job for {source.name}")
        
        # Run the spider in a separate process
        success = run_spider_process(source.spider_name, job.id, limit)
        
        if not success:
            # Update job record on failure
            job.status = 'failed'
            job.errors = "Failed to run spider"
            job.completed_at = timezone.now()
            job.save()
            logger.error(f"Failed to run spider for {source.name}")
            return f"Failed to run spider for {source.name}"
        
        # Update source last scraped timestamp
        source.last_scraped = timezone.now()
        source.save()
        
        logger.info(f"Completed scraping job for {source.name}")
        return f"Successfully scraped items from {source.name}"
    
    except ScrapingSource.DoesNotExist:
        logger.error(f"Scraping source with ID {source_id} does not exist")
        return f"Error: Scraping source with ID {source_id} does not exist"
    
    except Exception as e:
        logger.exception(f"Error scraping {source_id}: {str(e)}")
        
        # Update job record on failure if it exists
        try:
            job.status = 'failed'
            job.errors = str(e)
            job.completed_at = timezone.now()
            job.save()
        except:
            pass
        
        return f"Error scraping source {source_id}: {str(e)}"


@shared_task
def cleanup_old_scraping_jobs():
    """Cleanup task to remove old scraping jobs (runs weekly)."""
    thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
    old_jobs = ScrapingJob.objects.filter(started_at__lt=thirty_days_ago)
    count = old_jobs.count()
    old_jobs.delete()
    return f"Deleted {count} old scraping jobs" 