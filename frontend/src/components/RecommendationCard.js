import React, { useState } from 'react';
import { Card, Row, Col, Button, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import axios from 'axios';

const RecommendationCard = ({ recommendation, onUpdate }) => {
  const { id, game, score, reason, viewed, clicked, dismissed, saved } = recommendation;
  const [loading, setLoading] = useState(false);

  // Default image if none is provided
  const defaultImage = 'https://via.placeholder.com/300x200?text=No+Image';

  // Handle interaction with recommendation
  const handleInteraction = async (interactionType) => {
    setLoading(true);
    try {
      const updatedData = {
        [interactionType]: true
      };
      
      // Mark as viewed automatically when card is rendered
      if (interactionType === 'clicked' && !viewed) {
        updatedData.viewed = true;
      }
      
      await axios.post(`/api/recommendations/${id}/interaction/`, updatedData);
      
      if (onUpdate) {
        onUpdate(id, updatedData);
      }
    } catch (error) {
      console.error(`Error updating recommendation ${interactionType}:`, error);
    } finally {
      setLoading(false);
    }
  };

  // Format the score as a percentage
  const formattedScore = Math.round(score * 100) + '%';

  return (
    <Card className="recommendation-card mb-4">
      <Card.Body>
        <Row>
          <Col md={3}>
            <img 
              src={game.image_url || defaultImage} 
              alt={game.title} 
              className="img-fluid rounded"
              onError={(e) => {
                e.target.src = defaultImage;
              }}
            />
          </Col>
          <Col md={9}>
            <Card.Title>{game.title}</Card.Title>
            
            <div className="mb-2">
              {game.genres && game.genres.map(genre => (
                <Badge key={genre.id} bg="primary" className="me-1">{genre.name}</Badge>
              ))}
            </div>
            
            <Card.Text>
              <span className="recommendation-score">Match: {formattedScore}</span>
              <p className="recommendation-reason">{reason}</p>
            </Card.Text>
            
            <div className="d-flex gap-2 mt-3">
              <Link 
                to={`/games/${game.id}`} 
                className="btn btn-primary"
                onClick={() => handleInteraction('clicked')}
              >
                View Game
              </Link>
              
              {!saved ? (
                <Button 
                  variant="outline-success" 
                  onClick={() => handleInteraction('saved')}
                  disabled={loading}
                >
                  Save
                </Button>
              ) : (
                <Badge bg="success" className="p-2">Saved</Badge>
              )}
              
              {!dismissed ? (
                <Button 
                  variant="outline-danger" 
                  onClick={() => handleInteraction('dismissed')}
                  disabled={loading}
                >
                  Not Interested
                </Button>
              ) : (
                <Badge bg="secondary" className="p-2">Dismissed</Badge>
              )}
            </div>
          </Col>
        </Row>
      </Card.Body>
    </Card>
  );
};

export default RecommendationCard; 