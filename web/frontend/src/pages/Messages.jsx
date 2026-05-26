import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { messageAPI, matchAPI } from '../api';

export default function Messages() {
  const navigate = useNavigate();
  const [contacts, setContacts] = useState([]);
  const [selectedContact, setSelectedContact] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    try {
      const response = await messageAPI.getContacts();
      setContacts(response.data);
    } catch (err) {
      console.error('Error loading contacts:', err);
    } finally {
      setLoading(false);
    }
  };

  const selectContact = async (contact) => {
    setSelectedContact(contact);
    try {
      const response = await messageAPI.getConversation(contact.user_id);
      setMessages(response.data);
    } catch (err) {
      console.error('Error loading conversation:', err);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedContact) return;

    try {
      await messageAPI.sendMessage(selectedContact.user_id, newMessage);
      const response = await messageAPI.getConversation(selectedContact.user_id);
      setMessages(response.data);
      setNewMessage('');
    } catch (err) {
      console.error('Error sending message:', err);
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
          <button onClick={() => navigate('/matches')}>Матчи</button>
        </nav>
      </header>

      <div className="main-content">
        <div className="card">
          <h2>Сообщения</h2>
          
          <div className="messages-container">
            <div className="contacts-list">
              {contacts.length === 0 ? (
                <div style={{ padding: '1rem', textAlign: 'center', color: '#666' }}>
                  Пока нет матчей. Начните свайпать!
                </div>
              ) : (
                contacts.map(contact => (
                  <div
                    key={contact.user_id}
                    className={`contact-item ${selectedContact?.user_id === contact.user_id ? 'active' : ''}`}
                    onClick={() => selectContact(contact)}
                  >
                    {contact.name}
                  </div>
                ))
              )}
            </div>

            <div className="chat-window">
              {selectedContact ? (
                <>
                  <div className="chat-messages">
                    {messages.length === 0 ? (
                      <div style={{ textAlign: 'center', color: '#999', padding: '2rem' }}>
                        Напишите первое сообщение!
                      </div>
                    ) : (
                      messages.map(msg => (
                        <div
                          key={msg.id}
                          className={`message ${msg.sender_id === parseInt(localStorage.getItem('userId')) ? 'sent' : 'received'}`}
                        >
                          {msg.content}
                        </div>
                      ))
                    )}
                  </div>

                  <form className="chat-input" onSubmit={sendMessage}>
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Введите сообщение..."
                    />
                    <button type="submit" className="btn">
                      Отправить
                    </button>
                  </form>
                </>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#999' }}>
                  Выберите контакт для начала общения
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
