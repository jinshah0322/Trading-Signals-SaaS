import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Success = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const timer = setTimeout(() => {
      navigate('/dashboard');
    }, 3000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="card shadow-lg text-center">
          <div className="card-body p-5">
            <div className="mb-4">
              <i className="bi bi-check-circle-fill text-success" style={{ fontSize: '4rem' }}></i>
            </div>
            <h2 className="mb-3">Payment Successful!</h2>
            <p className="text-muted mb-4">
              Your subscription is now active. You have access to all premium trading signals.
            </p>
            <p className="text-muted">
              Redirecting to dashboard in 3 seconds...
            </p>
            <button className="btn btn-primary mt-3" onClick={() => navigate('/dashboard')}>
              Go to Dashboard Now
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Success;
