import React, { useEffect, useState, useCallback } from 'react';
import { useTelegramApp } from '../hooks/useTelegramApp';
import { apiService } from '../services/api';
import { ScheduleItem } from '../types';
import './SchedulePage.css';

const SchedulePage: React.FC = () => {
  const { user, hapticFeedback, showMainButton, hideMainButton } = useTelegramApp();
  const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
  const [filteredSchedule, setFilteredSchedule] = useState<ScheduleItem[]>([]);
  const [selectedLevel, setSelectedLevel] = useState<'all' | 'beginner' | 'advanced'>('all');
  const [isLoading, setIsLoading] = useState(true);
  const [selectedLesson, setSelectedLesson] = useState<ScheduleItem | null>(null);

  useEffect(() => {
    loadSchedule();
  }, []);

  const filterSchedule = useCallback(() => {
    if (selectedLevel === 'all') {
      setFilteredSchedule(schedule);
    } else {
      setFilteredSchedule(schedule.filter(item => item.level === selectedLevel));
    }
  }, [schedule, selectedLevel]);

  useEffect(() => {
    filterSchedule();
  }, [filterSchedule]);

  const handleBooking = useCallback(async () => {
    if (!selectedLesson || !user) return;

    try {
      const response = await apiService.bookLesson({
        lesson_id: selectedLesson.id,
        user_id: user.id.toString()
      });

      if (response.success) {
        hapticFeedback('medium');
        alert('Урок забронирован успешно!');
        setSelectedLesson(null);
      } else {
        hapticFeedback('heavy');
        alert('Ошибка при бронировании');
      }
    } catch (error) {
      console.error('Booking error:', error);
      hapticFeedback('heavy');
      alert('Ошибка при бронировании');
    }
  }, [selectedLesson, user, hapticFeedback]);

  useEffect(() => {
    if (selectedLesson) {
      showMainButton('Забронировать', handleBooking);
    } else {
      hideMainButton();
    }
  }, [selectedLesson, handleBooking, showMainButton, hideMainButton]);

  const loadSchedule = async () => {
    try {
      const response = await apiService.getSchedule();
      setSchedule(response.schedule);
    } catch (error) {
      console.error('Error loading schedule:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLevelFilter = (level: 'all' | 'beginner' | 'advanced') => {
    hapticFeedback('light');
    setSelectedLevel(level);
    setSelectedLesson(null);
  };

  const handleLessonSelect = (lesson: ScheduleItem) => {
    hapticFeedback('light');
    setSelectedLesson(selectedLesson?.id === lesson.id ? null : lesson);
  };

  const getLevelLabel = (level: string) => {
    return level === 'beginner' ? 'Начальный' : 'Продвинутый';
  };

  if (isLoading) {
    return (
      <div className="schedule-page">
        <div className="loading">Загрузка расписания...</div>
      </div>
    );
  }

  return (
    <div className="schedule-page">
      <div className="header">
        <h1>📅 Расписание занятий</h1>
      </div>

      <div className="filters">
        <div className="filter-buttons">
          <button
            className={`filter-btn ${selectedLevel === 'all' ? 'active' : ''}`}
            onClick={() => handleLevelFilter('all')}
          >
            Все уровни
          </button>
          <button
            className={`filter-btn ${selectedLevel === 'beginner' ? 'active' : ''}`}
            onClick={() => handleLevelFilter('beginner')}
          >
            Начальный
          </button>
          <button
            className={`filter-btn ${selectedLevel === 'advanced' ? 'active' : ''}`}
            onClick={() => handleLevelFilter('advanced')}
          >
            Продвинутый
          </button>
        </div>
      </div>

      <div className="schedule-list">
        {filteredSchedule.length === 0 ? (
          <div className="empty-state">
            <span className="empty-icon">📅</span>
            <p>Нет занятий для выбранного уровня</p>
          </div>
        ) : (
          filteredSchedule.map((lesson) => (
            <div
              key={lesson.id}
              className={`lesson-card ${selectedLesson?.id === lesson.id ? 'selected' : ''}`}
              onClick={() => handleLessonSelect(lesson)}
            >
              <div className="lesson-header">
                <h3 className="lesson-title">{lesson.title}</h3>
                <span className={`level-badge ${lesson.level}`}>
                  {getLevelLabel(lesson.level)}
                </span>
              </div>
              
              <div className="lesson-details">
                <div className="detail-item">
                  <span className="detail-icon">👨‍🏫</span>
                  <span className="detail-text">{lesson.teacher}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-icon">🕐</span>
                  <span className="detail-text">{lesson.time}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-icon">📍</span>
                  <span className="detail-text">{lesson.location}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-icon">⏱️</span>
                  <span className="detail-text">{lesson.duration}</span>
                </div>
              </div>

              {selectedLesson?.id === lesson.id && (
                <div className="booking-info">
                  <p>Нажмите кнопку внизу для бронирования</p>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default SchedulePage; 