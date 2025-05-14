import React, { createContext, useState, useContext, useEffect } from 'react';
import { getTopRatedGames, getRecentGames } from '../services/api';

// Create the game context
export const GameContext = createContext();

// Custom hook to use the game context
export const useGame = () => useContext(GameContext);

export const GameProvider = ({ children }) => {
  const [topRatedGames, setTopRatedGames] = useState([]);
  const [recentGames, setRecentGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch top rated and recent games
  useEffect(() => {
    const fetchGames = async () => {
      setLoading(true);
      setError(null);

      try {
        const [topRated, recent] = await Promise.all([
          getTopRatedGames(10),
          getRecentGames()
        ]);

        setTopRatedGames(topRated);
        setRecentGames(recent);
      } catch (error) {
        console.error('Error fetching games:', error);
        setError('Failed to load games. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchGames();
  }, []);

  // Context value
  const value = {
    topRatedGames,
    recentGames,
    loading,
    error,
    refreshGames: async () => {
      setLoading(true);
      try {
        const [topRated, recent] = await Promise.all([
          getTopRatedGames(10),
          getRecentGames()
        ]);

        setTopRatedGames(topRated);
        setRecentGames(recent);
        setError(null);
      } catch (error) {
        console.error('Error refreshing games:', error);
        setError('Failed to refresh games. Please try again later.');
      } finally {
        setLoading(false);
      }
    }
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}; 