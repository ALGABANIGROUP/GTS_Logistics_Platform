import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import gtsLogo from '../../assets/gabani_logo.png';
import bgLogin from '../../assets/bg_login.png';

const AccountInactive = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const navigate = useNavigate();

  const handleResendActivation = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/auth/resend-activation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage('Activation email sent! Please check your inbox.');
        setTimeout(() => navigate('/login'), 5000);
      } else {
        setMessage(data.message || 'Failed to resend activation email.');
      }
    } catch (error) {
      setMessage('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cover bg-center bg-no-repeat" style={{ backgroundImage: `url(${bgLogin})` }}>
      <div className="min-h-screen bg-black/70 flex items-center justify-center">
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-md mx-auto bg-black/40 backdrop-blur-sm rounded-xl p-8 border border-white/20">
            <div className="text-center mb-6">
              <div className="text-yellow-500 text-5xl mb-4">⚠️</div>
              <h1 className="text-2xl font-bold text-white mb-2">Account Inactive</h1>
              <p className="text-gray-300 text-sm">
                Your account has not been activated yet. Please check your email for the activation link.
              </p>
            </div>

            <form onSubmit={handleResendActivation} className="space-y-4">
              <div>
                <label className="block text-gray-300 text-sm mb-1">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white"
                  placeholder="Enter your email"
                />
              </div>

              {message && (
                <div className={`p-3 rounded-lg text-sm ${message.includes('sent') ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                  {message}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50"
              >
                {loading ? 'Sending...' : 'Resend Activation Email'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <Link to="/login" className="text-gray-400 hover:text-white text-sm transition">
                ← Back to Login
              </Link>
              <p className="text-gray-500 text-xs mt-4">
                Need help? <a href="/contact" className="text-red-400 hover:underline">Contact Support</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AccountInactive;
