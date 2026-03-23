// frontend/src/components/Chatbot.jsx
import { useState, useRef, useEffect } from "react";
import { toast } from "react-toastify";

const Chatbot = () => {
    const [query, setQuery] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    // Sample initial messages
    const initialMessages = [
        {
            id: 1,
            text: "Hello! I'm your Gabani Transport Solutions (GTS) assistant. How can I help you with shipments, tracking, or logistics today?",
            sender: "bot",
            timestamp: new Date()
        }
    ];

    useEffect(() => {
        setMessages(initialMessages);
    }, []);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // Send user query to the backend chatbot endpoint
    const sendQuery = async () => {
        if (!query.trim()) {
            toast.warning("Please enter a message");
            return;
        }

        const userMessage = {
            id: Date.now(),
            text: query,
            sender: "user",
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setLoading(true);

        const currentQuery = query;
        setQuery("");

        try {
            const token = localStorage.getItem("access_token");
            const res = await fetch("http://127.0.0.1:8000/chatbot/consult", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ query: currentQuery }),
            });

            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }

            const data = await res.json();

            const botMessage = {
                id: Date.now() + 1,
                text: data.response || "I'm sorry, I couldn't process your request. Please try again.",
                sender: "bot",
                timestamp: new Date()
            };

            setMessages(prev => [...prev, botMessage]);

        } catch (err) {
            console.error("Chatbot error:", err);

            const errorMessage = {
                id: Date.now() + 1,
                text: "Sorry, I'm having trouble connecting to the service. Please try again later.",
                sender: "bot",
                timestamp: new Date(),
                isError: true
            };

            setMessages(prev => [...prev, errorMessage]);
            toast.error("Failed to connect to chatbot service");
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendQuery();
        }
    };

    const clearChat = () => {
        setMessages(initialMessages);
    };

    const quickQuestions = [
        "Track my shipment",
        "Shipping rates",
        "Document requirements",
        "Contact support",
        "Update shipment status"
    ];

    return (
        <div className="flex flex-col h-full bg-white rounded-lg shadow-lg border border-gray-200">
            {/* Chat Header */}
            <div className="bg-blue-600 text-white p-4 rounded-t-lg">
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                        <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
                        <div>
                            <h3 className="font-semibold text-lg">Gabani Transport Solutions (GTS) Assistant</h3>
                            <p className="text-blue-100 text-sm">AI-powered support</p>
                        </div>
                    </div>
                    <button
                        onClick={clearChat}
                        className="text-blue-200 hover:text-white transition duration-200 text-sm"
                    >
                        Clear Chat
                    </button>
                </div>
            </div>

            {/* Messages Container */}
            <div className="flex-1 p-4 overflow-y-auto bg-gray-50 max-h-96">
                <div className="space-y-4">
                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                        >
                            <div
                                className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl ${message.sender === "user"
                                    ? "bg-blue-600 text-white rounded-br-none"
                                    : message.isError
                                        ? "bg-red-100 text-red-800 border border-red-200"
                                        : "bg-white text-gray-800 border border-gray-200 rounded-bl-none"
                                    } shadow-sm`}
                            >
                                <p className="text-sm whitespace-pre-wrap">{message.text}</p>
                                <p className={`text-xs mt-1 ${message.sender === "user" ? "text-blue-200" : "text-gray-500"
                                    }`}>
                                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </p>
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="flex justify-start">
                            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-none px-4 py-2 shadow-sm">
                                <div className="flex space-x-2">
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0.4s" }}></div>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Quick Questions */}
            {messages.length <= 2 && (
                <div className="px-4 py-2 bg-gray-50 border-t">
                    <p className="text-xs text-gray-500 mb-2">Quick questions:</p>
                    <div className="flex flex-wrap gap-2">
                        {quickQuestions.map((question, index) => (
                            <button
                                key={index}
                                onClick={() => setQuery(question)}
                                className="text-xs bg-white border border-gray-300 text-gray-700 px-3 py-1 rounded-full hover:bg-gray-50 transition duration-200"
                            >
                                {question}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Input Area */}
            <div className="p-4 border-t border-gray-200">
                <div className="flex space-x-2">
                    <div className="flex-1">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Type your message... (Press Enter to send)"
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
                            disabled={loading}
                        />
                    </div>
                    <button
                        onClick={sendQuery}
                        disabled={loading || !query.trim()}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                        ) : (
                            "Send"
                        )}
                    </button>
                </div>
                <p className="text-xs text-gray-500 mt-2 text-center">
                    Ask about shipments, tracking, rates, documents, or logistics support
                </p>
            </div>
        </div>
    );
};

export default Chatbot;
