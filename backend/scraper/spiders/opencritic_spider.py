import scrapy
import logging
import re
import json
from datetime import datetime
from ..models import ScrapingJob, ScrapingError

class OpenCriticSpider(scrapy.Spider):
    name = 'opencritic'
    allowed_domains = ['opencritic.com']
    start_urls = ['https://opencritic.com/browse/pc']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1.5,  # Be respectful with their servers
    }
    
    def __init__(self, *args, **kwargs):
        super(OpenCriticSpider, self).__init__(*args, **kwargs)
        # Get limit parameter or default to 100
        self.limit = int(kwargs.get('limit', 100))
        self.job_id = kwargs.get('job_id')
        self.job = None
        self.items_scraped = 0
        self.items_saved = 0
        self._logger = logging.getLogger(self.__class__.__name__)
        
        # Setup the job if job_id is provided
        if self.job_id:
            try:
                self.job = ScrapingJob.objects.get(id=self.job_id)
                self._logger.info(f"Spider initialized for job {self.job_id}")
            except ScrapingJob.DoesNotExist:
                self._logger.error(f"Job with ID {self.job_id} does not exist")
    
    @property
    def logger(self):
        return self._logger
        
    @logger.setter
    def logger(self, logger):
        self._logger = logger
    
    def parse(self, response):
        # Find all game entries
        game_entries = response.css('div[data-testid="game"]')
        
        for idx, game in enumerate(game_entries):
            # Stop if we've reached the limit
            if self.items_scraped >= self.limit:
                self._logger.info(f"Reached limit of {self.limit} games")
                break
            
            # Extract basic data
            title_element = game.css('div.game-name a::text').get()
            if not title_element:
                title_element = game.css('a[href*="/game/"]::text').get()
            
            title = title_element.strip() if title_element else None
            if not title:
                continue
                
            # Get game URL
            game_url = game.css('a[href*="/game/"]::attr(href)').get()
            if not game_url:
                continue
                
            # Score might be directly visible
            score_elem = game.css('span.score::text').get()
            metascore = None
            if score_elem:
                try:
                    metascore = int(score_elem.strip())
                except (ValueError, TypeError):
                    metascore = None
            
            # Increment counter
            self.items_scraped += 1
            
            # Follow the link to the game's page for more details
            if game_url:
                full_url = f"https://opencritic.com{game_url}"
                yield response.follow(
                    full_url, 
                    callback=self.parse_game,
                    meta={
                        'title': title,
                        'metascore': metascore,
                        'position': self.items_scraped
                    }
                )
        
        # Check if we need more games and if there's a next page
        if self.items_scraped < self.limit:
            next_page = response.css('a[aria-label="Next page"]::attr(href)').get()
            if next_page:
                yield response.follow(next_page, self.parse)
    
    def parse_game(self, response):
        try:
            # Extract data passed from list page
            title = response.meta.get('title')
            metascore = response.meta.get('metascore')
            position = response.meta.get('position')
            
            self._logger.info(f"Parsing game #{position}: {title}")
            
            # Extract game details
            # Get the image - OpenCritic often has high-quality box art
            image_url = response.css('div.game-image img::attr(src)').get()
            if not image_url:
                image_url = response.css('img.game-boxart::attr(src)').get()
            
            if image_url and not image_url.startswith('http'):
                image_url = f"https://opencritic.com{image_url}"
            
            # Get score if not already extracted
            if not metascore:
                score_elem = response.css('div.score::text').get()
                if score_elem:
                    try:
                        metascore = int(score_elem.strip())
                    except (ValueError, TypeError):
                        pass
            
            # Release date
            release_date = None
            release_date_text = response.css('div.release-date::text').get()
            if not release_date_text:
                # Try alternate selectors
                release_date_text = response.css('span[itemprop="datePublished"]::text').get()
            
            if release_date_text:
                try:
                    # Try multiple date formats
                    date_formats = ['%b %d, %Y', '%B %d, %Y', '%Y-%m-%d']
                    for fmt in date_formats:
                        try:
                            release_date = datetime.strptime(release_date_text.strip(), fmt)
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    self._logger.warning(f"Could not parse release date: {release_date_text} - {str(e)}")
            
            # Description - OpenCritic usually has a game summary
            description = response.css('div.description::text').get()
            if not description:
                description = response.css('div.summary p::text').get()
            
            # Extract genres
            genres = []
            genre_elements = response.css('span.genre::text').getall()
            if genre_elements:
                genres = [g.strip() for g in genre_elements]
            
            # Publishers and developers
            publisher = response.css('span[itemprop="publisher"]::text').get()
            developer = response.css('span[itemprop="developer"]::text').get()
            
            # User score
            user_score = None
            user_score_elem = response.css('div.user-score::text').get()
            if user_score_elem:
                try:
                    user_score = float(user_score_elem.strip())
                except (ValueError, TypeError):
                    pass
            
            self.items_saved += 1
            
            # Return the item
            yield {
                'title': title,
                'platform': 'PC',
                'release_date': release_date,
                'publisher': publisher,
                'developer': developer,
                'metascore': metascore,
                'user_score': user_score,
                'description': description,
                'genres': genres,
                'image_url': image_url,
                'source_url': response.url,
                'source_name': 'OpenCritic',
                'rank': position
            }
            
        except Exception as e:
            self._logger.error(f"Error parsing game page {response.url}: {str(e)}")
            
            # Record error if job is available
            if self.job:
                ScrapingError.objects.create(
                    job=self.job,
                    url=response.url,
                    error_type=type(e).__name__,
                    error_message=str(e)
                ) 
    
    def closed(self, reason):
        # Update the job when the spider is closed
        if self.job:
            self.job.status = 'completed' if reason == 'finished' else 'failed'
            self.job.items_scraped = self.items_scraped
            self.job.items_saved = self.items_saved
            self.job.errors = f"Spider closed with reason: {reason}" if reason != 'finished' else ''
            self.job.completed_at = datetime.now()
            self.job.save()
            
            self._logger.info(f"Job {self.job_id} updated with status {self.job.status}")
            self._logger.info(f"Items scraped: {self.items_scraped}, Items saved: {self.items_saved}") 