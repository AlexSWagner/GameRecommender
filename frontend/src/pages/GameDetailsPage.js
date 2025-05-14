import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Badge, Spinner, Alert, Button } from 'react-bootstrap';
import { useParams, Link } from 'react-router-dom';
import { getGame } from '../services/api';

const GameDetailsPage = () => {
  const { id } = useParams();
  const [game, setGame] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  useEffect(() => {
    const fetchGameDetails = async () => {
      try {
        setLoading(true);
        const gameData = await getGame(id);
        setGame(gameData);
        setError(null);
      } catch (err) {
        console.error('Error fetching game details:', err);
        setError('Failed to load game details. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      fetchGameDetails();
    }
  }, [id]);

  // Rating color based on score
  const getRatingColor = (score) => {
    if (!score) return 'secondary';
    if (score >= 90) return 'success';
    if (score >= 75) return 'primary';
    if (score >= 60) return 'warning';
    return 'danger';
  };

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    try {
      return new Date(dateString).toLocaleDateString(undefined, options);
    } catch (e) {
      return 'Unknown';
    }
  };

  // Handle image error
  const handleImageError = () => {
    console.log("Game details image failed to load:", game?.image_url);
    setImageError(true);
    setImageLoaded(true);
  };

  // Handle image load success
  const handleImageLoad = () => {
    setImageLoaded(true);
  };

  const placeholderImage = 'https://via.placeholder.com/400x600?text=No+Image';
  
  // Determine image URL properly with error handling
  let imageUrl = placeholderImage;
  
  if (game?.image_url && !imageError) {
    imageUrl = game.image_url;
    
    // If image URL starts with http and not https, try with https
    if (imageUrl.startsWith('http:') && !imageUrl.startsWith('https:')) {
      imageUrl = imageUrl.replace('http:', 'https:');
    }
    
    // Fix common issues with image URLs
    // 1. Check for double slashes in path (not protocol)
    if (imageUrl.includes('://')) {
      const urlParts = imageUrl.split('://');
      if (urlParts.length > 1 && urlParts[1].includes('//')) {
        urlParts[1] = urlParts[1].replace(/\/+/g, '/');
        imageUrl = urlParts[0] + '://' + urlParts[1];
      }
    }
    
    // 2. Make sure URL is properly encoded
    try {
      const url = new URL(imageUrl);
      // Keep the URL object as is, it's already valid
      imageUrl = url.toString();
    } catch (e) {
      // If URL is invalid, try to encode it
      try {
        // Try to fix common issues (spaces, etc)
        imageUrl = encodeURI(imageUrl);
      } catch (encodeError) {
        console.log("Could not encode URL:", imageUrl);
        imageUrl = placeholderImage;
      }
    }
  }

  if (loading) {
    return (
      <Container className="py-5 text-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-3">Loading game details...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="py-5">
        <Alert variant="danger">
          {error}
        </Alert>
        <div className="text-center mt-3">
          <Link to="/" className="btn btn-primary">
            Back to Home
          </Link>
        </div>
      </Container>
    );
  }

  if (!game) {
    return (
      <Container className="py-5">
        <Alert variant="warning">
          Game not found.
        </Alert>
        <div className="text-center mt-3">
          <Link to="/" className="btn btn-primary">
            Back to Home
          </Link>
        </div>
      </Container>
    );
  }

  return (
    <Container className="py-5">
      <Row className="mb-4">
        <Col>
          <Link to="/" className="btn btn-outline-secondary mb-3">
            &larr; Back to Home
          </Link>
          <h1>{game.title}</h1>
        </Col>
      </Row>

      <Row>
        {/* Game cover image */}
        <Col md={4} className="mb-4">
          <Card className="h-100">
            <div 
              style={{ 
                minHeight: '300px', 
                backgroundColor: '#f8f9fa',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              {!imageLoaded && (
                <div 
                  className="d-flex justify-content-center align-items-center" 
                  style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 }}
                >
                  <Spinner animation="border" />
                </div>
              )}
              <Card.Img 
                variant="top" 
                src={imageUrl} 
                alt={game.title}
                onError={handleImageError}
                onLoad={handleImageLoad}
                style={{ 
                  maxHeight: '500px', 
                  objectFit: imageError ? 'contain' : 'cover',
                  opacity: imageLoaded ? 1 : 0,
                  transition: 'opacity 0.3s ease',
                  padding: imageError ? '20px' : 0
                }}
              />
            </div>
            <Card.Body>
              {game.metacritic_score && (
                <div className="d-flex align-items-center mb-3">
                  <div className={`me-2 badge bg-${getRatingColor(game.metacritic_score)}`} 
                       style={{ fontSize: '1.2rem', padding: '8px 12px' }}>
                    {game.metacritic_score}
                  </div>
                  <span>Metacritic Score</span>
                </div>
              )}
              
              <div className="mb-3">
                <strong>Released:</strong> {formatDate(game.release_date)}
              </div>
              
              {game.publisher && (
                <div className="mb-3">
                  <strong>Publisher:</strong> {game.publisher}
                </div>
              )}
              
              {game.developer && (
                <div className="mb-3">
                  <strong>Developer:</strong> {game.developer}
                </div>
              )}
              
              {game.genres && game.genres.length > 0 && (
                <div className="mb-3">
                  <strong>Genres:</strong><br />
                  <div className="mt-1">
                    {game.genres.map((genre) => (
                      <Badge 
                        key={genre.id} 
                        bg="secondary" 
                        className="me-1 mb-1"
                      >
                        {genre.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {game.platforms && game.platforms.length > 0 && (
                <div className="mb-3">
                  <strong>Platforms:</strong><br />
                  <div className="mt-1">
                    {game.platforms.map((platform) => (
                      <Badge 
                        key={platform.id} 
                        bg="info" 
                        className="me-1 mb-1"
                      >
                        {platform.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
              
              {game.age_rating && (
                <div className="mb-3">
                  <strong>Age Rating:</strong> {game.age_rating}
                </div>
              )}
              
              {game.source_name && (
                <div className="mt-4 text-muted small">
                  <em>Data source: {game.source_name}</em>
                  {game.source_url && (
                    <a 
                      href={game.source_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="ms-2"
                    >
                      View Source
                    </a>
                  )}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        {/* Game details */}
        <Col md={8}>
          <Card className="mb-4">
            <Card.Body>
              <Card.Title>About</Card.Title>
              <Card.Text className="game-description">
                {game.description || 'No description available.'}
              </Card.Text>
            </Card.Body>
          </Card>
          
          {/* Game characteristics */}
          <Card className="mb-4">
            <Card.Body>
              <Card.Title>Game Features</Card.Title>
              <div className="d-flex flex-wrap mt-3">
                <div className="feature-badge me-3 mb-3">
                  <Badge bg={game.is_multiplayer ? 'success' : 'secondary'} className="p-2">
                    {game.is_multiplayer ? 'Multiplayer' : 'Single Player'}
                  </Badge>
                </div>
                
                <div className="feature-badge me-3 mb-3">
                  <Badge bg={game.is_free_to_play ? 'success' : 'secondary'} className="p-2">
                    {game.is_free_to_play ? 'Free to Play' : 'Paid'}
                  </Badge>
                </div>
                
                <div className="feature-badge me-3 mb-3">
                  <Badge bg={game.has_in_app_purchases ? 'warning' : 'success'} className="p-2">
                    {game.has_in_app_purchases ? 'Has In-App Purchases' : 'No In-App Purchases'}
                  </Badge>
                </div>
              </div>
            </Card.Body>
          </Card>
          
          {/* Reviews */}
          {game.reviews && game.reviews.length > 0 && (
            <Card>
              <Card.Body>
                <Card.Title>Reviews</Card.Title>
                {game.reviews.map((review) => (
                  <div key={review.id} className="mb-4 pb-3 border-bottom">
                    <div className="d-flex justify-content-between">
                      <h5>{review.source}</h5>
                      {review.rating && (
                        <Badge bg={getRatingColor(review.rating * 10)} className="p-2">
                          {review.rating}/10
                        </Badge>
                      )}
                    </div>
                    <p className="text-muted small">
                      {review.author ? `By ${review.author}` : ''} 
                      {review.review_date ? ` • ${formatDate(review.review_date)}` : ''}
                    </p>
                    <p>{review.content || 'No review content available.'}</p>
                    {review.url && (
                      <a 
                        href={review.url} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        className="btn btn-sm btn-outline-primary"
                      >
                        Read Full Review
                      </a>
                    )}
                  </div>
                ))}
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default GameDetailsPage; 