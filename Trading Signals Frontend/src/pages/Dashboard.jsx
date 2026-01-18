import { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { api } from '../utils/api';
import { auth } from '../utils/auth';
import Navbar from '../components/Navbar';
import Loader from '../components/Loader';

const Dashboard = () => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isPaid, setIsPaid] = useState(false);
  const [message, setMessage] = useState('');
  const [total, setTotal] = useState(0);
  const [creatingCheckout, setCreatingCheckout] = useState(false);

  useEffect(() => {
    fetchSignals();
  }, []);

  const fetchSignals = async () => {
    setLoading(true);
    try {
      const token = auth.getToken();
      const data = await api.getSignals(token);
      
      setSignals(data.signals);
      setIsPaid(data.is_paid);
      setMessage(data.message);
      setTotal(data.total);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async () => {
    setCreatingCheckout(true);
    try {
      const token = auth.getToken();
      const data = await api.createCheckout(token);
      
      // Redirect to Stripe checkout
      window.location.href = data.checkout_url;
    } catch (error) {
      toast.error(error.message);
      setCreatingCheckout(false);
    }
  };

  return (
    <>
      <Navbar />
      {(loading || creatingCheckout) && <Loader />}
      
      <div className="dashboard-container">
        <div className="container">
          <div className="row mb-4">
            <div className="col-12">
              <h2 className="mb-3">
                <i className="bi bi-bar-chart-line me-2"></i>
                Trading Signals Dashboard
              </h2>
              <p className="text-muted">Real-time trading signals updated every 5 minutes</p>
            </div>
          </div>

          {!isPaid && message && (
            <div className="row mb-4">
              <div className="col-12">
                <div className="upgrade-banner">
                  <h4 className="mb-3">
                    <i className="bi bi-star-fill me-2"></i>
                    Upgrade to Premium
                  </h4>
                  <p className="mb-3">{message}</p>
                  <button 
                    className="btn btn-light btn-lg" 
                    onClick={handleSubscribe}
                    disabled={creatingCheckout}
                  >
                    <i className="bi bi-credit-card me-2"></i>
                    {creatingCheckout ? 'Redirecting...' : 'Subscribe Now - ₹499'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {isPaid && (
            <div className="alert alert-success mb-4" role="alert">
              <i className="bi bi-check-circle-fill me-2"></i>
              You have access to all {total} premium signals!
            </div>
          )}

          <div className="row">
            <div className="col-12">
              <div className="table-container">
                <div className="table-responsive">
                  <table className="table table-hover signal-table mb-0">
                    <thead>
                      <tr>
                        <th scope="col">#</th>
                        <th scope="col">Symbol</th>
                        <th scope="col">Action</th>
                        <th scope="col">Price</th>
                        <th scope="col">Target</th>
                        <th scope="col">Stop Loss</th>
                        <th scope="col">Timestamp</th>
                      </tr>
                    </thead>
                    <tbody>
                      {signals.length === 0 && !loading ? (
                        <tr>
                          <td colSpan="7" className="text-center py-4">
                            No signals available
                          </td>
                        </tr>
                      ) : (
                        signals.map((signal, index) => (
                          <tr key={index}>
                            <td>{index + 1}</td>
                            <td>
                              <strong>{signal.symbol}</strong>
                            </td>
                            <td>
                              <span className={signal.action === 'BUY' ? 'action-badge-buy' : 'action-badge-sell'}>
                                {signal.action}
                              </span>
                            </td>
                            <td>₹{signal.price.toFixed(2)}</td>
                            <td className="text-success">₹{signal.target.toFixed(2)}</td>
                            <td className="text-danger">₹{signal.stoploss.toFixed(2)}</td>
                            <td className="text-muted">{signal.timestamp}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
              
              {!isPaid && signals.length > 0 && (
                <div className="text-center mt-3">
                  <small className="text-muted">
                    <i className="bi bi-lock-fill me-1"></i>
                    Showing {signals.length} of {total} signals. Subscribe to view all.
                  </small>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Dashboard;
