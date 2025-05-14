from django.db import models

# Create your models here.

class ScrapingSource(models.Model):
    """Represents a source website from which game data is scraped."""
    name = models.CharField(max_length=100)
    base_url = models.URLField()
    description = models.TextField(blank=True)
    
    # Scraping configuration
    spider_name = models.CharField(max_length=100)  # Name of the Scrapy spider for this source
    is_active = models.BooleanField(default=True)  # Whether to include this source in scraping runs
    
    # Source metadata
    requires_javascript = models.BooleanField(default=False)  # Whether the source requires JavaScript rendering
    requires_login = models.BooleanField(default=False)  # Whether the source requires login credentials
    
    # Rate limiting
    requests_per_minute = models.IntegerField(default=10)  # Rate limit for requests
    
    # Last scrape timestamp
    last_scraped = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.name


class ScrapingJob(models.Model):
    """Tracks individual scraping job executions."""
    source = models.ForeignKey(ScrapingSource, on_delete=models.CASCADE, related_name='jobs')
    
    # Job status
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    # Job execution timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Job results
    items_scraped = models.IntegerField(default=0)
    items_saved = models.IntegerField(default=0)
    errors = models.TextField(blank=True)
    
    # Job configuration
    task_id = models.CharField(max_length=50, blank=True)  # Celery task ID
    custom_settings = models.JSONField(default=dict, blank=True)  # Any custom scraping settings
    
    def __str__(self):
        return f"Scraping job for {self.source.name} ({self.status})"


class ScrapingError(models.Model):
    """Records specific errors encountered during scraping."""
    job = models.ForeignKey(ScrapingJob, on_delete=models.CASCADE, related_name='error_details')
    url = models.URLField()
    error_type = models.CharField(max_length=100)
    error_message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Error in {self.job.source.name}: {self.error_type}"
