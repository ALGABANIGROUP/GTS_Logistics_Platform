import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ChatSupportButton = () => {
    const navigate = useNavigate();
    const [isOpen, setIsOpen] = useState(false);
    const supportPhoneLabel = '+1 (778) 651-8297';
    const supportPhoneHref = 'tel:+17786518297';

    const openSupportRoute = (route) => {
        setIsOpen(false);
        navigate(route);
    };

    return (
        <>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="fixed bottom-6 right-6 w-14 h-14 bg-red-600 text-white rounded-full shadow-lg hover:bg-red-700 transition flex items-center justify-center z-40"
            >
                💬
            </button>

            {isOpen && (
                <div className="fixed bottom-20 right-6 w-80 bg-black/90 backdrop-blur-sm rounded-lg shadow-xl border border-white/20 z-50">
                    <div className="p-4">
                        <div className="flex justify-between items-center mb-3">
                            <h3 className="text-white font-semibold">Live Support</h3>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="text-gray-400 hover:text-white"
                            >
                                ✕
                            </button>
                        </div>
                        <p className="text-gray-300 text-sm mb-3">Hi! How can we help you today?</p>
                        <div className="space-y-2">
                            <button onClick={() => openSupportRoute('/support?topic=account')} className="w-full text-left p-2 bg-white/10 rounded text-white text-sm hover:bg-white/20 transition">
                                Account Issues
                            </button>
                            <button onClick={() => openSupportRoute('/find-loads')} className="w-full text-left p-2 bg-white/10 rounded text-white text-sm hover:bg-white/20 transition">
                                Load Board Help
                            </button>
                            <button onClick={() => openSupportRoute('/contact?inquiry=billing')} className="w-full text-left p-2 bg-white/10 rounded text-white text-sm hover:bg-white/20 transition">
                                Billing Questions
                            </button>
                        </div>
                        <div className="mt-3 pt-3 border-t border-white/20">
                            <p className="text-gray-400 text-xs">
                                Or call us: <a href={supportPhoneHref} className="hover:text-white">{supportPhoneLabel}</a>
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
};

export default ChatSupportButton;
