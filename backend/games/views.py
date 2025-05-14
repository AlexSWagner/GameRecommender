from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from .models import Game, Genre, Platform
from .serializers import (
    GameListSerializer, GameDetailSerializer,
    GenreSerializer, PlatformSerializer
)


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for game genres."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]


class PlatformViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for game platforms."""
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer
    permission_classes = [permissions.IsAuthenticated]


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for games."""
    queryset = Game.objects.all()
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genres', 'platforms', 'is_multiplayer', 'is_free_to_play']
    search_fields = ['title', 'description', 'publisher', 'developer']
    ordering_fields = ['title', 'release_date', 'rating', 'metacritic_score']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return GameDetailSerializer
        return GameListSerializer
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Enhanced search endpoint that allows searching across multiple fields 
        and filtering by various criteria simultaneously.
        """
        query = request.query_params.get('q', '')
        
        if not query:
            return Response({'results': []})
        
        # Create a complex query with Q objects
        search_query = Q(title__icontains=query) | \
                      Q(description__icontains=query) | \
                      Q(publisher__icontains=query) | \
                      Q(developer__icontains=query)
        
        # Apply filters from query params
        genre_id = request.query_params.get('genre')
        platform_id = request.query_params.get('platform')
        multiplayer = request.query_params.get('multiplayer')
        free_to_play = request.query_params.get('free_to_play')
        
        queryset = self.get_queryset().filter(search_query)
        
        if genre_id:
            queryset = queryset.filter(genres__id=genre_id)
        
        if platform_id:
            queryset = queryset.filter(platforms__id=platform_id)
        
        if multiplayer is not None:
            multiplayer_bool = multiplayer.lower() == 'true'
            queryset = queryset.filter(is_multiplayer=multiplayer_bool)
        
        if free_to_play is not None:
            free_bool = free_to_play.lower() == 'true'
            queryset = queryset.filter(is_free_to_play=free_bool)
        
        # Limit to 20 results for performance
        queryset = queryset[:20]
        
        serializer = GameListSerializer(queryset, many=True)
        return Response({'results': serializer.data})
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def top_rated(self, request):
        """Get top rated games."""
        # Get the limit parameter with a default of 50
        limit_param = request.query_params.get('limit', '50')
        try:
            limit = int(limit_param)
            # Cap at 100 for performance
            limit = min(limit, 100)
        except ValueError:
            limit = 50
        
        print(f"API: Requesting top {limit} rated games")
        
        # Get games with metacritic scores, sorted by score descending
        base_queryset = self.get_queryset().exclude(metacritic_score__isnull=True).order_by('-metacritic_score')
        
        # Count total qualifying games
        total_qualifying = base_queryset.count()
        print(f"API: Found {total_qualifying} qualifying games with metacritic scores")
        
        # Force evaluation to a list to avoid query issues
        all_qualifying_games = list(base_queryset)
        
        # Sort the games so that those with verified cached images are first
        games_with_verified_images = [g for g in all_qualifying_games if g.cached_image and g.cached_image.is_verified]
        games_with_unverified_images = [g for g in all_qualifying_games if g.cached_image and not g.cached_image.is_verified]
        games_with_uncached_images = [g for g in all_qualifying_games if g.image_url and not g.cached_image]
        games_without_images = [g for g in all_qualifying_games if not g.image_url and not g.cached_image]
        
        # Build the result list in priority order, respecting the limit
        result_list = []
        result_list.extend(games_with_verified_images[:limit])
        
        # If we need more games, add those with unverified cached images
        if len(result_list) < limit:
            remaining = limit - len(result_list)
            result_list.extend(games_with_unverified_images[:remaining])
        
        # If we need more games, add those with uncached images
        if len(result_list) < limit:
            remaining = limit - len(result_list)
            result_list.extend(games_with_uncached_images[:remaining])
        
        # If we need more games, add those without images
        if len(result_list) < limit:
            remaining = limit - len(result_list)
            result_list.extend(games_without_images[:remaining])
        
        final_count = len(result_list)
        print(f"API: Returning {final_count} total games")
        
        # Cache images for games without cached images - in a background process if possible
        uncached_games = [g for g in result_list if not g.cached_image]
        if uncached_games:
            print(f"API: Found {len(uncached_games)} games without cached images - scheduling caching")
            try:
                from games.utils.image_cache import cache_game_image
                for game in uncached_games[:10]:  # Limit to 10 to avoid blocking the API
                    cache_game_image(game)
            except Exception as e:
                print(f"API: Error caching images: {e}")
        
        serializer = GameListSerializer(result_list, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recently released games."""
        queryset = self.get_queryset().exclude(release_date__isnull=True).order_by('-release_date')[:10]
        serializer = GameListSerializer(queryset, many=True)
        return Response(serializer.data)
