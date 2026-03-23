import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const LiveSupportChat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [sessionId, setSessionId] = useState(null);
    const [online, setOnline] = useState(true);
    const messagesEndRef = useRef(null);

    // Load previous conversation
    useEffect(() => {
        const savedSession = localStorage.getItem('support_session_id');
        if (savedSession) {
            setSessionId(savedSession);
            loadConversation(savedSession);
        }

        // Check service health
        checkServiceHealth();
    }, []);

    // Scroll to latest message
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const checkServiceHealth = async () => {
        try {
            const response = await axios.get('/api/v1/support/health');
            setOnline(response.data.status === 'online');
        } catch (error) {
            setOnline(false);
        }
    };

    const loadConversation = async (sid) => {
        try {
            const response = await axios.get(`/api/v1/support/conversation/${sid}`);
            setMessages(response.data.history);
        } catch (error) {
            console.error('Error loading conversation:', error);
        }
    };

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMessage = {
            id: Date.now(),
            text: input,
            sender: 'user',
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const response = await axios.post('/api/v1/support/chat', {
                message: input,
                session_id: sessionId
            });

            // Save session_id
            if (response.data.session_id && !sessionId) {
                setSessionId(response.data.session_id);
                localStorage.setItem('support_session_id', response.data.session_id);
            }

            const botMessage = {
                id: Date.now() + 1,
                text: response.data.response,
                sender: 'bot',
                timestamp: response.data.timestamp,
                intent: response.data.intent
            };

            setMessages(prev => [...prev, botMessage]);

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                id: Date.now() + 1,
                text: 'Sorry, I encountered an error. Please try again later.',
                sender: 'bot',
                timestamp: new Date().toISOString(),
                isError: true
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !loading) {
            sendMessage();
        }
    };

    const quickActions = [
        { label: "📊 System Health", message: "Show system health" },
        { label: "🐛 Recent Errors", message: "Any recent errors?" },
        { label: "🛡️ Security Status", message: "Security status" },
        { label: "🌤️ Weather", message: "Current weather" },
        { label: "💰 Finance", message: "Financial summary" },
        { label: "🚛 Fleet Status", message: "Fleet status" }
    ];

    if (!online) {
        return (
            <div className="bg-gray-900 text-white p-6 rounded-lg text-center">
                <div className="text-red-500 text-2xl mb-2">⚠️</div>
                <h3 className="text-lg font-semibold mb-2">Service Unavailable</h3>
                <p className="text-gray-400">Live Support is currently offline. Please try again later.</p>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full bg-gray-900 rounded-lg overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-white font-bold text-lg">🔧 AI Maintenance & Development Hub</h2>
                        <p className="text-blue-100 text-sm">Live Support • Real-time Monitoring</p>
                    </div>
                    <div className="flex items-center gap-2">
                        <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                        <span className="text-white text-sm">Online</span>
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-800 p-3 border-b border-gray-700">
                <div className="flex flex-wrap gap-2">
                    {quickActions.map((action, idx) => (
                        <button
                            key={idx}
                            onClick={() => {
                                setInput(action.message);
                                setTimeout(() => sendMessage(), 100);
                            }}
                            className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded-full text-sm text-gray-300 transition"
                        >
                            {action.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 && (
                    <div className="text-center text-gray-500 py-8">
                        <p className="text-4xl mb-2">🤖</p>
                        <p className="font-semibold">Hello! I'm your AI Maintenance Assistant.</p>
                        <p className="text-sm mt-2">Ask me about system health, errors, security, or any operational issues.</p>
                    </div>
                )}

                {messages.map((msg) => (
                    <div
                        key={msg.id}
                        className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                        <div
                            className={`max-w-[80%] rounded-lg p-3 ${msg.sender === 'user'
                                    ? 'bg-blue-600 text-white'
                                    : msg.isError
                                        ? 'bg-red-800 text-white'
                                        : 'bg-gray-800 text-gray-200'
                                }`}
                        >
                            {msg.sender === 'bot' && (
                                <div className="text-xs text-gray-400 mb-1">
                                    🤖 Assistant
                                </div>
                            )}
                            <div className="whitespace-pre-wrap">{msg.text}</div>
                            <div className="text-xs mt-1 opacity-70">
                                {new Date(msg.timestamp).toLocaleTimeString()}
                            </div>
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex justify-start">
                        <div className="bg-gray-800 rounded-lg p-3">
                            <div className="flex gap-1">
                                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></span>
                                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></span>
                                <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></span>
                            </div>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="bg-gray-800 p-4 border-t border-gray-700">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Ask me anything about system operations..."
                        className="flex-1 bg-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                        disabled={loading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={loading || !input.trim()}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition"
                    >
                        Send
                    </button>
                </div>
                <p className="text-xs text-gray-500 mt-2 text-center">
                    Powered by GTS AI • Real-time system monitoring • Secure
                </p>
            </div>
        </div>
    );
};

export default LiveSupportChat;