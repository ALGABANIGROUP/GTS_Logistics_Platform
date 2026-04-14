import React from 'react';
import { Link } from 'react-router-dom';
import gtsLogo from '../assets/gabani_logo.png';
import bgLogin from '../assets/bg_login.png';

const Legal = () => {
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
                        <h1 className="text-3xl font-bold text-white mb-6">Legal Agreements</h1>
                        <p className="text-gray-400 text-sm mb-6">Effective Date: March 24, 2026</p>

                        <div className="space-y-6 text-gray-300">
                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">Data Processing Agreement (DPA)</h2>
                                <p>This DPA governs the processing of personal data by GTS Logistics on behalf of our customers. We are committed to GDPR and CCPA compliance.</p>
                                <div className="mt-3">
                                    <h3 className="font-medium text-white mb-2">Key Provisions:</h3>
                                    <ul className="list-disc list-inside space-y-1 text-gray-400">
                                        <li>Data processing scope and purposes</li>
                                        <li>Data subject rights and controller obligations</li>
                                        <li>Security measures and breach notification</li>
                                        <li>International data transfers and safeguards</li>
                                        <li>Subprocessor management and approval</li>
                                    </ul>
                                </div>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">Carrier-Broker Agreement</h2>
                                <p>This agreement establishes the relationship between carriers and brokers using the GTS platform.</p>
                                <div className="mt-3">
                                    <h3 className="font-medium text-white mb-2">Terms Include:</h3>
                                    <ul className="list-disc list-inside space-y-1 text-gray-400">
                                        <li>Load acceptance and rejection procedures</li>
                                        <li>Rate negotiation and payment terms</li>
                                        <li>Insurance requirements and coverage</li>
                                        <li>Dispute resolution and arbitration</li>
                                        <li>Termination and notice requirements</li>
                                    </ul>
                                </div>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">API License Agreement</h2>
                                <p>This agreement governs the use of GTS APIs for integration with third-party systems.</p>
                                <div className="mt-3">
                                    <h3 className="font-medium text-white mb-2">License Terms:</h3>
                                    <ul className="list-disc list-inside space-y-1 text-gray-400">
                                        <li>API usage limits and rate limiting</li>
                                        <li>Data access and privacy restrictions</li>
                                        <li>Authentication and security requirements</li>
                                        <li>Support and maintenance obligations</li>
                                        <li>Termination and data deletion procedures</li>
                                    </ul>
                                </div>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">Master Services Agreement (MSA)</h2>
                                <p>This MSA establishes the general terms for all services provided by GTS Logistics.</p>
                                <div className="mt-3">
                                    <h3 className="font-medium text-white mb-2">Core Provisions:</h3>
                                    <ul className="list-disc list-inside space-y-1 text-gray-400">
                                        <li>Service level agreements (SLAs)</li>
                                        <li>Confidentiality and non-disclosure</li>
                                        <li>Intellectual property rights</li>
                                        <li>Force majeure and liability limitations</li>
                                        <li>Governing law and dispute resolution</li>
                                    </ul>
                                </div>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">Acceptable Use Policy</h2>
                                <p>This policy outlines permitted and prohibited uses of the GTS platform.</p>
                                <div className="mt-3">
                                    <h3 className="font-medium text-white mb-2">Prohibited Activities:</h3>
                                    <ul className="list-disc list-inside space-y-1 text-gray-400">
                                        <li>Fraudulent or deceptive practices</li>
                                        <li>Violation of transportation regulations</li>
                                        <li>Harassment or discrimination</li>
                                        <li>Unauthorized data collection or sharing</li>
                                        <li>Interference with platform operations</li>
                                    </ul>
                                </div>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">Compliance Certifications</h2>
                                <p>GTS Logistics maintains compliance with industry standards and regulations.</p>
                                <div className="mt-3">
                                    <h3 className="font-medium text-white mb-2">Certifications:</h3>
                                    <ul className="list-disc list-inside space-y-1 text-gray-400">
                                        <li>SOC 2 Type II compliance</li>
                                        <li>ISO 27001 information security</li>
                                        <li>GDPR and CCPA compliance</li>
                                        <li>FMCSA operating authority</li>
                                        <li>Insurance coverage verification</li>
                                    </ul>
                                </div>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">Intellectual Property & Innovation</h2>
                                <p>GTS Logistics has filed a Canadian patent application for its AI-Powered Multi-Bot Orchestration System for Logistics Automation.</p>
                                <div className="mt-3">
                                    <h3 className="font-medium text-white mb-2">Patent Details:</h3>
                                    <p className="text-gray-400 mb-3"><strong>Application No.:</strong> 3306251</p>
                                    <p className="text-gray-400 mb-3"><strong>Title:</strong> AI Multi-Bot Orchestration System for Logistics Automation</p>
                                    <h4 className="font-medium text-white mb-2">Protected Systems:</h4>
                                    <ol className="list-decimal list-inside space-y-1 text-gray-400">
                                        <li>AI Multi-Bot Orchestration System</li>
                                        <li>Intelligent Freight Matching with Predictive Analytics</li>
                                        <li>Unified Cross-Border Payment Processing</li>
                                        <li>Autonomous Incident Detection and Response</li>
                                        <li>AI-Powered Document Processing and Compliance</li>
                                        <li>Predictive Fleet Maintenance and Analytics</li>
                                        <li>Carrier Onboarding and Continuous Verification</li>
                                    </ol>
                                    <p className="text-gray-400 mt-3">This patent protects the core technology that enables autonomous coordination between specialized AI agents without human intervention.</p>
                                </div>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">Download Legal Documents</h2>
                                <p>Access complete legal agreements and documentation:</p>
                                <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <a href="#" className="block p-4 bg-white/10 rounded-lg hover:bg-white/20 transition">
                                        <h4 className="font-medium text-white mb-1">Data Processing Agreement</h4>
                                        <p className="text-sm text-gray-400">Complete DPA for GDPR compliance</p>
                                    </a>
                                    <a href="#" className="block p-4 bg-white/10 rounded-lg hover:bg-white/20 transition">
                                        <h4 className="font-medium text-white mb-1">Carrier-Broker Agreement</h4>
                                        <p className="text-sm text-gray-400">Terms for carrier partnerships</p>
                                    </a>
                                    <a href="#" className="block p-4 bg-white/10 rounded-lg hover:bg-white/20 transition">
                                        <h4 className="font-medium text-white mb-1">API License Agreement</h4>
                                        <p className="text-sm text-gray-400">Terms for API integration</p>
                                    </a>
                                    <a href="#" className="block p-4 bg-white/10 rounded-lg hover:bg-white/20 transition">
                                        <h4 className="font-medium text-white mb-1">Master Services Agreement</h4>
                                        <p className="text-sm text-gray-400">General service terms</p>
                                    </a>
                                </div>
                            </section>

                            <section>
                                <h2 className="text-xl font-semibold text-white mb-3">Contact Legal Team</h2>
                                <p>For legal questions or to request specific agreements:</p>
                                <p className="mt-2 text-gray-400">📧 <a href="mailto:support@gabanilogistics.com" className="text-red-400 hover:underline">support@gabanilogistics.com</a></p>
                                <p className="mt-2 text-sm text-gray-400">Legal consultations are available for enterprise customers.</p>
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
                            <Link to="/terms" className="text-gray-400 hover:text-white transition">Terms of Service</Link>
                            <Link to="/legal" className="text-red-400 hover:text-white transition">Legal Agreements</Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Legal;