import React, { useEffect, useState } from 'react';

const CookieConsent = () => {
    const [show, setShow] = useState(false);

    useEffect(() => {
        try {
            const savedConsent = window.localStorage.getItem('cookie_consent');
            if (savedConsent === 'accepted') {
                window.__GTS_UPDATE_GOOGLE_CONSENT__?.('granted');
                setShow(false);
                return;
            }
            if (savedConsent === 'declined') {
                window.__GTS_UPDATE_GOOGLE_CONSENT__?.('denied');
                setShow(false);
                return;
            }
        } catch {
            // Ignore storage errors and show the banner.
        }

        setShow(true);
    }, []);

    const handleConsent = (choice) => {
        try {
            window.localStorage.setItem('cookie_consent', choice);
        } catch {
            // Ignore storage errors and still honor the in-session choice.
        }

        window.__GTS_UPDATE_GOOGLE_CONSENT__?.(choice === 'accepted' ? 'granted' : 'denied');
        setShow(false);
    };

    if (!show) return null;

    return (
        <div className="fixed bottom-0 left-0 right-0 z-50 border-t border-white/20 bg-black/90 p-4 backdrop-blur-sm">
            <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
                <p className="text-gray-300 text-sm">
                    We use cookies to improve site performance, measure traffic, and support essential website functionality.
                    <a href="/privacy" className="ml-2 text-red-400 hover:underline">Learn more</a>
                </p>
                <div className="flex gap-3">
                    <button
                        onClick={() => handleConsent('declined')}
                        className="px-4 py-2 border border-white/30 text-white rounded hover:bg-white/10 transition text-sm"
                    >
                        Decline
                    </button>
                    <button
                        onClick={() => handleConsent('accepted')}
                        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm"
                    >
                        Accept
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CookieConsent;
