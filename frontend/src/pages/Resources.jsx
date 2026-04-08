import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import gtsLogo from '../assets/gabani_logo.png';
import bgLogin from '../assets/bg_login.png';
import SeoHead from '../components/SeoHead';

const Resources = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('all');
    const [loadSearch, setLoadSearch] = useState({
        origin: '',
        destination: '',
        equipment: ''
    });

    const resources = {
        courses: [
            {
                title: "Trucking Mastery with Kevin Rutherford",
                description: "An exclusive FREE course series designed with owner-operators and small fleet owners in mind.",
                icon: "🎓",
                link: "/resources/trucking-mastery",
                featured: true
            },
            {
                title: "Owner-Operator Profit Guide",
                description: "Essential strategies to maximize profitability for independent owner-operators.",
                icon: "📊",
                link: "/resources/profit-guide"
            },
            {
                title: "The 2026 Guide to a Profitable Trucking Business",
                description: "Comprehensive guide covering rates, costs, and operational efficiency.",
                icon: "📈",
                link: "/resources/2026-guide"
            }
        ],
        blogs: [
            {
                title: "AI-Powered Logistics: The Future of Freight",
                description: "How AI agents are transforming freight brokerage, compliance, and finance operations.",
                date: "March 15, 2026",
                link: "/blog/ai-powered-logistics"
            },
            {
                title: "Reducing Empty Miles with Smart Route Planning",
                description: "Practical strategies to maximize asset productivity and reduce deadhead.",
                date: "March 10, 2026",
                link: "/blog/empty-miles"
            },
            {
                title: "Winter Weather Tips for Truckers",
                description: "Essential safety tips for navigating harsh winter conditions.",
                date: "February 28, 2026",
                link: "/blog/winter-weather"
            }
        ],
        tools: [
            { name: "Fuel Discount Finder", icon: "⛽", link: "/tools/fuel-finder" },
            { name: "Rate Checker", icon: "💰", link: "/tools/rate-checker" },
            { name: "Mileage Calculator", icon: "📏", link: "/tools/mileage-calculator" },
            { name: "Load Board ROI Calculator", icon: "📊", link: "/tools/roi-calculator" },
            { name: "Find Loads", icon: "🚚", link: "/find-loads" },
            { name: "DOT Safer System", icon: "🛡️", link: "https://safer.fmcsa.dot.gov" }
        ],
        checklists: [
            "Maintenance Checklist",
            "Cybersecurity Checklist for Carriers",
            "Broker Carrier Relationship Checklist"
        ],
        podcasts: [
            { title: "The Future of FreTech", guest: "Kevin Rutherford", duration: "45 min", link: "/podcast/fretech" },
            { title: "AI in Logistics: Hype or Reality?", guest: "Sarah Chen", duration: "38 min", link: "/podcast/ai-logistics" },
            { title: "Cross-Border Shipping Essentials", guest: "Michael Torres", duration: "52 min", link: "/podcast/cross-border" }
        ],
        webinars: [
            { title: "AI Bots Panel: How GTS Uses AI", date: "April 10, 2026", link: "/webinars/ai-bots" },
            { title: "Freight Fraud Prevention Strategies", date: "April 5, 2026", link: "/webinars/fraud-prevention" },
            { title: "2026 Market Outlook", date: "March 28, 2026", link: "/webinars/market-outlook" }
        ]
    };

    const handleLoadSearchChange = (field, value) => {
        setLoadSearch((current) => ({ ...current, [field]: value }));
    };

    const handleFindLoads = () => {
        const params = new URLSearchParams();
        if (loadSearch.origin.trim()) params.set('origin', loadSearch.origin.trim());
        if (loadSearch.destination.trim()) params.set('destination', loadSearch.destination.trim());
        if (loadSearch.equipment.trim()) params.set('equipment', loadSearch.equipment.trim());
        navigate(`/find-loads${params.toString() ? `?${params.toString()}` : ''}`);
    };

    return (
        <div className="min-h-screen bg-cover bg-center bg-no-repeat" style={{ backgroundImage: `url(${bgLogin})` }}>
            <SeoHead
                title="Resources - GTS Logistics"
                description="Explore GTS Logistics resources, freight industry insights, webinars, podcasts, checklists, and tools for carriers, brokers, and shippers."
                keywords="logistics resources, freight tools, trucking guides, freight webinars, logistics blog"
                canonical="https://www.gtsdispatcher.com/resources"
                ogTitle="GTS Logistics Resources"
                ogDescription="Freight tools, webinars, guides, and industry resources from GTS Logistics."
                ogUrl="https://www.gtsdispatcher.com/resources"
                twitterTitle="GTS Logistics Resources"
                twitterDescription="Freight tools, webinars, guides, and industry resources from GTS Logistics."
            />
            <div className="min-h-screen bg-black/70">
                {/* Header */}
                <div className="container mx-auto px-4 py-4">
                    <div className="flex flex-wrap justify-between items-center gap-4">
                        <Link to="/">
                            <img src={gtsLogo} alt="GTS Logistics" className="h-12" />
                        </Link>

                        <div className="hidden md:flex items-center gap-6">
                            <Link to="/products" className="text-white hover:text-red-400 transition text-sm">Products</Link>
                            <Link to="/pricing" className="text-white hover:text-red-400 transition text-sm">Pricing</Link>
                            <Link to="/resources" className="text-red-400 text-sm font-semibold">Resources</Link>
                            <Link to="/about" className="text-white hover:text-red-400 transition text-sm">About</Link>
                            <Link to="/contact" className="text-white hover:text-red-400 transition text-sm">Contact</Link>
                        </div>

                        <div className="flex gap-3">
                            <Link to="/login" className="px-5 py-2 border border-white text-white rounded hover:bg-white/10 transition text-sm">LOG IN</Link>
                            <Link to="/register" className="px-5 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm">SIGN UP</Link>
                        </div>
                    </div>
                </div>

                {/* Hero Section */}
                <div className="container mx-auto px-4 py-12">
                    <div className="text-center mb-12">
                        <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">Trucking Mastery</h1>
                        <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                            Resources, tools, and insights to help you succeed in the logistics industry
                        </p>
                    </div>

                    {/* Featured Course Banner */}
                    <div className="bg-gradient-to-r from-red-900/40 to-black/60 rounded-xl p-8 mb-12 border border-red-500/30">
                        <div className="flex flex-col md:flex-row items-center gap-6">
                            <div className="text-5xl">🎓</div>
                            <div className="flex-1 text-center md:text-left">
                                <h2 className="text-2xl font-bold text-white mb-2">Trucking Mastery with Kevin Rutherford</h2>
                                <p className="text-gray-300 mb-3">An exclusive FREE course series designed with owner-operators and small fleet owners in mind.</p>
                                <div className="flex items-center gap-2 text-yellow-400 text-sm">
                                    <span>★ ★ ★ ★ ★</span>
                                    <span className="text-gray-400">"Kevin Rutherford's Certified Master Carrier (CMC) program has changed my business which pretty much changed my life."</span>
                                </div>
                                <p className="text-gray-400 text-sm mt-1">— Rick Russell</p>
                            </div>
                            <Link to="/resources/trucking-mastery" className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition whitespace-nowrap">
                                Enroll for Free →
                            </Link>
                        </div>
                    </div>

                    {/* Main Content Grid */}
                    <div className="grid lg:grid-cols-3 gap-8">
                        {/* Left Column - Blogs & Community */}
                        <div className="space-y-6">
                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl">📝</span>
                                    <h2 className="text-xl font-bold text-white">Blogs</h2>
                                </div>
                                <p className="text-gray-400 text-sm mb-4">Go deeper: In-depth articles on industry trends, tips and tricks, technology tools, and hot topics.</p>
                                <div className="space-y-3">
                                    {resources.blogs.map((blog, idx) => (
                                        <Link key={idx} to={blog.link} className="block border-b border-white/10 pb-2 last:border-0 hover:bg-white/5 p-2 rounded transition">
                                            <h3 className="text-white text-sm font-semibold">{blog.title}</h3>
                                            <p className="text-gray-400 text-xs">{blog.date}</p>
                                        </Link>
                                    ))}
                                </div>
                                <Link to="/blog" className="inline-flex items-center gap-1 text-red-400 text-sm mt-4 hover:underline">
                                    Browse all blogs <span>→</span>
                                </Link>
                            </div>

                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl">👥</span>
                                    <h2 className="text-xl font-bold text-white">Community</h2>
                                </div>
                                <p className="text-gray-400 text-sm mb-4">Network with like minds in the industry, get to know our products, and share knowledge and ideas.</p>
                                <Link to="/community" className="inline-flex items-center gap-1 text-red-400 text-sm hover:underline">
                                    Visit our community <span>→</span>
                                </Link>
                            </div>

                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl">🎙️</span>
                                    <h2 className="text-xl font-bold text-white">Podcasts</h2>
                                </div>
                                <p className="text-gray-400 text-sm mb-4">Listen and learn as industry experts share practical advice and tips for success.</p>
                                <div className="space-y-3">
                                    {resources.podcasts.map((podcast, idx) => (
                                        <Link key={idx} to={podcast.link} className="flex justify-between items-center border-b border-white/10 pb-2 last:border-0 hover:bg-white/5 p-2 rounded">
                                            <div>
                                                <h3 className="text-white text-sm font-semibold">{podcast.title}</h3>
                                                <p className="text-gray-400 text-xs">with {podcast.guest}</p>
                                            </div>
                                            <span className="text-gray-500 text-xs">{podcast.duration}</span>
                                        </Link>
                                    ))}
                                </div>
                                <Link to="/podcasts" className="inline-flex items-center gap-1 text-red-400 text-sm mt-4 hover:underline">
                                    Listen now <span>→</span>
                                </Link>
                            </div>
                        </div>

                        {/* Middle Column - Tools, Checklists, Webinars */}
                        <div className="space-y-6">
                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl">🛠️</span>
                                    <h2 className="text-xl font-bold text-white">Tools & References</h2>
                                </div>
                                <div className="grid grid-cols-2 gap-3 mb-4">
                                    {resources.tools.map((tool, idx) => (
                                        <a key={idx} href={tool.link} target={tool.link.startsWith('http') ? '_blank' : '_self'} rel="noopener noreferrer" className="flex items-center gap-2 text-gray-300 text-sm hover:text-red-400 transition p-2 rounded hover:bg-white/5">
                                            <span>{tool.icon}</span> {tool.name}
                                        </a>
                                    ))}
                                </div>
                            </div>

                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <h2 className="text-xl font-bold text-white mb-4">📋 Checklists</h2>
                                <ul className="space-y-2">
                                    {resources.checklists.map((item, idx) => (
                                        <li key={idx} className="flex items-center gap-2 text-gray-300 text-sm">
                                            <span className="text-green-400">✓</span> {item}
                                        </li>
                                    ))}
                                </ul>
                                <Link to="/resources/checklists" className="inline-flex items-center gap-1 text-red-400 text-sm mt-4 hover:underline">
                                    View all checklists <span>→</span>
                                </Link>
                            </div>

                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl">🎥</span>
                                    <h2 className="text-xl font-bold text-white">Webinars</h2>
                                </div>
                                <div className="space-y-3">
                                    {resources.webinars.map((webinar, idx) => (
                                        <Link key={idx} to={webinar.link} className="flex justify-between items-center border-b border-white/10 pb-2 last:border-0 hover:bg-white/5 p-2 rounded">
                                            <span className="text-white text-sm">{webinar.title}</span>
                                            <span className="text-gray-500 text-xs">{webinar.date}</span>
                                        </Link>
                                    ))}
                                </div>
                                <Link to="/webinars" className="inline-flex items-center gap-1 text-red-400 text-sm mt-4 hover:underline">
                                    View all webinars <span>→</span>
                                </Link>
                            </div>
                        </div>

                        {/* Right Column - Fraud Prevention, Stories, Press */}
                        <div className="space-y-6">
                            <div className="bg-red-600/20 backdrop-blur-sm rounded-xl p-6 border border-red-500">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl">🚨</span>
                                    <h2 className="text-xl font-bold text-white">Freight Fraud Prevention</h2>
                                </div>
                                <p className="text-gray-300 text-sm mb-4">Discover how carriers and brokers can avoid fraud in the trucking industry.</p>
                                <Link to="/fraud-prevention" className="inline-flex items-center gap-1 text-red-400 text-sm hover:underline">
                                    View resource <span>→</span>
                                </Link>
                            </div>

                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl">📖</span>
                                    <h2 className="text-xl font-bold text-white">Stories</h2>
                                </div>
                                <p className="text-gray-400 text-sm mb-4">See how others in the industry are overcoming obstacles and experiencing success in our case studies.</p>
                                <Link to="/stories" className="inline-flex items-center gap-1 text-red-400 text-sm hover:underline">
                                    View stories <span>→</span>
                                </Link>
                            </div>

                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl">📰</span>
                                    <h2 className="text-xl font-bold text-white">Press</h2>
                                </div>
                                <p className="text-gray-400 text-sm mb-4">People are talking. Get in on the buzz.</p>
                                <Link to="/press" className="inline-flex items-center gap-1 text-red-400 text-sm hover:underline">
                                    Press releases <span>→</span>
                                </Link>
                            </div>

                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl">⚠️</span>
                                    <h2 className="text-xl font-bold text-white">Alerts</h2>
                                </div>
                                <p className="text-gray-400 text-sm mb-4">Keep your eyes and ears open. Find and post security alerts.</p>
                                <Link to="/alerts" className="inline-flex items-center gap-1 text-red-400 text-sm hover:underline">
                                    See alerts <span>→</span>
                                </Link>
                            </div>

                            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                                <div className="flex items-center gap-2 mb-4">
                                    <span className="text-2xl">🌍</span>
                                    <h2 className="text-xl font-bold text-white">Emergency Freight</h2>
                                </div>
                                <p className="text-gray-400 text-sm mb-4">Information on natural disasters, FEMA response, government regulations, and more.</p>
                                <Link to="/emergency" className="inline-flex items-center gap-1 text-red-400 text-sm hover:underline">
                                    Get Info <span>→</span>
                                </Link>
                            </div>

                            <div className="bg-gradient-to-r from-red-900/30 to-black/40 rounded-xl p-6 border border-red-500/30">
                                <h2 className="text-xl font-bold text-white mb-3">🤝 Partners</h2>
                                <p className="text-gray-300 text-sm mb-4">Become a GTS partner. Find the partner program that works for you.</p>
                                <Link to="/partners" className="inline-flex items-center gap-1 text-red-400 text-sm hover:underline">
                                    Get started <span>→</span>
                                </Link>
                            </div>
                        </div>
                    </div>

                    {/* Search Loads Section */}
                    <div className="mt-12 bg-white/5 rounded-xl p-6">
                        <div className="text-center mb-6">
                            <h2 className="text-2xl font-bold text-white">Loads await!</h2>
                        </div>
                        <div className="grid md:grid-cols-3 gap-4">
                            <div className="relative">
                                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">📍</span>
                                <input type="text" placeholder="Origin" value={loadSearch.origin} onChange={(e) => handleLoadSearchChange('origin', e.target.value)} className="w-full pl-10 pr-3 py-3 bg-black/50 border border-white/20 rounded-lg text-white placeholder-gray-400" />
                            </div>
                            <div className="relative">
                                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">📍</span>
                                <input type="text" placeholder="Destination" value={loadSearch.destination} onChange={(e) => handleLoadSearchChange('destination', e.target.value)} className="w-full pl-10 pr-3 py-3 bg-black/50 border border-white/20 rounded-lg text-white placeholder-gray-400" />
                            </div>
                            <div className="relative">
                                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">🚛</span>
                                <select value={loadSearch.equipment} onChange={(e) => handleLoadSearchChange('equipment', e.target.value)} className="w-full pl-10 pr-3 py-3 bg-black/50 border border-white/20 rounded-lg text-white">
                                    <option value="">Equipment Type</option>
                                    <option>Flatbed</option>
                                    <option>Dry Van</option>
                                    <option>Reefer</option>
                                    <option>Heavy Haul</option>
                                </select>
                            </div>
                        </div>
                        <button onClick={handleFindLoads} className="w-full mt-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
                            FIND LOADS
                        </button>
                    </div>

                    {/* FAQ Section */}
                    <div className="mt-12 bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                        <h2 className="text-xl font-bold text-white mb-6 text-center">Frequently Asked Questions</h2>
                        <div className="grid md:grid-cols-2 gap-4">
                            <details className="group">
                                <summary className="text-white font-semibold cursor-pointer list-none flex justify-between items-center p-3 bg-white/5 rounded-lg">
                                    How do I get started with GTS?
                                    <span className="group-open:rotate-180 transition">▼</span>
                                </summary>
                                <p className="text-gray-300 text-sm p-3">Sign up for an account, choose your plan, and start finding loads immediately. Our support team is available 24/7 to assist you.</p>
                            </details>
                            <details className="group">
                                <summary className="text-white font-semibold cursor-pointer list-none flex justify-between items-center p-3 bg-white/5 rounded-lg">
                                    What payment methods do you accept?
                                    <span className="group-open:rotate-180 transition">▼</span>
                                </summary>
                                <p className="text-gray-300 text-sm p-3">We accept credit cards, bank transfers, and factoring services. Contact our billing team for custom arrangements.</p>
                            </details>
                            <details className="group">
                                <summary className="text-white font-semibold cursor-pointer list-none flex justify-between items-center p-3 bg-white/5 rounded-lg">
                                    How does the AI bot system work?
                                    <span className="group-open:rotate-180 transition">▼</span>
                                </summary>
                                <p className="text-gray-300 text-sm p-3">Our AI bots automate operations, finance, safety, and customer service. Each bot handles specific tasks, working together as a virtual team.</p>
                            </details>
                            <details className="group">
                                <summary className="text-white font-semibold cursor-pointer list-none flex justify-between items-center p-3 bg-white/5 rounded-lg">
                                    Is GTS available in my country?
                                    <span className="group-open:rotate-180 transition">▼</span>
                                </summary>
                                <p className="text-gray-300 text-sm p-3">GTS is available worldwide except in restricted countries. Contact us to verify availability in your region.</p>
                            </details>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="container mx-auto px-4 py-6 border-t border-white/20 mt-8">
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

export default Resources;
