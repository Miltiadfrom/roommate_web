import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './pages/Auth';
import Profile from './pages/Profile';
import Swipe from './pages/Swipe';
import Messages from './pages/Messages';
import Matches from './pages/Matches';
import Admin from './pages/Admin';

function PrivateRoute({ children }) {
  const userId = localStorage.getItem('userId');
  return userId ? children : <Navigate to="/login" />;
}

function AdminRoute({ children }) {
  const userId = localStorage.getItem('userId');
  const isAdmin = localStorage.getItem('isAdmin') === 'true';
  return userId && isAdmin ? children : <Navigate to="/profile" />;
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
        <Route 
          path="/admin" 
          element={
            <AdminRoute>
              <Admin />
            </AdminRoute>
          } 
        />
        <Route path="/" element={<Navigate to="/profile" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
