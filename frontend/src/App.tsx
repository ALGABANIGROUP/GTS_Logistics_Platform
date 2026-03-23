import React, { useState } from 'react';
import UnifiedBotsDashboard from './components/UnifiedBotsDashboard';
import './App.css';

function App() {
    const [theme, setTheme] = useState<'light' | 'dark'>('light');

    const toggleTheme = () => {
        setTheme(theme === 'light' ? 'dark' : 'light');
    };

    return (
        <div className={`App ${theme}`}>
            <div className="theme-toggle">
                <button onClick={toggleTheme} className="theme-btn">
                    {theme === 'light' ? 'Light' : 'Dark'}
                </button>
            </div>
            <UnifiedBotsDashboard />

                        <div className="credits">
                <p>Unified AI Bot Management | Version 2.0</p>
                <p className="credit-sub">15 core bots, no duplication | Custom design and development</p>
            </div>
        </div>
    );
}

export default App;
