import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

const LiveChat = () => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            type: 'bot',
            text: 'Hello! I\'m the AI Customer Service Bot 🤖 How can I help you today?',
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

        setTimeout(() => {
            const botResponse = {
                id: Date.now() + 1,
                type: 'bot',
                text: generateBotResponse(inputMessage),
                timestamp: new Date()
            };
            setMessages(prev => [...prev, botResponse]);
            setIsTyping(false);
        }, 1500);
    };

    const generateBotResponse = (userInput) => {
        const input = userInput.toLowerCase();

        if (input.includes('help') || input.includes('assist')) {
            return 'Sure! I can help you with:\n✅ Shipment information\n✅ Order tracking\n✅ Technical support\n✅ Pricing and services\n\nWhat do you need help with?';
        } else if (input.includes('shipment') || input.includes('tracking') || input.includes('track')) {
            return 'To track your shipment, please provide me with the shipment number and I\'ll help you find its current location and estimated delivery time.';
        } else if (input.includes('price') || input.includes('cost') || input.includes('quote')) {
            return 'To get a custom quote, please specify:\n📍 Origin point\n📍 Destination point\n📦 Cargo type\n⚖️ Approximate weight';
        } else if (input.includes('contact') || input.includes('email') || input.includes('reach')) {
            return 'You can contact us via:\n📧 support@gabanilogistics.com\n🏢 operations@gabanilogistics.com\n⏰ Available Monday - Friday, 9 AM - 6 PM PST';
        } else if (input.includes('thanks') || input.includes('thank')) {
            return 'You\'re welcome! Happy to help 😊 Do you need any other assistance?';
        } else {
            return 'Thank you for your message. Our support team will review your request and respond as soon as possible. You can also contact us directly at: support@gabanilogistics.com';
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="live-chat-container" style={{ padding: '24px' }}>
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
                    height: '500px',
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
                                width: '32px',
                                height: '32px',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                flexShrink: 0,
                                background: message.type === 'bot'
                                    ? 'linear-gradient(to bottom right, #3b82f6, #06b6d4)'
                                    : 'linear-gradient(to bottom right, #10b981, #059669)'
                            }}>
                                {message.type === 'bot' ? (
                                    <Bot size={20} color="white" />
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
                                        : 'linear-gradient(to right, #2563eb, #0891b2)',
                                    color: 'white'
                                }}>
                                    <p style={{ whiteSpace: 'pre-line', margin: 0 }}>{message.text}</p>
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
                                width: '32px',
                                height: '32px',
                                borderRadius: '50%',
                                background: 'linear-gradient(to bottom right, #3b82f6, #06b6d4)',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}>
                                <Bot size={20} color="white" />
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
                            placeholder="Type your message here..."
                            style={{
                                flex: 1,
                                background: 'rgba(30, 41, 59, 0.6)',
                                border: '1px solid rgba(148, 163, 184, 0.6)',
                                borderRadius: '12px',
                                padding: '12px 16px',
                                color: 'white',
                                outline: 'none'
                            }}
                        />
                        <button
                            onClick={handleSendMessage}
                            disabled={!inputMessage.trim()}
                            style={{
                                background: inputMessage.trim()
                                    ? 'linear-gradient(to right, #2563eb, #0891b2)'
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
                                boxShadow: inputMessage.trim() ? '0 10px 15px -3px rgba(0, 0, 0, 0.4)' : 'none',
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
                        Press Enter to send
                    </p>
                </div>
            </div>

            {/* Quick Info */}
            <div style={{
                marginTop: '24px',
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '16px'
            }}>
                {[
                    { icon: '⚡', title: 'Instant Response', subtitle: 'Lightning fast support' },
                    { icon: '🤖', title: 'AI-Powered', subtitle: 'Smart automation' },
                    { icon: '🌐', title: '24/7 Available', subtitle: 'Always here to help' }
                ].map((item, i) => (
                    <div
                        key={i}
                        style={{
                            background: 'rgba(15, 23, 42, 0.4)',
                            backdropFilter: 'blur(20px)',
                            border: '1px solid rgba(148, 163, 184, 0.6)',
                            borderRadius: '12px',
                            padding: '16px',
                            textAlign: 'center'
                        }}
                    >
                        <div style={{ fontSize: '32px', marginBottom: '8px' }}>{item.icon}</div>
                        <div style={{ color: 'white', fontWeight: '600', marginBottom: '4px' }}>{item.title}</div>
                        <div style={{ color: '#94a3b8', fontSize: '14px' }}>{item.subtitle}</div>
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

export default LiveChat;
