import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { getTopRatedGames, getGenres, searchGames } from '../services/api';
import GameCard from '../components/GameCard';

const RecommendationsPage = () => {
  const [games, setGames] = useState([]);
  const [genres, setGenres] = useState([]);
  const [selectedGenre, setSelectedGenre] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch top rated games on initial load
    const fetchInitialData = async () => {
      try {
        setLoading(true);
        
        // Get top rated games, explicitly requesting 50 games with explicit string conversion
        console.log('Requesting 50 games from API');
        const gamesData = await getTopRatedGames('50');
        
        // Log how many games we actually received
        console.log(`Received ${gamesData.length} games from API`);
        
        // Ensure each game has valid image_url with proper validation
        const processedGames = gamesData.map(game => {
          // Make sure image_url is a string
          let imageUrl = game.image_url || '';
          
          // If we have an image URL, make sure it's HTTPS
          if (imageUrl && imageUrl.startsWith('http:')) {
            imageUrl = imageUrl.replace('http:', 'https:');
          }
          
          return {
            ...game,
            image_url: imageUrl
          };
        });
        
        // Only fall back to mock data if we got no games from the API
        if (processedGames.length === 0) {
          console.log('No games returned from API, using mock data');
          setGames(mockGames);
        } else {
          console.log(`Setting state with ${processedGames.length} games`);
          setGames(processedGames);
        }
        
        // Try to get genres separately
        try {
          const genresData = await getGenres();
          setGenres(genresData);
        } catch (genreError) {
          console.error('Error fetching genres:', genreError);
          // If genres fail to load, we can still show games
        }
        
        setError(null);
      } catch (err) {
        console.error('Error fetching initial data:', err);
        setError('Failed to load games. Please try again later.');
        // Fall back to mock data in case of error
        setGames(mockGames);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialData();
  }, []);

  const handleSearch = async (e) => {
    e.preventDefault();
    
    if (!searchQuery && !selectedGenre) {
      // If both search and genre are empty, load top rated games
      try {
        setLoading(true);
        // Request 50 games with explicit string conversion
        const gamesData = await getTopRatedGames('50');
        
        // Process the results to ensure image_url is valid
        const processedGames = gamesData.map(game => {
          // Make sure image_url is a string
          let imageUrl = game.image_url || '';
          
          // If we have an image URL, make sure it's HTTPS
          if (imageUrl && imageUrl.startsWith('http:')) {
            imageUrl = imageUrl.replace('http:', 'https:');
          }
          
          return {
            ...game,
            image_url: imageUrl
          };
        });
        
        setGames(processedGames);
        setError(null);
      } catch (err) {
        console.error('Error fetching top games:', err);
        setError('Failed to load games. Please try again later.');
      } finally {
        setLoading(false);
      }
      return;
    }
    
    try {
      setLoading(true);
      // Prepare filter parameters
      const filters = {};
      if (selectedGenre) filters.genre = selectedGenre;
      
      // Call search API
      const searchResults = await searchGames(searchQuery, filters);
      
      // Process the results to ensure image_url is valid
      const processedResults = searchResults.map(game => {
        // Make sure image_url is a string
        let imageUrl = game.image_url || '';
        
        // If we have an image URL, make sure it's HTTPS
        if (imageUrl && imageUrl.startsWith('http:')) {
          imageUrl = imageUrl.replace('http:', 'https:');
        }
        
        return {
          ...game,
          image_url: imageUrl
        };
      });
      
      if (processedResults.length === 0) {
        setError('No games found matching your criteria. Try different search terms or filters.');
      } else {
        setError(null);
      }
      
      setGames(processedResults);
    } catch (err) {
      console.error('Error searching games:', err);
      setError('Search failed. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="py-5">
      <h1 className="mb-4">Game Recommendations</h1>
      
      {/* Search and filter section */}
      <Card className="mb-4 shadow-sm">
        <Card.Body>
          <Form onSubmit={handleSearch}>
            <Row className="align-items-end">
              <Col md={6}>
                <Form.Group>
                  <Form.Label>Search Games</Form.Label>
                  <Form.Control
                    type="text"
                    placeholder="Search by title, publisher, etc."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group>
                  <Form.Label>Genre</Form.Label>
                  <Form.Select
                    value={selectedGenre}
                    onChange={(e) => setSelectedGenre(e.target.value)}
                  >
                    <option value="">All Genres</option>
                    {genres.map((genre) => (
                      <option key={genre.id} value={genre.id}>
                        {genre.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={2}>
                <Button type="submit" variant="primary" className="w-100">
                  Search
                </Button>
              </Col>
            </Row>
          </Form>
        </Card.Body>
      </Card>
      
      {/* Error message */}
      {error && (
        <Alert variant="danger" className="mb-4">
          {error}
        </Alert>
      )}
      
      {/* Loading spinner */}
      {loading ? (
        <div className="text-center my-5">
          <Spinner animation="border" role="status">
            <span className="visually-hidden">Loading...</span>
          </Spinner>
          <p className="mt-2">Loading games...</p>
        </div>
      ) : (
        <>
          {/* Game results */}
          <h2 className="mb-4">
            {searchQuery || selectedGenre 
              ? 'Search Results' 
              : 'Top Rated Games'}
            <span className="text-muted fs-6 ms-2">({games.length} games)</span>
          </h2>
          
          <Row>
            {games.map((game) => (
              <Col key={game.id} lg={3} md={4} sm={6} className="mb-4">
                <GameCard game={game} />
              </Col>
            ))}
            
            {games.length === 0 && !loading && !error && (
              <Col xs={12}>
                <p className="text-center text-muted">No games found. Try different search terms.</p>
              </Col>
            )}
          </Row>
        </>
      )}
    </Container>
  );
};

// Mock game data for development/fallback
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
  },
  {
    id: 4,
    title: "God of War",
    image_url: "https://images.igdb.com/igdb/image/upload/t_cover_big/co1tmu.jpg",
    release_date: "2018-04-20",
    metacritic_score: 94,
    genres: [
      { id: 1, name: "Action" },
      { id: 2, name: "Adventure" }
    ]
  }
];

export default RecommendationsPage; 