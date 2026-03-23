import React, { useMemo, useState } from "react";
import BaseBotPanel from "../../base/BaseBotPanel.jsx";
import FinanceDashboard from "./FinanceDashboard.jsx";
import LedgerManager from "./LedgerManager.jsx";
import TaxManager from "./TaxManager.jsx";
import ExpenseTracker from "./ExpenseTracker.jsx";
import RevenueManager from "./RevenueManager.jsx";
import FinancialReports from "./FinancialReports.jsx";
import BudgetPlanner from "./BudgetPlanner.jsx";
import FinanceConfig from "./FinanceConfig.jsx";
import InvoiceManager from "./InvoiceManager.jsx";
import LaneProfitability from "./LaneProfitability.jsx";
import PlatformExpenses from "./PlatformExpenses.jsx";
import { FINANCE_ZERO_MODE } from "../../../../config/financeConstants";
import "./FinanceBotPanel.css";

export default function FinanceBotPanel() {
    const [activeTab, setActiveTab] = useState("dashboard");

    const botConfig = useMemo(
        () => ({
            name: "AI Finance Bot",
            description: "Financial control panel for ledgers, taxes, revenue, expenses, and reporting.",
            status: FINANCE_ZERO_MODE ? "inactive" : "active",
            version: "1.0.0",
            lastUpdated: "Today",
            tabs: [
                { id: "dashboard", name: "Dashboard", icon: "" },
                { id: "invoices", name: "Invoices", icon: "" },
                { id: "lanes", name: "Lane Analysis", icon: "" },
                { id: "ledger", name: "Ledger", icon: "" },
                { id: "tax", name: "Tax", icon: "" },
                { id: "revenue", name: "Revenue", icon: "" },
                { id: "expense", name: "Expenses", icon: "" },
                { id: "platform_expenses", name: "Platform Expenses", icon: "" },
                { id: "reports", name: "Reports", icon: "" },
                { id: "budget", name: "Budget", icon: "" },
                { id: "config", name: "Config", icon: "" },
            ],
            quickStats: [],
        }),
        []
    );

    // PlatformExpenses is imported at the top as ES6 import

    const renderTabContent = () => {
        switch (activeTab) {
            case "dashboard":
                return <FinanceDashboard zeroMode={FINANCE_ZERO_MODE} />;
            case "invoices":
                return <InvoiceManager zeroMode={FINANCE_ZERO_MODE} />;
            case "lanes":
                return <LaneProfitability zeroMode={FINANCE_ZERO_MODE} />;
            case "ledger":
                return <LedgerManager zeroMode={FINANCE_ZERO_MODE} />;
            case "tax":
                return <TaxManager zeroMode={FINANCE_ZERO_MODE} />;
            case "revenue":
                return <RevenueManager zeroMode={FINANCE_ZERO_MODE} />;
            case "expense":
                return <ExpenseTracker zeroMode={FINANCE_ZERO_MODE} />;
            case "platform_expenses":
                return <PlatformExpenses />;
            case "reports":
                return <FinancialReports zeroMode={FINANCE_ZERO_MODE} />;
            case "budget":
                return <BudgetPlanner zeroMode={FINANCE_ZERO_MODE} />;
            case "config":
                return <FinanceConfig zeroMode={FINANCE_ZERO_MODE} />;
            default:
                return <FinanceDashboard zeroMode={FINANCE_ZERO_MODE} />;
        }
    };

    return (
        <div className="fin-panel-wrapper glass-page">
            <BaseBotPanel
                botId="finance-bot"
                botConfig={botConfig}
                activeTab={activeTab}
                onTabChange={setActiveTab}
            >
                {renderTabContent()}
            </BaseBotPanel>
        </div>
    );
}
