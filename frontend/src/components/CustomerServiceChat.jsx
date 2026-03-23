import React, { useEffect, useRef, useState } from "react";
import { RefreshCw, Send, Star } from "lucide-react";
import axiosClient from "../api/axiosClient";

const CustomerServiceChat = ({ userId }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [rating, setRating] = useState(0);
  const [hoverRating, setHoverRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    setConversationId(`conv_${userId}_${Date.now()}`);
  }, [userId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || !conversationId) return;

    const userMessage = { role: "user", content: trimmed, timestamp: new Date() };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await axiosClient.post("/api/v1/customer-service/chat", {
        message: trimmed,
        user_id: String(userId || "guest"),
        conversation_id: conversationId,
      });
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: response.data.response,
          intent: response.data.intent,
          sentiment: response.data.sentiment,
          timestamp: new Date(),
        },
      ]);
      setShowFeedback(true);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: "Sorry, I encountered an error. Please try again.",
          error: true,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async () => {
    if (!conversationId || rating < 1) return;
    try {
      await axiosClient.post("/api/v1/customer-service/feedback", {
        conversation_id: conversationId,
        rating,
        feedback: feedbackText || null,
      });
      setShowFeedback(false);
      setRating(0);
      setHoverRating(0);
      setFeedbackText("");
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: "Thank you for your feedback. It will be used to improve future responses.",
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "bot",
          content: "Feedback could not be saved right now.",
          error: true,
          timestamp: new Date(),
        },
      ]);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex h-[640px] flex-col overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl">
      <div className="border-b border-slate-700 bg-slate-800/70 p-4">
        <h2 className="text-lg font-semibold text-white">Customer Service Bot</h2>
        <p className="text-sm text-slate-400">Learning-enabled support chat</p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-4 text-sm text-slate-300">
            Hello. Ask about billing, shipments, portal access, or general support.
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={`${msg.role}-${index}`} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
                msg.role === "user"
                  ? "bg-sky-500 text-white"
                  : msg.error
                    ? "border border-red-500/40 bg-red-500/10 text-red-100"
                    : "border border-slate-700 bg-slate-800 text-slate-200"
              }`}
            >
              <p>{msg.content}</p>
              <p className="mt-2 text-xs opacity-60">
                {msg.timestamp?.toLocaleTimeString?.() || ""}
              </p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl border border-slate-700 bg-slate-800 p-3 text-slate-300">
              <RefreshCw className="h-4 w-4 animate-spin" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {showFeedback && (
        <div className="border-t border-slate-700 bg-slate-800/70 p-4">
          <p className="mb-2 text-sm text-slate-300">Rate the last response</p>
          <div className="mb-3 flex gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onMouseEnter={() => setHoverRating(star)}
                onMouseLeave={() => setHoverRating(0)}
                onClick={() => setRating(star)}
              >
                <Star
                  className={`h-6 w-6 ${
                    (hoverRating || rating) >= star ? "fill-yellow-400 text-yellow-400" : "text-slate-500"
                  }`}
                />
              </button>
            ))}
          </div>
          <textarea
            value={feedbackText}
            onChange={(event) => setFeedbackText(event.target.value)}
            rows={2}
            placeholder="Optional feedback"
            className="mb-3 w-full rounded-lg border border-slate-700 bg-slate-900 p-3 text-sm text-white outline-none focus:border-sky-500"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleFeedback}
              className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-sky-400"
            >
              Submit Feedback
            </button>
            <button
              type="button"
              onClick={() => setShowFeedback(false)}
              className="rounded-lg bg-slate-700 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-600"
            >
              Skip
            </button>
          </div>
        </div>
      )}

      <div className="border-t border-slate-700 bg-slate-800/70 p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
            placeholder="Type your message..."
            className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-white outline-none focus:border-sky-500 disabled:opacity-60"
          />
          <button
            type="button"
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="rounded-lg bg-sky-500 px-4 py-2 text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default CustomerServiceChat;
