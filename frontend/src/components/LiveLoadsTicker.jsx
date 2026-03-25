import React from 'react';

const LiveLoadsTicker = () => {
    return (
        <div className="bg-red-600 py-2 overflow-hidden">
            <div className="animate-pulse">
                <div className="flex items-center gap-4 text-white text-sm whitespace-nowrap">
                    <span className="font-semibold">🔴 LIVE:</span>
                    <span>12,450 Flatbed loads available</span>
                    <span>•</span>
                    <span>8,932 Van loads available</span>
                    <span>•</span>
                    <span>5,678 Reefer loads available</span>
                    <span>•</span>
                    <span>3,421 Heavy Haul loads available</span>
                    <span>•</span>
                    <span>2,156 loads moved today</span>
                </div>
            </div>
        </div>
    );
};

export default LiveLoadsTicker;