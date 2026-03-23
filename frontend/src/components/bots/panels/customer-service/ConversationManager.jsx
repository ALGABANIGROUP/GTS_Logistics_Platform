// src/components/bots/panels/customer-service/ConversationManager.jsx
import React, { useState, useEffect, useRef } from 'react';
import { customerServiceAPI } from '../../../../services/customerService';
import './ConversationManager.css';

const ConversationManager = ({ onNotification }) => {
    const [conversations, setConversations] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [filters, setFilters] = useState({ status: 'all', channel: 'all' });
    const [showTemplates, setShowTemplates] = useState(false);
    const messagesEndRef = useRef(null);

    const quickTemplates = [
        'Thank you for your message, I will help you shortly.',
        'I understand your concern. Let me check this for you.',
        'We appreciate your patience. Here is the information you need.',
        'Your issue has been escalated to our senior team.',
        'Thank you for choosing our service. Is there anything else?'
    ];

    useEffect(() => {
        loadConversations();
    }, [filters]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const loadConversations = async () => {
        setLoading(true);
        try {
            const data = await customerServiceAPI.getConversations(filters);
            setConversations(data);
        } catch (error) {
            console.error('Failed to load conversations:', error);
        } finally {
            setLoading(false);
        }
    };

    const selectConversation = async (conv) => {
        setSelectedConversation(conv);
        try {
            const msgs = await customerServiceAPI.getConversationMessages(conv.id);
            setMessages(msgs);
        } catch (error) {
            console.error('Failed to load messages:', error);
        }
    };

    const sendMessage = async () => {
        if (!newMessage.trim()) return;

        try {
            const msg = {
                id: Date.now(),
                sender: 'agent',
                text: newMessage,
                timestamp: new Date().toLocaleTimeString(),
                read: true
            };

            setMessages([...messages, msg]);
            setNewMessage('');

            // AI Response simulation
            setTimeout(() => {
                const aiReply = {
                    id: Date.now() + 1,
                    sender: 'customer',
                    text: 'Thank you for your help. This was exactly what I needed!',
                    timestamp: new Date().toLocaleTimeString(),
                    read: true
                };
                setMessages(prev => [...prev, aiReply]);
            }, 1000);
        } catch (error) {
            console.error('Failed to send message:', error);
        }
    };

    const generateAIResponse = async () => {
        if (!selectedConversation) return;

        try {
            const response = await customerServiceAPI.generateAIResponse(
                selectedConversation.id,
                messages
            );

            setNewMessage(response.suggestion || '');
            onNotification('AI response generated', '');
        } catch (error) {
            console.error('Failed to generate AI response:', error);
        }
    };

    const markAsRead = async () => {
        if (!selectedConversation) return;
        try {
            await customerServiceAPI.markConversationAsRead(selectedConversation.id);
        } catch (error) {
            console.error('Failed to mark as read:', error);
        }
    };

    return (
        <div className="conversation-manager">
            {/* Sidebar */}
            <div className="conversations-sidebar">
                <div className="sidebar-header">
                    <h3>Conversations</h3>
                    <button className="filter-btn" onClick={() => setShowTemplates(!showTemplates)}>
                         Filters
                    </button>
                </div>

                <div className="filters">
                    <select
                        value={filters.status}
                        onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                        className="filter-select"
                    >
                        <option value="all">All Status</option>
                        <option value="active">Active</option>
                        <option value="pending">Pending</option>
                        <option value="resolved">Resolved</option>
                        <option value="escalated">Escalated</option>
                    </select>

                    <select
                        value={filters.channel}
                        onChange={(e) => setFilters({ ...filters, channel: e.target.value })}
                        className="filter-select"
                    >
                        <option value="all">All Channels</option>
                        <option value="whatsapp">WhatsApp</option>
                        <option value="sms">SMS</option>
                        <option value="email">Email</option>
                        <option value="webchat">Web Chat</option>
                        <option value="facebook">Facebook</option>
                    </select>
                </div>

                <div className="conversations-list">
                    {conversations.length > 0 ? (
                        conversations.map((conv) => (
                            <div
                                key={conv.id}
                                className={`conversation-item ${selectedConversation?.id === conv.id ? 'active' : ''} ${conv.unread ? 'unread' : ''}`}
                                onClick={() => selectConversation(conv)}
                            >
                                <div className="conv-avatar">{conv.customerName?.charAt(0) || 'C'}</div>
                                <div className="conv-content">
                                    <div className="conv-header">
                                        <span className="conv-name">{conv.customerName}</span>
                                        <span className="conv-time">{conv.lastMessageTime}</span>
                                    </div>
                                    <div className="conv-preview">{conv.lastMessage}</div>
                                    <div className="conv-meta">
                                        <span className="channel-badge">{conv.channel}</span>
                                        <span className={`status-badge ${conv.status}`}>{conv.status}</span>
                                    </div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="empty-state">No conversations found</div>
                    )}
                </div>
            </div>

            {/* Main Chat Area */}
            <div className="conversation-main">
                {selectedConversation ? (
                    <>
                        {/* Header */}
                        <div className="chat-header">
                            <div className="chat-customer-info">
                                <div className="customer-avatar">{selectedConversation.customerName?.charAt(0)}</div>
                                <div className="customer-details">
                                    <h3>{selectedConversation.customerName}</h3>
                                    <span className="channel-indicator"> {selectedConversation.channel}</span>
                                </div>
                            </div>
                            <div className="chat-actions">
                                <button className="action-btn" title="Customer Info"></button>
                                <button className="action-btn" title="Call"></button>
                                <button className="action-btn" title="More"></button>
                            </div>
                        </div>

                        {/* Messages */}
                        <div className="messages-container">
                            {messages.length > 0 ? (
                                messages.map((msg) => (
                                    <div key={msg.id} className={`message ${msg.sender}`}>
                                        <div className="message-bubble">
                                            <p>{msg.text}</p>
                                            <span className="message-time">{msg.timestamp}</span>
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="empty-messages">No messages yet. Start the conversation!</div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="chat-footer">
                            <div className="message-input-area">
                                <div className="input-wrapper">
                                    <textarea
                                        value={newMessage}
                                        onChange={(e) => setNewMessage(e.target.value)}
                                        onKeyPress={(e) => {
                                            if (e.key === 'Enter' && !e.shiftKey) {
                                                e.preventDefault();
                                                sendMessage();
                                            }
                                        }}
                                        placeholder="Type your message... (Shift+Enter for new line)"
                                        className="message-input"
                                    />
                                    <button className="attach-btn" title="Attach File"></button>
                                </div>

                                <div className="input-actions">
                                    <button
                                        className="ai-reply-btn"
                                        onClick={generateAIResponse}
                                        title="Generate AI Response"
                                    >
                                         AI Reply
                                    </button>
                                    <button
                                        className="templates-btn"
                                        onClick={() => setShowTemplates(!showTemplates)}
                                        title="Quick Templates"
                                    >
                                         Templates
                                    </button>
                                    <button
                                        className="send-btn"
                                        onClick={sendMessage}
                                        disabled={!newMessage.trim()}
                                    >
                                         Send
                                    </button>
                                </div>

                                {showTemplates && (
                                    <div className="quick-templates">
                                        <h4>Quick Responses</h4>
                                        <div className="templates-grid">
                                            {quickTemplates.map((template, idx) => (
                                                <button
                                                    key={idx}
                                                    className="template-btn"
                                                    onClick={() => {
                                                        setNewMessage(template);
                                                        setShowTemplates(false);
                                                    }}
                                                >
                                                    {template}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="no-conversation-selected">
                        <div className="empty-state">
                            <span className="icon"></span>
                            <h3>Select a conversation</h3>
                            <p>Choose a conversation from the list to start messaging</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ConversationManager;
