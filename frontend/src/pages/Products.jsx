import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import gtsLogo from '../assets/gabani_logo.png';
import bgLogin from '../assets/bg_login.png';

const Products = () => {
    const [activeCategory, setActiveCategory] = useState('all');

    const products = {
        // Load Boards & Freight Matching
        loadBoards: [
            {
                id: 'carrier-load-board',
                name: 'Carrier Load Board',
                description: 'Find high-paying loads with real-time matching. Search by lane, equipment, and rate.',
                icon: '🚛',
                features: ['Real-time load matching', 'Rate insights', 'Carrier performance rating'],
                link: '/products/carrier-load-board',
                category: 'loadBoard'
            },
            {
                id: 'broker-load-board',
                name: 'Broker Load Board',
                description: 'Post loads, find qualified carriers, and manage your freight network.',
                icon: '📊',
                features: ['Post unlimited loads', 'Carrier search', 'Load insights', 'Private loads'],
                link: '/products/broker-load-board',
                category: 'loadBoard'
            },
            {
                id: 'shipper-load-board',
                name: 'Shipper Load Board',
                description: 'Connect with reliable carriers and move your freight efficiently.',
                icon: '📦',
                features: ['Post shipments', 'Carrier discovery', 'Rate benchmarking'],
                link: '/products/shipper-load-board',
                category: 'loadBoard'
            },
            {
                id: 'mapleload-canada',
                name: 'MapleLoad Canada',
                description: 'Canadian freight marketplace with cross-border capabilities and AI-powered load matching.',
                icon: '🍁',
                features: ['Canadian loads', 'Cross-border shipping', 'Carrier verification'],
                link: '/products/mapleload-canada',
                category: 'loadBoard'
            }
        ],
        // AI Bots
        aiBots: [
            {
                id: 'ai-freight-broker',
                name: 'AI Freight Broker',
                description: 'Automated load matching, rate negotiation, and carrier discovery powered by AI.',
                icon: '🤖',
                features: ['Smart load matching', 'Rate optimization', 'Carrier sourcing'],
                link: '/ai-bots/freight-broker',
                category: 'aiBot'
            },
            {
                id: 'ai-operations-manager',
                name: 'AI Operations Manager',
                description: 'Automate dispatch, route planning, and fleet coordination.',
                icon: '⚙️',
                features: ['Dispatch automation', 'Route optimization', 'Real-time tracking'],
                link: '/ai-bots/operations-manager',
                category: 'aiBot'
            },
            {
                id: 'ai-finance-bot',
                name: 'AI Finance Bot',
                description: 'Automated invoicing, expense tracking, and financial analytics.',
                icon: '💰',
                features: ['Invoice processing', 'Expense tracking', 'Profit analysis'],
                link: '/ai-bots/finance',
                category: 'aiBot'
            },
            {
                id: 'ai-documents-manager',
                name: 'AI Documents Manager',
                description: 'OCR-powered document processing with expiry alerts and secure storage.',
                icon: '📄',
                features: ['Document digitization', 'Expiry alerts', 'Secure storage'],
                link: '/ai-bots/documents',
                category: 'aiBot'
            },
            {
                id: 'ai-safety-manager',
                name: 'AI Safety Manager',
                description: 'Compliance monitoring, incident tracking, and safety analytics.',
                icon: '🛡️',
                features: ['Safety compliance', 'Incident tracking', 'Risk assessment'],
                link: '/ai-bots/safety',
                category: 'aiBot'
            },
            {
                id: 'ai-legal-consultant',
                name: 'AI Legal Consultant',
                description: 'Contract review, compliance checks, and regulatory updates.',
                icon: '⚖️',
                features: ['Contract review', 'Compliance alerts', 'Legal updates'],
                link: '/ai-bots/legal',
                category: 'aiBot'
            },
            {
                id: 'ai-security-manager',
                name: 'AI Security Manager',
                description: 'Threat detection, access control, and security auditing.',
                icon: '🔒',
                features: ['Threat detection', 'Access control', 'Audit logging'],
                link: '/ai-bots/security',
                category: 'aiBot'
            },
            {
                id: 'ai-general-manager',
                name: 'AI General Manager',
                description: 'Executive insights, performance analytics, and strategic recommendations.',
                icon: '👔',
                features: ['Performance reports', 'Strategic insights', 'KPI monitoring'],
                link: '/ai-bots/general-manager',
                category: 'aiBot'
            }
        ],
        // Financial & Payment
        financial: [
            {
                id: 'factoring',
                name: 'Carrier Factoring',
                description: 'Get paid faster with same-day funding and competitive rates.',
                icon: '💵',
                features: ['Same-day funding', 'Competitive rates', 'No long-term contracts'],
                link: '/products/factoring',
                category: 'financial'
            },
            {
                id: 'fuel-card',
                name: 'GTS Fuel Card',
                description: 'Save up to $1 per gallon with nationwide fuel discounts.',
                icon: '⛽',
                features: ['Fuel discounts', 'No credit check', 'Nationwide network'],
                link: '/products/fuel-card',
                category: 'financial'
            },
            {
                id: 'payment-gateway',
                name: 'SUDAPAY Payment Gateway',
                description: 'Secure payment processing for Sudanese Pound (SDG) and USD.',
                icon: '💳',
                features: ['Multi-currency support', 'Secure processing', 'Real-time settlement'],
                link: '/products/sudapay',
                category: 'financial'
            }
        ],
        // Technology & Data
        technology: [
            {
                id: 'rate-insights',
                name: 'Rate Insights',
                description: 'Real-time market rates, historical data, and predictive analytics.',
                icon: '📈',
                features: ['Spot market rates', 'Historical trends', 'Rate forecasts'],
                link: '/products/rate-insights',
                category: 'technology'
            },
            {
                id: 'tms',
                name: 'GTS TMS',
                description: 'Complete transportation management system for carriers, brokers, and shippers.',
                icon: '📋',
                features: ['Order management', 'Dispatch', 'Billing', 'Analytics'],
                link: '/products/tms',
                category: 'technology'
            },
            {
                id: 'rmis',
                name: 'RMIS Carrier Onboarding',
                description: 'Streamline carrier onboarding with automated verification and compliance checks.',
                icon: '✅',
                features: ['Automated verification', 'Compliance checks', 'Document management'],
                link: '/products/rmis',
                category: 'technology'
            },
            {
                id: 'saferwatch',
                name: 'SaferWatch',
                description: 'Continuous carrier monitoring with real-time alerts for safety and compliance changes.',
                icon: '👁️',
                features: ['Continuous monitoring', 'Real-time alerts', 'Compliance tracking'],
                link: '/products/saferwatch',
                category: 'technology'
            }
        ]
    };

    const categories = [
        { id: 'all', name: 'All Products', icon: '🔍' },
        { id: 'loadBoard', name: 'Load Boards', icon: '🚚' },
        { id: 'aiBot', name: 'AI Bots', icon: '🤖' },
        { id: 'financial', name: 'Financial', icon: '💰' },
        { id: 'technology', name: 'Technology & Data', icon: '📊' }
    ];

    const getAllProducts = () => {
        return [
            ...products.loadBoards,
            ...products.aiBots,
            ...products.financial,
            ...products.technology
        ];
    };

    const filteredProducts = activeCategory === 'all'
        ? getAllProducts()
        : getAllProducts().filter(p => p.category === activeCategory);

    return (
        <div className="min-h-screen bg-cover bg-center bg-no-repeat" style={{ backgroundImage: `url(${bgLogin})` }}>
            <div className="min-h-screen bg-black/70">
                {/* Header */}
                <div className="container mx-auto px-4 py-4">
                    <div className="flex flex-wrap justify-between items-center gap-4">
                        <Link to="/">
                            <img src={gtsLogo} alt="GTS Logistics" className="h-12" />
                        </Link>

                        <div className="hidden md:flex items-center gap-6">
                            <Link to="/products" className="text-red-400 text-sm font-semibold">Products</Link>
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

                {/* Hero Section */}
                <div className="container mx-auto px-4 py-12 text-center">
                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">GTS Logistics Products</h1>
                    <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                        AI-powered solutions for freight brokerage, fleet management, compliance, and finance.
                    </p>
                </div>

                {/* Category Tabs */}
                <div className="container mx-auto px-4">
                    <div className="flex flex-wrap justify-center gap-2 mb-8">
                        {categories.map(cat => (
                            <button
                                key={cat.id}
                                onClick={() => setActiveCategory(cat.id)}
                                className={`px-5 py-2 rounded-full transition flex items-center gap-2 ${activeCategory === cat.id
                                        ? 'bg-red-600 text-white'
                                        : 'bg-white/10 text-gray-300 hover:bg-white/20'
                                    }`}
                            >
                                <span>{cat.icon}</span>
                                {cat.name}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Products Grid */}
                <div className="container mx-auto px-4 py-8">
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {filteredProducts.map((product, idx) => (
                            <div key={idx} className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:border-red-500/50 transition group">
                                <div className="flex items-start justify-between mb-4">
                                    <div className="text-4xl">{product.icon}</div>
                                    {product.id === 'ai-freight-broker' && (
                                        <span className="bg-red-600 text-white text-xs px-2 py-1 rounded-full">AI-Powered</span>
                                    )}
                                    {product.id === 'mapleload-canada' && (
                                        <span className="bg-green-600 text-white text-xs px-2 py-1 rounded-full">🇨🇦 Canada</span>
                                    )}
                                </div>
                                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-red-400 transition">
                                    {product.name}
                                </h3>
                                <p className="text-gray-300 text-sm mb-4">{product.description}</p>
                                <ul className="space-y-1 mb-4">
                                    {product.features.slice(0, 3).map((feature, i) => (
                                        <li key={i} className="flex items-center gap-2 text-gray-400 text-xs">
                                            <span className="text-green-400">✓</span> {feature}
                                        </li>
                                    ))}
                                </ul>
                                <Link to={product.link} className="inline-flex items-center gap-1 text-red-400 text-sm hover:underline">
                                    Learn more <span>→</span>
                                </Link>
                            </div>
                        ))}
                    </div>
                </div>

                {/* AI Bots Panel Section */}
                <div className="container mx-auto px-4 py-12">
                    <div className="bg-gradient-to-r from-red-900/30 to-black/60 rounded-xl p-8">
                        <div className="text-center mb-8">
                            <h2 className="text-3xl font-bold text-white mb-2">AI Bots Panel</h2>
                            <p className="text-gray-300">A virtual team of AI agents working together to automate your logistics operations</p>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4">
                            <div className="text-center">
                                <div className="w-12 h-12 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-2">
                                    <span className="text-xl">🚛</span>
                                </div>
                                <p className="text-white text-xs">Freight Broker</p>
                            </div>
                            <div className="text-center">
                                <div className="w-12 h-12 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-2">
                                    <span className="text-xl">⚙️</span>
                                </div>
                                <p className="text-white text-xs">Operations</p>
                            </div>
                            <div className="text-center">
                                <div className="w-12 h-12 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-2">
                                    <span className="text-xl">💰</span>
                                </div>
                                <p className="text-white text-xs">Finance</p>
                            </div>
                            <div className="text-center">
                                <div className="w-12 h-12 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-2">
                                    <span className="text-xl">📄</span>
                                </div>
                                <p className="text-white text-xs">Documents</p>
                            </div>
                            <div className="text-center">
                                <div className="w-12 h-12 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-2">
                                    <span className="text-xl">🛡️</span>
                                </div>
                                <p className="text-white text-xs">Safety</p>
                            </div>
                            <div className="text-center">
                                <div className="w-12 h-12 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-2">
                                    <span className="text-xl">⚖️</span>
                                </div>
                                <p className="text-white text-xs">Legal</p>
                            </div>
                            <div className="text-center">
                                <div className="w-12 h-12 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-2">
                                    <span className="text-xl">🔒</span>
                                </div>
                                <p className="text-white text-xs">Security</p>
                            </div>
                            <div className="text-center">
                                <div className="w-12 h-12 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-2">
                                    <span className="text-xl">👔</span>
                                </div>
                                <p className="text-white text-xs">General Manager</p>
                            </div>
                        </div>
                        <div className="text-center mt-6">
                            <Link to="/ai-bots" className="inline-flex items-center gap-1 text-red-400 hover:underline">
                                Explore all AI Bots →
                            </Link>
                        </div>
                    </div>
                </div>

                {/* Integration Partners */}
                <div className="container mx-auto px-4 py-8">
                    <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                        <h3 className="text-xl font-bold text-white text-center mb-6">Integration Partners</h3>
                        <div className="flex flex-wrap justify-center gap-8">
                            <div className="text-center">
                                <div className="w-16 h-16 bg-white/10 rounded-lg flex items-center justify-center mx-auto mb-2">
                                    <span className="text-2xl">📦</span>
                                </div>
                                <p className="text-gray-400 text-xs">QuickBooks</p>
                            </div>
                            <div className="text-center">
                                <div className="w-16 h-16 bg-white/10 rounded-lg flex items-center justify-center mx-auto mb-2">
                                    <span className="text-2xl">📊</span>
                                </div>
                                <p className="text-gray-400 text-xs">Salesforce</p>
                            </div>
                            <div className="text-center">
                                <div className="w-16 h-16 bg-white/10 rounded-lg flex items-center justify-center mx-auto mb-2">
                                    <span className="text-2xl">🗺️</span>
                                </div>
                                <p className="text-gray-400 text-xs">Google Maps</p>
                            </div>
                            <div className="text-center">
                                <div className="w-16 h-16 bg-white/10 rounded-lg flex items-center justify-center mx-auto mb-2">
                                    <span className="text-2xl">💳</span>
                                </div>
                                <p className="text-gray-400 text-xs">SUDAPAY</p>
                            </div>
                            <div className="text-center">
                                <div className="w-16 h-16 bg-white/10 rounded-lg flex items-center justify-center mx-auto mb-2">
                                    <span className="text-2xl">🔒</span>
                                </div>
                                <p className="text-gray-400 text-xs">FMCSA</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* CTA Section */}
                <div className="container mx-auto px-4 py-12">
                    <div className="bg-gradient-to-r from-red-800/50 to-black/60 rounded-xl p-8 text-center">
                        <h3 className="text-2xl font-bold text-white mb-4">Ready to transform your logistics operations?</h3>
                        <p className="text-gray-300 mb-6">Join thousands of carriers, brokers, and shippers using GTS Logistics</p>
                        <div className="flex flex-wrap justify-center gap-4">
                            <Link to="/register" className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
                                Start Free Trial
                            </Link>
                            <Link to="/contact" className="px-6 py-3 border border-white text-white rounded-lg hover:bg-white/10 transition">
                                Contact Sales
                            </Link>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="container mx-auto px-4 py-6 border-t border-white/20 mt-8">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                        <p className="text-gray-400 text-xs">© 2026 Gabani Transport Solutions LLC – All rights reserved.</p>
                        <div className="flex gap-4 text-xs">
                            <Link to="/privacy" className="text-gray-400 hover:text-white transition">Privacy Policy</Link>
                            <Link to="/terms" className="text-gray-400 hover:text-white transition">Terms of Service</Link>
                            <Link to="/legal" className="text-gray-400 hover:text-white transition">Legal Agreements</Link>
                        </div>
                        <p className="text-gray-500 text-xs">
                            📞 <a href="tel:+17786518297" className="hover:text-white">+1 (778) 651-8297</a>
                        </p>
                    </div>
                    <div className="text-center text-gray-500 text-xs mt-2">
                        329 HOWE ST UNIT #957, VANCOUVER BC V6C 3N2, CANADA
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Products;