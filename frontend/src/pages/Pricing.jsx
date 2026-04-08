import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import gtsLogo from '../assets/gabani_logo.png';
import bgLogin from '../assets/bg_login.png';
import SeoHead from '../components/SeoHead';

const Pricing = () => {
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [userType, setUserType] = useState('carrier');
  const CAD_PER_USD = 1.37;

  // Competitive pricing for market entry
  const pricingPlans = {
    carrier: {
      basic: {
        monthly: 19,
        yearly: 199,
        features: [
          'Load Search (unlimited)',
          'Truck Post (unlimited)',
          'Basic Rate Insights',
          'Email Support',
          'Mobile App Access'
        ],
        popular: false
      },
      pro: {
        monthly: 49,
        yearly: 499,
        features: [
          'Everything in Basic',
          'Advanced Rate Insights',
          'Book It Now',
          'Real-Time Live Loads',
          'Broker Rating System',
          'Priority Support',
          'API Access'
        ],
        popular: true
      },
      premium: {
        monthly: 99,
        yearly: 999,
        features: [
          'Everything in Pro',
          'Carrier Monitoring (SaferWatch)',
          'Predictive Carrier Sourcing',
          'Multi-Trip Search',
          'Fuel Card Discounts',
          'Dedicated Account Manager',
          '24/7 Priority Support',
          'Advanced Analytics Dashboard'
        ],
        popular: false
      }
    },
    broker: {
      basic: {
        monthly: 29,
        yearly: 299,
        features: [
          'Load Board Access',
          'Basic Analytics',
          'Carrier Search',
          'Email Support',
          'Post Unlimited Loads'
        ],
        popular: false
      },
      pro: {
        monthly: 79,
        yearly: 799,
        features: [
          'Everything in Basic',
          'Rate Insights',
          'Risk Factors',
          'Carrier Performance Rating',
          'Load Insights',
          'API Access',
          'Priority Support'
        ],
        popular: true
      },
      premium: {
        monthly: 149,
        yearly: 1499,
        features: [
          'Everything in Pro',
          'Carrier Monitoring',
          'Predictive Sourcing',
          'RMIS Integration',
          'Custom Reporting',
          'Dedicated Account Manager',
          '24/7 Priority Support',
          'Advanced AI Analytics'
        ],
        popular: false
      }
    },
    shipper: {
      basic: {
        monthly: 29,
        yearly: 299,
        features: [
          'Load Posting',
          'Basic Tracking',
          'Carrier Search',
          'Email Support'
        ],
        popular: false
      },
      pro: {
        monthly: 79,
        yearly: 799,
        features: [
          'Everything in Basic',
          'Rate Insights',
          'Carrier Performance Rating',
          'Real-Time Updates',
          'Load Insights',
          'API Access'
        ],
        popular: true
      },
      premium: {
        monthly: 149,
        yearly: 1499,
        features: [
          'Everything in Pro',
          'TMS Integration',
          'Advanced Analytics',
          'Dedicated Support',
          'Custom Workflows',
          '24/7 Priority Support',
          'Multi-User Access (5 users)'
        ],
        popular: false
      }
    }
  };

  // TMS Pricing (Backend System)
  const tmsPlans = [
    { name: 'FREE', price: 0, users: 1, vehicles: 1, features: ['GPS Tracking', 'Basic Invoicing'] },
    { name: 'STARTER', price: 5, users: 3, vehicles: 5, features: ['Trip Management', 'Real-time Tracking', 'Email Support'] },
    { name: 'GROWTH', price: 12, users: 7, vehicles: 15, features: ['Driver Coordination', 'Smart Alerts', 'API Access'] },
    { name: 'PROFESSIONAL', price: 25, users: 15, vehicles: 40, features: ['Advanced Analytics', 'Document Management', 'Priority Support'] },
    { name: 'ENTERPRISE', price: 49, users: 'Unlimited', vehicles: 'Unlimited', features: ['All Features', 'Full Bot Package', 'Dedicated Support'], popular: true }
  ];

  // Bot Add-ons Pricing
  const botAddons = [
    { name: 'Freight Bot', price: 2 },
    { name: 'Finance Bot', price: 2 },
    { name: 'Dispatcher Bot', price: 2 },
    { name: 'Documents Bot', price: 1 },
    { name: 'Customer Service Bot', price: 1 },
    { name: 'Safety Bot', price: 1 },
    { name: 'System Monitor Bot', price: 1 },
    { name: 'Full Bot Package', price: 8, popular: true }
  ];

  // Vehicle Pricing Add-ons
  const vehiclePricing = [
    { range: 'Up to 5 vehicles', price: 2 },
    { range: '6-20 vehicles', price: 1.5 },
    { range: '20+ vehicles', price: 1 }
  ];

  // User Add-on Pricing
  const userAddons = [
    { name: 'Additional User', price: 1 },
    { name: 'Admin User', price: 2 }
  ];

  // Additional Services
  const additionalServices = [
    { name: 'Automated Billing', price: 1 },
    { name: 'Advanced Financial Reports', price: 1 },
    { name: 'Route Analytics', price: 1 },
    { name: 'Fuel Analytics', price: 1 },
    { name: 'API Integration', price: 3 }
  ];

  const enterpriseFeatures = [
    'Custom AI Bot Development',
    'White-label Solutions',
    'Dedicated Infrastructure',
    'SLA 99.99% Uptime',
    'Custom Integration Support',
    'On-site Training',
    '24/7 VIP Support Line',
    'Quarterly Business Reviews'
  ];

  const currentPlan = pricingPlans[userType];
  const planMeta = {
    basic: { title: 'Basic', subtitle: 'Everything you need to start' },
    pro: { title: 'Pro', subtitle: 'Level up your profits' },
    premium: { title: 'Premium', subtitle: 'Maximum efficiency' }
  };

  const formatPrice = (price) => {
    return price.toLocaleString();
  };

  const toCad = (usdPrice) => {
    return Math.round(Number(usdPrice || 0) * CAD_PER_USD);
  };

  const formatPricePair = (usdPrice) => {
    return `$${formatPrice(toCad(usdPrice))} CAD (≈ $${formatPrice(Number(usdPrice || 0))} USD)`;
  };

  return (
    <div className="min-h-screen bg-cover bg-center bg-no-repeat" style={{ backgroundImage: `url(${bgLogin})` }}>
      <SeoHead
        title="Pricing - GTS Logistics"
        description="Review GTS Logistics pricing for carriers, brokers, and shippers, including platform access, AI bots, and logistics automation tools."
        keywords="gts pricing, freight broker pricing, logistics software pricing, load board pricing"
        canonical="https://www.gtsdispatcher.com/pricing"
        ogTitle="GTS Logistics Pricing"
        ogDescription="Transparent pricing for carriers, brokers, shippers, and logistics teams."
        ogUrl="https://www.gtsdispatcher.com/pricing"
        twitterTitle="GTS Logistics Pricing"
        twitterDescription="Transparent pricing for carriers, brokers, shippers, and logistics teams."
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
              <Link to="/pricing" className="text-red-400 text-sm font-semibold">Pricing</Link>
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
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">Simple, Transparent Pricing</h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-8">
            CAD-first pricing for Canada and U.S. teams, with USD reference shown for clarity.
          </p>

          {/* User Type Tabs */}
          <div className="flex justify-center gap-2 mb-8 bg-white/10 rounded-lg p-1 inline-flex">
            <button
              onClick={() => setUserType('carrier')}
              className={`px-6 py-2 rounded-lg transition ${userType === 'carrier' ? 'bg-red-600 text-white' : 'text-gray-300 hover:text-white'}`}
            >
              Carrier
            </button>
            <button
              onClick={() => setUserType('broker')}
              className={`px-6 py-2 rounded-lg transition ${userType === 'broker' ? 'bg-red-600 text-white' : 'text-gray-300 hover:text-white'}`}
            >
              Broker
            </button>
            <button
              onClick={() => setUserType('shipper')}
              className={`px-6 py-2 rounded-lg transition ${userType === 'shipper' ? 'bg-red-600 text-white' : 'text-gray-300 hover:text-white'}`}
            >
              Shipper
            </button>
          </div>

          {/* Billing Toggle */}
          <div className="flex justify-center items-center gap-4 mb-12">
            <span className={`text-sm ${billingCycle === 'monthly' ? 'text-white' : 'text-gray-400'}`}>Monthly</span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className="relative w-16 h-8 bg-white/20 rounded-full transition-all"
            >
              <div className={`absolute top-1 w-6 h-6 bg-red-500 rounded-full transition-all ${billingCycle === 'yearly' ? 'right-1' : 'left-1'}`} />
            </button>
            <span className={`text-sm ${billingCycle === 'yearly' ? 'text-white' : 'text-gray-400'}`}>
              Yearly <span className="text-green-400 text-xs ml-1">Save 15%</span>
            </span>
          </div>
          <p className="text-xs text-gray-400 mb-8">All plans are billed in CAD by default. USD values are approximate references.</p>

          {/* Pricing Cards */}
          <div className="max-w-4xl mx-auto space-y-5">
            {['basic', 'pro', 'premium'].map((planKey) => {
              const isPopular = Boolean(currentPlan[planKey]?.popular);
              const plan = currentPlan[planKey];
              const meta = planMeta[planKey];
              return (
                <div
                  key={planKey}
                  className={`relative rounded-xl p-6 border transition ${isPopular
                      ? 'bg-gradient-to-r from-red-700/25 to-black/60 border-red-500'
                      : 'bg-black/40 border-white/20 hover:border-red-500/50'
                    }`}
                >
                  {isPopular ? (
                    <div className="absolute -top-3 left-6 bg-red-600 text-white text-xs px-3 py-1 rounded-full">
                      Most Popular
                    </div>
                  ) : null}
                  <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
                    <div className="text-left">
                      <h3 className="text-2xl font-bold text-white mb-1">{meta.title}</h3>
                      <p className="text-gray-400 text-sm mb-4">{meta.subtitle}</p>
                      <div className="mb-2">
                        <span className="text-3xl font-bold text-white">{formatPricePair(plan[billingCycle])}</span>
                      </div>
                      <p className="text-xs text-gray-400">per {billingCycle === 'monthly' ? 'month' : 'year'}</p>
                    </div>
                    <Link
                      to={`/register?plan=${planKey}`}
                      className={`inline-flex items-center justify-center px-6 py-3 rounded-lg text-sm font-semibold transition ${isPopular
                          ? 'bg-red-600 text-white hover:bg-red-700'
                          : 'border border-white/30 text-white hover:bg-white/10'
                        }`}
                    >
                      Get Started
                    </Link>
                  </div>
                  <ul className="space-y-2 mt-5 text-left">
                    {plan.features.map((feature, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-gray-300 text-sm">
                        <span className="text-green-400">✓</span> {feature}
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>

          {/* Enterprise Section */}
          <div className="mt-12 bg-gradient-to-r from-red-900/30 to-black/60 rounded-xl p-8 max-w-4xl mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="text-center md:text-left">
                <h3 className="text-2xl font-bold text-white mb-2">Enterprise</h3>
                <p className="text-gray-300">Custom solutions for large fleets, brokers, and logistics companies</p>
              </div>
              <Link to="/contact?inquiry=enterprise" className="px-8 py-3 border-2 border-red-500 text-red-400 rounded-lg hover:bg-red-500/10 transition">
                Contact Sales →
              </Link>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-6 pt-6 border-t border-white/10">
              {enterpriseFeatures.map((feature, idx) => (
                <div key={idx} className="flex items-center gap-2 text-gray-300 text-xs">
                  <span className="text-red-400">✓</span> {feature}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* TMS Pricing Section */}
        <div className="container mx-auto px-4 py-12">
          <h2 className="text-2xl font-bold text-white text-center mb-8">TMS Plans for Logistics Companies</h2>
          <div className="grid md:grid-cols-5 gap-4">
            {tmsPlans.map((plan, idx) => (
              <div key={idx} className={`bg-black/40 backdrop-blur-sm rounded-xl p-4 border ${plan.popular ? 'border-red-500' : 'border-white/20'}`}>
                <h3 className="text-lg font-bold text-white text-center">{plan.name}</h3>
                <div className="text-center my-3">
                  <span className="text-2xl font-bold text-white">{formatPricePair(plan.price)}</span>
                  <span className="text-gray-400 text-xs">/month</span>
                </div>
                <p className="text-gray-400 text-xs text-center mb-2">{plan.users} users • {plan.vehicles} vehicles</p>
                <ul className="text-xs space-y-1 mb-3">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-center gap-1 text-gray-300">
                      <span className="text-green-400">✓</span> {feature}
                    </li>
                  ))}
                </ul>
                <Link to="/register?tms=true" className="block text-center py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition">
                  Get Started
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* Add-ons Section */}
        <div className="container mx-auto px-4 py-8">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Bot Add-ons */}
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4">AI Bot Add-ons</h3>
              <div className="grid grid-cols-2 gap-3">
                {botAddons.map((bot, idx) => (
                  <div key={idx} className="flex justify-between items-center border-b border-white/10 py-2">
                    <span className="text-gray-300 text-sm">{bot.name}</span>
                    <span className="text-white text-sm font-semibold">{formatPricePair(bot.price)}/mo</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Vehicle & User Add-ons */}
            <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
              <h3 className="text-xl font-bold text-white mb-4">Vehicle & User Add-ons</h3>
              <div className="mb-4">
                <p className="text-gray-400 text-sm mb-2">Vehicle Pricing:</p>
                {vehiclePricing.map((vp, idx) => (
                  <div key={idx} className="flex justify-between items-center border-b border-white/10 py-1">
                    <span className="text-gray-300 text-xs">{vp.range}</span>
                    <span className="text-white text-xs">{formatPricePair(vp.price)}/vehicle/month</span>
                  </div>
                ))}
              </div>
              <div>
                <p className="text-gray-400 text-sm mb-2">User Pricing:</p>
                {userAddons.map((ua, idx) => (
                  <div key={idx} className="flex justify-between items-center border-b border-white/10 py-1">
                    <span className="text-gray-300 text-xs">{ua.name}</span>
                    <span className="text-white text-xs">{formatPricePair(ua.price)}/user/month</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Additional Services */}
          <div className="mt-6 bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
            <h3 className="text-xl font-bold text-white mb-4">Additional Services</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {additionalServices.map((service, idx) => (
                <div key={idx} className="flex justify-between items-center border-b border-white/10 py-2">
                  <span className="text-gray-300 text-sm">{service.name}</span>
                  <span className="text-white text-sm font-semibold">{formatPricePair(service.price)}/mo</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Pricing Philosophy */}
        <div className="container mx-auto px-4 py-8">
          <div className="bg-gradient-to-r from-green-900/20 to-transparent rounded-xl p-6 border border-green-500/30">
            <h3 className="text-xl font-bold text-white text-center mb-4">Our Pricing Philosophy</h3>
            <p className="text-gray-300 text-center max-w-3xl mx-auto">
              We believe in sustainable growth through affordable pricing. Our goal is to help you succeed
              with competitive rates that make sense for your business. We keep our margins modest to build
              long-term partnerships and grow together.
            </p>
            <div className="flex justify-center gap-6 mt-4 text-sm text-gray-400">
              <span>No hidden fees</span>
              <span>Cancel anytime</span>
              <span>14-day free trial</span>
              <span>Volume discounts available</span>
            </div>
          </div>
        </div>

        {/* FAQ */}
        <div className="container mx-auto px-4 py-8">
          <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6">
            <h3 className="text-xl font-bold text-white mb-6 text-center">Frequently Asked Questions</h3>
            <div className="grid md:grid-cols-2 gap-4 text-left">
              <details className="group">
                <summary className="text-white font-semibold cursor-pointer list-none flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  Can I switch plans later?
                  <span className="group-open:rotate-180 transition">▼</span>
                </summary>
                <p className="text-gray-300 text-sm p-3">Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.</p>
              </details>
              <details className="group">
                <summary className="text-white font-semibold cursor-pointer list-none flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  Is there a free trial?
                  <span className="group-open:rotate-180 transition">▼</span>
                </summary>
                <p className="text-gray-300 text-sm p-3">Yes, we offer a 14-day free trial for all plans. No credit card required.</p>
              </details>
              <details className="group">
                <summary className="text-white font-semibold cursor-pointer list-none flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  What payment methods do you accept?
                  <span className="group-open:rotate-180 transition">▼</span>
                </summary>
                <p className="text-gray-300 text-sm p-3">We accept all major credit cards, bank transfers, and factoring services.</p>
              </details>
              <details className="group">
                <summary className="text-white font-semibold cursor-pointer list-none flex justify-between items-center p-3 bg-white/5 rounded-lg">
                  Can I add bots to my existing plan?
                  <span className="group-open:rotate-180 transition">▼</span>
                </summary>
                <p className="text-gray-300 text-sm p-3">Yes, you can add any bot or service to your plan as an add-on at any time.</p>
              </details>
            </div>
          </div>
        </div>

        {/* Trust Badges */}
        <div className="container mx-auto px-4 pb-12 text-center">
          <div className="flex justify-center gap-6 text-gray-400 text-xs">
            <span>No setup fees</span>
            <span>Cancel anytime</span>
            <span>14-day free trial</span>
            <span>Volume discounts available</span>
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

export default Pricing;
