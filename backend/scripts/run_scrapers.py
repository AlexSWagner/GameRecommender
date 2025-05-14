#!/usr/bin/env python
"""
Script to manually run all scrapers
"""
import os
import sys
import django

# Add the project path to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from scraper.models import ScrapingSource
from scraper.tasks import scrape_source


def run_all_scrapers(limit=50):
    """
    Run all active scrapers
    
    Args:
        limit: Maximum number of games to scrape per source
    """
    sources = ScrapingSource.objects.filter(is_active=True)
    
    if not sources:
        print("No active scraping sources found!")
        return
    
    print(f"Running {sources.count()} active scrapers with limit {limit} per source")
    
    for source in sources:
        print(f"Starting scraper for {source.name}...")
        try:
            # Run the scraper synchronously
            result = scrape_source(source.id, limit)
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error running scraper for {source.name}: {str(e)}")
    
    print("All scrapers have been run")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run all active scrapers')
    parser.add_argument('--limit', type=int, default=50, 
                        help='Maximum number of games to scrape per source')
    
    args = parser.parse_args()
    run_all_scrapers(args.limit) 