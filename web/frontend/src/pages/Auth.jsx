import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI, profileAPI } from '../api';

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  
  // Дополнительные поля для регистрации
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState(18);
  const [gender, setGender] = useState('');
  const [occupation, setOccupation] = useState('');
  const [contactInfo, setContactInfo] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (isLogin) {
        // Вход
        const response = await authAPI.login(phone, password);
        const userId = response.data.user_id;
        const isAdmin = response.data.is_admin;
        
        localStorage.setItem('userId', userId.toString());
        if (isAdmin) {
          localStorage.setItem('isAdmin', 'true');
        } else {
          localStorage.removeItem('isAdmin');
        }
        
        // Перенаправляем админа в админку, обычного пользователя в профиль
        if (isAdmin) {
          navigate('/admin');
        } else {
          navigate('/profile');
        }
      } else {
        // Регистрация с данными профиля
        const registerResponse = await authAPI.register(phone, password);
        const userId = registerResponse.data.user_id;
        localStorage.setItem('userId', userId.toString());
        
        // Сразу сохраняем профиль с данными
        const profileData = {
          full_name: fullName,
          age: parseInt(age),
          gender: gender,
          occupation: occupation,
          contact_info: contactInfo,
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
        };
        
        await profileAPI.updateProfile(profileData);
        navigate('/profile');
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Произошла ошибка');
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{isLogin ? 'Вход' : 'Регистрация'}</h2>
        
        {error && (
          <div style={{ color: 'red', marginBottom: '1rem', textAlign: 'center' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Телефон или логин</label>
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              required
              placeholder="+7..."
            />
          </div>

          <div className="form-group">
            <label>Пароль</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
            />
          </div>

          {!isLogin && (
            <>
              <div className="form-group">
                <label>ФИО</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                  placeholder="Иван Иванов"
                />
              </div>

              <div className="form-group">
                <label>Возраст</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(e.target.value)}
                  required
                  min="18"
                  max="100"
                />
              </div>

              <div className="form-group">
                <label>Пол</label>
                <select
                  value={gender}
                  onChange={(e) => setGender(e.target.value)}
                  required
                >
                  <option value="">Выберите пол</option>
                  <option value="male">Мужской</option>
                  <option value="female">Женский</option>
                </select>
              </div>

              <div className="form-group">
                <label>Занятие</label>
                <input
                  type="text"
                  value={occupation}
                  onChange={(e) => setOccupation(e.target.value)}
                  required
                  placeholder="Студент, Работаю..."
                />
              </div>

              <div className="form-group">
                <label>Контакты (Telegram, WhatsApp)</label>
                <input
                  type="text"
                  value={contactInfo}
                  onChange={(e) => setContactInfo(e.target.value)}
                  required
                  placeholder="@username или номер"
                />
              </div>
            </>
          )}

          <button type="submit" className="btn btn-block">
            {isLogin ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className="auth-switch">
          {isLogin ? (
            <>
              Нет аккаунта?{' '}
              <button onClick={() => setIsLogin(false)}>
                Зарегистрироваться
              </button>
            </>
          ) : (
            <>
              Уже есть аккаунт?{' '}
              <button onClick={() => setIsLogin(true)}>
                Войти
              </button>
            </>
          )}
        </div>

        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <button 
            onClick={() => {
              localStorage.removeItem('userId');
              navigate('/');
            }}
            style={{ background: 'none', border: 'none', color: '#666', cursor: 'pointer', textDecoration: 'underline' }}
          >
            Выйти из профиля
          </button>
        </div>
      </div>
    </div>
  );
}
