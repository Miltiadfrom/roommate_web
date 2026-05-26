import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

export default function Admin() {
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    loadAdminData();
  }, []);

  const loadAdminData = async () => {
    try {
      const [statsRes, usersRes] = await Promise.all([
        api.get('/admin/statistics'),
        api.get('/admin/users')
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!confirm(`Удалить пользователя ${userId}?`)) return;
    
    try {
      await api.delete(`/admin/users/${userId}`);
      loadAdminData();
    } catch (err) {
      alert('Ошибка удаления: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('userId');
    localStorage.removeItem('isAdmin');
    navigate('/login');
  };

  if (loading) return <div className="container">Загрузка...</div>;
  if (error) return <div className="container" style={{color: 'red'}}>{error}</div>;

  return (
    <div className="container">
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
        <h1>Админ-панель</h1>
        <button onClick={handleLogout} className="btn btn-secondary">Выйти</button>
      </div>

      <div className="card" style={{marginBottom: '2rem'}}>
        <h2>Статистика</h2>
        {stats && (
          <div style={{display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem'}}>
            <div className="stat-card">
              <h3>{stats.total_users || 0}</h3>
              <p>Пользователей</p>
            </div>
            <div className="stat-card">
              <h3>{stats.total_profiles || 0}</h3>
              <p>Профилей</p>
            </div>
            <div className="stat-card">
              <h3>{stats.total_matches || 0}</h3>
              <p>Мэтчей</p>
            </div>
            <div className="stat-card">
              <h3>{stats.total_messages || 0}</h3>
              <p>Сообщений</p>
            </div>
          </div>
        )}
      </div>

      <div className="card">
        <h2>Пользователи</h2>
        <table style={{width: '100%', borderCollapse: 'collapse'}}>
          <thead>
            <tr style={{borderBottom: '2px solid #ddd'}}>
              <th style={{padding: '0.5rem', textAlign: 'left'}}>ID</th>
              <th style={{padding: '0.5rem', textAlign: 'left'}}>Телефон</th>
              <th style={{padding: '0.5rem', textAlign: 'left'}}>Админ</th>
              <th style={{padding: '0.5rem', textAlign: 'left'}}>Активен</th>
              <th style={{padding: '0.5rem', textAlign: 'left'}}>Действия</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.id} style={{borderBottom: '1px solid #eee'}}>
                <td style={{padding: '0.5rem'}}>{user.id}</td>
                <td style={{padding: '0.5rem'}}>{user.phone}</td>
                <td style={{padding: '0.5rem'}}>{user.is_admin ? '✓' : '-'}</td>
                <td style={{padding: '0.5rem'}}>{user.is_active ? '✓' : '-'}</td>
                <td style={{padding: '0.5rem'}}>
                  <button 
                    onClick={() => handleDeleteUser(user.id)}
                    className="btn btn-danger"
                    style={{padding: '0.25rem 0.5rem', fontSize: '0.875rem'}}
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
