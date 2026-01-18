import { useNavigate } from 'react-router-dom';
import { auth } from '../utils/auth';

const Navbar = () => {
  const navigate = useNavigate();
  const user = auth.getUser();

  const handleLogout = () => {
    auth.logout();
    navigate('/login');
  };

  return (
    <nav className="navbar navbar-dark bg-dark">
      <div className="container-fluid">
        <span className="navbar-brand mb-0 h1">
          <i className="bi bi-graph-up me-2"></i>
          Trading Signals SaaS
        </span>
        <div className="d-flex align-items-center">
          <span className="text-white me-3">
            <i className="bi bi-person-circle me-2"></i>
            {user?.email}
          </span>
          <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>
            <i className="bi bi-box-arrow-right me-1"></i>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
