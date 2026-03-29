import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Code, Wrench, Terminal } from 'lucide-react';
import { API_BASE_URL } from '../../../../config/env';

const API_ROOT = String(API_BASE_URL || '').replace(/\/+$/, '');

const DevMaintenanceLiveChat = () => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            type: 'bot',
            text: '🔧 **AI Maintenance & Development Hub**\n\nHello! I\'m your advanced AI assistant specialized in system maintenance and development.\n\n**My Intelligent Capabilities:**\n✓ Real-time system health checks\n✓ Error analysis & performance troubleshooting\n✓ Automated task management\n✓ Live resource monitoring\n✓ Smart recommendations\n\nHow can I help you today?',
            timestamp: new Date()
        }
    ]);
    const [inputMessage, setInputMessage] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async () => {
        if (!inputMessage.trim()) return;

        const userMessage = {
            id: Date.now(),
            type: 'user',
            text: inputMessage,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsTyping(true);

        try {
            // Call real AI API with full URL
            const endpoint = `${API_ROOT}/api/v1/ai/maintenance/chat/ask`;

            console.log('📤 Sending AI request to:', endpoint);
            console.log('📝 Message:', inputMessage);

            const aiResponse = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: inputMessage,
                    context: {}
                })
            });

            if (aiResponse.ok) {
                const data = await aiResponse.json();
                console.log('✅ AI Response received:', data);
                const botResponse = {
                    id: Date.now() + 1,
                    type: 'bot',
                    text: data.response,
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, botResponse]);
            } else {
                console.error('❌ AI API returned status:', aiResponse.status, aiResponse.statusText);
                const errorText = await aiResponse.text();
                console.error('Response body:', errorText);
                const botResponse = {
                    id: Date.now() + 1,
                    type: 'bot',
                    text: `⚠️ AI connection error (${aiResponse.status}). Please try again later.`,
                    timestamp: new Date()
                };
                setMessages(prev => [...prev, botResponse]);
            }
        } catch (error) {
            console.error('❌ Chat error details:', {
                name: error.name,
                message: error.message,
                stack: error.stack
            });
            const botResponse = {
                id: Date.now() + 1,
                type: 'bot',
                text: '❌ Sorry, a connection error occurred. Please try again shortly.',
                timestamp: new Date()
            };
            setMessages(prev => [...prev, botResponse]);
        } finally {
            setIsTyping(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const quickActions = [
        { label: 'Report Bug', icon: '🐛', message: 'I found a bug' },
        { label: 'Feature Request', icon: '💡', message: 'I have a feature request' },
        { label: 'System Status', icon: '📊', message: 'Show system status' },
        { label: 'API Docs', icon: '🔌', message: 'Show API documentation' }
    ];

    const handleQuickAction = (message) => {
        setInputMessage(message);
    };

    return (
        <div className="dev-maintenance-live-chat" style={{ padding: '24px' }}>
            {/* Header Banner */}
            <div style={{
                background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.2) 0%, rgba(59, 130, 246, 0.2) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.4)',
                borderRadius: '16px',
                padding: '20px',
                marginBottom: '24px',
                backdropFilter: 'blur(20px)'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{
                        width: '56px',
                        height: '56px',
                        background: 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)',
                        borderRadius: '16px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <Wrench size={28} color="white" />
                    </div>
                    <div style={{ flex: 1 }}>
                        <h2 style={{ color: 'white', fontSize: '24px', fontWeight: 'bold', margin: '0 0 4px 0' }}>
                            Dev & Maintenance Bot
                        </h2>
                        <p style={{ color: '#94a3b8', margin: 0 }}>
                            Technical Support • Bug Tracking • System Monitoring
                        </p>
                    </div>
                    <div style={{
                        background: 'rgba(34, 197, 94, 0.2)',
                        border: '1px solid rgba(34, 197, 94, 0.4)',
                        borderRadius: '12px',
                        padding: '8px 16px',
                        color: '#22c55e',
                        fontSize: '14px',
                        fontWeight: '600'
                    }}>
                        🟢 Online
                    </div>
                </div>
            </div>

            {/* Quick Actions */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                gap: '12px',
                marginBottom: '24px'
            }}>
                {quickActions.map((action, i) => (
                    <button
                        key={i}
                        onClick={() => handleQuickAction(action.message)}
                        style={{
                            background: 'rgba(30, 41, 59, 0.6)',
                            border: '1px solid rgba(148, 163, 184, 0.4)',
                            borderRadius: '12px',
                            padding: '12px',
                            color: 'white',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            gap: '4px'
                        }}
                        onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(59, 130, 246, 0.2)';
                            e.currentTarget.style.borderColor = 'rgba(59, 130, 246, 0.6)';
                        }}
                        onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(30, 41, 59, 0.6)';
                            e.currentTarget.style.borderColor = 'rgba(148, 163, 184, 0.4)';
                        }}
                    >
                        <span style={{ fontSize: '24px' }}>{action.icon}</span>
                        <span style={{ fontSize: '12px', fontWeight: '600' }}>{action.label}</span>
                    </button>
                ))}
            </div>

            {/* Chat Container */}
            <div style={{
                background: 'rgba(15, 23, 42, 0.6)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(148, 163, 184, 0.6)',
                borderRadius: '16px',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
                overflow: 'hidden'
            }}>
                {/* Messages Area */}
                <div style={{
                    height: '450px',
                    overflowY: 'auto',
                    padding: '24px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '16px'
                }}>
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            style={{
                                display: 'flex',
                                gap: '12px',
                                flexDirection: message.type === 'user' ? 'row-reverse' : 'row'
                            }}
                        >
                            <div style={{
                                width: '36px',
                                height: '36px',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                flexShrink: 0,
                                background: message.type === 'bot'
                                    ? 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)'
                                    : 'linear-gradient(135deg, #10b981 0%, #059669 100%)'
                            }}>
                                {message.type === 'bot' ? (
                                    <Wrench size={20} color="white" />
                                ) : (
                                    <User size={20} color="white" />
                                )}
                            </div>
                            <div style={{
                                maxWidth: '70%',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: message.type === 'user' ? 'flex-end' : 'flex-start'
                            }}>
                                <div style={{
                                    borderRadius: '16px',
                                    padding: '12px 16px',
                                    background: message.type === 'bot'
                                        ? 'rgba(30, 41, 59, 0.8)'
                                        : 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)',
                                    color: 'white'
                                }}>
                                    <p style={{ whiteSpace: 'pre-line', margin: 0, lineHeight: '1.6' }}>{message.text}</p>
                                </div>
                                <span style={{
                                    fontSize: '12px',
                                    color: '#94a3b8',
                                    marginTop: '4px',
                                    paddingLeft: '8px',
                                    paddingRight: '8px'
                                }}>
                                    {message.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                                </span>
                            </div>
                        </div>
                    ))}

                    {isTyping && (
                        <div style={{ display: 'flex', gap: '12px' }}>
                            <div style={{
                                width: '36px',
                                height: '36px',
                                borderRadius: '50%',
                                background: 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}>
                                <Wrench size={20} color="white" />
                            </div>
                            <div style={{
                                background: 'rgba(30, 41, 59, 0.8)',
                                borderRadius: '16px',
                                padding: '12px 16px'
                            }}>
                                <div style={{ display: 'flex', gap: '4px' }}>
                                    {[0, 150, 300].map((delay, i) => (
                                        <div
                                            key={i}
                                            style={{
                                                width: '8px',
                                                height: '8px',
                                                background: '#94a3b8',
                                                borderRadius: '50%',
                                                animation: 'bounce 1s infinite',
                                                animationDelay: `${delay}ms`
                                            }}
                                        />
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                {/* Input Area */}
                <div style={{
                    borderTop: '1px solid rgba(148, 163, 184, 0.6)',
                    background: 'rgba(15, 23, 42, 0.8)',
                    padding: '16px'
                }}>
                    <div style={{ display: 'flex', gap: '12px' }}>
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Describe your technical issue or request..."
                            style={{
                                flex: 1,
                                background: 'rgba(30, 41, 59, 0.6)',
                                border: '1px solid rgba(148, 163, 184, 0.6)',
                                borderRadius: '12px',
                                padding: '12px 16px',
                                color: 'white',
                                outline: 'none',
                                fontSize: '14px'
                            }}
                        />
                        <button
                            onClick={handleSendMessage}
                            disabled={!inputMessage.trim()}
                            style={{
                                background: inputMessage.trim()
                                    ? 'linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%)'
                                    : 'linear-gradient(to right, #334155, #334155)',
                                color: 'white',
                                padding: '12px 24px',
                                borderRadius: '12px',
                                fontWeight: '600',
                                border: 'none',
                                cursor: inputMessage.trim() ? 'pointer' : 'not-allowed',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                boxShadow: inputMessage.trim() ? '0 10px 15px -3px rgba(139, 92, 246, 0.4)' : 'none',
                                transition: 'all 0.2s'
                            }}
                        >
                            <Send size={20} />
                            Send
                        </button>
                    </div>
                    <p style={{
                        fontSize: '12px',
                        color: '#94a3b8',
                        marginTop: '8px',
                        textAlign: 'center',
                        margin: '8px 0 0 0'
                    }}>
                        Press Enter to send • Available 24/7 for technical support
                    </p>
                </div>
            </div>

            {/* Support Info Cards */}
            <div style={{
                marginTop: '24px',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '16px'
            }}>
                {[
                    { icon: <Code size={24} />, title: 'Development Support', subtitle: 'Bug tracking & features', color: '#8b5cf6' },
                    { icon: <Terminal size={24} />, title: 'System Monitoring', subtitle: 'Real-time status', color: '#3b82f6' },
                    { icon: <Wrench size={24} />, title: 'Maintenance', subtitle: 'Proactive support', color: '#06b6d4' }
                ].map((item, i) => (
                    <div
                        key={i}
                        style={{
                            background: 'rgba(15, 23, 42, 0.4)',
                            backdropFilter: 'blur(20px)',
                            border: '1px solid rgba(148, 163, 184, 0.4)',
                            borderRadius: '12px',
                            padding: '16px',
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            textAlign: 'center',
                            gap: '8px'
                        }}
                    >
                        <div style={{ color: item.color }}>{item.icon}</div>
                        <div style={{ color: 'white', fontWeight: '600', fontSize: '14px' }}>{item.title}</div>
                        <div style={{ color: '#94a3b8', fontSize: '12px' }}>{item.subtitle}</div>
                    </div>
                ))}
            </div>

            <style>{`
        @keyframes bounce {
          0%, 80%, 100% { transform: translateY(0); }
          40% { transform: translateY(-8px); }
        }
      `}</style>
        </div>
    );
};

export default DevMaintenanceLiveChat;
