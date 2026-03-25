import React from 'react';
import { Link } from 'react-router-dom';

const MobileAppPromo = () => {
    return (
        <div className="bg-gradient-to-r from-red-600 to-red-800 py-12">
            <div className="container mx-auto px-4 text-center">
                <h2 className="text-white text-3xl font-bold mb-4">Get the GTS Mobile App</h2>
                <p className="text-gray-200 text-lg mb-8 max-w-2xl mx-auto">
                    Access loads, track shipments, and manage your business on the go with our powerful mobile app.
                </p>
                <div className="flex justify-center gap-4">
                    <Link to="/app-store" className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition flex items-center gap-2">
                        <span>📱</span> App Store
                    </Link>
                    <Link to="/google-play" className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition flex items-center gap-2">
                        <span>🤖</span> Google Play
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default MobileAppPromo;