import React from "react";
import { Plus } from "lucide-react";
import "./QuickActionCard.css";

export default function QuickActionCard({
    title = "Add New Shipment",
    subtitle = "Start your logistics journey.",
    onClick,
    badge = "Quick Actions",
    icon: Icon = Plus,
}) {
    return (
        <button type="button" className="qa-card glass-card" onClick={onClick}>
            <div className="qa-head">
                <span className="qa-badge">{badge}</span>
                <span className="qa-icon"><Icon size={18} /></span>
            </div>
            <div className="qa-body">
                <h3 className="qa-title">{title}</h3>
                <p className="qa-subtitle">{subtitle}</p>
            </div>
            <div className="qa-footer">
                <span className="qa-cta">Create</span>
            </div>
        </button>
    );
}
