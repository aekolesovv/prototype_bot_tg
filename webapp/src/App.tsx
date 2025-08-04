import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useTelegramApp } from './hooks/useTelegramApp';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import SchedulePage from './pages/SchedulePage';
import ClubsPage from './pages/ClubsPage';
import TestsPage from './pages/TestsPage';
import NotificationsPage from './pages/NotificationsPage';
import AdminPage from './pages/AdminPage';
import ProfilePage from './pages/ProfilePage';
import './App.css';

function App() {
  const { isReady, hapticFeedback } = useTelegramApp();

  useEffect(() => {
    if (isReady) {
      console.log('App is ready');
    }
  }, [isReady]);

  const handleNavigation = (path: string) => {
    hapticFeedback('light');
  };

  if (!isReady) {
    return (
      <div className="app">
        <div className="loading-screen">
          <div className="loading-spinner"></div>
          <p>Загрузка приложения...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/schedule" element={<SchedulePage />} />
          <Route path="/clubs" element={<ClubsPage />} />
          <Route path="/tests" element={<TestsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Routes>
        <Navigation onNavigate={handleNavigation} />
      </div>
    </Router>
  );
}

export default App;
