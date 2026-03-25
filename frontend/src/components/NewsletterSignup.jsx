import React, { useState } from 'react';

const NewsletterSignup = () => {
    const [email, setEmail] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        // Handle newsletter signup
        alert('Thank you for subscribing!');
        setEmail('');
    };

    return (
        <div className="bg-black/40 backdrop-blur-sm rounded-xl p-4">
            <h3 className="text-white font-semibold text-sm mb-3">📧 Stay Updated</h3>
            <p className="text-gray-300 text-xs mb-3">Get the latest market insights and platform updates.</p>
            <form onSubmit={handleSubmit} className="space-y-2">
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="Enter your email"
                    className="w-full px-3 py-2 bg-black/50 border border-white/20 rounded text-white placeholder-gray-400 text-xs"
                    required
                />
                <button
                    type="submit"
                    className="w-full py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-xs"
                >
                    Subscribe
                </button>
            </form>
            <p className="text-gray-500 text-[10px] mt-2">No spam, unsubscribe anytime.</p>
        </div>
    );
};

export default NewsletterSignup;