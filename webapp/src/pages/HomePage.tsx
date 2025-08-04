import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTelegramApp } from '../hooks/useTelegramApp';
import { apiService } from '../services/api';
import { UserProfile } from '../types';
import './HomePage.css';

const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { user, hapticFeedback } = useTelegramApp();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadProfile = async () => {
      if (user) {
        try {
          const userProfile = await apiService.getProfile(user.id.toString());
          setProfile(userProfile);
        } catch (error) {
          console.error('Error loading profile:', error);
        } finally {
          setIsLoading(false);
        }
      } else {
        setIsLoading(false);
      }
    };

    loadProfile();
  }, [user]);

  const handleQuickAction = (action: string) => {
    hapticFeedback('light');
    switch (action) {
      case 'schedule':
        navigate('/schedule');
        break;
      case 'clubs':
        navigate('/clubs');
        break;
      case 'tests':
        navigate('/tests');
        break;
      case 'profile':
        navigate('/profile');
        break;
    }
  };

  const quickActions = [
    { id: 'schedule', title: 'Расписание', icon: '📅', color: '#8b2635' },
    { id: 'clubs', title: 'Клубы', icon: '👥', color: '#d4a574' },
    { id: 'tests', title: 'Тесты', icon: '📝', color: '#e8b4b8' },
    { id: 'profile', title: 'Профиль', icon: '👤', color: '#b8946f' },
  ];

  if (isLoading) {
    return (
      <div className="home-page">
        <div className="loading">Загрузка...</div>
      </div>
    );
  }

  return (
    <div className="home-page">
      <div className="header">
        <h1>🎓 Школа английского</h1>
        <p className="welcome">
          Привет, {user?.first_name || 'студент'}! 👋
        </p>
      </div>

      {profile && (
        <div className="profile-summary">
          <div className="progress-card">
            <div className="progress-info">
              <span className="level-badge">
                {profile.level === 'beginner' ? 'Начальный' : 
                 profile.level === 'advanced' ? 'Продвинутый' : 'Не выбран'}
              </span>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${profile.progress}%` }}
                ></div>
              </div>
              <span className="progress-text">{profile.progress}% прогресса</span>
            </div>
            <div className="stats">
              <div className="stat">
                <span className="stat-number">{profile.lessons_completed}</span>
                <span className="stat-label">уроков</span>
              </div>
              <div className="stat">
                <span className="stat-number">{profile.points}</span>
                <span className="stat-label">баллов</span>
              </div>
              <div className="stat">
                <span className="stat-number">{profile.current_streak}</span>
                <span className="stat-label">дней подряд</span>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="quick-actions">
        <h2>Быстрые действия</h2>
        <div className="actions-grid">
          {quickActions.map((action) => (
            <button
              key={action.id}
              className="action-card"
              onClick={() => handleQuickAction(action.id)}
              style={{ '--action-color': action.color } as React.CSSProperties}
            >
              <span className="action-icon">{action.icon}</span>
              <span className="action-title">{action.title}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="features">
        <h2>Возможности</h2>
        <div className="features-list">
          <div className="feature-item">
            <span className="feature-icon">📚</span>
            <div className="feature-content">
              <h3>Уроки и тесты</h3>
              <p>Изучайте грамматику и проходите тесты</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">👥</span>
            <div className="feature-content">
              <h3>Разговорные клубы</h3>
              <p>Практикуйте английский с другими студентами</p>
            </div>
          </div>
          <div className="feature-item">
            <span className="feature-icon">📊</span>
            <div className="feature-content">
              <h3>Отслеживание прогресса</h3>
              <p>Следите за своими успехами в обучении</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 