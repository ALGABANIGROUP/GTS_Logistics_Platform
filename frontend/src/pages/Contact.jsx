import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import gtsLogo from '../assets/gabani_logo.png';
import bgLogin from '../assets/bg_login.png';

const Contact = () => {
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
    const [config, setConfig] = useState(null);

    useEffect(() => {
        const loadConfig = async () => {
            try {
                const response = await fetch('/api/contact/config');
                if (response.ok) {
                    const configData = await response.json();
                    setConfig(configData);
                }
            } catch (err) {
                console.error('Failed to load contact config:', err);
            }
        };
        loadConfig();
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const data = await response.json();

            if (response.ok) {
                setSubmitted(true);
                setFormData({ name: '', email: '', phone: '', company: '', message: '', inquiryType: 'general' });
            } else {
                setError(data.message || 'Failed to send message. Please try again.');
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

        const userMessage = { role: 'user', message: userInput, timestamp: new Date() };
        setChatMessages(prev => [...prev, userMessage]);
        setChatLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: userInput, context: 'sales_marketing' }),
            });

            const data = await response.json();
            const botReply = data.reply || "Thanks for reaching out! Our team will get back to you shortly.";
            const botMessage = { role: 'bot', message: botReply, timestamp: new Date() };

            setChatMessages(prev => [...prev, botMessage]);
        } catch (err) {
            console.error('Chat error:', err);
            const errorMessage = { role: 'bot', message: 'Sorry, I am having trouble connecting. Please try again or email us directly.', timestamp: new Date() };
            setChatMessages(prev => [...prev, errorMessage]);
        } finally {
            setChatLoading(false);
            setUserInput('');
        }
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

                {/* Chat Bot Section */}
                <div className="container mx-auto px-4 mb-8">
                    <div className="bg-gradient-to-r from-red-900/30 to-black/60 rounded-xl p-6 border border-red-500/30">
                        <h2 className="text-2xl font-bold text-white mb-4">AI Assistant Chat</h2>
                        <p className="text-gray-400 mb-4">Chat with our AI bots for instant assistance.</p>

                        {/* Chat Messages */}
                        <div className="bg-black/50 rounded-lg p-4 mb-4 h-64 overflow-y-auto">
                            {chatMessages.map((msg, idx) => (
                                <div key={idx} className={`mb-3 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-red-600 text-white' : 'bg-white/10 text-gray-300'}`}>
                                        <p className="text-sm">{msg.message}</p>
                                        <p className="text-xs opacity-70 mt-1">
                                            {msg.timestamp ? new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                                        </p>
                                    </div>
                                </div>
                            ))}
                            {chatLoading && (
                                <div className="flex justify-start mb-3">
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
                                placeholder="Ask about pricing, features, demos, support, or anything else..."
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
                                    <h3 className="text-white text-xl font-bold mb-2">Message Sent!</h3>
                                    <p className="text-gray-300">Thank you for contacting us. We'll get back to you within 24 hours.</p>
                                </div>
                            ) : (
                                <form onSubmit={handleSubmit}>
                                    <div className="space-y-4">
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-white text-sm font-medium mb-2">Name *</label>
                                                <input
                                                    type="text"
                                                    name="name"
                                                    value={formData.name}
                                                    onChange={handleChange}
                                                    required
                                                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-red-400"
                                                    placeholder="Your full name"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-white text-sm font-medium mb-2">Email *</label>
                                                <input
                                                    type="email"
                                                    name="email"
                                                    value={formData.email}
                                                    onChange={handleChange}
                                                    required
                                                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-red-400"
                                                    placeholder="your@email.com"
                                                />
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-white text-sm font-medium mb-2">Phone</label>
                                                <input
                                                    type="tel"
                                                    name="phone"
                                                    value={formData.phone}
                                                    onChange={handleChange}
                                                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-red-400"
                                                    placeholder="+1 (555) 123-4567"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-white text-sm font-medium mb-2">Inquiry Type</label>
                                                <select
                                                    name="inquiryType"
                                                    value={formData.inquiryType}
                                                    onChange={handleChange}
                                                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-red-400"
                                                >
                                                    <option value="general">General Inquiry</option>
                                                    <option value="sales">Sales</option>
                                                    <option value="support">Support</option>
                                                    <option value="partnership">Partnership</option>
                                                    <option value="billing">Billing</option>
                                                </select>
                                            </div>
                                        </div>

                                        <div>
                                            <label className="block text-white text-sm font-medium mb-2">Company</label>
                                            <input
                                                type="text"
                                                name="company"
                                                value={formData.company}
                                                onChange={handleChange}
                                                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-red-400"
                                                placeholder="Your company name"
                                            />
                                        </div>

                                        <div>
                                            <label className="block text-white text-sm font-medium mb-2">Message *</label>
                                            <textarea
                                                name="message"
                                                value={formData.message}
                                                onChange={handleChange}
                                                required
                                                rows="5"
                                                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-red-400 resize-none"
                                                placeholder="Tell us how we can help you..."
                                            />
                                        </div>

                                        <button
                                            type="submit"
                                            disabled={loading}
                                            className="w-full py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50"
                                        >
                                            {loading ? 'Sending...' : 'Send Message'}
                                        </button>
                                    </div>
                                </form>
                            )}
                        </div>

                        {/* Contact Info & Bots */}
                        <div className="space-y-6">
                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <h2 className="text-xl font-bold text-white mb-4">Contact Information</h2>
                                <div className="space-y-3">
                                    {config ? (
                                        <>
                                            <p className="text-gray-300"><span className="text-red-400">📧 Sales:</span> <a href={`mailto:${config.sales_email}`} className="hover:text-red-400">{config.sales_email}</a></p>
                                            <p className="text-gray-300"><span className="text-red-400">📧 Marketing:</span> <a href={`mailto:${config.marketing_email}`} className="hover:text-red-400">{config.marketing_email}</a></p>
                                            <p className="text-gray-300"><span className="text-red-400">📧 Support:</span> <a href={`mailto:${config.support_email}`} className="hover:text-red-400">{config.support_email}</a></p>
                                            <p className="text-gray-300"><span className="text-red-400">📞 Phone:</span> <a href={`tel:${config.phone}`} className="hover:text-red-400">{config.phone}</a></p>
                                            <p className="text-gray-300"><span className="text-red-400">📍 Address:</span> {config.address}</p>
                                        </>
                                    ) : (
                                        <>
                                            <p className="text-gray-300"><span className="text-red-400">📧 Sales:</span> <a href="mailto:sales@gtslogistics.com" className="hover:text-red-400">sales@gtslogistics.com</a></p>
                                            <p className="text-gray-300"><span className="text-red-400">📧 Marketing:</span> <a href="mailto:marketing@gtslogistics.com" className="hover:text-red-400">marketing@gtslogistics.com</a></p>
                                            <p className="text-gray-300"><span className="text-red-400">📧 Support:</span> <a href="mailto:support@gtslogistics.com" className="hover:text-red-400">support@gtslogistics.com</a></p>
                                            <p className="text-gray-300"><span className="text-red-400">📞 Phone:</span> <a href="tel:+18883641189" className="hover:text-red-400">+1 (888) 364-1189</a></p>
                                            <p className="text-gray-300"><span className="text-red-400">📍 Address:</span> 2261 Market Street, San Francisco, CA 94114, USA</p>
                                        </>
                                    )}
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
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Contact;