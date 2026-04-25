--- cake-marketplace/frontend/src/components/Navbar.jsx (原始)


+++ cake-marketplace/frontend/src/components/Navbar.jsx (修改后)
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const { isAuthenticated, user, logout, isConfectioner, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/">🎂 CakeMarket</Link>
      </div>

      <div className="nav-links">
        {!isAuthenticated ? (
          <>
            <Link to="/login">Вход</Link>
            <Link to="/register">Регистрация</Link>
          </>
        ) : (
          <>
            {isConfectioner && <Link to="/dashboard">Моя панель</Link>}
            {isAdmin && <Link to="/admin">Админка</Link>}
            <span className="user-greeting">Привет, {user?.full_name}!</span>
            <button onClick={handleLogout} className="btn-logout">
              Выход
            </button>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;