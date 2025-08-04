import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import './Navigation.css';

interface NavigationProps {
  onNavigate: (path: string) => void;
}

const Navigation: React.FC<NavigationProps> = ({ onNavigate }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Главная', icon: '🏠' },
    { path: '/schedule', label: 'Расписание', icon: '📅' },
    { path: '/clubs', label: 'Клубы', icon: '👥' },
    { path: '/tests', label: 'Тесты', icon: '📝' },
    { path: '/notifications', label: 'Уведомления', icon: '🔔' },
    { path: '/admin', label: 'Админ', icon: '⚙️' },
    { path: '/profile', label: 'Профиль', icon: '👤' },
  ];

  const handleNavClick = (path: string) => {
    navigate(path);
    onNavigate(path);
  };

  return (
    <nav className="navigation">
      <div className="nav-container">
        {navItems.map((item) => (
          <button
            key={item.path}
            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            onClick={() => handleNavClick(item.path)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
};

export default Navigation; 