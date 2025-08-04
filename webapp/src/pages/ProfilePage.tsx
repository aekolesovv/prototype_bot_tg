import React, { useEffect, useState, useCallback } from 'react';
import { useTelegramApp } from '../hooks/useTelegramApp';
import { apiService } from '../services/api';
import { UserProfile } from '../types';
import './ProfilePage.css';

const ProfilePage: React.FC = () => {
  const { user } = useTelegramApp();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadProfile = useCallback(async () => {
    if (!user) return;

    try {
      const response = await apiService.getProfile(user.id.toString());
      setProfile(response);
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setIsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const getLevelLabel = (level: string) => {
    return level === 'beginner' ? 'Начальный' : 'Продвинутый';
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 80) return '#27ae60';
    if (percentage >= 60) return '#f39c12';
    return '#e74c3c';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (isLoading) {
    return (
      <div className="profile-page">
        <div className="loading">Загрузка профиля...</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="profile-page">
        <div className="error-state">
          <span className="error-icon">❌</span>
          <p>Не удалось загрузить профиль</p>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-page">
      <div className="header">
        <h1>👤 Профиль</h1>
        <p className="subtitle">Ваш прогресс в изучении английского</p>
      </div>

      <div className="profile-content">
        {/* Основная информация */}
        <div className="profile-card main-info">
          <div className="avatar-section">
            <div className="avatar">
              {user?.first_name?.charAt(0) || 'U'}
            </div>
            <div className="user-info">
              <h2 className="user-name">
                {user?.first_name} {user?.last_name}
              </h2>
              <p className="user-username">@{user?.username || 'username'}</p>
              <span className="level-badge">{getLevelLabel(profile.level)}</span>
            </div>
          </div>
        </div>

        {/* Статистика */}
        <div className="profile-card stats">
          <h3 className="card-title">📊 Статистика</h3>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-number">{profile.lessons_completed}</span>
              <span className="stat-label">Уроков пройдено</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{profile.tests_passed}</span>
              <span className="stat-label">Тестов сдано</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{profile.clubs_joined}</span>
              <span className="stat-label">Клубов</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">{profile.points}</span>
              <span className="stat-label">Баллов</span>
            </div>
          </div>
        </div>

        {/* Прогресс */}
        <div className="profile-card progress">
          <h3 className="card-title">📈 Общий прогресс</h3>
          <div className="progress-section">
            <div className="progress-info">
              <span className="progress-label">Прогресс курса</span>
              <span className="progress-percentage">{profile.progress}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ 
                  width: `${profile.progress}%`,
                  backgroundColor: getProgressColor(profile.progress)
                }}
              ></div>
            </div>
          </div>
        </div>

        {/* Последние достижения */}
        <div className="profile-card achievements">
          <h3 className="card-title">🏆 Последние достижения</h3>
          {profile.recent_achievements && profile.recent_achievements.length > 0 ? (
            <div className="achievements-list">
              {profile.recent_achievements.map((achievement, index) => (
                <div key={index} className="achievement-item">
                  <span className="achievement-icon">🏆</span>
                  <div className="achievement-content">
                    <span className="achievement-title">{achievement.title}</span>
                    <span className="achievement-date">{formatDate(achievement.date)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-achievements">
              <span className="empty-icon">🏆</span>
              <p>Пока нет достижений</p>
            </div>
          )}
        </div>

        {/* Информация о курсе */}
        <div className="profile-card course-info">
          <h3 className="card-title">📚 Информация о курсе</h3>
          <div className="course-details">
            <div className="detail-item">
              <span className="detail-icon">📅</span>
              <span className="detail-text">Дата начала: {formatDate(profile.start_date)}</span>
            </div>
            <div className="detail-item">
              <span className="detail-icon">🎯</span>
              <span className="detail-text">Цель: {profile.goal}</span>
            </div>
            <div className="detail-item">
              <span className="detail-icon">⏱️</span>
              <span className="detail-text">Время обучения: {profile.study_time} часов</span>
            </div>
          </div>
        </div>

        {/* Следующие цели */}
        <div className="profile-card goals">
          <h3 className="card-title">🎯 Следующие цели</h3>
          <div className="goals-list">
            {profile.next_goals && profile.next_goals.length > 0 ? (
              profile.next_goals.map((goal, index) => (
                <div key={index} className="goal-item">
                  <span className="goal-icon">🎯</span>
                  <span className="goal-text">{goal}</span>
                </div>
              ))
            ) : (
              <div className="empty-goals">
                <span className="empty-icon">🎯</span>
                <p>Цели пока не установлены</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage; 