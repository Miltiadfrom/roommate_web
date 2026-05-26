import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { profileAPI } from '../api';

const DISTRICTS = [
  'Центральный', 'Северный', 'Южный', 'Восточный', 'Западный',
  'Замоскворечье', 'Арбат', 'Пресненский', 'Хамовники'
];

export default function Profile() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: '',
    age: 25,
    gender: '',
    occupation: '',
    contact_info: '',
    budget_min: 10000,
    budget_max: 30000,
    preferred_districts: [],
    housing_type: '',
    rental_period: '',
    daily_schedule: '',
    cleanliness_level: 5,
    noise_tolerance: 5,
    smoking: false,
    alcohol: false,
    personality_type: 5,
    hobbies: [],
    has_pets: false,
    preferred_neighbor_gender: '',
    neighbor_age_min: 18,
    neighbor_age_max: 60,
    important_criteria: [],
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await profileAPI.getMyProfile();
      setFormData(response.data);
    } catch (err) {
      console.error('Error loading profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleDistrictChange = (district) => {
    setFormData(prev => ({
      ...prev,
      preferred_districts: prev.preferred_districts.includes(district)
        ? prev.preferred_districts.filter(d => d !== district)
        : [...prev.preferred_districts, district]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await profileAPI.updateProfile(formData);
      alert('Профиль сохранен!');
      navigate('/swipe');
    } catch (err) {
      alert('Ошибка сохранения профиля');
    }
  };

  if (loading) return <div className="main-content">Загрузка...</div>;

  return (
    <div className="app-container">
      <header className="header">
        <h1>Roommate Finder</h1>
        <nav>
          <button onClick={() => navigate('/swipe')}>Поиск</button>
          <button onClick={() => navigate('/messages')}>Сообщения</button>
          <button onClick={() => navigate('/matches')}>Матчи</button>
          {localStorage.getItem('isAdmin') === 'true' && (
            <button onClick={() => navigate('/admin')} style={{background: '#dc3545', color: 'white'}}>
              Админка
            </button>
          )}
          <button 
            onClick={() => {
              localStorage.removeItem('token');
              localStorage.removeItem('userId');
              localStorage.removeItem('isAdmin');
              navigate('/login');
            }}
            style={{ background: 'none', border: '1px solid #ddd', color: '#666', cursor: 'pointer' }}
          >
            Выйти
          </button>
        </nav>
      </header>

      <div className="main-content">
        <div className="card">
          <h2>Мой профиль</h2>
          
          <form onSubmit={handleSubmit}>
            <div className="form-row">
              <div className="form-group">
                <label>ФИО</label>
                <input
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  placeholder="Иван Иванов"
                />
              </div>

              <div className="form-group">
                <label>Возраст</label>
                <input
                  type="number"
                  name="age"
                  value={formData.age}
                  onChange={handleChange}
                  min="18"
                  max="100"
                />
              </div>

              <div className="form-group">
                <label>Пол</label>
                <select name="gender" value={formData.gender} onChange={handleChange}>
                  <option value="">Не указано</option>
                  <option value="male">Мужской</option>
                  <option value="female">Женский</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Занятие</label>
                <input
                  name="occupation"
                  value={formData.occupation}
                  onChange={handleChange}
                  placeholder="Студент, Работаю..."
                />
              </div>

              <div className="form-group">
                <label>Контакты</label>
                <input
                  name="contact_info"
                  value={formData.contact_info}
                  onChange={handleChange}
                  placeholder="Telegram, WhatsApp..."
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Бюджет от (₽)</label>
                <input
                  type="number"
                  name="budget_min"
                  value={formData.budget_min}
                  onChange={handleChange}
                  min="5000"
                />
              </div>

              <div className="form-group">
                <label>Бюджет до (₽)</label>
                <input
                  type="number"
                  name="budget_max"
                  value={formData.budget_max}
                  onChange={handleChange}
                  max="100000"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Предпочитаемые районы</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {DISTRICTS.map(district => (
                  <button
                    key={district}
                    type="button"
                    className={`btn ${formData.preferred_districts.includes(district) ? 'btn-success' : 'btn-secondary'}`}
                    style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}
                    onClick={() => handleDistrictChange(district)}
                  >
                    {district}
                  </button>
                ))}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Тип жилья</label>
                <select name="housing_type" value={formData.housing_type} onChange={handleChange}>
                  <option value="">Любой</option>
                  <option value="apartment">Квартира</option>
                  <option value="room">Комната</option>
                  <option value="studio">Студия</option>
                </select>
              </div>

              <div className="form-group">
                <label>Распорядок дня</label>
                <select name="daily_schedule" value={formData.daily_schedule} onChange={handleChange}>
                  <option value="">Не указано</option>
                  <option value="утро">Раннее утро</option>
                  <option value="день">День</option>
                  <option value="ночь">Ночь/Вечер</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Чистоплотность (1-10)</label>
                <input
                  type="range"
                  name="cleanliness_level"
                  value={formData.cleanliness_level}
                  onChange={handleChange}
                  min="1"
                  max="10"
                />
                <span>{formData.cleanliness_level}</span>
              </div>

              <div className="form-group">
                <label>Толерантность к шуму (1-10)</label>
                <input
                  type="range"
                  name="noise_tolerance"
                  value={formData.noise_tolerance}
                  onChange={handleChange}
                  min="1"
                  max="10"
                />
                <span>{formData.noise_tolerance}</span>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    name="smoking"
                    checked={formData.smoking}
                    onChange={handleChange}
                  />
                  Курение
                </label>
              </div>

              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    name="alcohol"
                    checked={formData.alcohol}
                    onChange={handleChange}
                  />
                  Алкоголь
                </label>
              </div>

              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    name="has_pets"
                    checked={formData.has_pets}
                    onChange={handleChange}
                  />
                  Есть животные
                </label>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Предпочтительный пол соседа</label>
                <select name="preferred_neighbor_gender" value={formData.preferred_neighbor_gender} onChange={handleChange}>
                  <option value="">Любой</option>
                  <option value="male">Мужской</option>
                  <option value="female">Женский</option>
                </select>
              </div>

              <div className="form-group">
                <label>Личностный тип (1-10)</label>
                <input
                  type="range"
                  name="personality_type"
                  value={formData.personality_type}
                  onChange={handleChange}
                  min="1"
                  max="10"
                />
                <span>{formData.personality_type}</span>
              </div>
            </div>

            <button type="submit" className="btn btn-block">
              Сохранить и начать поиск
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
