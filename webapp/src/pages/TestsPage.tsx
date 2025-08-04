import React, { useEffect, useState, useCallback } from 'react';
import { useTelegramApp } from '../hooks/useTelegramApp';
import { apiService } from '../services/api';
import { Test } from '../types';
import './TestsPage.css';

const TestsPage: React.FC = () => {
  const { user, hapticFeedback, showMainButton, hideMainButton } = useTelegramApp();
  const [tests, setTests] = useState<Test[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedTest, setSelectedTest] = useState<Test | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<{[key: string]: string}>({});
  const [isTestActive, setIsTestActive] = useState(false);
  const [testResults, setTestResults] = useState<{[key: number]: any}>({});

  const loadTests = async () => {
    try {
      const response = await apiService.getTests();
      // The response should be TestsResponse which has a tests property
      setTests(response.tests || []);
    } catch (error) {
      console.error('Error loading tests:', error);
      setTests([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartTest = useCallback(() => {
    if (!selectedTest) return;
    
    hapticFeedback('medium');
    setIsTestActive(true);
    setCurrentQuestion(0);
    setAnswers({});
  }, [selectedTest, hapticFeedback]);

  const handleFinishTest = useCallback(async () => {
    if (!selectedTest || !user) return;

    try {
      const response = await apiService.submitTest({
        test_id: selectedTest.id,
        user_id: user.id.toString(),
        answers: answers
      });

      if (response.success) {
        hapticFeedback('medium');
        setTestResults(prev => ({ ...prev, [selectedTest.id]: response }));
        alert(`Тест завершен! Ваш результат: ${response.score}%`);
        setIsTestActive(false);
        setSelectedTest(null);
      } else {
        hapticFeedback('heavy');
        alert('Ошибка при отправке результатов');
      }
    } catch (error) {
      console.error('Test submission error:', error);
      hapticFeedback('heavy');
      alert('Ошибка при отправке результатов');
    }
  }, [selectedTest, user, answers, hapticFeedback]);

  useEffect(() => {
    loadTests();
  }, []);

  useEffect(() => {
    if (selectedTest && !isTestActive) {
      showMainButton('Начать тест', handleStartTest);
    } else if (isTestActive) {
      showMainButton('Завершить тест', handleFinishTest);
    } else {
      hideMainButton();
    }
  }, [selectedTest, isTestActive, showMainButton, hideMainButton, handleStartTest, handleFinishTest]);

  const handleTestSelect = (test: Test) => {
    hapticFeedback('light');
    setSelectedTest(selectedTest?.id === test.id ? null : test);
    setIsTestActive(false);
  };

  const handleAnswerSelect = (questionId: string, answer: string) => {
    hapticFeedback('light');
    setAnswers(prev => ({ ...prev, [questionId]: answer }));
  };

  const getLevelLabel = (level: string) => {
    return level === 'beginner' ? 'Начальный' : 'Продвинутый';
  };

  const getTestStatus = (testId: number) => {
    if (testResults[testId]) {
      return `Пройден (${testResults[testId].score}%)`;
    }
    return 'Не пройден';
  };

  // Моковые вопросы для демонстрации
  const mockQuestions = [
    {
      id: '1',
      question: 'Выберите правильную форму глагола: "I ___ to school every day."',
      options: ['go', 'goes', 'going', 'went'],
      correct: 'go'
    },
    {
      id: '2', 
      question: 'Какое слово означает "дом" на английском?',
      options: ['house', 'home', 'building', 'room'],
      correct: 'house'
    },
    {
      id: '3',
      question: 'Выберите правильное время: "She ___ TV now."',
      options: ['watch', 'watches', 'is watching', 'watched'],
      correct: 'is watching'
    }
  ];

  if (isLoading) {
    return (
      <div className="tests-page">
        <div className="loading">Загрузка тестов...</div>
      </div>
    );
  }

  return (
    <div className="tests-page">
      <div className="header">
        <h1>📝 Тесты</h1>
        <p className="subtitle">Проверьте свои знания английского языка</p>
      </div>

      {!isTestActive ? (
        <div className="tests-list">
          {tests.length === 0 ? (
            <div className="empty-state">
              <span className="empty-icon">📝</span>
              <p>Тесты пока не доступны</p>
            </div>
          ) : (
            tests.map((test) => (
              <div
                key={test.id}
                className={`test-card ${selectedTest?.id === test.id ? 'selected' : ''} ${
                  testResults[test.id] ? 'completed' : ''
                }`}
                onClick={() => handleTestSelect(test)}
              >
                <div className="test-header">
                  <h3 className="test-title">{test.title}</h3>
                  <span className={`status-badge ${testResults[test.id] ? 'completed' : ''}`}>
                    {getTestStatus(test.id)}
                  </span>
                </div>
                
                <div className="test-details">
                  <div className="detail-item">
                    <span className="detail-icon">📊</span>
                    <span className="detail-text">{getLevelLabel(test.level)}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-icon">❓</span>
                    <span className="detail-text">{test.questions_count} вопросов</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-icon">⏱️</span>
                    <span className="detail-text">{test.duration}</span>
                  </div>
                </div>

                {selectedTest?.id === test.id && !testResults[test.id] && (
                  <div className="start-info">
                    <p>Нажмите кнопку внизу для начала теста</p>
                  </div>
                )}

                {testResults[test.id] && (
                  <div className="result-info">
                    <p>✅ Тест пройден! Результат: {testResults[test.id].score}%</p>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      ) : (
        <div className="test-interface">
          <div className="test-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${((currentQuestion + 1) / mockQuestions.length) * 100}%` }}
              ></div>
            </div>
            <span className="progress-text">
              Вопрос {currentQuestion + 1} из {mockQuestions.length}
            </span>
          </div>

          <div className="question-card">
            <h3 className="question-title">{mockQuestions[currentQuestion].question}</h3>
            
            <div className="options-list">
              {mockQuestions[currentQuestion].options.map((option, index) => (
                <button
                  key={index}
                  className={`option-button ${
                    answers[mockQuestions[currentQuestion].id] === option ? 'selected' : ''
                  }`}
                  onClick={() => handleAnswerSelect(mockQuestions[currentQuestion].id, option)}
                >
                  <span className="option-letter">{String.fromCharCode(65 + index)}</span>
                  <span className="option-text">{option}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="test-navigation">
            <button
              className="nav-button"
              onClick={() => setCurrentQuestion(prev => Math.max(0, prev - 1))}
              disabled={currentQuestion === 0}
            >
              ← Назад
            </button>
            
            <button
              className="nav-button"
              onClick={() => setCurrentQuestion(prev => Math.min(mockQuestions.length - 1, prev + 1))}
              disabled={currentQuestion === mockQuestions.length - 1}
            >
              Далее →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestsPage; 