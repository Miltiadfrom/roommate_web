import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { swipeAPI } from '../api';

export default function Swipe() {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCandidates();
  }, []);

  const loadCandidates = async () => {
    try {
      const response = await swipeAPI.getCandidates();
      setCandidates(response.data);
    } catch (err) {
      console.error('Error loading candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSwipe = async (direction) => {
    if (currentIndex >= candidates.length) return;

    const candidate = candidates[currentIndex];
    
    try {
      const response = await swipeAPI.createSwipe(candidate.profile.user_id, direction);
      
      if (response.data.is_match) {
        alert('Это матч! Вы можете написать друг другу.');
      }
    } catch (err) {
      console.error('Error creating swipe:', err);
    }

    setCurrentIndex(prev => prev + 1);
  };

  if (loading) {
    return (
      <div className="app-container">
        <Header navigate={navigate} />
        <div className="main-content">Загрузка кандидатов...</div>
      </div>
    );
  }

  if (currentIndex >= candidates.length) {
    return (
      <div className="app-container">
        <Header navigate={navigate} />
        <div className="main-content">
          <div className="card" style={{ textAlign: 'center' }}>
            <h2>Кандидаты закончились</h2>
            <p>Заходите позже или измените параметры профиля</p>
            <button className="btn" onClick={() => navigate('/profile')}>
              Редактировать профиль
            </button>
          </div>
        </div>
      </div>
    );
  }

  const candidate = candidates[currentIndex];
  const { profile, compatibility_score, compatibility_details } = candidate;

  return (
    <div className="app-container">
      <Header navigate={navigate} />
      
      <div className="main-content">
        <div className="swipe-container">
          <div className="swipe-card">
            <h3>{profile.full_name || `Пользователь ${profile.user_id}`}</h3>
            <div className="compatibility-score">
              Совместимость: {compatibility_score}%
            </div>

            <div className="profile-details">
              <div className="profile-detail">
                <span>Возраст:</span>
                <span>{profile.age} лет</span>
              </div>
              <div className="profile-detail">
                <span>Пол:</span>
                <span>{profile.gender === 'male' ? 'Мужской' : profile.gender === 'female' ? 'Женский' : 'Не указано'}</span>
              </div>
              <div className="profile-detail">
                <span>Занятие:</span>
                <span>{profile.occupation || 'Не указано'}</span>
              </div>
              <div className="profile-detail">
                <span>Бюджет:</span>
                <span>{profile.budget_min} - {profile.budget_max} ₽</span>
              </div>
              <div className="profile-detail">
                <span>Районы:</span>
                <span>{profile.preferred_districts.join(', ') || 'Не указаны'}</span>
              </div>
              <div className="profile-detail">
                <span>Распорядок:</span>
                <span>{profile.daily_schedule || 'Не указан'}</span>
              </div>
              <div className="profile-detail">
                <span>Чистоплотность:</span>
                <span>{profile.cleanliness_level}/10</span>
              </div>
              <div className="profile-detail">
                <span>Шум:</span>
                <span>{profile.noise_tolerance}/10</span>
              </div>
              <div className="profile-detail">
                <span>Курение:</span>
                <span>{profile.smoking ? 'Да' : 'Нет'}</span>
              </div>
              <div className="profile-detail">
                <span>Алкоголь:</span>
                <span>{profile.alcohol ? 'Да' : 'Нет'}</span>
              </div>
              <div className="profile-detail">
                <span>Животные:</span>
                <span>{profile.has_pets ? 'Есть' : 'Нет'}</span>
              </div>
            </div>

            {/* Детали совместимости */}
            <div className="compatibility-details">
              <h4>Детали совместимости:</h4>
              {Object.entries(compatibility_details).map(([key, value]) => (
                <CompatibilityBar 
                  key={key} 
                  label={getCategoryLabel(key)} 
                  value={value} 
                />
              ))}
            </div>

            <div className="swipe-actions">
              <button 
                className="btn-left"
                onClick={() => handleSwipe('left')}
              >
                ✕
              </button>
              <button 
                className="btn-right"
                onClick={() => handleSwipe('right')}
              >
                ✓
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function Header({ navigate }) {
  return (
    <header className="header">
      <h1>Roommate Finder</h1>
      <nav>
        <button onClick={() => navigate('/profile')}>Профиль</button>
        <button onClick={() => navigate('/messages')}>Сообщения</button>
        <button onClick={() => navigate('/matches')}>Матчи</button>
      </nav>
    </header>
  );
}

function CompatibilityBar({ label, value }) {
  return (
    <div className="compatibility-bar">
      <span className="compatibility-bar-label">{label}</span>
      <div className="compatibility-bar-track">
        <div 
          className="compatibility-bar-fill" 
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="compatibility-bar-value">{value}%</span>
    </div>
  );
}

function getCategoryLabel(key) {
  const labels = {
    budget: 'Бюджет',
    location: 'Район',
    cleanliness: 'Чистота',
    noise: 'Шум',
    schedule: 'Распорядок',
    habits: 'Привычки',
    personality: 'Личность'
  };
  return labels[key] || key;
}
