import React, { useState } from 'react';
import { Mail, CheckCircle, AlertCircle, X } from 'lucide-react';

const NewsletterSignup = () => {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState(null); // 'success', 'error'
    const [message, setMessage] = useState('');
    const [showModal, setShowModal] = useState(false);

    const validateEmail = (email) => {
        return /^[^\s@]+@([^\s@]+\.)+[^\s@]+$/.test(email);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!email) {
            setStatus('error');
            setMessage('Please enter your email address');
            return;
        }

        if (!validateEmail(email)) {
            setStatus('error');
            setMessage('Please enter a valid email address');
            return;
        }

        setLoading(true);
        setStatus(null);
        setMessage('');

        try {
            const response = await fetch('/api/newsletter/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    source: 'footer',
                    consent: true,
                    subscribed_at: new Date().toISOString()
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setStatus('success');
                setMessage(data.message || 'Thank you for subscribing! Check your inbox for confirmation.');
                setEmail('');
                setShowModal(true);
                // Auto-hide modal after 5 seconds
                setTimeout(() => setShowModal(false), 5000);
            } else {
                setStatus('error');
                setMessage(data.message || 'Something went wrong. Please try again.');
            }
        } catch (error) {
            console.error('Newsletter signup error:', error);
            setStatus('error');
            setMessage('Network error. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative">
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
                <div className="flex-1 relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        placeholder="Enter your email"
                        className="w-full pl-10 pr-4 py-3 bg-black/50 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-red-500 transition"
                        disabled={loading}
                    />
                </div>
                <button
                    type="submit"
                    disabled={loading}
                    className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50 whitespace-nowrap"
                >
                    {loading ? (
                        <span className="flex items-center gap-2">
                            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                            Subscribing...
                        </span>
                    ) : (
                        'Subscribe'
                    )}
                </button>
            </form>

            {status === 'error' && message && (
                <div className="mt-3 flex items-center gap-2 text-red-400 text-sm">
                    <AlertCircle className="w-4 h-4" />
                    <span>{message}</span>
                </div>
            )}

            {/* Success Modal */}
            {showModal && (
                <div className="fixed bottom-6 right-6 z-50 animate-slide-up">
                    <div className="bg-green-600 text-white rounded-lg shadow-xl p-4 flex items-center gap-3 max-w-md">
                        <CheckCircle className="w-5 h-5 flex-shrink-0" />
                        <p className="text-sm">{message || 'Thank you for subscribing!'}</p>
                        <button
                            onClick={() => setShowModal(false)}
                            className="ml-auto hover:bg-green-500 rounded-full p-1 transition"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}

            <style jsx>{`
        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-slide-up {
          animation: slide-up 0.3s ease-out;
        }
      `}</style>
        </div>
    );
};

export default NewsletterSignup;