import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { matchAPI } from '../api';

export default function Matches() {
  const navigate = useNavigate();
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMatches();
  }, []);

  const loadMatches = async () => {
    try {
      const response = await matchAPI.getMatches();
      setMatches(response.data);
    } catch (err) {
      console.error('Error loading matches:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="main-content">Загрузка...</div>;

  return (
    <div className="app-container">
      <header className="header">
        <h1>Roommate Finder</h1>
        <nav>
          <button onClick={() => navigate('/profile')}>Профиль</button>
          <button onClick={() => navigate('/swipe')}>Поиск</button>
          <button onClick={() => navigate('/messages')}>Сообщения</button>
        </nav>
      </header>

      <div className="main-content">
        <div className="card">
          <h2>Мои матчи ({matches.length})</h2>
          
          {matches.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem' }}>
              <p style={{ color: '#666', marginBottom: '1.5rem' }}>
                У вас пока нет матчей. Продолжайте свайпать!
              </p>
              <button className="btn" onClick={() => navigate('/swipe')}>
                Начать поиск
              </button>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
              {matches.map(match => (
                <div 
                  key={match.user_id}
                  className="card"
                  style={{ marginBottom: 0, cursor: 'pointer' }}
                  onClick={() => {
                    navigate('/messages');
                    // В реальном приложении здесь можно сразу открыть чат
                  }}
                >
                  <h3 style={{ color: '#667eea', marginBottom: '0.5rem' }}>
                    {match.name}
                  </h3>
                  <p style={{ color: '#666', fontSize: '0.9rem' }}>
                    Нажмите, чтобы написать сообщение
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
