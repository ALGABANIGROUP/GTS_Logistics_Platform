import React from 'react';

export default function SupportCenter() {
    return (
        <div className="p-6">
            <h1 className="text-3xl font-bold mb-6 text-white">🆘 Support Center</h1>

            {/* AI Bot Support Notice */}
            <div className="mb-6 rounded-2xl border border-blue-500/60 bg-gradient-to-r from-blue-900/60 to-cyan-900/60 p-6 shadow-2xl shadow-black/40 backdrop-blur-xl">
                <div className="flex items-start gap-4">
                    <div className="text-4xl">🤖</div>
                    <div className="flex-1">
                        <h3 className="text-xl font-bold text-white mb-2">AI-Powered Support via Customer Service Bot</h3>
                        <p className="text-slate-200 mb-4">
                            All support requests are now handled by our intelligent Customer Service Bot with 24/7 availability and instant responses.
                        </p>
                        <a
                            href="/ai-bots/customer-service"
                            className="inline-flex items-center gap-2 bg-blue-500/80 hover:bg-blue-500 text-white px-6 py-3 rounded-lg font-semibold transition backdrop-blur-sm"
                        >
                            <span>💬</span>
                            <span>Chat with Customer Service Bot</span>
                        </a>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-6 shadow-2xl shadow-black/40 backdrop-blur-xl transition duration-200 hover:border-blue-500/50">
                    <h2 className="text-xl font-semibold mb-4 flex items-center text-white">
                        <span className="mr-2">📧</span> Contact Support
                    </h2>
                    <p className="text-slate-300 mb-4">
                        For technical assistance, platform issues, or general inquiries:
                    </p>
                    <a
                        href="mailto:support@gabanistore.com"
                        className="inline-block bg-blue-600/80 text-white px-6 py-3 rounded-lg hover:bg-blue-600 backdrop-blur-sm transition"
                    >
                        support@gabanistore.com
                    </a>
                </div>

                <div className="rounded-2xl border border-slate-700/60 bg-slate-900/60 p-6 shadow-2xl shadow-black/40 backdrop-blur-xl transition duration-200 hover:border-green-500/50">
                    <h2 className="text-xl font-semibold mb-4 flex items-center text-white">
                        <span className="mr-2">🏢</span> Operations Team
                    </h2>
                    <p className="text-slate-300 mb-4">
                        For business operations, logistics, and freight management:
                    </p>
                    <a
                        href="mailto:operations@gabanilogistics.com"
                        className="inline-block bg-green-600/80 text-white px-6 py-3 rounded-lg hover:bg-green-600 backdrop-blur-sm transition"
                    >
                        operations@gabanilogistics.com
                    </a>
                </div>
            </div>

            <div className="rounded-2xl border border-slate-700/60 bg-gradient-to-r from-blue-900/40 to-indigo-900/40 p-6 shadow-2xl shadow-black/40 backdrop-blur-xl">
                <h2 className="text-xl font-semibold mb-4 text-white">📚 Quick Links</h2>
                <ul className="space-y-2">
                    <li>
                        <a href="/emails" className="text-blue-400 hover:text-blue-300 hover:underline transition">📬 Email Command Center</a>
                    </li>
                    <li>
                        <a href="/admin/settings" className="text-blue-400 hover:text-blue-300 hover:underline transition">⚙️ Platform Settings</a>
                    </li>
                    <li>
                        <a href="/admin/system-health" className="text-blue-400 hover:text-blue-300 hover:underline transition">🏥 System Health</a>
                    </li>
                    <li>
                        <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:text-blue-300 hover:underline transition">🔗 API Documentation</a>
                    </li>
                </ul>
            </div>

            <div className="mt-6 text-center text-slate-400 text-sm">
                <p>Response Time: Within 24 hours | Available: Monday - Friday, 9 AM - 6 PM PST</p>
            </div>
        </div>
    );
}