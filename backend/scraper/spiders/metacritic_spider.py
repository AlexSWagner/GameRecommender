import scrapy
import logging
from datetime import datetime
from ..models import ScrapingJob, ScrapingError


class MetacriticSpider(scrapy.Spider):
    name = 'metacritic'
    allowed_domains = ['metacritic.com']
    start_urls = ['https://www.metacritic.com/browse/games/score/metascore/all/pc/filtered']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'ROBOTSTXT_OBEY': False,  # We need to disable this for Metacritic
        'DOWNLOAD_DELAY': 2,      # Be respectful with their servers
    }
    
    def __init__(self, *args, **kwargs):
        super(MetacriticSpider, self).__init__(*args, **kwargs)
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
        # Find all game listings on the page
        game_listings = response.css('td.clamp-summary-wrap')
        
        for game in game_listings:
            # Stop if we've reached the limit
            if self.items_scraped >= self.limit:
                self._logger.info(f"Reached limit of {self.limit} games")
                break
            
            # Extract basic data
            title = game.css('a.title h3::text').get().strip()
            url = game.css('a.title::attr(href)').get()
            score = game.css('div.metascore_w::text').get()
            metascore = int(score) if score and score.strip().isdigit() else None
            
            # Increment counter
            self.items_scraped += 1
            
            # Follow the link to the game's page for more details
            if url:
                yield response.follow(
                    url, 
                    callback=self.parse_game,
                    meta={
                        'title': title,
                        'metascore': metascore,
                        'position': self.items_scraped
                    }
                )
        
        # Check if we need more games and if there's a next page
        if self.items_scraped < self.limit:
            next_page = response.css('a.action.next::attr(href)').get()
            if next_page:
                yield response.follow(next_page, self.parse)
    
    def parse_game(self, response):
        try:
            # Extract data passed from list page
            title = response.meta.get('title')
            metascore = response.meta.get('metascore')
            position = response.meta.get('position')
            
            self._logger.info(f"Parsing game #{position}: {title}")
            
            # Details section
            details_section = response.css('div.details_section')
            
            # Release date
            release_date_text = details_section.css('li.summary_detail.release_data span.data::text').get()
            release_date = None
            if release_date_text:
                try:
                    release_date = datetime.strptime(release_date_text.strip(), '%b %d, %Y')
                except ValueError:
                    self._logger.warning(f"Could not parse release date: {release_date_text}")
            
            # Publisher & Developer
            publisher = details_section.css('li.summary_detail.publisher span.data a::text').get()
            developer = details_section.css('li.summary_detail.developer span.data a::text').get()
            
            # User score
            user_score_elem = response.css('div.userscore_wrap a.metascore_anchor div.user::text').get()
            user_score = None
            if user_score_elem:
                try:
                    user_score = float(user_score_elem.strip())
                except ValueError:
                    pass
            
            # Description/summary
            description = response.css('div.product_details span.blurb_expanded::text').get()
            if not description:
                description = response.css('div.product_details span.blurb::text').get()
            
            # Genres
            genres = []
            genre_elements = details_section.css('li.summary_detail.product_genre span.data::text').getall()
            if genre_elements:
                genres = [g.strip() for g in genre_elements]
            
            # Image URL - this is important for the cover art
            image_url = response.css('div.product_image img::attr(src)').get()
            
            # Rating
            rating_elem = details_section.css('li.summary_detail.product_rating span.data::text').get()
            age_rating = rating_elem.strip() if rating_elem else None
            
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
                'source_name': 'Metacritic',
                'age_rating': age_rating,
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