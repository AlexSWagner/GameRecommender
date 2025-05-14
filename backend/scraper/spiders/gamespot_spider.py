import scrapy
import logging
import re
from datetime import datetime
from ..models import ScrapingJob, ScrapingError


class GameSpotSpider(scrapy.Spider):
    name = 'gamespot'
    allowed_domains = ['gamespot.com']
    start_urls = ['https://www.gamespot.com/gallery/best-pc-games/2900-4143/']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 1.5,  # Be respectful with their servers
    }
    
    def __init__(self, *args, **kwargs):
        super(GameSpotSpider, self).__init__(*args, **kwargs)
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
        # In the new gallery format, each game has its own section
        game_listings = response.css('div.gallery-embed__item')
        
        for game in game_listings:
            # Check if we've reached the limit
            if self.items_scraped >= self.limit:
                self._logger.info(f"Reached limit of {self.limit} games")
                break
                
            # Extract basic data
            title_elem = game.css('h3::text').get()
            if not title_elem:
                title_elem = game.css('h2::text').get()
            
            title = title_elem.strip() if title_elem else None
            if not title:
                continue
                
            # Extract image - GameSpot gallery has large game images
            img_url = game.css('img::attr(src)').get()
            if not img_url:
                # Try to find it in a background style
                style = game.css('div[style*="background-image"]::attr(style)').get()
                if style:
                    img_match = re.search(r'url\([\'"]?(.*?)[\'"]?\)', style)
                    if img_match:
                        img_url = img_match.group(1)
            
            # Sometimes need to construct full URL
            if img_url and not img_url.startswith('http'):
                img_url = f"https:{img_url}"
                
            # Get the game page link
            link = game.css('a::attr(href)').get()
            if not link:
                # Try alternate selectors
                link = game.css('a[href*="/game/"]::attr(href)').get()
                
            # Increment counter only if we have a title and will process this game
            if title:
                self.items_scraped += 1
                
                # For the gallery page, we might need to extract additional info
                # from the description
                description = game.css('p::text').get()
                
                # If we have a link to the game detail page, follow it
                if link and link.startswith('/game/'):
                    full_url = f"https://www.gamespot.com{link}"
                    yield scrapy.Request(
                        full_url,
                        callback=self.parse_game,
                        meta={
                            'title': title,
                            'image_url': img_url,
                            'position': self.items_scraped,
                            'description': description
                        }
                    )
                else:
                    # If no link, just yield what we have
                    self.items_saved += 1
                    yield {
                        'title': title,
                        'platform': 'PC',
                        'description': description,
                        'image_url': img_url,
                        'source_name': 'GameSpot Gallery',
                        'rank': self.items_scraped
                    }
        
        # Check if we need more games and if there's a next page
        if self.items_scraped < self.limit:
            next_page = response.css('a.btn-load-more::attr(href)').get()
            if next_page:
                yield response.follow(next_page, self.parse)
    
    def parse_game(self, response):
        try:
            # Extract data passed from list page
            title = response.meta.get('title')
            img_url = response.meta.get('image_url')
            position = response.meta.get('position')
            description = response.meta.get('description')
            
            self._logger.info(f"Parsing game #{position}: {title}")
            
            # Details section
            info_section = response.css('div.kubrick-info')
            
            # If we don't have a description from the gallery, get one now
            if not description:
                description = response.css('div.kubrick-game-overview p::text').get()
                if not description:
                    description = response.css('div.game-summary p::text').get()
                if not description:
                    description = response.css('div.pod-description::text').get()
            
            # Release date
            release_date_text = info_section.css('li.release-date time::text').get()
            release_date = None
            if release_date_text:
                try:
                    # Try different date formats
                    date_formats = ['%B %d, %Y', '%b %d, %Y']
                    for fmt in date_formats:
                        try:
                            release_date = datetime.strptime(release_date_text.strip(), fmt)
                            break
                        except ValueError:
                            continue
                except Exception as e:
                    self._logger.warning(f"Could not parse release date: {release_date_text} - {str(e)}")
            
            # Publisher & Developer
            publisher = info_section.css('li.publisher::text').get()
            if publisher:
                publisher = publisher.strip()
                
            developer = info_section.css('li.developer::text').get()
            if developer:
                developer = developer.strip()
            
            # Get GameSpot score
            score = None
            score_elem = response.css('div.gs-score__cell span::text').get()
            if score_elem:
                try:
                    score = float(score_elem.strip())
                    # Convert to 0-100 scale to match Metacritic
                    if score <= 10:
                        score = score * 10
                except ValueError:
                    pass
            
            # Extract genres
            genres = []
            genre_elements = info_section.css('li.genre a::text').getall()
            if genre_elements:
                genres = [g.strip() for g in genre_elements]
            
            # Make sure we have an image URL - try to get a high quality one
            if not img_url:
                # GameSpot tends to have large hero images
                img_url = response.css('div.kubrick-hero__image img::attr(src)').get()
                if not img_url:
                    img_url = response.css('img.hero-image::attr(src)').get()
                if not img_url:
                    # Try other selectors for newer layout
                    img_url = response.css('picture.hero-image source::attr(srcset)').get()
                    if img_url and ',' in img_url:
                        # Take largest image from srcset
                        img_url = img_url.split(',')[-1].strip().split(' ')[0]
            
            # If still no image, check for article images that might be relevant
            if not img_url:
                img_url = response.css('div.article-image img::attr(src)').get()
            
            # ESRB Rating
            age_rating = None
            rating_elem = info_section.css('li.rating::text').get()
            if rating_elem:
                # Try to extract just the rating code (like "M" or "T")
                rating_match = re.search(r'([ETKMA](?:\d+)?)', rating_elem)
                if rating_match:
                    age_rating = rating_match.group(1)
                else:
                    age_rating = rating_elem.strip()
            
            self.items_saved += 1
            
            # Return the item
            yield {
                'title': title,
                'platform': 'PC',
                'release_date': release_date,
                'publisher': publisher,
                'developer': developer,
                'description': description,
                'genres': genres,
                'image_url': img_url,
                'source_url': response.url,
                'source_name': 'GameSpot',
                'age_rating': age_rating,
                'rank': position,
                'metascore': int(score) if score else None
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