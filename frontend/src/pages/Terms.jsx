import React from 'react';
import { Link } from 'react-router-dom';
import gtsLogo from '../assets/gabani_logo.png';
import bgLogin from '../assets/bg_login.png';

const Terms = () => {
    return (
        <div className="min-h-screen bg-cover bg-center bg-no-repeat" style={{ backgroundImage: `url(${bgLogin})` }}>
            <div className="min-h-screen bg-black/70">
                {/* Header */}
                <div className="container mx-auto px-4 py-4">
                    <div className="flex flex-wrap justify-between items-center gap-4">
                        <div className="flex items-center gap-4">
                            <Link to="/" className="inline-flex items-center px-4 py-2 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-white text-sm transition duration-200">
                                ← Back to Portal
                            </Link>
                            <Link to="/">
                                <img src={gtsLogo} alt="GTS Logistics" className="h-12" />
                            </Link>
                        </div>
                        <div className="hidden md:flex items-center gap-6">
                            <Link to="/products" className="text-white hover:text-red-400 transition text-sm">Products</Link>
                            <Link to="/pricing" className="text-white hover:text-red-400 transition text-sm">Pricing</Link>
                            <Link to="/resources" className="text-white hover:text-red-400 transition text-sm">Resources</Link>
                            <Link to="/about" className="text-white hover:text-red-400 transition text-sm">About</Link>
                            <Link to="/contact" className="text-white hover:text-red-400 transition text-sm">Contact</Link>
                        </div>
                        <div className="flex gap-3">
                            <Link to="/login" className="px-5 py-2 border border-white text-white rounded hover:bg-white/10 transition text-sm">LOG IN</Link>
                            <Link to="/register" className="px-5 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm">SIGN UP</Link>
                        </div>
                    </div>
                </div>

                {/* Content */}
                <div className="container mx-auto px-4 py-12 max-w-4xl">
                    <div className="bg-black/40 backdrop-blur-sm rounded-xl p-8 border border-white/20">
                        <h1 className="text-3xl font-bold text-white mb-6">Terms of Service</h1>
                        <p className="text-gray-400 text-sm mb-6">Effective Date: March 24, 2026</p>

                        <div className="space-y-6 text-gray-300">
                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">1. Acceptance of Terms</h2>
                                <p>By accessing or using the GTS Logistics platform (the "Service"), you agree to be bound by these Terms of Service ("Terms"). If you do not agree, please do not use the Service.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">2. Description of Service</h2>
                                <p>GTS Logistics provides a freight brokerage and logistics platform connecting carriers, brokers, and shippers. The Service includes load boards, AI-powered automation, shipment tracking, rate insights, and related tools.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">3. Eligibility</h2>
                                <p>You must be at least 18 years old and capable of forming a binding contract. Carriers and brokers must hold valid operating authority and comply with all applicable regulations. Users from restricted countries may not use the Service.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">4. Accounts and Registration</h2>
                                <p>You are responsible for maintaining the confidentiality of your account credentials. You agree to provide accurate information and notify us immediately of any unauthorized access. We reserve the right to suspend or terminate accounts for violation of these Terms.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">5. User Conduct</h2>
                                <p>You agree not to:</p>
                                <ul className="list-disc list-inside mt-2 space-y-1 text-gray-400">
                                    <li>Use the Service for unlawful purposes or in violation of any regulations</li>
                                    <li>Post fraudulent or misleading loads or shipments</li>
                                    <li>Engage in price fixing or anti-competitive behavior</li>
                                    <li>Attempt to gain unauthorized access to other accounts or systems</li>
                                    <li>Upload malicious code or interfere with the Service's operation</li>
                                    <li>Harass, threaten, or defraud other users</li>
                                </ul>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">6. Payments and Subscriptions</h2>
                                <p>Fees for paid plans are billed in advance on a monthly or annual basis. All fees are non-refundable except as required by law. We may change pricing with notice, and continued use constitutes acceptance of new pricing.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">7. Cancellation and Termination</h2>
                                <p>You may cancel your subscription at any time through your account settings. Upon cancellation, access will continue until the end of your billing period. We may terminate your account for violation of these Terms.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">8. Intellectual Property</h2>
                                <p>The Service and its content (including software, trademarks, and AI bots) are owned by Gabani Transport Solutions LLC. You may not copy, modify, or reverse engineer any part of the Service without permission.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">9. Disclaimer of Warranties</h2>
                                <p>The Service is provided "as is" without warranties of any kind. We do not guarantee uninterrupted or error-free operation. You assume all risks associated with using the Service.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">10. Limitation of Liability</h2>
                                <p>To the fullest extent permitted by law, GTS Logistics shall not be liable for any indirect, incidental, or consequential damages arising from your use of the Service. Our total liability shall not exceed the fees paid by you in the preceding 12 months.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">11. Indemnification</h2>
                                <p>You agree to indemnify and hold harmless GTS Logistics from any claims, damages, or expenses arising from your use of the Service or violation of these Terms.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">12. Governing Law</h2>
                                <p>These Terms shall be governed by the laws of the State of California, without regard to conflict of law principles. Disputes shall be resolved exclusively in the courts of San Francisco County, California.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">13. Changes to Terms</h2>
                                <p>We may modify these Terms at any time. Continued use after changes constitutes acceptance. If you do not agree, you may discontinue use of the Service.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">14. Contact Information</h2>
                                <p>For questions about these Terms, contact our Legal Team:</p>
                                <p className="mt-2 text-gray-400">📧 <a href="mailto:support@gabanistore.com" className="text-red-400 hover:underline">support@gabanistore.com</a></p>
                            </section>
                        </div>

                        <div className="mt-8 pt-6 border-t border-white/10 text-center text-gray-500 text-xs">
                            <p>© 2026 Gabani Transport Solutions LLC. All rights reserved.</p>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="container mx-auto px-4 py-6 border-t border-white/20">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                        <div className="flex flex-col items-center md:items-start gap-2">
                            <p className="text-gray-400 text-xs">
                                © 2026 Gabani Transport Solutions LLC – All rights reserved.
                            </p>
                            <p className="text-gray-500 text-xs text-center md:text-left">
                                Canadian Patent Application No. 3306251 | AI Multi-Bot Orchestration System for Logistics Automation
                            </p>
                        </div>
                        <div className="flex gap-4 text-xs">
                            <Link to="/privacy" className="text-gray-400 hover:text-white transition">Privacy Policy</Link>
                            <Link to="/terms" className="text-red-400 hover:text-white transition">Terms of Service</Link>
                            <Link to="/legal" className="text-gray-400 hover:text-white transition">Legal Agreements</Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Terms;