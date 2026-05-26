import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './pages/Auth';
import Profile from './pages/Profile';
import Swipe from './pages/Swipe';
import Messages from './pages/Messages';
import Matches from './pages/Matches';

function PrivateRoute({ children }) {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Auth />} />
        <Route 
          path="/profile" 
          element={
            <PrivateRoute>
              <Profile />
            </PrivateRoute>
          } 
        />
        <Route 
          path="/swipe" 
          element={
            <PrivateRoute>
              <Swipe />
            </PrivateRoute>
          } 
        />
        <Route 
          path="/messages" 
          element={
            <PrivateRoute>
              <Messages />
            </PrivateRoute>
          } 
        />
        <Route 
          path="/matches" 
          element={
            <PrivateRoute>
              <Matches />
            </PrivateRoute>
          } 
        />
        <Route path="/" element={<Navigate to="/profile" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
