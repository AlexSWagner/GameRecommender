from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import ScrapingSource, ScrapingJob, ScrapingError

# Register your models here.

@admin.register(ScrapingSource)
class ScrapingSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_url', 'spider_name', 'is_active', 'last_scraped', 'run_scraper_link')
    list_filter = ('is_active',)
    search_fields = ('name', 'base_url', 'spider_name')
    actions = ['run_scraper']
    
    def run_scraper_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Run Scraper</a>',
            reverse('admin:run-scraper', args=[obj.pk])
        )
    run_scraper_link.short_description = 'Run'
    
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/run-scraper/',
                self.admin_site.admin_view(self.run_scraper_view),
                name='run-scraper',
            ),
        ]
        return custom_urls + urls
    
    def run_scraper_view(self, request, object_id):
        from scraper.tasks import scrape_source
        result = scrape_source.delay(object_id)
        self.message_user(request, f"Scraper task started with ID: {result.id}")
        return HttpResponseRedirect("../../../")
    
    def run_scraper(self, request, queryset):
        from scraper.tasks import scrape_source
        for source in queryset:
            scrape_source.delay(source.id)
        self.message_user(request, f"Started scraper tasks for {queryset.count()} sources")
    run_scraper.short_description = "Run scraper for selected sources"


@admin.register(ScrapingJob)
class ScrapingJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'source', 'status', 'started_at', 'completed_at', 'items_scraped', 'items_saved')
    list_filter = ('status', 'source')
    search_fields = ('source__name',)
    readonly_fields = ('started_at', 'completed_at', 'task_id')


@admin.register(ScrapingError)
class ScrapingErrorAdmin(admin.ModelAdmin):
    list_display = ('job', 'error_type', 'timestamp', 'url')
    list_filter = ('error_type', 'job__source')
    search_fields = ('error_message', 'url')
