import React, { useState, useEffect, useCallback } from 'react';
import { useTelegramApp } from '../hooks/useTelegramApp';
import apiService from '../services/api';
import './NotificationsPage.css';

interface Notification {
  id: number;
  type: string;
  title: string;
  message: string;
  scheduled_time?: string;
  is_read: boolean;
  created_at: string;
}

interface NotificationSettings {
  lesson_reminders: boolean;
  test_notifications: boolean;
  club_reminders: boolean;
  daily_motivation: boolean;
  reminder_time: string;
  timezone: string;
}

const NotificationsPage: React.FC = () => {
  const { user } = useTelegramApp();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [settings, setSettings] = useState<NotificationSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  const loadNotifications = useCallback(async () => {
    if (!user?.id) return;
    
    try {
      const response = await apiService.getNotifications(user.id.toString());
      setNotifications(response.notifications || []);
    } catch (error) {
      console.error('Ошибка загрузки уведомлений:', error);
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  const loadSettings = useCallback(async () => {
    if (!user?.id) return;
    
    try {
      const response = await apiService.getNotificationSettings(user.id.toString());
      setSettings(response);
    } catch (error) {
      console.error('Ошибка загрузки настроек:', error);
    }
  }, [user?.id]);

  useEffect(() => {
    if (user?.id) {
      loadNotifications();
      loadSettings();
    }
  }, [user?.id, loadNotifications, loadSettings]);

  const markAsRead = async (notificationId: number) => {
    if (!user?.id) return;
    
    try {
      await apiService.markNotificationRead(notificationId, user.id.toString());
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
    } catch (error) {
      console.error('Ошибка отметки уведомления:', error);
    }
  };

  const markAllAsRead = async () => {
    if (!user?.id) return;
    
    try {
      await apiService.markAllNotificationsRead(user.id.toString());
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (error) {
      console.error('Ошибка отметки всех уведомлений:', error);
    }
  };

  const updateSetting = async (key: keyof NotificationSettings, value: boolean | string) => {
    if (!settings || !user?.id) return;

    const updatedSettings = { ...settings, [key]: value };
    
    try {
      await apiService.updateNotificationSettings(user.id.toString(), updatedSettings);
      setSettings(updatedSettings);
    } catch (error) {
      console.error('Ошибка обновления настроек:', error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'lesson_reminder':
        return '📚';
      case 'test_notification':
        return '📝';
      case 'club_reminder':
        return '👥';
      case 'daily_motivation':
        return '💪';
      default:
        return '🔔';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="notifications-page">
        <div className="loading">
          <div className="loading-spinner"></div>
          <p>Загрузка уведомлений...</p>
        </div>
      </div>
    );
  }

  const unreadCount = notifications.filter(n => !n.is_read).length;

  return (
    <div className="notifications-page">
      <div className="header">
        <h1>🔔 Уведомления</h1>
        <p className="subtitle">
          {unreadCount > 0 ? `${unreadCount} непрочитанных` : 'Все уведомления прочитаны'}
        </p>
      </div>

      <div className="notifications-content">
        {showSettings ? (
          <div className="settings-section">
            <div className="settings-header">
              <h2>⚙️ Настройки уведомлений</h2>
              <button 
                className="back-button"
                onClick={() => setShowSettings(false)}
              >
                ← Назад
              </button>
            </div>

            {settings && (
              <div className="settings-form">
                <div className="setting-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.lesson_reminders}
                      onChange={(e) => updateSetting('lesson_reminders', e.target.checked)}
                    />
                    <span>📚 Напоминания о занятиях</span>
                  </label>
                </div>

                <div className="setting-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.test_notifications}
                      onChange={(e) => updateSetting('test_notifications', e.target.checked)}
                    />
                    <span>📝 Уведомления о тестах</span>
                  </label>
                </div>

                <div className="setting-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.club_reminders}
                      onChange={(e) => updateSetting('club_reminders', e.target.checked)}
                    />
                    <span>👥 Напоминания о клубах</span>
                  </label>
                </div>

                <div className="setting-item">
                  <label>
                    <input
                      type="checkbox"
                      checked={settings.daily_motivation}
                      onChange={(e) => updateSetting('daily_motivation', e.target.checked)}
                    />
                    <span>💪 Ежедневная мотивация</span>
                  </label>
                </div>

                <div className="setting-item">
                  <label>
                    <span>⏰ Время напоминаний:</span>
                    <input
                      type="time"
                      value={settings.reminder_time}
                      onChange={(e) => updateSetting('reminder_time', e.target.value)}
                    />
                  </label>
                </div>
              </div>
            )}
          </div>
        ) : (
          <>
            <div className="notifications-actions">
              <button 
                className="action-button"
                onClick={() => setShowSettings(true)}
              >
                ⚙️ Настройки
              </button>
              {unreadCount > 0 && (
                <button 
                  className="action-button"
                  onClick={markAllAsRead}
                >
                  ✅ Отметить все прочитанными
                </button>
              )}
            </div>

            <div className="notifications-list">
              {notifications.length === 0 ? (
                <div className="empty-notifications">
                  <div className="empty-icon">🔔</div>
                  <p>У вас пока нет уведомлений</p>
                </div>
              ) : (
                notifications.map((notification) => (
                  <div 
                    key={notification.id} 
                    className={`notification-item ${!notification.is_read ? 'unread' : ''}`}
                    onClick={() => !notification.is_read && markAsRead(notification.id)}
                  >
                    <div className="notification-icon">
                      {getNotificationIcon(notification.type)}
                    </div>
                    <div className="notification-content">
                      <div className="notification-header">
                        <h3>{notification.title}</h3>
                        <span className="notification-date">
                          {formatDate(notification.created_at)}
                        </span>
                      </div>
                      <p className="notification-message">{notification.message}</p>
                      {!notification.is_read && (
                        <div className="unread-indicator">Новое</div>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default NotificationsPage; 