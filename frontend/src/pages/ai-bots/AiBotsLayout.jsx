import React from "react";
import { NavLink, Outlet } from "react-router-dom";
import "./AiBotsLayout.css";

const navItems = [
  { label: "Overview", to: "/ai-bots" },
  { label: "Bot Operating System", to: "/ai-bots/bot-os" },
];

const AiBotsLayout = () => {
  return (
    <div className="ai-bots-layout">
      <aside className="ai-bots-panel glass-panel">
        <h3>AI Bots</h3>
        <nav>
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/ai-bots"}
              className={({ isActive }) =>
                `ai-bots-link ${isActive ? "active" : ""}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="ai-bots-content">
        <Outlet />
      </main>
    </div>
  );
};

export default AiBotsLayout;
