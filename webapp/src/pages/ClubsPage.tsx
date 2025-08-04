import React, { useEffect, useState, useCallback } from 'react';
import { useTelegramApp } from '../hooks/useTelegramApp';
import { apiService } from '../services/api';
import { Club } from '../types';
import './ClubsPage.css';

const ClubsPage: React.FC = () => {
  const { user, hapticFeedback, showMainButton, hideMainButton } = useTelegramApp();
  const [clubs, setClubs] = useState<Club[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedClub, setSelectedClub] = useState<Club | null>(null);
  const [joinStatus, setJoinStatus] = useState<{[key: number]: boolean}>({});

  const loadClubs = async () => {
    try {
      const response = await apiService.getClubs();
      setClubs(response.clubs);
    } catch (error) {
      console.error('Error loading clubs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinClub = useCallback(async () => {
    if (!selectedClub || !user) return;

    try {
      const response = await apiService.joinClub(selectedClub.id, user.id.toString());
      
      if (response.success) {
        hapticFeedback('medium');
        setJoinStatus(prev => ({ ...prev, [selectedClub.id]: true }));
        alert(`Вы успешно присоединились к клубу "${selectedClub.name}"!`);
        setSelectedClub(null);
      } else {
        hapticFeedback('heavy');
        alert(response.error || 'Ошибка при присоединении к клубу');
      }
    } catch (error) {
      console.error('Join club error:', error);
      hapticFeedback('heavy');
      alert('Ошибка при присоединении к клубу');
    }
  }, [selectedClub, user, hapticFeedback]);

  useEffect(() => {
    loadClubs();
  }, []);

  useEffect(() => {
    if (selectedClub) {
      showMainButton('Присоединиться', handleJoinClub);
    } else {
      hideMainButton();
    }
  }, [selectedClub, showMainButton, hideMainButton, handleJoinClub]);

  const handleClubSelect = (club: Club) => {
    hapticFeedback('light');
    setSelectedClub(selectedClub?.id === club.id ? null : club);
  };

  const getAvailabilityColor = (current: number, max: number) => {
    const percentage = (current / max) * 100;
    if (percentage >= 90) return '#e74c3c'; // Красный
    if (percentage >= 70) return '#f39c12'; // Оранжевый
    return '#27ae60'; // Зеленый
  };

  const getAvailabilityText = (current: number, max: number) => {
    const percentage = (current / max) * 100;
    if (percentage >= 90) return 'Почти заполнен';
    if (percentage >= 70) return 'Мало мест';
    return 'Есть места';
  };

  if (isLoading) {
    return (
      <div className="clubs-page">
        <div className="loading">Загрузка клубов...</div>
      </div>
    );
  }

  return (
    <div className="clubs-page">
      <div className="header">
        <h1>👥 Клубы</h1>
        <p className="subtitle">Присоединяйтесь к разговорным клубам и практикуйте английский</p>
      </div>

      <div className="clubs-list">
        {clubs.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">👥</span>
            <p>Клубы пока не доступны</p>
          </div>
        ) : (
          clubs.map((club) => (
            <div
              key={club.id}
              className={`club-card ${selectedClub?.id === club.id ? 'selected' : ''} ${
                joinStatus[club.id] ? 'joined' : ''
              }`}
              onClick={() => handleClubSelect(club)}
            >
              <div className="club-header">
                <h3 className="club-title">{club.name}</h3>
                <span className={`availability-badge ${joinStatus[club.id] ? 'joined' : ''}`}>
                  {joinStatus[club.id] ? 'Вы участник' : getAvailabilityText(club.current_participants, club.max_participants)}
                </span>
              </div>
              
              <p className="club-description">{club.description}</p>
              
              <div className="club-details">
                <div className="detail-item">
                  <span className="detail-icon">🕐</span>
                  <span className="detail-text">{club.schedule}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-icon">👥</span>
                  <span className="detail-text">
                    {club.current_participants}/{club.max_participants} участников
                  </span>
                </div>
              </div>

              <div className="progress-container">
                <div className="progress-bar">
                  <div 
                    className="progress-fill"
                    style={{ 
                      width: `${(club.current_participants / club.max_participants) * 100}%`,
                      backgroundColor: getAvailabilityColor(club.current_participants, club.max_participants)
                    }}
                  ></div>
                </div>
                <span className="progress-text">
                  {Math.round((club.current_participants / club.max_participants) * 100)}% заполнен
                </span>
              </div>

              {selectedClub?.id === club.id && !joinStatus[club.id] && (
                <div className="join-info">
                  <p>Нажмите кнопку внизу для присоединения</p>
                </div>
              )}

              {joinStatus[club.id] && (
                <div className="joined-info">
                  <p>✅ Вы уже участник этого клуба</p>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ClubsPage; 