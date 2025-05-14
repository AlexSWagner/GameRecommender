import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import './App.css';

// Components
import NavigationBar from './components/NavigationBar';
import PrivateRoute from './components/PrivateRoute';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import SurveyPage from './pages/SurveyPage';
import RecommendationsPage from './pages/RecommendationsPage';
import GameDetailsPage from './pages/GameDetailsPage';
import ProfilePage from './pages/ProfilePage';
import NotFoundPage from './pages/NotFoundPage';

// Context
import { useAuth } from './context/AuthContext';

function App() {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="loading-spinner">Loading...</div>;
  }

  return (
    <div className="app">
      <NavigationBar />
      <Container className="py-4">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={!isAuthenticated ? <LoginPage /> : <Navigate to="/recommendations" />} />
          <Route path="/register" element={!isAuthenticated ? <RegisterPage /> : <Navigate to="/recommendations" />} />
          
          {/* Public route for game details */}
          <Route path="/game/:id" element={<GameDetailsPage />} />
          
          {/* Make recommendations page public, but keep other protected routes */}
          <Route path="/recommendations" element={<RecommendationsPage />} />
          
          {/* Protected routes */}
          <Route path="/survey" element={<PrivateRoute element={<SurveyPage />} />} />
          <Route path="/profile" element={<PrivateRoute element={<ProfilePage />} />} />
          
          {/* 404 route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Container>
      <footer className="footer mt-auto py-3 bg-light">
        <Container className="text-center">
          <span className="text-muted">Game Recommender © {new Date().getFullYear()}</span>
        </Container>
      </footer>
    </div>
  );
}

export default App; 