// frontend/src/pages/SimpleDevDashboard.jsx
import React from 'react';

const SimpleDevDashboard = () => {
    return (
        <div className="p-6 bg-green-100 border border-green-400 rounded-lg">
            <h1 className="text-2xl font-bold text-green-800">✅ Simple Dashboard Loaded!</h1>
            <p className="text-green-700">If you can see this, the component is working.</p>

            <div className="mt-4 grid grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded shadow">Bot 1</div>
                <div className="bg-white p-4 rounded shadow">Bot 2</div>
                <div className="bg-white p-4 rounded shadow">Bot 3</div>
            </div>
        </div>
    );
};

export default SimpleDevDashboard;