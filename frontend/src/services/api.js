import axios from 'axios';

// Game related API calls
export const getGames = async (params = {}) => {
  try {
    const response = await axios.get('/api/games/', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching games:', error);
    throw error;
  }
};

export const getGame = async (id) => {
  try {
    const response = await axios.get(`/api/games/${id}/`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching game ${id}:`, error);
    throw error;
  }
};

export const searchGames = async (query, filters = {}) => {
  try {
    const response = await axios.get('/api/games/search/', { 
      params: { q: query, ...filters }
    });
    // Process the results to ensure image_url is present and valid
    return response.data.results.map(game => {
      // Use cached_image_url if available, otherwise fallback to image_url
      let imageUrl = game.cached_image_url || game.image_url || '';
      
      // If URL starts with http:// convert to https:// to avoid mixed content issues
      if (imageUrl.startsWith('http:') && !imageUrl.startsWith('https:')) {
        imageUrl = imageUrl.replace('http:', 'https:');
      }
      
      return {
        ...game,
        image_url: imageUrl
      };
    });
  } catch (error) {
    console.error('Error searching games:', error);
    throw error;
  }
};

export const getTopRatedGames = async (limit = 50) => {
  try {
    console.log(`Fetching top ${limit} rated games`);
    
    // Make sure limit is a number and within reasonable bounds
    const parsedLimit = parseInt(limit, 10);
    const safeLimit = isNaN(parsedLimit) ? 50 : Math.min(Math.max(parsedLimit, 10), 100);
    
    // Request games with explicit limit parameter as string to avoid type issues
    const response = await axios.get('/api/games/top_rated/', {
      params: { limit: safeLimit.toString() }
    });
    
    console.log(`Received ${response.data.length} games from API`);
    
    // Process the returned data to ensure image_url is valid
    const games = response.data.map(game => {
      // Use cached_image_url if available, otherwise fallback to image_url
      let imageUrl = game.cached_image_url || game.image_url || '';
      
      // If URL starts with http:// convert to https:// to avoid mixed content issues
      if (imageUrl.startsWith('http:') && !imageUrl.startsWith('https:')) {
        imageUrl = imageUrl.replace('http:', 'https:');
      }
      
      return {
        ...game,
        image_url: imageUrl
      };
    });
    
    // Verify we got the right number of games
    if (games.length < safeLimit) {
      console.warn(`API returned fewer games (${games.length}) than requested (${safeLimit})`);
    }
    
    return games;
  } catch (error) {
    console.error('Error fetching top rated games:', error);
    // Return empty array instead of throwing to prevent errors on public page
    return [];
  }
};

export const getRecentGames = async () => {
  try {
    const response = await axios.get('/api/games/recent/');
    // Process the results to ensure image_url is present and valid
    return response.data.map(game => {
      // Use cached_image_url if available, otherwise fallback to image_url
      let imageUrl = game.cached_image_url || game.image_url || '';
      
      // If URL starts with http:// convert to https:// to avoid mixed content issues
      if (imageUrl.startsWith('http:') && !imageUrl.startsWith('https:')) {
        imageUrl = imageUrl.replace('http:', 'https:');
      }
      
      return {
        ...game,
        image_url: imageUrl
      };
    });
  } catch (error) {
    console.error('Error fetching recent games:', error);
    // Return empty array instead of throwing
    return [];
  }
};

// Profile and survey related API calls
export const getUserProfile = async () => {
  try {
    const response = await axios.get('/api/profile/');
    return response.data[0];
  } catch (error) {
    console.error('Error fetching user profile:', error);
    throw error;
  }
};

export const getSurveyData = async () => {
  try {
    const response = await axios.get('/api/profile/survey/');
    return response.data;
  } catch (error) {
    console.error('Error fetching survey data:', error);
    throw error;
  }
};

export const submitSurvey = async (surveyData) => {
  try {
    const response = await axios.post('/api/profile/survey/', surveyData);
    return response.data;
  } catch (error) {
    console.error('Error submitting survey:', error);
    throw error;
  }
};

// Recommendation related API calls
export const getRecommendations = async (params = {}) => {
  try {
    const response = await axios.get('/api/recommendations/', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching recommendations:', error);
    throw error;
  }
};

export const refreshRecommendations = async () => {
  try {
    const response = await axios.post('/api/recommendations/refresh/');
    return response.data;
  } catch (error) {
    console.error('Error refreshing recommendations:', error);
    throw error;
  }
};

export const updateRecommendationInteraction = async (id, data) => {
  try {
    const response = await axios.post(`/api/recommendations/${id}/interaction/`, data);
    return response.data;
  } catch (error) {
    console.error(`Error updating recommendation ${id}:`, error);
    throw error;
  }
};

export const submitRecommendationFeedback = async (id, feedbackData) => {
  try {
    const response = await axios.post(`/api/recommendations/${id}/feedback/`, feedbackData);
    return response.data;
  } catch (error) {
    console.error(`Error submitting feedback for recommendation ${id}:`, error);
    throw error;
  }
};

// Game rating related API calls
export const getUserGameRatings = async () => {
  try {
    const response = await axios.get('/api/profile/game_ratings/');
    return response.data;
  } catch (error) {
    console.error('Error fetching user game ratings:', error);
    throw error;
  }
};

export const rateGame = async (gameId, rating, comments = '') => {
  try {
    const response = await axios.post('/api/profile/game_ratings/', {
      game_id: gameId,
      rating,
      comments,
      has_played: true
    });
    return response.data;
  } catch (error) {
    console.error(`Error rating game ${gameId}:`, error);
    throw error;
  }
};

// Category related API calls
export const getGenres = async () => {
  try {
    const response = await axios.get('/api/genres/');
    return response.data;
  } catch (error) {
    console.error('Error fetching genres:', error);
    // Return empty array instead of throwing to prevent errors on public page
    return [];
  }
};

export const getPlatforms = async () => {
  try {
    const response = await axios.get('/api/platforms/');
    return response.data;
  } catch (error) {
    console.error('Error fetching platforms:', error);
    throw error;
  }
}; 