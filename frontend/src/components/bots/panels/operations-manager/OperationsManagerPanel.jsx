import React, { useMemo, useState } from "react";
import BaseBotPanel from "../../base/BaseBotPanel.jsx";
import OperationsManagerDashboard from "./OperationsManagerDashboard.jsx";
import OperationsManagerControls from "./OperationsManagerControls.jsx";
import OperationsManagerConfig from "./OperationsManagerConfig.jsx";
import OperationsManagerLogs from "./OperationsManagerLogs.jsx";
import "./OperationsManagerPanel.css";

export default function OperationsManagerPanel() {
    const [activeTab, setActiveTab] = useState("dashboard");

    const botConfig = useMemo(
        () => ({
            name: "AI Operations Manager",
            description: "Coordinates workflows, tasks, and performance across the platform.",
            status: "active",
            version: "1.0.0",
            lastUpdated: "Today",
            tabs: [
                { id: "dashboard", name: "Dashboard", icon: "" },
                { id: "workflows", name: "Workflows", icon: "" },
                { id: "tasks", name: "Tasks", icon: "" },
                { id: "performance", name: "Performance", icon: "" },
                { id: "config", name: "Config", icon: "" },
                { id: "logs", name: "Logs", icon: "" },
            ],
            quickStats: [
                { label: "Active Workflows", value: "24", icon: "", trend: "+3" },
                { label: "Tasks Today", value: "156", icon: "", trend: "+12%" },
                { label: "Success Rate", value: "98.5%", icon: "", trend: "+0.5%" },
                { label: "Avg Response", value: "2.3s", icon: "", trend: "-0.4s" },
            ],
        }),
        []
    );

    const renderTabContent = () => {
        switch (activeTab) {
            case "dashboard":
                return <OperationsManagerDashboard />;
            case "workflows":
            case "tasks":
            case "performance":
                return <OperationsManagerControls activeTab={activeTab} />;
            case "config":
                return <OperationsManagerConfig />;
            case "logs":
                return <OperationsManagerLogs />;
            default:
                return <OperationsManagerDashboard />;
        }
    };

    return (
        <div className="ops-panel-wrapper">
            <BaseBotPanel
                botId="operations-manager"
                botConfig={botConfig}
                activeTab={activeTab}
                onTabChange={setActiveTab}
            >
                {renderTabContent()}
            </BaseBotPanel>
        </div>
    );
}
