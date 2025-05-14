# Game Recommendations Web Application

A web application that provides personalized game recommendations to users based on scraped game data and user preferences.

## Features

- **User Authentication**: Sign up, login, and user profiles
- **Preference Survey**: Detailed user survey to capture gaming preferences
- **Game Recommendations**: Personalized game recommendations based on user preferences
- **Game Database**: Comprehensive database of games with details and metadata
- **Web Scraping**: Automated scraping of game data from popular sources

## Technologies Used

### Backend
- **Django**: Web framework
- **Django REST Framework**: API development
- **PostgreSQL**: Database
- **Celery**: Task queue for background processing
- **Redis**: Message broker for Celery
- **Scrapy**: Web scraping framework
- **BeautifulSoup4 & Requests**: Additional web scraping tools
- **Pandas & scikit-learn**: For recommendation engine

### Frontend
- **React**: Frontend library
- **React Bootstrap**: UI components
- **Axios**: HTTP client
- **React Router**: Navigation
- **Formik & Yup**: Form handling and validation

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd GameRecommender
   ```

2. Build and start the containers
   ```bash
   docker-compose up -d --build
   ```

3. Create a superuser for the Django admin
   ```bash
   docker-compose exec backend python manage.py createsuperuser
   ```

4. Access the application
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Admin Panel: http://localhost:8000/admin/

## Project Structure

```
GameRecommender/
├── backend/               # Django backend
│   ├── core/              # Project settings & configuration
│   ├── games/             # Game models and API
│   ├── users/             # User profiles and preferences
│   ├── recommendations/   # Recommendation engine
│   ├── scraper/           # Web scraping module
│   └── ...
├── frontend/              # React frontend
│   ├── public/
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context providers
│   │   ├── services/      # API services
│   │   └── ...
│   └── ...
└── docker-compose.yml     # Docker configuration
```

## Usage

1. Register a new account on the application
2. Complete the gaming preferences survey
3. Receive personalized game recommendations
4. Provide feedback on recommendations to improve future suggestions

## Development

### Running in Development Mode

```bash
# Start the development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Backend development
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

# Frontend development
docker-compose exec frontend npm install
docker-compose exec frontend npm start
```

### Scraping Data

```bash
# Run all active scrapers manually (recommended for populating images)
docker-compose exec backend python manage.py run_all_scrapers --limit 50

# Run a specific scraping job manually
docker-compose exec backend python manage.py run_scraper <source_name>

# Run the scraping scheduler
docker-compose exec backend python manage.py shell -c "from scraper.tasks import scrape_game_data; scrape_game_data()"
```

### Troubleshooting

#### Images Not Appearing

If game images are not appearing on the site:

1. Make sure scrapers have been run to populate the database with image URLs:
   ```bash
   docker-compose exec backend python manage.py run_all_scrapers
   ```

2. Check browser console for image loading errors

3. Verify that games have valid image_url values in the database:
   ```bash
   docker-compose exec backend python manage.py shell -c "from games.models import Game; print(Game.objects.exclude(image_url='').count())"
   ```

4. If using a production environment, ensure your CORS settings allow loading images from external domains

## License

This project is licensed under the MIT License - see the LICENSE file for details. 