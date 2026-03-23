import React from "react";
import { useNavigate } from "react-router-dom";

const HomepageNavbar = () => {
  const navigate = useNavigate();

  return (
    <nav className="w-full bg-black bg-opacity-40 backdrop-blur-md 
                    text-white h-16 flex items-center justify-between px-6 shadow">
      {/* Left – Logo / Title */}
      <h1 className="text-xl font-semibold">Gabani Transport Solutions (GTS) Platform</h1>

      {/* Right – Auth Buttons */}
      <div className="flex items-center space-x-4">
        <button
          onClick={() => navigate("/login")}
          className="px-4 py-1.5 rounded bg-white text-blue-600 hover:bg-gray-100 transition"
        >
          Login
        </button>
      </div>
    </nav>
  );
};

export default HomepageNavbar;
