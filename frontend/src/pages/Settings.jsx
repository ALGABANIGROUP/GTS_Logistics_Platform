import React, { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";
import { API_BASE_URL } from "../config/env";

const Settings = () => {
  const [debugInfo, setDebugInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [apiBase] = useState(API_BASE_URL || "");
  const [tokenPreview, setTokenPreview] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      setTokenPreview(
        token.length > 20 ? `${token.slice(0, 20)}...` : token
      );
    } else {
      setTokenPreview("No token in localStorage.");
    }

    fetchDebug();
  }, []);

  const fetchDebug = async () => {
    setLoading(true);
    setError("");
    setDebugInfo(null);
    try {
      const res = await axiosClient.get("/api/v1/auth/debug");
      setDebugInfo(res.data);
    } catch (err) {
      console.error("Settings debug error:", err);
      setError("Failed to fetch auth debug information.");
    } finally {
      setLoading(false);
    }
  };

  const clearToken = () => {
    localStorage.removeItem("access_token");
    setTokenPreview("No token in localStorage.");
    setDebugInfo(null);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">System Settings</h1>
        <p className="text-slate-300">Configure your application preferences and debug information</p>
      </div>

      <div className="glass-card p-6 space-y-4">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-blue-400"></span>
          API & Authentication
        </h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
            <span className="text-slate-300 font-medium">API Base URL</span>
            <span className="text-white font-mono text-sm">{apiBase}</span>
          </div>
          <div className="flex justify-between items-center py-2 border-b border-slate-700/50">
            <span className="text-slate-300 font-medium">JWT Token Preview</span>
            <span className="text-slate-400 font-mono text-sm">{tokenPreview}</span>
          </div>
        </div>
        <div className="flex gap-3 mt-4">
          <button
            onClick={fetchDebug}
            className="glass-button"
            disabled={loading}
          >
            {loading ? "Checking..." : "Check Auth Debug"}
          </button>
          <button
            onClick={clearToken}
            className="glass-button text-red-300 border-red-400/30 hover:bg-red-500/20"
          >
            Clear Token
          </button>
        </div>
        {error && (
          <div className="mt-4 p-3 rounded-lg bg-red-500/10 border border-red-400/30">
            <p className="text-red-300 text-sm">{error}</p>
          </div>
        )}
      </div>

      <div className="glass-card p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-green-400"></span>
          Authentication Debug Information
        </h2>
        {loading && (
          <div className="flex items-center gap-3 text-slate-300">
            <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
            Loading debug information...
          </div>
        )}
        {!loading && !debugInfo && !error && (
          <p className="text-slate-400">
            No debug information loaded yet. Click "Check Auth Debug" to load authentication details.
          </p>
        )}
        {debugInfo && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-300">Debug Data:</span>
              <span className="text-xs text-slate-400">JSON Response</span>
            </div>
            <pre className="text-xs bg-slate-800/50 p-4 rounded-lg overflow-auto max-h-80 border border-slate-600/50 text-slate-200">
              {JSON.stringify(debugInfo, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <div className="glass-card p-6">
        <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-purple-400"></span>
          System Information
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-400">Frontend Version</span>
              <span className="text-white">v1.0.0-rc.1</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">React Version</span>
              <span className="text-white">18.x</span>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-400">Backend Status</span>
              <span className="text-green-400">Connected</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Database</span>
              <span className="text-green-400">PostgreSQL</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
