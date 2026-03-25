import React, { useState } from 'react';

const CookieConsent = () => {
    const [show, setShow] = useState(true);

    if (!show) return null;

    return (
        <div className="fixed bottom-0 left-0 right-0 bg-black/90 backdrop-blur-sm border-t border-white/20 p-4 z-50">
            <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
                <p className="text-gray-300 text-sm">
                    We use cookies to enhance your experience. By continuing to visit this site you agree to our use of cookies.
                    <a href="/privacy" className="text-red-400 hover:underline ml-2">Learn more</a>
                </p>
                <div className="flex gap-3">
                    <button
                        onClick={() => setShow(false)}
                        className="px-4 py-2 border border-white/30 text-white rounded hover:bg-white/10 transition text-sm"
                    >
                        Decline
                    </button>
                    <button
                        onClick={() => setShow(false)}
                        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm"
                    >
                        Accept All
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CookieConsent;