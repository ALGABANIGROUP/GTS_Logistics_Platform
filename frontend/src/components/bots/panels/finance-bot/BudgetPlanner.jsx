import React, { useMemo, useState } from "react";
import { FINANCE_ZERO_MODE } from "../../../../config/financeConstants";

export default function BudgetPlanner({ zeroMode = FINANCE_ZERO_MODE }) {
    const [showBudgetModal, setShowBudgetModal] = useState(false);
    const [budgetList, setBudgetList] = useState([]);

    const baseBudgets = useMemo(() => [
        { category: "Operations", planned: 50000, actual: 42300 },
        { category: "Marketing", planned: 15000, actual: 12500 },
        { category: "Development", planned: 30000, actual: 28500 },
    ], []);

    const budgets = useMemo(() => (
        zeroMode ? [] : [...baseBudgets, ...budgetList]
    ), [zeroMode, baseBudgets, budgetList]);

    const handleAddPlan = (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const newBudget = {
            category: formData.get('category'),
            planned: parseFloat(formData.get('planned')),
            actual: 0
        };
        setBudgetList(prev => [...prev, newBudget]);
        setShowBudgetModal(false);
        alert(`Budget plan added for ${newBudget.category}: $${newBudget.planned.toLocaleString()}`);
    };

    const handleExport = () => {
        const csvContent = "Category,Planned,Actual\n" +
            budgets.map(b => `${b.category},${b.planned},${b.actual}`).join("\n");
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'budget_export.csv';
        a.click();
        alert('Budget exported successfully!');
    };

    return (
        <div className="fin-section">
            <div className="fin-card-title">Budget Planning</div>
            <div className="fin-grid fin-grid-compact">
                {budgets.length === 0 ? (
                    <div style={{ padding: "16px", color: "#9fb2d3" }}>No budgets available.</div>
                ) : (
                    budgets.map((b) => {
                        const pct = Math.min((b.actual / b.planned) * 100, 120);
                        const over = b.actual > b.planned;
                        return (
                            <div key={b.category} className="fin-card fin-budget-card">
                                <div className="fin-budget-header">
                                    <span>{b.category}</span>
                                    <span className={`fin-budget-flag ${over ? "warn" : "ok"}`}>{over ? "Over" : "On track"}</span>
                                </div>
                                <div className="fin-progress">
                                    <div className="fin-progress-bar" style={{ width: `${pct}%`, backgroundColor: over ? "#ef4444" : "#10b981" }} />
                                </div>
                                <div className="fin-budget-meta">
                                    <span>Planned ${b.planned.toLocaleString()}</span>
                                    <span>Actual ${b.actual.toLocaleString()}</span>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>
            <div className="fin-row fin-justify-end fin-gap-sm">
                <button className="fin-btn" disabled={zeroMode} onClick={handleExport}>Export Budget</button>
                <button className="fin-btn primary" disabled={zeroMode} onClick={() => setShowBudgetModal(true)}>Add Plan</button>
            </div>

            {showBudgetModal && (
                <div className="fin-modal-overlay" onClick={() => setShowBudgetModal(false)}>
                    <div className="fin-modal" onClick={(e) => e.stopPropagation()}>
                        <h3>Add Budget Plan</h3>
                        <form onSubmit={handleAddPlan}>
                            <label>Category</label>
                            <input type="text" name="category" required placeholder="Budget category" />
                            <label>Planned Amount ($)</label>
                            <input type="number" name="planned" required min="0" step="0.01" />
                            <div className="fin-modal-actions">
                                <button type="button" className="fin-btn" onClick={() => setShowBudgetModal(false)}>Cancel</button>
                                <button type="submit" className="fin-btn primary">Add Plan</button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
