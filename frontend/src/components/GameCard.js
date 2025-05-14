import React, { useState, useEffect } from 'react';
import { Card, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import './GameCard.css'; // We'll create this CSS file next

const GameCard = ({ game }) => {
  // Default image if none is provided
  const defaultImage = 'https://via.placeholder.com/300x400?text=Game+Image';
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [finalImageUrl, setFinalImageUrl] = useState('');
  
  // Default genres if none are provided
  const genres = game.genres || [];
  
  // Format release date if available
  const formatReleaseDate = (dateString) => {
    if (!dateString) return 'Unknown';
    
    const date = new Date(dateString);
    const year = date.getFullYear();
    
    // Only return the year if it's a valid number
    return !isNaN(year) ? year.toString() : 'Unknown';
  };
  
  // Get rating color based on score
  const getRatingColor = (score) => {
    if (!score) return 'secondary';
    if (score >= 90) return 'success';
    if (score >= 75) return 'primary';
    if (score >= 60) return 'warning';
    return 'danger';
  };
  
  // Handle image error
  const handleImageError = (e) => {
    console.log("Image failed to load:", game.image_url);
    setImageError(true);
    setIsLoading(false);
    setFinalImageUrl(defaultImage);
    e.target.src = defaultImage;
  };

  // Handle image load success
  const handleImageLoad = () => {
    setIsLoading(false);
  };

  // Set up image URL when component mounts or game changes
  useEffect(() => {
    // Start with loading state
    setIsLoading(true);
    setImageError(false);
    
    // Determine image URL
    let imageUrl = '';
    
    if (game.image_url && game.image_url.trim() !== '') {
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
          imageUrl = defaultImage;
          setIsLoading(false);
        }
      }
    } else {
      // No valid image URL, use default
      imageUrl = defaultImage;
      // We know the image will load since it's default
      setIsLoading(false);
    }
    
    // Always set the final image URL to either the valid image URL or the default
    setFinalImageUrl(imageUrl);
  }, [game.image_url, defaultImage]);
  
  return (
    <Card className="h-100 game-card">
      <Link to={`/game/${game.id}`} className="text-decoration-none">
        <div className="game-card-img-container">
          {isLoading && !imageError && (
            <div className="image-loading-spinner">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          )}
          <Card.Img 
            variant="top" 
            src={finalImageUrl}
            alt={game.title}
            className={`game-card-img ${isLoading ? 'loading' : 'loaded'}`}
            onError={handleImageError}
            onLoad={handleImageLoad}
            loading="lazy"
          />
          {game.metacritic_score && (
            <div className={`metacritic-score bg-${getRatingColor(game.metacritic_score)}`}>
              {game.metacritic_score}
            </div>
          )}
        </div>
        <Card.Body>
          <Card.Title className="game-title">{game.title}</Card.Title>
          <div className="game-details">
            <div className="release-year">{formatReleaseDate(game.release_date)}</div>
            <div className="genre-badges">
              {genres.slice(0, 2).map((genre, index) => (
                <Badge 
                  key={index} 
                  bg="secondary" 
                  className="me-1"
                >
                  {genre.name}
                </Badge>
              ))}
              {genres.length > 2 && (
                <Badge bg="secondary">+{genres.length - 2}</Badge>
              )}
            </div>
          </div>
        </Card.Body>
      </Link>
    </Card>
  );
};

export default GameCard; 