// frontend/src/data/mockAIData.js
export const mockAIData = {
    financial_analysis: {
        total_income: 12500,
        total_revenue: 9800,
        total_expenses: 2700,
        profit: 7100,
        profit_margin: '58%'
    },
    operational_metrics: {
        total_shipments: 45,
        completed_shipments: 38,
        active_shipments: 7,
        on_time_rate: '84%'
    },
    weekly_reports: {
        period: "Last 7 days",
        summary: {
            new_shipments: 12,
            completed_shipments: 15,
            revenue: 4500,
            expenses: 1200
        }
    }
};

export const getMockAIData = () => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve(mockAIData);
        }, 1000);
    });
};
