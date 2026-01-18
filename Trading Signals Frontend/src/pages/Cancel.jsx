import { useNavigate } from 'react-router-dom';

const Cancel = () => {
  const navigate = useNavigate();

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="card shadow-lg text-center">
          <div className="card-body p-5">
            <div className="mb-4">
              <i className="bi bi-x-circle-fill text-danger" style={{ fontSize: '4rem' }}></i>
            </div>
            <h2 className="mb-3">Payment Cancelled</h2>
            <p className="text-muted mb-4">
              Your payment was cancelled. No charges were made to your account.
            </p>
            <p className="text-muted mb-4">
              You can still access limited signals or try subscribing again anytime.
            </p>
            <button className="btn btn-primary" onClick={() => navigate('/dashboard')}>
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cancel;
