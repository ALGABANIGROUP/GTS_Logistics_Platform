import React from 'react';
import { Link } from 'react-router-dom';
import gtsLogo from '../assets/gabani_logo.png';
import bgLogin from '../assets/bg_login.png';
import SeoHead from '../components/SeoHead';

const About = () => {
    return (
        <div className="min-h-screen bg-cover bg-center bg-no-repeat" style={{ backgroundImage: `url(${bgLogin})` }}>
            <SeoHead
                title="About GTS Logistics - Freight Broker & Load Board Platform"
                description="Learn about GTS Logistics, our freight brokerage operations, AI-driven logistics platform, and cross-border trade expertise."
                keywords="about gts logistics, freight broker company, canada logistics, cross-border freight"
                canonical="https://www.gtsdispatcher.com/about"
                ogTitle="About GTS Logistics"
                ogDescription="Learn about GTS Logistics, our mission, and our logistics operations."
                ogUrl="https://www.gtsdispatcher.com/about"
                twitterTitle="About GTS Logistics"
                twitterDescription="Learn about GTS Logistics, our mission, and our logistics operations."
            />
            <div className="min-h-screen bg-black/70">
                {/* Header */}
                <div className="container mx-auto px-4 py-4">
                    <div className="flex flex-wrap justify-between items-center gap-4">
                        <Link to="/">
                            <img src={gtsLogo} alt="GTS Logistics" className="h-12" />
                        </Link>

                        {/* Desktop Navigation */}
                        <div className="hidden md:flex items-center gap-6">
                            <Link to="/products" className="text-white hover:text-red-400 transition text-sm">Products</Link>
                            <Link to="/pricing" className="text-white hover:text-red-400 transition text-sm">Pricing</Link>
                            <Link to="/resources" className="text-white hover:text-red-400 transition text-sm">Resources</Link>
                            <Link to="/about" className="text-red-400 text-sm font-semibold">About</Link>
                            <Link to="/contact" className="text-white hover:text-red-400 transition text-sm">Contact</Link>
                        </div>

                        <div className="flex gap-3">
                            <Link to="/login" className="px-5 py-2 border border-white text-white rounded hover:bg-white/10 transition text-sm">
                                LOG IN
                            </Link>
                            <Link to="/register" className="px-5 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm">
                                SIGN UP
                            </Link>
                        </div>
                    </div>
                </div>

                {/* Hero Section */}
                <div className="container mx-auto px-4 py-12">
                    <div className="text-center mb-12">
                        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">About Gabani Transport Solutions (GTS)</h1>
                        <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                            Founder-led logistics and technology company combining freight brokerage, AI automation,
                            and international trade expertise to deliver practical, measurable value.
                        </p>
                    </div>

                    <div className="grid lg:grid-cols-2 gap-12">
                        {/* Left Column - Who We Are */}
                        <div className="space-y-8">
                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <h2 className="text-2xl font-bold text-white mb-4">Who We Are</h2>
                                <p className="text-gray-300 leading-relaxed mb-4">
                                    GTS focuses on the real work of freight and forwarding: planning loads, coordinating carriers,
                                    handling documentation, and aligning with regulators and customers. Our technology is built
                                    on top of this operational experience, not the other way around.
                                </p>
                                <p className="text-gray-300 leading-relaxed">
                                    We work across North America and key global trade corridors, especially
                                    <span className="text-red-400 font-semibold"> Canada – UAE – Egypt – Sudan – China</span>,
                                    with an emphasis on reliability, transparency, and long-term partnerships.
                                </p>
                            </div>

                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <h2 className="text-2xl font-bold text-white mb-4">Our Focus</h2>
                                <ul className="space-y-3">
                                    <li className="flex items-start gap-3">
                                        <span className="text-red-400 text-xl">✓</span>
                                        <span className="text-gray-300">Freight brokerage and transportation management</span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <span className="text-red-400 text-xl">✓</span>
                                        <span className="text-gray-300">AI-based optimization, pricing, and market visibility</span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <span className="text-red-400 text-xl">✓</span>
                                        <span className="text-gray-300">Compliance, safety, and regulatory alignment</span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <span className="text-red-400 text-xl">✓</span>
                                        <span className="text-gray-300">Digitizing dispatch, documentation, and finance workflows</span>
                                    </li>
                                    <li className="flex items-start gap-3">
                                        <span className="text-red-400 text-xl">✓</span>
                                        <span className="text-gray-300">Supporting cross-border and international freight forwarding</span>
                                    </li>
                                </ul>
                            </div>
                        </div>

                        {/* Right Column - Canada & USA */}
                        <div className="space-y-8">
                            <div className="bg-gradient-to-r from-red-900/30 to-black/40 backdrop-blur-sm rounded-xl p-6 border border-red-500/30">
                                <div className="flex items-center gap-3 mb-4">
                                    <span className="text-3xl">🍁</span>
                                    <h2 className="text-2xl font-bold text-white">Canada – GTS Logistics</h2>
                                </div>
                                <p className="text-gray-300 leading-relaxed mb-4">
                                    In Canada, GTS operates as a freight brokerage and logistics solutions provider with
                                    strong integration of AI-driven analytics and automation. Services include:
                                </p>
                                <ul className="space-y-2 mb-4">
                                    <li className="flex items-center gap-2 text-gray-300 text-sm">
                                        <span className="text-green-400">✓</span> Shipper–carrier matching
                                    </li>
                                    <li className="flex items-center gap-2 text-gray-300 text-sm">
                                        <span className="text-green-400">✓</span> Live status updates
                                    </li>
                                    <li className="flex items-center gap-2 text-gray-300 text-sm">
                                        <span className="text-green-400">✓</span> Route planning
                                    </li>
                                    <li className="flex items-center gap-2 text-gray-300 text-sm">
                                        <span className="text-green-400">✓</span> Utilization analytics
                                    </li>
                                </ul>
                                <p className="text-gray-300 leading-relaxed">
                                    The Canadian branch also supports international freight forwarding, including
                                    <span className="text-red-400"> FCL and LCL consolidation</span> and combinations of
                                    air, sea, and sea–air routes for door-to-door solutions.
                                </p>
                            </div>

                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="flex items-center gap-3 mb-4">
                                    <span className="text-3xl">🇺🇸</span>
                                    <h2 className="text-2xl font-bold text-white">USA – GTS LLC</h2>
                                </div>
                                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-3 mb-4">
                                    <p className="text-yellow-400 text-sm font-semibold">📋 FMCSA Registration</p>
                                    <p className="text-gray-300 text-sm">USDOT: <span className="text-white font-mono">4317957</span></p>
                                </div>
                                <p className="text-gray-300 leading-relaxed mb-3">
                                    Gabani Transport Solutions LLC is registered with the FMCSA under USDOT 4317957.
                                    As of late 2025, public records show no inspections or crashes, which indicates
                                    limited or paused activity.
                                </p>
                                <p className="text-gray-300 leading-relaxed">
                                    The entity is maintained for future growth, while the main operational and product
                                    development focus is driven from Canada and global GTS Logistics operations.
                                </p>
                            </div>

                            {/* Stats */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-black/40 backdrop-blur-sm rounded-xl p-4 text-center">
                                    <p className="text-2xl font-bold text-white">50,000+</p>
                                    <p className="text-gray-400 text-xs">Active Carriers</p>
                                </div>
                                <div className="bg-black/40 backdrop-blur-sm rounded-xl p-4 text-center">
                                    <p className="text-2xl font-bold text-white">98%</p>
                                    <p className="text-gray-400 text-xs">On-Time Delivery</p>
                                </div>
                                <div className="bg-black/40 backdrop-blur-sm rounded-xl p-4 text-center">
                                    <p className="text-2xl font-bold text-white">15+</p>
                                    <p className="text-gray-400 text-xs">Countries Served</p>
                                </div>
                                <div className="bg-black/40 backdrop-blur-sm rounded-xl p-4 text-center">
                                    <p className="text-2xl font-bold text-white">24/7</p>
                                    <p className="text-gray-400 text-xs">Support Available</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Mission Statement */}
                    <div className="mt-12 bg-gradient-to-r from-red-600/20 to-transparent rounded-xl p-8 border border-red-500/30">
                        <h2 className="text-2xl font-bold text-white text-center mb-4">Our Mission</h2>
                        <p className="text-gray-300 text-center max-w-3xl mx-auto leading-relaxed">
                            To empower logistics companies with a self-learning digital ecosystem that reduces overhead,
                            improves transparency, and streamlines freight operations across all channels — delivering
                            practical, measurable value to carriers, brokers, and shippers worldwide.
                        </p>
                    </div>
                </div>

                {/* Footer */}
                <div className="container mx-auto px-4 py-6 border-t border-white/20 mt-8">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                        <p className="text-gray-400 text-xs">
                            © 2026 Gabani Transport Solutions LLC – All rights reserved.
                        </p>
                        <div className="flex gap-4 text-xs">
                            <a href="/privacy" className="text-gray-400 hover:text-white transition">Privacy Policy</a>
                            <a href="/terms" className="text-gray-400 hover:text-white transition">Terms of Service</a>
                            <a href="/legal" className="text-gray-400 hover:text-white transition">Legal Agreements</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default About;
