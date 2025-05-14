#!/bin/bash
# Script to set up and run the game scraper

echo "Setting up scraper sources..."
python manage.py setup_scraper_sources

echo "Running scraper for Metacritic..."
python manage.py run_scraper --source metacritic --limit 100

echo "Running scraper for GameSpot..."
python manage.py run_scraper --source gamespot --limit 100

echo "Scraping complete! Check the admin site to view the results."
echo "Admin URL: http://localhost:8000/admin/" 