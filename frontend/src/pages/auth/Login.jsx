import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import FormError from '../../components/ui/FormError.jsx';
import gtsLogo from '../../assets/gts_logo.png';
import bgLogin from '../../assets/bg_login.png';
import { useAuth } from '../../contexts/AuthContext.jsx';

const initialForm = {
  email: '',
  password: ''
};

const Login = () => {
  const [formData, setFormData] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [generalError, setGeneralError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { login, authReady, isAuthenticated } = useAuth();

  useEffect(() => {
    if (!authReady || !isAuthenticated) {
      return;
    }

    const next = new URLSearchParams(location.search).get('next');
    navigate(next || '/dashboard', { replace: true });
  }, [authReady, isAuthenticated, location.search, navigate]);

  const validateField = (name, value) => {
    switch (name) {
      case 'email':
        if (!value.trim()) {
          return 'Email is required';
        }
        if (!/\S+@\S+\.\S+/.test(value)) {
          return 'Please enter a valid email';
        }
        return '';
      case 'password':
        if (!value) {
          return 'Password is required';
        }
        if (value.length < 6) {
          return 'Password must be at least 6 characters';
        }
        return '';
      default:
        return '';
    }
  };

  const validateForm = () => {
    const nextErrors = {
      email: validateField('email', formData.email),
      password: validateField('password', formData.password)
    };

    setErrors(nextErrors);
    setTouched({ email: true, password: true });
    return !nextErrors.email && !nextErrors.password;
  };

  const handleInputChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value
    }));

    if (generalError) {
      setGeneralError('');
    }

    if (touched[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: validateField(name, value)
      }));
    }
  };

  const handleBlur = (event) => {
    const { name, value } = event.target;
    setTouched((prev) => ({
      ...prev,
      [name]: true
    }));
    setErrors((prev) => ({
      ...prev,
      [name]: validateField(name, value)
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setGeneralError('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const result = await login(formData.email, formData.password, rememberMe);

      if (result?.success) {
        const next = new URLSearchParams(location.search).get('next');
        navigate(next || '/dashboard', { replace: true });
        return;
      }

      if (result?.fieldErrors && Object.keys(result.fieldErrors).length > 0) {
        setErrors((prev) => ({
          ...prev,
          ...result.fieldErrors
        }));
      }

      setGeneralError(
        result?.message ||
        result?.error ||
        'Login failed. Please check your credentials.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen bg-cover bg-center bg-no-repeat"
      style={{ backgroundImage: `url(${bgLogin})` }}
    >
      <div className="min-h-screen bg-black/70 flex items-center justify-center p-4">
        <div className="w-full max-w-6xl grid md:grid-cols-2 gap-8 items-center">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-8 border border-white/20">
            <div className="text-center mb-8">
              <div className="mb-4">
                <Link
                  to="/"
                  className="inline-flex items-center px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-white text-sm transition duration-200"
                >
                  Back to Portal
                </Link>
              </div>
              <img src={gtsLogo} alt="GTS Logistics" className="h-12 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-white mb-2">Welcome Back</h1>
              <p className="text-gray-300">Sign in to your GTS account</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6" noValidate>
              {generalError && (
                <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3">
                  <p className="text-red-400 text-sm">{generalError}</p>
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
                  onBlur={handleBlur}
                  className={`w-full px-4 py-3 bg-white/5 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent ${errors.email ? 'border-red-500' : 'border-white/20'}`}
                  placeholder="Enter your email"
                  disabled={isLoading}
                  required
                />
                <FormError message={touched.email ? errors.email : ''} className="mt-1" />
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
                  onBlur={handleBlur}
                  className={`w-full px-4 py-3 bg-white/5 border rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent ${errors.password ? 'border-red-500' : 'border-white/20'}`}
                  placeholder="Enter your password"
                  disabled={isLoading}
                  required
                />
                <FormError message={touched.password ? errors.password : ''} className="mt-1" />
              </div>

              <div className="flex items-center justify-between">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(event) => setRememberMe(event.target.checked)}
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
                Don&apos;t have an account?{' '}
                <Link to="/register" className="text-red-400 hover:underline">
                  Create Account
                </Link>
              </p>
            </div>
          </div>

          <div className="bg-black/40 backdrop-blur-sm rounded-xl p-8 border border-white/20">
            <h2 className="text-red-500 text-xl font-bold mb-4">SECURITY FIRST</h2>

            <h3 className="text-white text-lg font-semibold mb-3">PROTECTING YOUR ACCOUNT</h3>
            <p className="text-gray-300 text-sm mb-4">
              When you sign in from a new or unrecognized device, you may be asked to verify your identity.
            </p>

            <ul className="space-y-2 mb-6">
              <li className="flex items-center gap-2 text-gray-300 text-sm">
                <span className="text-green-500">+</span> Push notification on your mobile device
              </li>
              <li className="flex items-center gap-2 text-gray-300 text-sm">
                <span className="text-green-500">+</span> Security code via an authentication app
              </li>
              <li className="flex items-center gap-2 text-gray-300 text-sm">
                <span className="text-green-500">+</span> Biometric input such as your face or fingerprint
              </li>
            </ul>

            <div className="border-t border-white/20 pt-6">
              <h3 className="text-white text-lg font-semibold mb-3">NEED HELP?</h3>
              <p className="text-gray-300 text-sm mb-4">
                If you are having trouble signing in, try these steps:
              </p>
              <ul className="space-y-1 text-gray-300 text-sm">
                <li>- Make sure your email and password are correct</li>
                <li>- Check if Caps Lock is on</li>
                <li>- Clear your browser cache and cookies</li>
                <li>- Try using a different browser or device</li>
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
