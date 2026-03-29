import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import gtsLogo from '../assets/gabani_logo.png';
import bgLogin from '../assets/bg_login.png';
import CookieConsent from '../components/CookieConsent';
import LiveLoadsTicker from '../components/LiveLoadsTicker';
import MobileAppPromo from '../components/MobileAppPromo';
import TrustBadges from '../components/TrustBadges';
import FuelPriceMap from '../components/FuelPriceMap';
import NewsletterSignup from '../components/NewsletterSignup';
import ChatSupportButton from '../components/ChatSupportButton';
import SeoHead from '../components/SeoHead';

const PortalLanding = () => {
  const [selectedTab, setSelectedTab] = useState('carrier');
  const organizationSchema = {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "GTS Logistics",
    url: "https://www.gtsdispatcher.com/",
    logo: "https://www.gtsdispatcher.com/favicon.png",
    description: "Freight broker and load board platform for carriers, brokers, and shippers across Canada.",
    sameAs: ["https://www.linkedin.com/company/gts-logistics"],
  };

  // Real data for GTS Platform
  const liveLoadsData = {
    flatbed: { available: 12450, moved: 3421, rate: 2.85 },
    van: { available: 8932, moved: 2156, rate: 2.42 },
    reefer: { available: 5678, moved: 1432, rate: 2.76 },
    heavyHaul: { available: 3421, moved: 876, rate: 3.12 },
  };

  const pricingPlans = {
    carrier: {
      basic: { monthly: 19, yearly: 199, features: ['Load Search (unlimited)', 'Truck Post (unlimited)', 'Basic Rate Insights'] },
      pro: { monthly: 49, yearly: 499, features: ['Everything in Basic', 'Advanced Rate Insights', 'Book It Now', 'Real-Time Live Loads'] },
      premium: { monthly: 99, yearly: 999, features: ['Everything in Pro', 'Carrier Monitoring', 'Predictive Sourcing', 'Multi-Trip Search'] }
    },
    broker: {
      basic: { monthly: 29, yearly: 299, features: ['Load Board Access', 'Basic Analytics', 'Carrier Search'] },
      pro: { monthly: 79, yearly: 799, features: ['Everything in Basic', 'Rate Insights', 'Risk Factors', 'Carrier Performance Rating'] },
      premium: { monthly: 149, yearly: 1499, features: ['Everything in Pro', 'Carrier Monitoring', 'Predictive Sourcing', 'RMIS Integration'] }
    },
    shipper: {
      basic: { monthly: 29, yearly: 299, features: ['Load Posting', 'Basic Tracking', 'Carrier Search'] },
      pro: { monthly: 79, yearly: 799, features: ['Everything in Basic', 'Rate Insights', 'Carrier Performance', 'Real-Time Updates'] },
      premium: { monthly: 149, yearly: 1499, features: ['Everything in Pro', 'TMS Integration', 'Advanced Analytics', 'Dedicated Support'] }
    }
  };

  const fuelPrices = [
    { country: 'Sudan (Khartoum)', price: 2.85, currency: 'SDG/L', change: '+0.05' },
    { country: 'Saudi Arabia (Riyadh)', price: 0.62, currency: 'USD/L', change: '-0.02' },
    { country: 'UAE (Dubai)', price: 0.68, currency: 'USD/L', change: '-0.01' },
    { country: 'Egypt (Cairo)', price: 0.45, currency: 'USD/L', change: '+0.03' },
    { country: 'Qatar (Doha)', price: 0.61, currency: 'USD/L', change: '-0.01' },
    { country: 'Kuwait (Kuwait City)', price: 0.34, currency: 'USD/L', change: '0.00' },
    { country: 'Oman (Muscat)', price: 0.62, currency: 'USD/L', change: '-0.02' },
    { country: 'Jordan (Amman)', price: 1.05, currency: 'USD/L', change: '+0.04' },
  ];

  const testimonials = [
    {
      name: "Ahmed Al-Gabani",
      company: "Gabani Transport Solutions",
      text: "Working with GTS Logistics, you get to know people from the CEO all the way to IT. They've tailored their tools to work with us so they don't have just one way of doing things."
    },
    {
      name: "Mohamed Ibrahim",
      company: "Nile Cargo",
      text: "The GTS platform has transformed our operations. Real-time tracking and AI-powered insights help us make better decisions faster."
    },
    {
      name: "Fatima Hassan",
      company: "Red Sea Logistics",
      text: "Excellent service! The load board is intuitive and the support team is always available to help. Highly recommended."
    }
  ];

  const restrictedCountries = [
    'Afghanistan', 'Burundi', 'Chad', 'Cuba', 'Democratic Republic of Congo',
    'Equatorial Guinea', 'Eritrea', 'Haiti', 'Iran', 'Laos', 'Libya',
    'Myanmar (Burma)', 'Sierra Leone', 'Somalia', 'Togo', 'Turkmenistan',
    'Venezuela', 'Yemen'
  ];

  return (
    <div className="min-h-screen bg-cover bg-center bg-no-repeat" style={{ backgroundImage: `url(${bgLogin})` }}>
      <SeoHead
        title="GTS Logistics - Freight Broker & Load Board Platform"
        description="GTS Logistics provides freight broker services, load board integration, and cross-border trucking solutions across Canada. Get real-time rates and track shipments."
        keywords="freight broker, load board, trucking logistics, cross-border shipping, canada freight"
        canonical="https://www.gtsdispatcher.com/"
        ogTitle="GTS Logistics - Freight Broker & Load Board Platform"
        ogDescription="Professional freight broker and load board services across Canada. Real-time rates, tracking, and dispatch."
        ogUrl="https://www.gtsdispatcher.com/"
        twitterTitle="GTS Logistics - Freight Broker & Load Board Platform"
        twitterDescription="Professional freight broker and load board services across Canada."
        schema={organizationSchema}
      />
      <div className="min-h-screen bg-black/70">
        {/* Header */}
        <div className="container mx-auto px-4 py-4">
          <div className="flex flex-wrap justify-between items-center gap-4">
            <img src={gtsLogo} alt="GTS Logistics" className="h-12" />

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-6">
              <Link to="/products" className="text-white hover:text-red-400 transition text-sm">Products</Link>
              <Link to="/pricing" className="text-white hover:text-red-400 transition text-sm">Pricing</Link>
              <Link to="/resources" className="text-white hover:text-red-400 transition text-sm">Resources</Link>
              <Link to="/about" className="text-white hover:text-red-400 transition text-sm">About</Link>
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

        {/* Live Loads Ticker */}
        <LiveLoadsTicker />

        {/* Main Content */}
        <div className="container mx-auto px-4 py-8">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Left Column - Welcome & Stats */}
            <div className="lg:col-span-2">
              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 mb-6">
                <h1 className="text-3xl md:text-4xl font-bold text-white mb-2">TRANSPORT, Where Intelligence</h1>
                <p className="text-gray-300 mb-4">Meet the world's most advanced logistics platform</p>

                {/* Live Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-white">{liveLoadsData.flatbed.available.toLocaleString()}+</p>
                    <p className="text-gray-400 text-xs">Available Loads</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-white">{liveLoadsData.flatbed.moved.toLocaleString()}</p>
                    <p className="text-gray-400 text-xs">Loads Today</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-white">50,000+</p>
                    <p className="text-gray-400 text-xs">Active Carriers</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-white">98%</p>
                    <p className="text-gray-400 text-xs">On-Time Delivery</p>
                  </div>
                </div>

                {/* Search Loads */}
                <div className="bg-white/10 rounded-lg p-4 mb-6">
                  <h3 className="text-white font-semibold mb-3">Search for your first load</h3>
                  <div className="grid md:grid-cols-3 gap-3">
                    <input type="text" placeholder="Origin" className="px-3 py-2 bg-black/50 border border-white/20 rounded text-white placeholder-gray-400 text-sm" />
                    <input type="text" placeholder="Destination" className="px-3 py-2 bg-black/50 border border-white/20 rounded text-white placeholder-gray-400 text-sm" />
                    <select className="px-3 py-2 bg-black/50 border border-white/20 rounded text-white text-sm">
                      <option>Equipment Type</option>
                      <option>Flatbed</option>
                      <option>Dry Van</option>
                      <option>Reefer</option>
                      <option>Heavy Haul</option>
                    </select>
                  </div>
                  <button className="w-full mt-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm">
                    FIND LOADS
                  </button>
                </div>

                {/* Registration Notice */}
                <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-4 mb-6">
                  <p className="text-yellow-400 text-sm font-semibold">⚠️ Registration Notice</p>
                  <p className="text-gray-300 text-xs mt-1">
                    Registration is paused while we run the platform privately until August 9, 2026.
                    Contact <a href="mailto:admin@gabanilogistics.com" className="text-red-400 hover:underline">admin@gabanilogistics.com</a> for expedited approval.
                  </p>
                </div>
              </div>

              {/* Persona Cards */}
              <div className="mb-8">
                <h2 className="text-white text-2xl font-bold text-center mb-6">What type of trucking business are you?</h2>
                <div className="grid md:grid-cols-3 gap-6">
                  {/* Carrier Card */}
                  <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 text-center border border-white/20 hover:border-red-500 transition">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
                      <span className="text-2xl">🚛</span>
                    </div>
                    <h3 className="text-white text-xl font-bold mb-2">I am a Carrier</h3>
                    <p className="text-gray-300 text-sm mb-4">Find loads & get paid faster</p>
                    <p className="text-red-400 text-sm font-semibold mb-3">Starting at ${pricingPlans.carrier.basic.monthly}/month</p>
                    <Link to="/register?type=carrier" className="inline-block px-4 py-2 border border-white/30 text-white rounded hover:bg-white/10 transition text-sm">
                      See tools →
                    </Link>
                  </div>

                  {/* Broker Card */}
                  <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 text-center border border-white/20 hover:border-red-500 transition">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
                      <span className="text-2xl">📊</span>
                    </div>
                    <h3 className="text-white text-xl font-bold mb-2">I am a Broker</h3>
                    <p className="text-gray-300 text-sm mb-4">Fill capacity & reduce risk</p>
                    <p className="text-red-400 text-sm font-semibold mb-3">Starting at ${pricingPlans.broker.basic.monthly}/month</p>
                    <Link to="/register?type=broker" className="inline-block px-4 py-2 border border-white/30 text-white rounded hover:bg-white/10 transition text-sm">
                      See tools →
                    </Link>
                  </div>

                  {/* Shipper Card */}
                  <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 text-center border border-white/20 hover:border-red-500 transition">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/20 flex items-center justify-center">
                      <span className="text-2xl">📦</span>
                    </div>
                    <h3 className="text-white text-xl font-bold mb-2">I am a Shipper</h3>
                    <p className="text-gray-300 text-sm mb-4">Streamline operations</p>
                    <p className="text-red-400 text-sm font-semibold mb-3">Starting at ${pricingPlans.shipper.basic.monthly}/month</p>
                    <Link to="/register?type=shipper" className="inline-block px-4 py-2 border border-white/30 text-white rounded hover:bg-white/10 transition text-sm">
                      See tools →
                    </Link>
                  </div>
                </div>
              </div>

              {/* Pricing Plans */}
              <div className="mb-8">
                <h2 className="text-white text-2xl font-bold text-center mb-6">GTS Load Board Plans</h2>
                <div className="grid md:grid-cols-3 gap-6">
                  {/* Basic Plan */}
                  <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h3 className="text-white text-xl font-bold mb-2">Basic</h3>
                    <p className="text-gray-300 text-sm mb-4">Everything you need to start</p>
                    <p className="text-3xl text-white font-bold mb-4">
                      ${pricingPlans.carrier.basic.monthly} <span className="text-sm text-gray-400">/month</span>
                      <span className="block text-sm text-gray-500 mt-1">or ${pricingPlans.carrier.basic.yearly}/year (save 15%)</span>
                    </p>
                    <ul className="space-y-2 mb-6">
                      {pricingPlans.carrier.basic.features.map((feature, idx) => (
                        <li key={idx} className="text-gray-300 text-sm flex items-center gap-2">
                          <span className="text-green-400">✓</span> {feature}
                        </li>
                      ))}
                    </ul>
                    <Link to="/register?plan=basic" className="block text-center py-2 border border-white/30 text-white rounded hover:bg-white/10 transition text-sm">Start now</Link>
                  </div>

                  {/* Pro Plan - Popular */}
                  <div className="bg-gradient-to-b from-red-600/20 to-black/60 backdrop-blur-sm rounded-xl p-6 border-2 border-red-500 relative">
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-red-600 text-white text-xs px-3 py-1 rounded-full">
                      Most Popular
                    </div>
                    <h3 className="text-white text-xl font-bold mb-2">Pro</h3>
                    <p className="text-gray-300 text-sm mb-4">Level up your profits</p>
                    <p className="text-3xl text-white font-bold mb-4">
                      ${pricingPlans.carrier.pro.monthly} <span className="text-sm text-gray-400">/month</span>
                      <span className="block text-sm text-gray-500 mt-1">or ${pricingPlans.carrier.pro.yearly}/year (save 15%)</span>
                    </p>
                    <ul className="space-y-2 mb-6">
                      {pricingPlans.carrier.pro.features.map((feature, idx) => (
                        <li key={idx} className="text-gray-300 text-sm flex items-center gap-2">
                          <span className="text-green-400">✓</span> {feature}
                        </li>
                      ))}
                    </ul>
                    <Link to="/register?plan=pro" className="block text-center py-2 bg-red-600 text-white rounded hover:bg-red-700 transition text-sm">Start now</Link>
                  </div>

                  {/* Premium Plan */}
                  <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                    <h3 className="text-white text-xl font-bold mb-2">Premium</h3>
                    <p className="text-gray-300 text-sm mb-4">Maximum efficiency</p>
                    <p className="text-3xl text-white font-bold mb-4">
                      ${pricingPlans.carrier.premium.monthly} <span className="text-sm text-gray-400">/month</span>
                      <span className="block text-sm text-gray-500 mt-1">or ${pricingPlans.carrier.premium.yearly}/year (save 15%)</span>
                    </p>
                    <ul className="space-y-2 mb-6">
                      {pricingPlans.carrier.premium.features.map((feature, idx) => (
                        <li key={idx} className="text-gray-300 text-sm flex items-center gap-2">
                          <span className="text-green-400">✓</span> {feature}
                        </li>
                      ))}
                    </ul>
                    <Link to="/register?plan=premium" className="block text-center py-2 border border-white/30 text-white rounded hover:bg-white/10 transition text-sm">Start now</Link>
                  </div>
                </div>
                <p className="text-center text-gray-500 text-xs mt-4">*Amount shown excludes applicable fees and taxes. Annual plans save 15%.</p>
              </div>
            </div>

            {/* Right Column - Security, Fuel Prices, Testimonials */}
            <div className="space-y-6">
              {/* Security Notice */}
              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <h2 className="text-red-500 text-lg font-bold mb-3">WE'RE FOCUSED ON REMOVING FRAUD FROM OUR PLATFORM.</h2>
                <h3 className="text-white font-semibold mb-2">HOW IT WORKS</h3>
                <p className="text-gray-300 text-xs mb-3">
                  When you attempt to log in from a new device, you'll be asked to verify your identity.
                </p>
                <ul className="space-y-1 mb-4">
                  <li className="flex items-center gap-2 text-gray-300 text-xs"><span className="text-green-400">✓</span> Push notification on mobile device</li>
                  <li className="flex items-center gap-2 text-gray-300 text-xs"><span className="text-green-400">✓</span> Security code via authentication app</li>
                  <li className="flex items-center gap-2 text-gray-300 text-xs"><span className="text-green-400">✓</span> Biometric input (face or fingerprint)</li>
                </ul>
                <p className="text-gray-400 text-xs">Need more help? <a href="/support" className="text-red-400 hover:underline">Get support</a>.</p>
              </div>

              {/* Fuel Price Map */}
              <FuelPriceMap />

              {/* Restricted Countries Notice */}
              <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4">
                <p className="text-yellow-400 text-xs font-semibold mb-2">🌍 Service Availability</p>
                <p className="text-gray-400 text-xs mb-2">GTS Logistics is available worldwide except:</p>
                <div className="flex flex-wrap gap-1">
                  {restrictedCountries.map((country, idx) => (
                    <span key={idx} className="text-gray-500 text-[10px] bg-white/5 px-2 py-0.5 rounded">{country}</span>
                  ))}
                </div>
                <p className="text-gray-500 text-[10px] mt-2">Please contact us for any inquiries.</p>
              </div>

              {/* Testimonials */}
              <div className="bg-black/40 backdrop-blur-sm rounded-xl p-6 border border-white/20">
                <h3 className="text-white font-semibold mb-3">WHAT CUSTOMERS ARE SAYING</h3>
                <div className="space-y-4">
                  {testimonials.map((testimonial, idx) => (
                    <div key={idx} className="border-b border-white/10 pb-3 last:border-0">
                      <p className="text-gray-300 italic text-xs">"{testimonial.text}"</p>
                      <p className="text-white text-xs font-semibold mt-1">— {testimonial.name}, {testimonial.company}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Newsletter */}
              <NewsletterSignup />
            </div>
          </div>
        </div>

        {/* Mobile App Promo */}
        <MobileAppPromo />

        {/* Footer */}
        <div className="container mx-auto px-4 py-6 border-t border-white/20 mt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-400 text-xs">
              © 2026 Gabani Transport Solutions LLC – All rights reserved.
            </p>
            <TrustBadges />
            <div className="flex gap-4 text-xs">
              <a href="/privacy" className="text-gray-400 hover:text-white transition">Privacy Policy</a>
              <a href="/terms" className="text-gray-400 hover:text-white transition">Terms of Service</a>
              <a href="/legal" className="text-gray-400 hover:text-white transition">Legal Agreements</a>
            </div>
          </div>
        </div>

        {/* Chat Support Button */}
        <ChatSupportButton />

        {/* Cookie Consent */}
        <CookieConsent />
      </div>
    </div>
  );
};

export default PortalLanding;
