from django.contrib import admin
from django.utils.html import format_html
from .models import Game, Genre, Platform, GameReview

# Register your models here.

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_count')
    search_fields = ('name',)
    
    def game_count(self, obj):
        return obj.games.count()
    game_count.short_description = 'Number of Games'


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_count')
    search_fields = ('name',)
    
    def game_count(self, obj):
        return obj.games.count()
    game_count.short_description = 'Number of Games'


class GameReviewInline(admin.TabularInline):
    model = GameReview
    extra = 0
    fields = ('source', 'author', 'rating', 'review_date')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'metacritic_score', 'display_genres', 'display_platforms', 'display_image')
    list_filter = ('genres', 'platforms', 'is_multiplayer', 'is_free_to_play')
    search_fields = ('title', 'description', 'publisher', 'developer')
    readonly_fields = ('source_url', 'source_name', 'last_updated')
    filter_horizontal = ('genres', 'platforms')
    date_hierarchy = 'release_date'
    inlines = [GameReviewInline]
    
    def display_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()[:3]])
    display_genres.short_description = 'Genres'
    
    def display_platforms(self, obj):
        return ", ".join([platform.name for platform in obj.platforms.all()])
    display_platforms.short_description = 'Platforms'
    
    def display_image(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image_url)
        return "-"
    display_image.short_description = 'Image'


@admin.register(GameReview)
class GameReviewAdmin(admin.ModelAdmin):
    list_display = ('game', 'source', 'author', 'rating', 'review_date')
    list_filter = ('source', 'review_date')
    search_fields = ('game__title', 'author', 'content')
    readonly_fields = ('url',)
