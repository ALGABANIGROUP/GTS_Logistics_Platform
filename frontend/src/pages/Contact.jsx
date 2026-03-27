import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import gtsLogo from '../assets/gabani_logo.png';
import bgLogin from '../assets/bg_login.png';
import { API_BASE_URL } from '../config/env';

const CONTACT_RESPONSE_TIME = '24 hours';

const buildApiUrl = (path) => `${String(API_BASE_URL || '').replace(/\/+$/, '')}${path}`;

const readResponsePayload = async (response) => {
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) {
    return response.json();
  }

  const text = await response.text();
  return { message: text || response.statusText };
};

const Contact = () => {
  const location = useLocation();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    company: '',
    message: '',
    inquiryType: 'general'
  });
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [chatMessages, setChatMessages] = useState([
    { role: 'bot', message: 'Hello! I am the GTS Sales & Marketing Bot. How can I help you today?', timestamp: new Date() }
  ]);
  const [userInput, setUserInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [registrationMessage, setRegistrationMessage] = useState(null);

  useEffect(() => {
    if (location.state?.message) {
      setRegistrationMessage(location.state);
    }
  }, [location]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(buildApiUrl('/api/contact'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await readResponsePayload(response);

      if (response.ok) {
        setSubmitted(true);
        setFormData({ name: '', email: '', phone: '', company: '', message: '', inquiryType: 'general' });
        setTimeout(() => setSubmitted(false), 10000);
      } else {
        const fallbackMessage =
          response.status === 404
            ? 'Contact form service is not available yet. Please email sales@gtslogistics.com or support@gtslogistics.com.'
            : 'Failed to send message. Please try again.';
        setError(data.message || fallbackMessage);
      }
    } catch (err) {
      setError('Network error. Please check your connection and try again.');
      console.error('Contact form error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    const userMessage = userInput.trim();
    setChatMessages(prev => [...prev, {
      role: 'user',
      message: userMessage,
      timestamp: new Date()
    }]);
    setChatLoading(true);
    setUserInput('');

    try {
      const response = await fetch(buildApiUrl('/api/v1/support/chat'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await readResponsePayload(response);

      if (!response.ok) {
        const fallbackReply =
          response.status === 401 || response.status === 403
            ? 'Live support chat currently requires sign-in. Please log in or email sales@gtslogistics.com.'
            : 'Live support chat is temporarily unavailable. Please try again later or email support@gtslogistics.com.';
        throw new Error(data.message || fallbackReply);
      }

      const botReply =
        data.response ||
        data.reply ||
        "Thanks for reaching out! Our team will get back to you shortly.";

      setChatMessages(prev => [...prev, {
        role: 'bot',
        message: botReply,
        timestamp: new Date()
      }]);
    } catch (err) {
      console.error('Chat error:', err);
      setChatMessages(prev => [...prev, {
        role: 'bot',
        message:
          err?.message ||
          'Sorry, I am having trouble connecting. Please try again or email us directly at support@gtslogistics.com.',
        timestamp: new Date()
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="min-h-screen bg-cover bg-center bg-no-repeat" style={{ backgroundImage: `url(${bgLogin})` }}>
      <div className="min-h-screen bg-black/70">
        {/* Header */}
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <Link to="/">
              <img src={gtsLogo} alt="GTS Logistics" className="h-12" />
            </Link>
            <div className="hidden md:flex items-center gap-6">
              <Link to="/products" className="text-white hover:text-red-400 transition text-sm">Products</Link>
              <Link to="/pricing" className="text-white hover:text-red-400 transition text-sm">Pricing</Link>
              <Link to="/resources" className="text-white hover:text-red-400 transition text-sm">Resources</Link>
              <Link to="/about" className="text-white hover:text-red-400 transition text-sm">About</Link>
              <Link to="/contact" className="text-red-400 text-sm font-semibold">Contact</Link>
            </div>
            <div className="flex gap-3">
              <Link to="/login" className="px-5 py-2 border border-white text-white rounded hover:bg-white/10 transition text-sm">LOG IN</Link>
              <Link to="/register" className="px-5 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm">SIGN UP</Link>
            </div>
          </div>
        </div>

        {/* Hero */}
        <div className="container mx-auto px-4 py-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">Contact GTS Logistics</h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Our Sales, Marketing, and Customer Service teams are ready to help. Chat with our AI bot or fill out the form.
          </p>
        </div>

        {/* Registration Message */}
        {registrationMessage && (
          <div className="container mx-auto px-4 mb-6">
            <div className="bg-yellow-500/20 border border-yellow-500 rounded-xl p-4">
              <p className="text-yellow-400 text-sm">{registrationMessage.message}</p>
              <p className="text-gray-300 text-xs mt-1">
                Expected to reopen on {registrationMessage.reopenDate}.
                Contact <a href="mailto:admin@gtslogistics.com" className="text-red-400 hover:underline">admin@gtslogistics.com</a> for expedited approval.
              </p>
            </div>
          </div>
        )}

        {/* Chat Bot Section */}
        <div className="container mx-auto px-4 mb-8">
          <div className="bg-gradient-to-r from-red-900/30 to-black/60 rounded-xl p-6 border border-red-500/30">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-red-500/30 rounded-full flex items-center justify-center">
                <span className="text-xl">🤖</span>
              </div>
              <h2 className="text-xl font-bold text-white">GTS Sales & Marketing Bot</h2>
              <span className="text-xs text-green-400 ml-auto">● Online</span>
            </div>

            {/* Chat Messages */}
            <div className="bg-black/40 rounded-xl p-4 h-80 overflow-y-auto mb-4 space-y-3">
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-red-600 text-white' : 'bg-white/10 text-gray-300'}`}>
                    <p className="text-sm">{msg.message}</p>
                    <p className="text-[10px] mt-1 opacity-50">{formatTime(msg.timestamp)}</p>
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-white/10 rounded-lg p-3">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                      <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <form onSubmit={handleChatSubmit} className="flex gap-2">
              <input
                type="text"
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="Ask about pricing, features, demos, or support..."
                className="flex-1 px-4 py-2 bg-black/50 border border-white/20 rounded-lg text-white placeholder-gray-400 text-sm"
                disabled={chatLoading}
              />
              <button
                type="submit"
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm disabled:opacity-50"
                disabled={chatLoading || !userInput.trim()}
              >
                Send
              </button>
            </form>
            <p className="text-gray-500 text-xs mt-2">Powered by GTS AI Customer Service, Sales & Marketing Bots</p>
          </div>
        </div>

        {/* Contact Form and Info */}
        <div className="container mx-auto px-4 py-8">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Contact Form */}
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <h2 className="text-xl font-bold text-white mb-4">Send us a message</h2>
              {submitted ? (
                <div className="text-center py-8">
                  <div className="text-green-400 text-4xl mb-3">✓</div>
                  <p className="text-white">Thank you for contacting us!</p>
                  <p className="text-gray-400 text-sm mt-2">Our team will respond within {CONTACT_RESPONSE_TIME}.</p>
                  <button
                    onClick={() => setSubmitted(false)}
                    className="mt-4 px-4 py-2 border border-white/30 text-white rounded-lg hover:bg-white/10 transition text-sm"
                  >
                    Send another message
                  </button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-4">
                  {error && (
                    <div className="bg-red-500/20 border border-red-500 rounded-lg p-3 mb-4">
                      <p className="text-red-400 text-sm">{error}</p>
                    </div>
                  )}
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Full Name *</label>
                    <input type="text" name="name" value={formData.name} onChange={handleChange} required className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white" />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Email *</label>
                    <input type="email" name="email" value={formData.email} onChange={handleChange} required className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white" />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Phone</label>
                    <input type="tel" name="phone" value={formData.phone} onChange={handleChange} className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white" />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Company</label>
                    <input type="text" name="company" value={formData.company} onChange={handleChange} className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white" />
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Inquiry Type</label>
                    <select name="inquiryType" value={formData.inquiryType} onChange={handleChange} className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white">
                      <option value="general">General Inquiry</option>
                      <option value="sales">Sales / Pricing</option>
                      <option value="support">Technical Support</option>
                      <option value="partnership">Partnership / Integration</option>
                      <option value="billing">Billing / Account</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-gray-300 text-sm mb-1">Message *</label>
                    <textarea name="message" rows="4" value={formData.message} onChange={handleChange} required className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded-lg text-white"></textarea>
                  </div>
                  <button
                    type="submit"
                    disabled={loading}
                    className="w-full py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50"
                  >
                    {loading ? 'Sending...' : 'Send Message'}
                  </button>
                </form>
              )}
            </div>

            {/* Contact Info & Bots - UPDATED WITH NEW ADDRESS */}
            <div className="space-y-6">
              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <h2 className="text-xl font-bold text-white mb-4">Contact Information</h2>
                <div className="space-y-3">
                  <p className="text-gray-300">
                    <span className="text-red-400">📧 Sales:</span>
                    <a href="mailto:sales@gtslogistics.com" className="hover:text-red-400 ml-2">sales@gtslogistics.com</a>
                  </p>
                  <p className="text-gray-300">
                    <span className="text-red-400">📧 Marketing:</span>
                    <a href="mailto:marketing@gtslogistics.com" className="hover:text-red-400 ml-2">marketing@gtslogistics.com</a>
                  </p>
                  <p className="text-gray-300">
                    <span className="text-red-400">📧 Support:</span>
                    <a href="mailto:support@gtslogistics.com" className="hover:text-red-400 ml-2">support@gtslogistics.com</a>
                  </p>
                  <p className="text-gray-300">
                    <span className="text-red-400">📞 Phone:</span>
                    <a href="tel:+17786518297" className="hover:text-red-400 ml-2">+1 (778) 651-8297</a>
                  </p>
                  <div className="pt-2 border-t border-white/10 mt-2">
                    <p className="text-gray-300">
                      <span className="text-red-400">📬 Mailing Address:</span>
                    </p>
                    <p className="text-gray-400 text-sm mt-1 pl-2">329 HOWE ST UNIT #957</p>
                    <p className="text-gray-400 text-sm pl-2">VANCOUVER BC V6C 3N2</p>
                    <p className="text-gray-400 text-sm pl-2">CANADA</p>
                  </div>
                  <div className="pt-2 border-t border-white/10 mt-2">
                    <p className="text-gray-300">
                      <span className="text-red-400">🚚 Delivery Address:</span>
                    </p>
                    <p className="text-gray-400 text-sm mt-1 pl-2">329 HOWE ST UNIT #957</p>
                    <p className="text-gray-400 text-sm pl-2">VANCOUVER BC V6C 3N2</p>
                    <p className="text-gray-400 text-sm pl-2">CANADA</p>
                  </div>
                </div>
              </div>

              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <h2 className="text-xl font-bold text-white mb-4">Our AI Bots at Your Service</h2>
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-white/5 rounded-lg p-3 text-center">
                    <div className="text-2xl mb-1">💼</div>
                    <p className="text-white text-sm">Sales Bot</p>
                    <p className="text-gray-500 text-xs">Product info, pricing, quotes</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 text-center">
                    <div className="text-2xl mb-1">📢</div>
                    <p className="text-white text-sm">Marketing Bot</p>
                    <p className="text-gray-500 text-xs">Campaigns, events, resources</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 text-center">
                    <div className="text-2xl mb-1">💬</div>
                    <p className="text-white text-sm">Customer Service Bot</p>
                    <p className="text-gray-500 text-xs">Support, troubleshooting, FAQ</p>
                  </div>
                  <div className="bg-white/5 rounded-lg p-3 text-center">
                    <div className="text-2xl mb-1">⚖️</div>
                    <p className="text-white text-sm">Legal Consultant Bot</p>
                    <p className="text-gray-500 text-xs">Contracts, compliance, policies</p>
                  </div>
                </div>
                <p className="text-gray-500 text-xs text-center mt-4">Chat with any bot using the chat window above</p>
              </div>

              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <h2 className="text-xl font-bold text-white mb-3">Business Hours</h2>
                <p className="text-gray-300">Monday - Friday: 9:00 AM - 6:00 PM (PST)</p>
                <p className="text-gray-300">24/7 Emergency Support for active customers</p>
                <div className="mt-4 pt-4 border-t border-white/10">
                  <p className="text-gray-400 text-sm">📱 Download our mobile app for instant support:</p>
                  <div className="flex gap-3 mt-2">
                    <a href="#" className="text-gray-400 hover:text-white text-sm">App Store</a>
                    <a href="#" className="text-gray-400 hover:text-white text-sm">Google Play</a>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="container mx-auto px-4 py-6 border-t border-white/20 mt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-400 text-xs">© 2026 Gabani Transport Solutions LLC – All rights reserved.</p>
            <div className="flex gap-4 text-xs">
              <Link to="/privacy" className="text-gray-400 hover:text-white transition">Privacy Policy</Link>
              <Link to="/terms" className="text-gray-400 hover:text-white transition">Terms of Service</Link>
              <Link to="/legal" className="text-gray-400 hover:text-white transition">Legal Agreements</Link>
            </div>
            <div className="text-right">
              <p className="text-gray-500 text-xs">
                📞 <a href="tel:+17786518297" className="hover:text-white">+1 (778) 651-8297</a>
              </p>
              <p className="text-gray-500 text-xs mt-1">
                329 HOWE ST UNIT #957, VANCOUVER BC V6C 3N2, CANADA
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;
