import { useEffect, useState } from "react";
import { API_BASE_URL } from "../config/env";

const API_ROOT = String(API_BASE_URL || "").replace(/\/+$/, "");

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${API_ROOT}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) throw new Error("Invalid credentials");

      const data = await response.json();
      localStorage.setItem("token", data.access_token);
      alert("✅ Login successful!");
      window.location.href = "/dashboard";
    } catch (err) {
      alert("❌ Login failed: " + err.message);
    }
  };

  useEffect(() => {
    document.body.classList.add('logout');
    return () => document.body.classList.remove('logout');
  }, []);
  return (
    <div className="min-h-screen bg-blue-900 text-white flex items-center justify-center">
      <form onSubmit={handleLogin} className="bg-white text-blue-900 p-10 rounded-xl shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold mb-4 text-center">Login</h1>
        <input
          type="email"
          placeholder="Email"
          className="block w-full border p-2 mb-4"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          className="block w-full border p-2 mb-4"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          type="submit"
          className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded"
        >
          Login
        </button>
      </form>
    </div>
  );
};

export default Login;
