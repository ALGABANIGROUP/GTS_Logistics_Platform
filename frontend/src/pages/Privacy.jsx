import React from 'react';
import { Link } from 'react-router-dom';
import gtsLogo from '../assets/gabani_logo.png';
import bgLogin from '../assets/bg_login.png';

const Privacy = () => {
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
                        <h1 className="text-3xl font-bold text-white mb-6">Privacy Policy</h1>
                        <p className="text-gray-400 text-sm mb-6">Last Updated: March 24, 2026</p>

                        <div className="space-y-6 text-gray-300">
                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">1. Information We Collect</h2>
                                <p>GTS Logistics collects information you provide directly to us, such as when you create an account, use our services, or contact us. This may include:</p>
                                <ul className="list-disc list-inside mt-2 space-y-1 text-gray-400">
                                    <li>Name, email address, phone number, and company details</li>
                                    <li>Payment information (processed securely via third-party providers)</li>
                                    <li>Shipping and logistics data including loads, shipments, and tracking information</li>
                                    <li>Usage data, IP addresses, and device information</li>
                                </ul>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">2. How We Use Your Information</h2>
                                <p>We use your information to:</p>
                                <ul className="list-disc list-inside mt-2 space-y-1 text-gray-400">
                                    <li>Provide, maintain, and improve our logistics platform</li>
                                    <li>Process shipments, payments, and facilitate carrier-broker-shipper connections</li>
                                    <li>Communicate with you about your account and our services</li>
                                    <li>Detect and prevent fraud, security incidents, and prohibited activities</li>
                                    <li>Comply with legal and regulatory requirements</li>
                                </ul>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">3. Data Sharing and Disclosure</h2>
                                <p>We may share your information with:</p>
                                <ul className="list-disc list-inside mt-2 space-y-1 text-gray-400">
                                    <li>Carriers, brokers, and shippers to facilitate freight matching and shipments</li>
                                    <li>Service providers who assist in operating our platform (payment processors, hosting, analytics)</li>
                                    <li>Government authorities when required by law or to protect legal rights</li>
                                    <li>In connection with a merger, acquisition, or sale of assets</li>
                                </ul>
                                <p className="mt-2">We do not sell your personal information to third parties.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">4. Data Security</h2>
                                <p>We implement industry-standard security measures to protect your information, including encryption, access controls, and regular security audits. However, no method of transmission over the internet is 100% secure.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">5. Your Rights and Choices</h2>
                                <p>Depending on your location, you may have the right to:</p>
                                <ul className="list-disc list-inside mt-2 space-y-1 text-gray-400">
                                    <li>Access and receive a copy of your personal data</li>
                                    <li>Correct inaccurate information</li>
                                    <li>Request deletion of your data</li>
                                    <li>Opt out of marketing communications</li>
                                </ul>
                                <p className="mt-2">To exercise these rights, contact us at <a href="mailto:support@gabanistore.com" className="text-red-400 hover:underline">support@gabanistore.com</a>.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">6. Cookies and Tracking Technologies</h2>
                                <p>We use cookies and similar technologies to enhance your experience, analyze usage, and personalize content. You can manage cookie preferences through your browser settings.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">7. International Data Transfers</h2>
                                <p>Your information may be transferred to and processed in countries outside your residence, including Canada, the United States, and Sudan. We ensure appropriate safeguards are in place for such transfers.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">8. Children's Privacy</h2>
                                <p>Our services are not directed to individuals under 18. We do not knowingly collect personal information from children.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">9. Changes to This Policy</h2>
                                <p>We may update this Privacy Policy from time to time. We will notify you of material changes by posting the new policy on this page and updating the "Last Updated" date.</p>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">10. Contact Us</h2>
                                <p>If you have questions about this Privacy Policy, please contact our Legal Team:</p>
                                <p className="mt-2 text-gray-400">📧 <a href="mailto:support@gabanistore.com" className="text-red-400 hover:underline">support@gabanistore.com</a></p>
                                <p>📍 Gabani Transport Solutions LLC, 2261 Market Street, San Francisco, CA 94114, USA</p>
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
                        <p className="text-gray-400 text-xs">© 2026 Gabani Transport Solutions LLC – All rights reserved.</p>
                        <div className="flex gap-4 text-xs">
                            <Link to="/privacy" className="text-red-400 hover:text-white transition">Privacy Policy</Link>
                            <Link to="/terms" className="text-gray-400 hover:text-white transition">Terms of Service</Link>
                            <Link to="/legal" className="text-gray-400 hover:text-white transition">Legal Agreements</Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Privacy;