import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import bgLogin from '../assets/bg-login.jpg';
import gtsLogo from '../assets/gts-logo.png';

const Products = () => {
    const [activeCategory, setActiveCategory] = useState('all');

    const categories = [
        { id: 'all', name: 'All Products', icon: '📦' },
        { id: 'loadBoard', name: 'Load Boards', icon: '🚛' },
        { id: 'aiBot', name: 'AI Bots', icon: '🤖' },
        { id: 'financial', name: 'Financial Services', icon: '💰' },
        { id: 'technology', name: 'Technology & Data', icon: '💻' },
        { id: 'compliance', name: 'Compliance & Safety', icon: '🛡️' }
    ];

    const products = {
        loadBoards: [
            {
                id: 'gts-loadboard',
                name: 'GTS Load Board',
                description: 'Comprehensive load board with AI-powered matching and real-time pricing.',
                icon: '🚛',
                features: ['AI load matching', 'Real-time pricing', 'Carrier network', 'Mobile app'],
                price: 'Free to $99/month',
                link: '/products/loadboard',
                popular: true
            },
            {
                id: 'truckstop-com',
                name: 'Truckstop.com',
                description: 'Industry-leading load board with extensive carrier and shipper network.',
                icon: '🛣️',
                features: ['Large network', 'Load posting', 'Rate insights', 'Fuel cards'],
                price: 'Contact sales',
                link: '/products/truckstop'
            },
            {
                id: 'dat-loadboard',
                name: 'DAT Load Board',
                description: 'Premium load board with advanced analytics and carrier verification.',
                icon: '📊',
                features: ['Carrier verification', 'Advanced analytics', 'Insurance checking', 'Credit reports'],
                price: '$99/month',
                link: '/products/dat'
            },
            {
                id: '123loadboard',
                name: '123LoadBoard',
                description: 'User-friendly load board with integrated dispatch and tracking.',
                icon: '🔢',
                features: ['Easy interface', 'Dispatch integration', 'GPS tracking', 'Customer support'],
                price: '$49/month',
                link: '/products/123loadboard'
            }
        ],
        aiBots: [
            {
                id: 'ai-freight-broker',
                name: 'AI Freight Broker',
                description: 'Automated load matching, rate negotiation, and carrier discovery powered by AI.',
                icon: '🤖',
                features: ['Smart load matching', 'Rate optimization', 'Carrier sourcing', '24/7 operation'],
                price: 'Included in Pro',
                link: '/ai-bots/freight-broker',
                popular: true
            },
            {
                id: 'ai-operations-manager',
                name: 'AI Operations Manager',
                description: 'Automate dispatch, route planning, and fleet coordination.',
                icon: '⚙️',
                features: ['Dispatch automation', 'Route optimization', 'Real-time tracking', 'Performance analytics'],
                price: 'Included in Pro',
                link: '/ai-bots/operations-manager'
            },
            {
                id: 'ai-finance-bot',
                name: 'AI Finance Bot',
                description: 'Automated invoicing, expense tracking, and financial analytics.',
                icon: '💰',
                features: ['Invoice processing', 'Expense tracking', 'Profit analysis', 'Cash flow forecasting'],
                price: 'Included in Premium',
                link: '/ai-bots/finance'
            },
            {
                id: 'ai-documents-manager',
                name: 'AI Documents Manager',
                description: 'OCR-powered document processing with expiry alerts and secure storage.',
                icon: '📄',
                features: ['Document digitization', 'Expiry alerts', 'Secure storage', 'Compliance tracking'],
                price: 'Included in Pro',
                link: '/ai-bots/documents'
            },
            {
                id: 'ai-safety-manager',
                name: 'AI Safety Manager',
                description: 'Compliance monitoring, incident tracking, and safety analytics.',
                icon: '🛡️',
                features: ['Safety compliance', 'Incident tracking', 'Risk assessment', 'FMCSA reporting'],
                price: 'Included in Premium',
                link: '/ai-bots/safety'
            },
            {
                id: 'ai-legal-consultant',
                name: 'AI Legal Consultant',
                description: 'Contract review, compliance checks, and regulatory updates.',
                icon: '⚖️',
                features: ['Contract review', 'Compliance alerts', 'Legal updates', 'Risk mitigation'],
                price: 'Included in Premium',
                link: '/ai-bots/legal'
            },
            {
                id: 'ai-security-manager',
                name: 'AI Security Manager',
                description: 'Threat detection, access control, and security auditing.',
                icon: '🔒',
                features: ['Threat detection', 'Access control', 'Security auditing', 'Incident response'],
                price: 'Included in Premium',
                link: '/ai-bots/security'
            },
            {
                id: 'ai-customer-service',
                name: 'AI Customer Service',
                description: '24/7 customer support with intelligent query resolution.',
                icon: '🎧',
                features: ['24/7 support', 'Query resolution', 'Multi-language', 'CRM integration'],
                price: 'Included in Pro',
                link: '/ai-bots/customer-service'
            }
        ],
        financial: [
            {
                id: 'factoring-services',
                name: 'Factoring Services',
                description: 'Fast invoice factoring with competitive rates and flexible terms.',
                icon: '💳',
                features: ['Fast funding', 'Competitive rates', 'Flexible terms', 'Online portal'],
                price: '1-3% fee',
                link: '/products/factoring'
            },
            {
                id: 'insurance-brokerage',
                name: 'Insurance Brokerage',
                description: 'Comprehensive insurance solutions for carriers and shippers.',
                icon: '🛡️',
                features: ['Cargo insurance', 'Liability coverage', 'Claims processing', 'Risk assessment'],
                price: 'Contact sales',
                link: '/products/insurance'
            },
            {
                id: 'fuel-cards',
                name: 'Fuel Cards',
                description: 'Discounted fuel prices with nationwide network and detailed reporting.',
                icon: '⛽',
                features: ['Discounted fuel', 'Nationwide network', 'Detailed reporting', 'Fleet management'],
                price: 'Contact sales',
                link: '/products/fuel-cards'
            },
            {
                id: 'credit-reports',
                name: 'Credit Reports',
                description: 'Comprehensive credit reports for carriers and shippers.',
                icon: '📊',
                features: ['Carrier credit', 'Shipper credit', 'Payment history', 'Risk scoring'],
                price: '$25/report',
                link: '/products/credit-reports'
            }
        ],
        technology: [
            {
                id: 'telematics',
                name: 'Telematics',
                description: 'GPS tracking, fuel monitoring, and driver behavior analytics.',
                icon: '📡',
                features: ['GPS tracking', 'Fuel monitoring', 'Driver behavior', 'Maintenance alerts'],
                price: '$49/month',
                link: '/products/telematics'
            },
            {
                id: 'eld-systems',
                name: 'ELD Systems',
                description: 'Electronic logging devices for HOS compliance and record keeping.',
                icon: '📱',
                features: ['HOS compliance', 'Automated logging', 'FMCSA reports', 'Driver management'],
                price: '$39/month',
                link: '/products/eld'
            },
            {
                id: 'api-integration',
                name: 'API Integration',
                description: 'Seamless integration with existing TMS and accounting systems.',
                icon: '🔗',
                features: ['TMS integration', 'Accounting sync', 'Real-time data', 'Custom APIs'],
                price: 'Contact sales',
                link: '/products/api'
            },
            {
                id: 'rmis',
                name: 'RMIS',
                description: 'Risk management information system for safety and claims tracking.',
                icon: '📈',
                features: ['Incident tracking', 'Claims management', 'Safety analytics', 'Compliance reporting'],
                price: 'Included in Premium',
                link: '/products/rmis'
            },
            {
                id: 'saferwatch',
                name: 'SaferWatch',
                description: 'Continuous carrier monitoring with real-time alerts for safety and compliance changes.',
                icon: '👁️',
                features: ['Continuous monitoring', 'Real-time alerts', 'Compliance tracking', 'Safety scores'],
                price: 'Included in Premium',
                link: '/products/saferwatch'
            }
        ],
        compliance: [
            {
                id: 'fincen-reporting',
                name: 'FinCEN Reporting',
                description: 'Automated financial crime reporting and compliance with US Treasury regulations.',
                icon: '🏦',
                features: ['CTR filing', 'SAR reporting', 'Automated compliance', 'Audit trails'],
                price: 'Contact sales',
                link: '/products/fincen'
            },
            {
                id: 'fmcsa-compliance',
                name: 'FMCSA Compliance',
                description: 'Stay compliant with FMCSA regulations including HOS, ELD, and safety monitoring.',
                icon: '📋',
                features: ['HOS tracking', 'ELD integration', 'Safety monitoring', 'Audit preparation'],
                price: 'Included in Premium',
                link: '/products/fmcsa'
            },
            {
                id: 'insurance-verification',
                name: 'Insurance Verification',
                description: 'Automated carrier insurance verification and expiration alerts.',
                icon: '🛡️',
                features: ['COI verification', 'Expiration alerts', 'Coverage validation', 'Document storage'],
                price: 'Included in Pro',
                link: '/products/insurance'
            }
        ]
    };

    const getProductsByCategory = (category) => {
        switch (category) {
            case 'all':
                return [
                    ...products.loadBoards,
                    ...products.aiBots,
                    ...products.financial,
                    ...products.technology,
                    ...products.compliance
                ];
            case 'loadBoard':
                return products.loadBoards;
            case 'aiBot':
                return products.aiBots;
            case 'financial':
                return products.financial;
            case 'technology':
                return products.technology;
            case 'compliance':
                return products.compliance;
            default:
                return [];
        }
    };

    const filteredProducts = getProductsByCategory(activeCategory);

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

                {/* Hero */}
                <div className="container mx-auto px-4 py-12 text-center">
                    <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">GTS Logistics Products</h1>
                    <p className="text-xl text-gray-300 max-w-2xl mx-auto">
                        AI-powered solutions for freight brokerage, fleet management, compliance, and finance.
                    </p>
                </div>

                {/* Categories */}
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
                                    {product.popular && (
                                        <span className="bg-red-600 text-white text-xs px-2 py-1 rounded-full">Popular</span>
                                    )}
                                    {product.badge && (
                                        <span className="bg-blue-600 text-white text-xs px-2 py-1 rounded-full">{product.badge}</span>
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
                                    {product.features.length > 3 && (
                                        <li className="text-gray-500 text-xs">+{product.features.length - 3} more features</li>
                                    )}
                                </ul>
                                <div className="flex items-center justify-between mt-4 pt-4 border-t border-white/10">
                                    <span className="text-red-400 text-sm font-semibold">{product.price}</span>
                                    <Link to={product.link} className="inline-flex items-center gap-1 text-white text-sm hover:text-red-400 transition">
                                        Learn more <span>→</span>
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* AI Bots Panel Highlight */}
                <div className="container mx-auto px-4 py-12">
                    <div className="bg-gradient-to-r from-red-900/30 to-black/60 rounded-xl p-8">
                        <div className="text-center mb-8">
                            <h2 className="text-3xl font-bold text-white mb-2">AI Bots Panel</h2>
                            <p className="text-gray-300">A virtual team of AI agents working together to automate your logistics operations</p>
                        </div>
                        <div className="grid grid-cols-4 md:grid-cols-8 gap-4">
                            {products.aiBots.slice(0, 8).map((bot, idx) => (
                                <Link key={idx} to={bot.link} className="text-center group">
                                    <div className="w-12 h-12 mx-auto bg-red-500/20 rounded-full flex items-center justify-center mb-2 group-hover:bg-red-500/40 transition">
                                        <span className="text-xl">{bot.icon}</span>
                                    </div>
                                    <p className="text-white text-xs group-hover:text-red-400 transition">{bot.name.split(' ').slice(1).join(' ') || bot.name}</p>
                                </Link>
                            ))}
                        </div>
                        <div className="text-center mt-6">
                            <Link to="/ai-bots" className="inline-flex items-center gap-1 text-red-400 hover:underline">
                                Explore all AI Bots →
                            </Link>
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
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Products;