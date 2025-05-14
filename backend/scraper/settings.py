BOT_NAME = 'game_recommender'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

# Crawl responsibly by identifying yourself 
USER_AGENT = 'GameRecommender (+http://gamerecommender.example.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 8

# Configure a delay for requests for the same website 
DOWNLOAD_DELAY = 1

# Disable cookies 
COOKIES_ENABLED = False

# Configure item pipelines
ITEM_PIPELINES = {
   'scraper.pipelines.GameDataPipeline': 300,
}

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8" 