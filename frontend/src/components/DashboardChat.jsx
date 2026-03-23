import React, { useState, useEffect, useRef } from 'react';

const DashboardChat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [activeChannel, setActiveChannel] = useState('incidents');
    const [loading, setLoading] = useState(false);
    const [channels, setChannels] = useState({});
    const messagesEndRef = useRef(null);

    const channelConfig = [
        { id: 'general', name: '💬 General', icon: '💬' },
        { id: 'incidents', name: '🚨 Incidents', icon: '🚨' },
        { id: 'alerts', name: '⚠️ Alerts', icon: '⚠️' }
    ];

    useEffect(() => {
        loadChannels();
        loadMessages();
        const interval = setInterval(loadMessages, 10000); // Check every 10 seconds
        return () => clearInterval(interval);
    }, [activeChannel]);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const loadChannels = async () => {
        try {
            const response = await fetch('/api/v1/chat/channels');
            if (response.ok) {
                const data = await response.json();
                setChannels(data.channels);
            }
        } catch (error) {
            console.error('Error loading channels:', error);
        }
    };

    const loadMessages = async () => {
        try {
            const response = await fetch(`/api/v1/chat/${activeChannel}/messages?limit=50`);
            if (response.ok) {
                const data = await response.json();
                setMessages(data.messages);
            }
        } catch (error) {
            console.error('Error loading messages:', error);
        }
    };

    const sendMessage = async () => {
        if (!input.trim()) return;

        setLoading(true);
        try {
            const response = await fetch('/api/v1/chat/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    channel: activeChannel,
                    message: input.trim()
                })
            });

            if (response.ok) {
                setInput('');
                loadMessages();
                loadChannels(); // Update channel counts
            }
        } catch (error) {
            console.error('Error sending message:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const formatTime = (timestamp) => {
        return new Date(timestamp).toLocaleTimeString('ar-SA', {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="bg-gray-900 rounded-lg overflow-hidden h-96 flex flex-col border border-gray-700">
            {/* Header */}
            <div className="bg-gray-800 p-3 border-b border-gray-700">
                <div className="flex gap-2 mb-2">
                    {channelConfig.map(ch => (
                        <button
                            key={ch.id}
                            onClick={() => setActiveChannel(ch.id)}
                            className={`px-3 py-1 rounded-lg text-sm transition-colors ${activeChannel === ch.id
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                                }`}
                        >
                            {ch.name}
                            {channels[ch.id]?.unread_count > 0 && (
                                <span className="ml-1 bg-red-500 text-white text-xs px-1 rounded-full">
                                    {channels[ch.id].unread_count}
                                </span>
                            )}
                        </button>
                    ))}
                </div>
                <div className="text-xs text-gray-400">
                    {channels[activeChannel]?.message_count || 0} messages
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3">
                {messages.length === 0 ? (
                    <div className="text-center text-gray-500 text-sm py-8">
                        No messages in #{activeChannel} yet
                    </div>
                ) : (
                    messages.map(msg => (
                        <div
                            key={msg.id}
                            className={`flex ${msg.user === 'system' ? 'justify-center' : 'justify-start'}`}
                        >
                            {msg.user === 'system' ? (
                                <div className="text-xs text-gray-500 bg-gray-800 px-3 py-1 rounded-full">
                                    {msg.message}
                                </div>
                            ) : (
                                <div className="max-w-[80%] bg-gray-800 rounded-lg p-2">
                                    <div className="text-xs text-blue-400 mb-1">
                                        {msg.user}
                                        {msg.user === 'incident_bot' && ' 🤖'}
                                    </div>
                                    <div className="text-sm text-white whitespace-pre-wrap">
                                        {msg.message}
                                    </div>
                                    <div className="text-xs text-gray-500 mt-1">
                                        {formatTime(msg.timestamp)}
                                    </div>
                                </div>
                            )}
                        </div>
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-3 border-t border-gray-700">
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder={`Message #${activeChannel}...`}
                        className="flex-1 bg-gray-800 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500"
                        disabled={loading}
                    />
                    <button
                        onClick={sendMessage}
                        disabled={loading || !input.trim()}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-sm transition-colors"
                    >
                        {loading ? '...' : 'Send'}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default DashboardChat;