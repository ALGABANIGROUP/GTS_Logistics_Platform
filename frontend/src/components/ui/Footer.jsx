import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-slate-800 border-t border-slate-700 py-4 px-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex flex-col items-center md:items-start gap-2">
            <p className="text-slate-400 text-xs">
              © 2026 Gabani Transport Solutions LLC – All rights reserved.
            </p>
            <p className="text-slate-500 text-xs text-center md:text-left">
              Canadian Patent Application No. 3306251 | AI Multi-Bot Orchestration System for Logistics Automation
            </p>
          </div>
          <div className="flex gap-4 text-xs">
            <a href="/privacy" className="text-slate-400 hover:text-white transition">Privacy Policy</a>
            <a href="/terms" className="text-slate-400 hover:text-white transition">Terms of Service</a>
            <a href="/legal" className="text-slate-400 hover:text-white transition">Legal Agreements</a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;