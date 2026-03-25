import React from 'react';
import { Link } from 'react-router-dom';

const FuelPriceMap = () => {
    const fuelPrices = [
        { country: 'Sudan (Khartoum)', price: 2.85, currency: 'SDG/L', change: '+0.05', trend: 'up' },
        { country: 'Saudi Arabia (Riyadh)', price: 0.62, currency: 'USD/L', change: '-0.02', trend: 'down' },
        { country: 'UAE (Dubai)', price: 0.68, currency: 'USD/L', change: '-0.01', trend: 'down' },
        { country: 'Egypt (Cairo)', price: 0.45, currency: 'USD/L', change: '+0.03', trend: 'up' },
        { country: 'Qatar (Doha)', price: 0.61, currency: 'USD/L', change: '-0.01', trend: 'down' },
        { country: 'Kuwait (Kuwait City)', price: 0.34, currency: 'USD/L', change: '0.00', trend: 'stable' },
        { country: 'Oman (Muscat)', price: 0.62, currency: 'USD/L', change: '-0.02', trend: 'down' },
        { country: 'Jordan (Amman)', price: 1.05, currency: 'USD/L', change: '+0.04', trend: 'up' },
    ];

    return (
        <div className="bg-black/40 backdrop-blur-sm rounded-xl p-4">
            <div className="flex justify-between items-center mb-3">
                <h3 className="text-white font-semibold text-sm">⛽ Fuel Price Map</h3>
                <span className="text-gray-400 text-[10px]">Updated hourly</span>
            </div>
            <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                {fuelPrices.map((fuel, idx) => (
                    <div key={idx} className="flex justify-between items-center py-1 border-b border-white/10">
                        <span className="text-gray-300 text-xs">{fuel.country}</span>
                        <div className="flex gap-3">
                            <span className="text-white text-xs font-medium">{fuel.price} {fuel.currency}</span>
                            <span className={`text-[10px] ${fuel.trend === 'up' ? 'text-red-400' : fuel.trend === 'down' ? 'text-green-400' : 'text-gray-400'}`}>
                                {fuel.change.startsWith('+') ? '↑' : fuel.change.startsWith('-') ? '↓' : '→'} {fuel.change}
                            </span>
                        </div>
                    </div>
                ))}
            </div>
            <div className="mt-3 pt-2 border-t border-white/10">
                <div className="flex justify-between text-[10px] text-gray-500">
                    <span>🔥 Hot Market</span>
                    <span>❄️ Cool Market</span>
                    <span>📊 Source: Global Fuel Index</span>
                </div>
            </div>
        </div>
    );
};

export default FuelPriceMap;