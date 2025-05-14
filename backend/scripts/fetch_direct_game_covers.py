#!/usr/bin/env python
"""
Script to directly fetch game cover images without requiring API keys
"""
import os
import sys
import time
import json
import requests
import urllib.parse
from bs4 import BeautifulSoup
import sqlite3
import re

# Add the project path to the sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from games.models import Game

# Store game covers in this SQLite DB
COVERS_DB = "game_covers.db"

def create_covers_db():
    """Create SQLite database to store game cover URLs"""
    conn = sqlite3.connect(COVERS_DB)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_covers (
        game_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        image_url TEXT NOT NULL,
        source TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()
    print(f"Created covers database at {COVERS_DB}")

def store_cover(game_id, title, image_url, source):
    """Store a game cover in the SQLite database"""
    conn = sqlite3.connect(COVERS_DB)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO game_covers (game_id, title, image_url, source) VALUES (?, ?, ?, ?)",
        (game_id, title, image_url, source)
    )
    conn.commit()
    conn.close()

def get_stored_cover(game_id):
    """Get a stored cover URL for a game ID"""
    conn = sqlite3.connect(COVERS_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT image_url FROM game_covers WHERE game_id = ?", (game_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def google_image_search(query, max_results=5):
    """Search for images using Google Images"""
    try:
        search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}&tbm=isch"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            print(f"Error: Google search returned status code {response.status_code}")
            return []
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract image URLs using different methods
        images = []
        
        # Method 1: Look for JSON data in the page
        for script in soup.find_all('script'):
            if script.string and 'AF_initDataCallback' in script.string:
                data_matches = re.findall(r'AF_initDataCallback\((.*?)\);', script.string, re.DOTALL)
                for data_match in data_matches:
                    try:
                        data = json.loads(data_match)
                        if 'data' in data and isinstance(data['data'], list):
                            for item in data['data']:
                                # Navigate the complex JSON structure
                                if isinstance(item, list) and len(item) > 1:
                                    for subitem in item:
                                        if isinstance(subitem, list):
                                            for element in subitem:
                                                if isinstance(element, dict) and 'ou' in element:
                                                    images.append(element['ou'])
                    except:
                        pass
        
        # Method 2: Look for image elements with src or data-src attributes
        for img in soup.find_all('img'):
            src = img.get('src', '')
            data_src = img.get('data-src', '')
            if src and 'http' in src and '.jpg' in src:
                images.append(src)
            elif data_src and 'http' in data_src and '.jpg' in data_src:
                images.append(data_src)
        
        # Method 3: Look for <div> elements with background-image style
        for div in soup.find_all('div', style=True):
            if 'background-image: url(' in div['style']:
                url = div['style'].split('background-image: url(')[1].split(')')[0].strip("'\"")
                if url.startswith('http'):
                    images.append(url)
        
        return list(dict.fromkeys(images))[:max_results]  # Remove duplicates
    except Exception as e:
        print(f"Error in Google image search: {str(e)}")
        return []

def duckduckgo_image_search(query, max_results=5):
    """Search for images using DuckDuckGo"""
    try:
        search_term = query.replace(' ', '+')
        url = f"https://duckduckgo.com/?q={search_term}&iax=images&ia=images"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: DuckDuckGo search returned status code {response.status_code}")
            return []
        
        # Parse the vqd parameter needed for the API request
        vqd_match = re.search(r'vqd="([^"]+)"', response.text)
        if not vqd_match:
            vqd_match = re.search(r'vqd=([^&]+)&', response.text)
            if not vqd_match:
                print("Could not find vqd parameter in DuckDuckGo response")
                return []
        
        vqd = vqd_match.group(1)
        
        # Make the API request to get image results
        api_url = f"https://duckduckgo.com/i.js?q={search_term}&vqd={vqd}&p=1"
        api_response = requests.get(api_url, headers=headers)
        
        if api_response.status_code != 200:
            print(f"Error: DuckDuckGo API returned status code {api_response.status_code}")
            return []
        
        data = api_response.json()
        images = []
        
        if 'results' in data:
            for result in data['results'][:max_results]:
                if 'image' in result:
                    images.append(result['image'])
        
        return images
    except Exception as e:
        print(f"Error in DuckDuckGo image search: {str(e)}")
        return []

def fetch_game_cover(game):
    """Fetch cover image for a game from multiple sources"""
    # Check if we already have this game's cover stored
    stored_url = get_stored_cover(game.id)
    if stored_url:
        print(f"Using stored cover for {game.title} from database")
        return stored_url
    
    # Format search query with release year if available
    release_year = f" {game.release_date.year}" if game.release_date else ""
    query = f"{game.title}{release_year} game cover art"
    
    # Try Google Image Search first
    print(f"Searching Google for {query}")
    images = google_image_search(query)
    if images:
        image_url = images[0]
        store_cover(game.id, game.title, image_url, "google")
        return image_url
    
    # Try DuckDuckGo if Google fails
    print(f"Searching DuckDuckGo for {query}")
    images = duckduckgo_image_search(query)
    if images:
        image_url = images[0]
        store_cover(game.id, game.title, image_url, "duckduckgo")
        return image_url
    
    return None

def update_game_covers():
    """Update all games with cover images"""
    # Create the database if it doesn't exist
    create_covers_db()
    
    # Get all games
    games = Game.objects.all().order_by('-release_date')
    total_games = games.count()
    
    print(f"Found {total_games} games to process")
    
    # Process each game
    success_count = 0
    failure_count = 0
    
    for i, game in enumerate(games):
        print(f"\nProcessing [{i+1}/{total_games}] {game.title}...")
        
        # Skip if game already has an image
        if game.image_url and 'placeholder' not in game.image_url.lower():
            print(f"Game already has an image URL: {game.image_url}")
            success_count += 1
            continue
        
        try:
            # Fetch cover image
            image_url = fetch_game_cover(game)
            
            if image_url:
                # Update the game with the new image URL
                game.image_url = image_url
                game.save()
                print(f"✓ Found and saved image: {image_url}")
                success_count += 1
            else:
                print(f"✗ No image found for {game.title}")
                failure_count += 1
        except Exception as e:
            print(f"✗ Error processing {game.title}: {str(e)}")
            failure_count += 1
        
        # Add a delay to avoid rate limiting
        if i < total_games - 1:
            time.sleep(1)
    
    # Print summary
    print(f"\nCompleted: {success_count} successes, {failure_count} failures")

if __name__ == "__main__":
    update_game_covers() 