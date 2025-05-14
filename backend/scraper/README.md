# Game Scraper

This module scrapes game data from various sources like Metacritic and GameSpot.

## Setup

1. Ensure all requirements are installed:
   ```
   pip install -r requirements.txt
   ```

2. Set up the scraping sources in the database:
   ```
   python manage.py setup_scraper_sources
   ```

## Running the Scraper

You can run the scraper in several ways:

### Using the Management Command

Run the scraper directly from the command line:

```bash
# Scrape all sources
python manage.py run_scraper

# Scrape a specific source
python manage.py run_scraper --source metacritic

# Limit the number of games to scrape
python manage.py run_scraper --limit 50
```

### Using Celery Task

You can trigger the scraper via Celery tasks:

```python
from scraper.tasks import scrape_game_data

# Scrape all sources
scrape_game_data.delay()

# Limit the number of games to scrape
scrape_game_data.delay(limit=50)
```

## Scheduled Scraping

The scraper is scheduled to run periodically using Celery Beat. The schedule is defined in `settings.py` under `CELERY_BEAT_SCHEDULE`.

## Data Storage

Scraped game data is stored in the `games_game` table. Each game record includes:

- Title
- Description
- Release date
- Publisher
- Developer
- Genres
- Platforms
- Metacritic score
- User score
- Image URL
- Source URL
- Source name

## Adding New Sources

To add a new source:

1. Create a new spider in `scraper/spiders/`
2. Add the source to the database using the `setup_scraper_sources` command or manually through the Django admin

## Troubleshooting

Check the scraping job status in the `scraper_scrapingjob` table. Failed jobs will have error details in the `errors` field.

You can also check the logs for more detailed error information. 