import os
import sys
import django
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def run_spider(spider_name, limit=20):
    """Run a spider with the given name."""
    settings = get_project_settings()
    
    process = CrawlerProcess(settings)
    
    # The spider needs to be imported after Django setup
    if spider_name == 'metacritic':
        from scraper.spiders.metacritic_spider import MetacriticSpider
        process.crawl(MetacriticSpider, limit=limit)
    elif spider_name == 'gamespot':
        from scraper.spiders.gamespot_spider import GameSpotSpider
        process.crawl(GameSpotSpider, limit=limit)
    else:
        print(f"Spider {spider_name} not found.")
        return
    
    process.start()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run_spider.py <spider_name> [limit]")
        sys.exit(1)
    
    spider_name = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    run_spider(spider_name, limit) 