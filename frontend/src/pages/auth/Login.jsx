import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import gtsLogo from '../../assets/gts_logo.png';
import bgLogin from '../../assets/bg_login.png';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // TODO: Implement actual login API call
      console.log('Login attempt:', formData);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      // For now, just navigate to dashboard
      navigate('/dashboard');
    } catch (error) {
      setErrors({ general: 'Login failed. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-cover bg-center bg-no-repeat" style={{ backgroundImage: `url(${bgLogin})` }}>
      {/* Overlay */}
      <div className="min-h-screen bg-black/70 flex items-center justify-center p-4">
        <div className="w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
          {/* Left Column - Login Form */}
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-8 border border-white/20">
            <div className="text-center mb-8">
              <div className="mb-4">
                <Link to="/" className="inline-flex items-center px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-white text-sm transition duration-200">
                  ← Back to Portal
                </Link>
              </div>
              <img src={gtsLogo} alt="GTS Logistics" className="h-12 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-white mb-2">Sign In</h1>
              <p className="text-gray-300">Access your GTS Logistics account</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {errors.general && (
                <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3">
                  <p className="text-red-400 text-sm">{errors.general}</p>
                </div>
              )}

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 bg-white/5 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent ${errors.email ? 'border-red-500' : 'border-white/20'
                    }`}
                  placeholder="Enter your email"
                  disabled={isLoading}
                />
                {errors.email && (
                  <p className="text-red-400 text-sm mt-1">{errors.email}</p>
                )}
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  className={`w-full px-4 py-3 bg-white/5 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent ${errors.password ? 'border-red-500' : 'border-white/20'
                    }`}
                  placeholder="Enter your password"
                  disabled={isLoading}
                />
                {errors.password && (
                  <p className="text-red-400 text-sm mt-1">{errors.password}</p>
                )}
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    className="w-4 h-4 text-red-600 bg-white/5 border-white/20 rounded focus:ring-red-500 focus:ring-2"
                  />
                  <span className="ml-2 text-sm text-gray-300">Remember me</span>
                </label>
                <Link to="/forgot-password" className="text-sm text-red-400 hover:underline">
                  Forgot password?
                </Link>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full py-3 px-4 bg-red-600 hover:bg-red-700 disabled:bg-red-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-transparent"
              >
                {isLoading ? 'Signing in...' : 'Sign In'}
              </button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-gray-400 text-sm">
                Don't have an account?{' '}
                <Link to="/register" className="text-red-400 hover:underline">
                  Request access
                </Link>
              </p>
            </div>
          </div>

          {/* Right Column - Security Info */}
          <div className="bg-black/40 backdrop-blur-sm rounded-xl p-8 border border-white/20">
            <h2 className="text-red-500 text-xl font-bold mb-4">SECURITY FIRST</h2>

            <h3 className="text-white text-lg font-semibold mb-3">PROTECTING YOUR ACCOUNT</h3>
            <p className="text-gray-300 text-sm mb-4">
              When you attempt to log in to your account from a new or unrecognized device, you will be asked to verify your identity.
            </p>

            <ul className="space-y-2 mb-6">
              <li className="flex items-center gap-2 text-gray-300 text-sm">
                <span className="text-green-500">✓</span> Push notification on your mobile device
              </li>
              <li className="flex items-center gap-2 text-gray-300 text-sm">
                <span className="text-green-500">✓</span> Security code via an authentication app
              </li>
              <li className="flex items-center gap-2 text-gray-300 text-sm">
                <span className="text-green-500">✓</span> Biometric input such as your face or fingerprint
              </li>
            </ul>

            <div className="border-t border-white/20 pt-6">
              <h3 className="text-white text-lg font-semibold mb-3">NEED HELP?</h3>
              <p className="text-gray-300 text-sm mb-4">
                If you're having trouble signing in, try these steps:
              </p>
              <ul className="space-y-1 text-gray-300 text-sm">
                <li>• Make sure your email and password are correct</li>
                <li>• Check if Caps Lock is on</li>
                <li>• Clear your browser cache and cookies</li>
                <li>• Try using a different browser or device</li>
              </ul>
              <p className="text-gray-400 text-sm mt-4">
                Still need help? <a href="/support" className="text-red-400 hover:underline">Contact support</a>.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
