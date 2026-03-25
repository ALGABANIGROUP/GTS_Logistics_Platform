import React from 'react';

const TrustBadges = () => {
    return (
        <div className="flex items-center gap-4 text-xs text-gray-400">
            <span>🔒 SSL Secured</span>
            <span>•</span>
            <span>🛡️ SOC 2 Compliant</span>
            <span>•</span>
            <span>📊 99.9% Uptime</span>
        </div>
    );
};

export default TrustBadges;