import React from "react";
import "./BaseBotPanel.css";

export default function BaseBotPanel({ botId, botConfig, activeTab, onTabChange, children }) {
    return (
        <div className="bot-panel-shell">
            <div className="bot-panel-header">
                <div>
                    <div className="bot-panel-eyebrow">{botId}</div>
                    <div className="bot-panel-title">{botConfig.name}</div>
                    <div className="bot-panel-desc">{botConfig.description}</div>
                </div>
                <div className="bot-panel-stats">
                    {botConfig.quickStats?.map((stat) => (
                        <div key={stat.label} className="bot-stat-card">
                            <span className="bot-stat-icon">{stat.icon}</span>
                            <div className="bot-stat-text">
                                <div className="bot-stat-value">{stat.value}</div>
                                <div className="bot-stat-label">{stat.label}</div>
                            </div>
                            {stat.trend ? (
                                <span className={`bot-stat-trend ${stat.trend.startsWith("-") ? "down" : "up"}`}>
                                    {stat.trend}
                                </span>
                            ) : null}
                        </div>
                    ))}
                </div>
            </div>

            <div className="bot-panel-tabs">
                {botConfig.tabs?.map((tab) => (
                    <button
                        key={tab.id}
                        className={`bot-tab ${activeTab === tab.id ? "active" : ""}`}
                        onClick={() => onTabChange?.(tab.id)}
                        type="button"
                    >
                        <span className="bot-tab-icon">{tab.icon}</span>
                        <span className="bot-tab-name">{tab.name}</span>
                    </button>
                ))}
            </div>

            <div className="bot-panel-body">{children}</div>

            <div className="bot-panel-footer">
                <div className="bot-status-pill">
                    <span className={`bot-status-dot ${botConfig.status || "inactive"}`} />
                    <span>{botConfig.status || "inactive"}</span>
                </div>
                <div className="bot-panel-meta">
                    <span>Version: {botConfig.version || "1.0.0"}</span>
                    <span>Updated: {botConfig.lastUpdated || "-"}</span>
                </div>
            </div>
        </div>
    );
}
