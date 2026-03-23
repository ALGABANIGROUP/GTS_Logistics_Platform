// src/components/bots/panels/system-admin/PlatformFeatures.jsx
import React from 'react';
import './PlatformFeatures.css';

const features = [
  { name: 'Ad Free', essential: true, preferred: true },
  { name: 'Unlimited Views', essential: true, preferred: true },
  { name: 'Toll Charge Estimate', essential: true, preferred: true },
  { name: 'Fuel Surcharge Calculator', essential: true, preferred: true },
  { name: 'Driving Time', essential: true, preferred: true },
  { name: 'Backhaul', essential: true, preferred: true },
  { name: 'Days to Pay & Credit Score', essential: false, preferred: true },
  { name: '30-Day Rate Check', essential: false, preferred: true },
  { name: '1, 7, 15-Day Rate Check', essential: false, preferred: true },
  { name: 'Load Density Report', essential: false, preferred: true },
  { name: 'Capacity Indicator', essential: false, preferred: true },
  { name: 'Historical Trend', essential: false, preferred: true }
];

const PlatformFeatures = () => (
  <div className="platform-features">
    <h2>GTS Platform - Features</h2>
    <div className="features-table">
      <div className="features-header">
        <span>Feature</span>
        <span>Essential</span>
        <span>Preferred</span>
      </div>
      {features.map((f, idx) => (
        <div className="feature-row" key={idx}>
          <span>{f.name}</span>
          <span>{f.essential ? '✔️' : '❌'}</span>
          <span>{f.preferred ? '✔️' : '❌'}</span>
        </div>
      ))}
    </div>
    <div className="features-note">
      <strong>Note:</strong> The GTS platform relies on the Preferred plan to ensure full features and smart analytics.
    </div>
  </div>
);

export default PlatformFeatures;
