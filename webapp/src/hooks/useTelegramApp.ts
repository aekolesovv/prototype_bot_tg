import { useEffect, useState } from 'react';
import { TelegramWebApp, TelegramUser } from '../types';

declare global {
  interface Window {
    Telegram: {
      WebApp: TelegramWebApp;
    };
  }
}

export const useTelegramApp = () => {
  const [webApp, setWebApp] = useState<TelegramWebApp | null>(null);
  const [user, setUser] = useState<TelegramUser | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Проверяем, что мы в Telegram Web App
    if (window.Telegram && window.Telegram.WebApp) {
      const tg = window.Telegram.WebApp;
      
      // Инициализируем Web App
      tg.ready();
      
      // Устанавливаем тему
      tg.expand();
      
      // Получаем пользователя
      const telegramUser = tg.initDataUnsafe?.user;
      
      setWebApp(tg);
      setUser(telegramUser || null);
      setIsReady(true);
      
      console.log('Telegram Web App initialized:', {
        user: telegramUser,
        theme: tg.colorScheme,
        viewportHeight: tg.viewportHeight
      });
    } else {
      console.warn('Telegram Web App not available');
      // Для разработки создаем моковые данные
      const mockUser: TelegramUser = {
        id: 123456789,
        first_name: 'Тестовый',
        last_name: 'Пользователь',
        username: 'test_user'
      };
      setUser(mockUser);
      setIsReady(true);
    }
  }, []);

  const showMainButton = (text: string, callback: () => void) => {
    if (webApp) {
      webApp.mainButton.setText(text);
      webApp.mainButton.onClick(callback);
      webApp.mainButton.show();
    }
  };

  const hideMainButton = () => {
    if (webApp) {
      webApp.mainButton.hide();
    }
  };

  const showBackButton = (callback: () => void) => {
    if (webApp) {
      webApp.backButton.onClick(callback);
      webApp.backButton.show();
    }
  };

  const hideBackButton = () => {
    if (webApp) {
      webApp.backButton.hide();
    }
  };

  const hapticFeedback = (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft' = 'light') => {
    if (webApp) {
      webApp.HapticFeedback.impactOccurred(style);
    }
  };

  const closeApp = () => {
    if (webApp) {
      webApp.close();
    }
  };

  return {
    webApp,
    user,
    isReady,
    showMainButton,
    hideMainButton,
    showBackButton,
    hideBackButton,
    hapticFeedback,
    closeApp
  };
}; 