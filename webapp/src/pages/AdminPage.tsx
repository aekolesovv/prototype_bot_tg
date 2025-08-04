import React, { useState, useEffect } from 'react';
import { useTelegramApp } from '../hooks/useTelegramApp';
import apiService from '../services/api';
import './AdminPage.css';

interface CRMStatus {
  status: string;
  message: string;
  crm_type?: string;
  running?: boolean;
  last_sync?: string;
  sync_interval?: number;
}

interface CRMConfig {
  crm_type: string;
  base_url: string;
  api_token: string;
  course_id?: string;
}

const AdminPage: React.FC = () => {
  const { user } = useTelegramApp();
  const [crmStatus, setCrmStatus] = useState<CRMStatus | null>(null);
  const [config, setConfig] = useState<CRMConfig>({
    crm_type: 'moodle',
    base_url: '',
    api_token: '',
    course_id: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadCRMStatus();
  }, []);

  const loadCRMStatus = async () => {
    try {
      const response = await apiService.getCRMStatus();
      setCrmStatus(response);
    } catch (error) {
      console.error('Ошибка загрузки статуса CRM:', error);
    }
  };

  const handleConfigChange = (field: keyof CRMConfig, value: string) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  const configureCRM = async () => {
    setLoading(true);
    setMessage('');

    try {
      const response = await apiService.configureCRM({
        crm_type: config.crm_type,
        base_url: config.base_url,
        api_token: config.api_token,
        course_id: config.course_id
      });

      if (response.success) {
        setMessage('✅ CRM/LMS интеграция настроена успешно');
        await loadCRMStatus();
      } else {
        setMessage(`❌ Ошибка: ${response.message}`);
      }
    } catch (error) {
      setMessage('❌ Ошибка настройки CRM/LMS');
      console.error('Ошибка настройки CRM:', error);
    } finally {
      setLoading(false);
    }
  };

  const testConnection = async () => {
    setLoading(true);
    setMessage('');

    try {
      const response = await apiService.testCRMConnection();
      
      if (response.success) {
        setMessage(`✅ Подключение успешно! Студентов: ${response.data.students_count}, Занятий: ${response.data.lessons_count}`);
      } else {
        setMessage(`❌ Ошибка подключения: ${response.message}`);
      }
    } catch (error) {
      setMessage('❌ Ошибка тестирования подключения');
      console.error('Ошибка тестирования CRM:', error);
    } finally {
      setLoading(false);
    }
  };

  const startSync = async () => {
    setLoading(true);
    setMessage('');

    try {
      const response = await apiService.startCRMSync();
      
      if (response.success) {
        setMessage('✅ Автоматическая синхронизация запущена');
        await loadCRMStatus();
      } else {
        setMessage(`❌ Ошибка запуска синхронизации: ${response.message}`);
      }
    } catch (error) {
      setMessage('❌ Ошибка запуска синхронизации');
      console.error('Ошибка запуска синхронизации:', error);
    } finally {
      setLoading(false);
    }
  };

  const stopSync = async () => {
    setLoading(true);
    setMessage('');

    try {
      const response = await apiService.stopCRMSync();
      
      if (response.success) {
        setMessage('✅ Автоматическая синхронизация остановлена');
        await loadCRMStatus();
      } else {
        setMessage(`❌ Ошибка остановки синхронизации: ${response.message}`);
      }
    } catch (error) {
      setMessage('❌ Ошибка остановки синхронизации');
      console.error('Ошибка остановки синхронизации:', error);
    } finally {
      setLoading(false);
    }
  };

  const manualSync = async () => {
    setLoading(true);
    setMessage('');

    try {
      const response = await apiService.manualCRMSync();
      
      if (response.success) {
        setMessage('✅ Ручная синхронизация завершена');
        await loadCRMStatus();
      } else {
        setMessage(`❌ Ошибка синхронизации: ${response.message}`);
      }
    } catch (error) {
      setMessage('❌ Ошибка ручной синхронизации');
      console.error('Ошибка ручной синхронизации:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return '🟢';
      case 'stopped':
        return '🔴';
      case 'not_configured':
        return '⚪';
      default:
        return '❓';
    }
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return 'Не синхронизировалось';
    
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU');
  };

  return (
    <div className="admin-page">
      <div className="header">
        <h1>⚙️ Администрирование CRM/LMS</h1>
        <p className="subtitle">Настройка интеграции с внешними системами</p>
      </div>

      <div className="admin-content">
        {/* Статус CRM/LMS */}
        <div className="status-section">
          <h2>📊 Статус интеграции</h2>
          {crmStatus ? (
            <div className="status-card">
              <div className="status-header">
                <span className="status-icon">{getStatusIcon(crmStatus.status)}</span>
                <span className="status-text">{crmStatus.message}</span>
              </div>
              
              {crmStatus.crm_type && (
                <div className="status-details">
                  <div className="detail-item">
                    <span className="label">Тип CRM/LMS:</span>
                    <span className="value">{crmStatus.crm_type.toUpperCase()}</span>
                  </div>
                  
                  {crmStatus.running !== undefined && (
                    <div className="detail-item">
                      <span className="label">Синхронизация:</span>
                      <span className="value">{crmStatus.running ? 'Запущена' : 'Остановлена'}</span>
                    </div>
                  )}
                  
                  {crmStatus.last_sync && (
                    <div className="detail-item">
                      <span className="label">Последняя синхронизация:</span>
                      <span className="value">{formatDate(crmStatus.last_sync)}</span>
                    </div>
                  )}
                  
                  {crmStatus.sync_interval && (
                    <div className="detail-item">
                      <span className="label">Интервал синхронизации:</span>
                      <span className="value">{crmStatus.sync_interval} сек</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          ) : (
            <div className="loading">Загрузка статуса...</div>
          )}
        </div>

        {/* Настройка интеграции */}
        <div className="config-section">
          <h2>🔧 Настройка интеграции</h2>
          <div className="config-form">
            <div className="form-group">
              <label>Тип CRM/LMS:</label>
              <select
                value={config.crm_type}
                onChange={(e) => handleConfigChange('crm_type', e.target.value)}
              >
                <option value="moodle">Moodle LMS</option>
                <option value="canvas">Canvas LMS</option>
              </select>
            </div>

            <div className="form-group">
              <label>URL системы:</label>
              <input
                type="url"
                value={config.base_url}
                onChange={(e) => handleConfigChange('base_url', e.target.value)}
                placeholder="https://your-lms-site.com"
              />
            </div>

            <div className="form-group">
              <label>API токен:</label>
              <input
                type="password"
                value={config.api_token}
                onChange={(e) => handleConfigChange('api_token', e.target.value)}
                placeholder="Введите API токен"
              />
            </div>

            <div className="form-group">
              <label>ID курса:</label>
              <input
                type="text"
                value={config.course_id}
                onChange={(e) => handleConfigChange('course_id', e.target.value)}
                placeholder="ID курса (опционально)"
              />
            </div>

            <div className="form-actions">
              <button
                className="action-button primary"
                onClick={configureCRM}
                disabled={loading || !config.base_url || !config.api_token}
              >
                {loading ? 'Настройка...' : 'Настроить интеграцию'}
              </button>
              
              <button
                className="action-button"
                onClick={testConnection}
                disabled={loading || !config.base_url || !config.api_token}
              >
                {loading ? 'Тестирование...' : 'Тестировать подключение'}
              </button>
            </div>
          </div>
        </div>

        {/* Управление синхронизацией */}
        <div className="sync-section">
          <h2>🔄 Управление синхронизацией</h2>
          <div className="sync-actions">
            <button
              className="action-button success"
              onClick={startSync}
              disabled={loading || crmStatus?.status === 'not_configured'}
            >
              ▶️ Запустить синхронизацию
            </button>
            
            <button
              className="action-button warning"
              onClick={stopSync}
              disabled={loading || crmStatus?.status === 'not_configured'}
            >
              ⏹️ Остановить синхронизацию
            </button>
            
            <button
              className="action-button"
              onClick={manualSync}
              disabled={loading || crmStatus?.status === 'not_configured'}
            >
              🔄 Ручная синхронизация
            </button>
          </div>
        </div>

        {/* Сообщения */}
        {message && (
          <div className={`message ${message.includes('✅') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPage; 