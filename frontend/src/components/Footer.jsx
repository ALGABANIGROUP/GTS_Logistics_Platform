import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
  return (
    <footer className="container mx-auto px-4 py-6 border-t border-white/20">
      <div className="flex flex-col md:flex-row justify-between items-center gap-4">
        <p className="text-gray-400 text-xs">
          © 2026 Gabani Transport Solutions LLC – All rights reserved.
        </p>
        <div className="flex gap-6 text-xs">
          <Link to="/privacy" className="text-gray-400 hover:text-white transition">Privacy Policy</Link>
          <Link to="/terms" className="text-gray-400 hover:text-white transition">Terms of Service</Link>
          <Link to="/legal" className="text-gray-400 hover:text-white transition">Legal Agreements</Link>
        </div>
        <div className="text-right">
          <p className="text-gray-500 text-xs">
            📞 <a href="tel:+17786518297" className="hover:text-white">+1 (778) 651-8297</a>
          </p>
          <p className="text-gray-500 text-xs mt-1">
            329 HOWE ST UNIT #957, VANCOUVER BC V6C 3N2, CANADA
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
