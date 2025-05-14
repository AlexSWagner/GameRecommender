import React, { useEffect, useState } from 'react';
import { Container, Row, Col, Card } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getTopRatedGames } from '../services/api';
import GameCard from '../components/GameCard';

const HomePage = () => {
  const { isAuthenticated, hasCompletedSurvey } = useAuth();
  const [topGames, setTopGames] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTopGames = async () => {
      try {
        // Request exactly 6 games with explicit string conversion
        const data = await getTopRatedGames('6');
        
        // Ensure we only display exactly 6 games, even if API returns more
        const limitedData = data.slice(0, 6);
        
        setTopGames(limitedData);
      } catch (error) {
        console.error('Error fetching top games:', error);
        // Fall back to mock data if API fails - only use 3 mock games for homepage
        setTopGames(mockGames.slice(0, 3));
      } finally {
        setLoading(false);
      }
    };

    fetchTopGames();
  }, []);

  return (
    <Container>
      {/* Hero Section */}
      <Row className="mb-5 py-5 bg-light rounded">
        <Col md={6} className="d-flex flex-column justify-content-center">
          <h1>Find Your Next Favorite Game</h1>
          <p className="lead">
            Get personalized game recommendations based on your preferences, gaming history, and interests.
          </p>
          {isAuthenticated ? (
            hasCompletedSurvey() ? (
              <Link to="/recommendations" className="btn btn-primary btn-lg">
                View Your Recommendations
              </Link>
            ) : (
              <Link to="/survey" className="btn btn-primary btn-lg">
                Take the Survey
              </Link>
            )
          ) : (
            <div className="d-flex gap-2">
              <Link to="/register" className="btn btn-primary btn-lg">
                Sign Up
              </Link>
              <Link to="/login" className="btn btn-outline-primary btn-lg">
                Login
              </Link>
            </div>
          )}
        </Col>
        <Col md={6}>
          <img 
            src="https://via.placeholder.com/600x400?text=Game+Recommender" 
            alt="Game Recommendations" 
            className="img-fluid rounded shadow"
          />
        </Col>
      </Row>

      {/* How It Works Section */}
      <Row className="mb-5">
        <Col xs={12}>
          <h2 className="text-center mb-4">How It Works</h2>
        </Col>
        <Col md={4}>
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="text-center">
              <div className="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center mb-3" style={{ width: '64px', height: '64px' }}>
                1
              </div>
              <Card.Title>Create an Account</Card.Title>
              <Card.Text>
                Sign up for free and create your personal gaming profile to start receiving recommendations.
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="text-center">
              <div className="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center mb-3" style={{ width: '64px', height: '64px' }}>
                2
              </div>
              <Card.Title>Take the Survey</Card.Title>
              <Card.Text>
                Tell us about your gaming preferences, favorite genres, platforms, and play style.
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
        <Col md={4}>
          <Card className="h-100 border-0 shadow-sm">
            <Card.Body className="text-center">
              <div className="rounded-circle bg-primary text-white d-inline-flex align-items-center justify-content-center mb-3" style={{ width: '64px', height: '64px' }}>
                3
              </div>
              <Card.Title>Get Recommendations</Card.Title>
              <Card.Text>
                Receive personalized game recommendations tailored specifically to your preferences.
              </Card.Text>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Featured Games Section */}
      {!loading && topGames.length > 0 && (
        <Row className="mb-5">
          <Col xs={12}>
            <h2 className="text-center mb-4">Top Rated Games</h2>
            <p className="text-center text-muted mb-4">
              Discover the highest-rated games based on critic reviews
            </p>
          </Col>
          {topGames.map(game => (
            <Col md={4} key={game.id} className="mb-4">
              <GameCard game={game} />
            </Col>
          ))}
          <Col xs={12} className="text-center mt-3">
            <Link to="/recommendations" className="btn btn-outline-primary">
              View More Games
            </Link>
          </Col>
        </Row>
      )}

      {/* Call to Action */}
      <Row className="py-5 bg-primary text-white rounded mb-5">
        <Col xs={12} className="text-center py-4">
          <h2>Ready to discover your next gaming adventure?</h2>
          <p className="lead">
            Join thousands of gamers and get personalized recommendations today.
          </p>
          {isAuthenticated ? (
            hasCompletedSurvey() ? (
              <Link to="/recommendations" className="btn btn-light btn-lg">
                View Your Recommendations
              </Link>
            ) : (
              <Link to="/survey" className="btn btn-light btn-lg">
                Take the Survey
              </Link>
            )
          ) : (
            <div className="d-flex gap-2 justify-content-center">
              <Link to="/recommendations" className="btn btn-light btn-lg">
                Browse Games
              </Link>
              <Link to="/register" className="btn btn-outline-light btn-lg">
                Sign Up
              </Link>
            </div>
          )}
        </Col>
      </Row>
    </Container>
  );
};

// Mock game data for development
const mockGames = [
  {
    id: 1,
    title: "The Legend of Zelda: Breath of the Wild",
    image_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co3p2d.jpg",
    release_date: "2017-03-03",
    metacritic_score: 97,
    genres: [
      { id: 1, name: "Action" },
      { id: 2, name: "Adventure" },
      { id: 3, name: "RPG" }
    ]
  },
  {
    id: 2,
    title: "Red Dead Redemption 2",
    image_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1q1f.jpg",
    release_date: "2018-10-26",
    metacritic_score: 93,
    genres: [
      { id: 1, name: "Action" },
      { id: 4, name: "Open World" }
    ]
  },
  {
    id: 3,
    title: "Elden Ring",
    image_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co4jni.jpg",
    release_date: "2022-02-25",
    metacritic_score: 94,
    genres: [
      { id: 1, name: "Action" },
      { id: 3, name: "RPG" },
      { id: 5, name: "Souls-like" }
    ]
  }
];

export default HomePage; 