/**
 * SudaPaymentForm Component - SUDAPAY payment form component
 * Provides an optimized payment interface for SUDAPAY
 * 
 * Features:
 * - Support for Sudanese Pound (SDG) and US Dollar (USD)
 * - Mobile-optimized design
 * - Comprehensive error handling
 * - Full English language support
 * 
 * Author: GTS Development Team
 * Date: March 2026
 */

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import paymentApi from '../api/paymentApi';

/**
 * SudaPaymentForm Component
 * 
 * Props:
 * - invoiceId (number): Invoice ID
 * - amount (number): Payment amount
 * - currency (string): Currency (SDG, USD)
 * - onSuccess (function): Success callback
 * - onError (function): Error callback
 */
export function SudaPaymentForm({
  invoiceId,
  amount,
  currency = 'SDG',
  onSuccess,
  onError,
}) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCurrency, setSelectedCurrency] = useState(currency);
  const [paymentId, setPaymentId] = useState(null);

  /**
   * Handle Payment - Creates new payment with SUDAPAY and redirects
   */
  const handlePayment = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('Creating SUDAPAY payment');

      // Create payment on backend
      const payment = await paymentApi.create({
        invoice_id: invoiceId,
        amount: amount,
        currency: selectedCurrency,
        gateway: 'sudapay',
        description: `Invoice #${invoiceId} payment`,
      });

      setPaymentId(payment.payment_id);
      console.log('Payment created:', payment);

      // Check if SUDAPAY is in sandbox or production
      if (!payment.checkout_url) {
        throw new Error('Could not get payment link');
      }

      // Redirect to SUDAPAY checkout
      console.log('Redirecting to SUDAPAY checkout...');
      window.location.href = payment.checkout_url;

    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Payment creation failed';
      console.error('Payment creation failed:', errorMsg);
      setError(errorMsg);

      if (onError) {
        onError(errorMsg);
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Format Amount - Formats amount for display
   */
  const formattedAmount = paymentApi.formatAmount(amount, selectedCurrency);

  /**
   * Currency Symbol - Currency symbols
   */
  const getCurrencySymbol = (curr) => {
    return curr === 'SDG' ? 'SDG' : '$';
  };

  return (
    <div className="suda-payment-form">
      {/* Header */}
      <div className="payment-header">
        <h2>💳 Secure Payment via SUDAPAY</h2>
        <p className="subtitle">Sudanese Unified Government Payment Platform</p>
      </div>

      {/* Payment Info */}
      <div className="payment-info-card">
        <div className="info-row">
          <span className="label">Invoice Number:</span>
          <span className="value">#{invoiceId}</span>
        </div>

        <div className="info-row">
          <span className="label">Amount Due:</span>
          <span className="value amount">{formattedAmount}</span>
        </div>

        <div className="info-row">
          <span className="label">Payment Method:</span>
          <span className="value gateway">🇸🇩 SUDAPAY</span>
        </div>
      </div>

      {/* Currency Selection */}
      <div className="currency-selector">
        <label className="label">Select Currency:</label>
        <div className="currency-options">
          {['SDG', 'USD'].map((curr) => (
            <button
              key={curr}
              className={`currency-btn ${selectedCurrency === curr ? 'active' : ''}`}
              onClick={() => setSelectedCurrency(curr)}
              disabled={loading}
            >
              <span className="symbol">{getCurrencySymbol(curr)}</span>
              <span className="name">{curr}</span>
              {curr === 'SDG' && <span className="badge">🇸🇩 Local</span>}
            </button>
          ))}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          <span className="icon">❌</span>
          <span className="text">{error}</span>
        </div>
      )}

      {/* Features */}
      <div className="features">
        <div className="feature">
          <span className="icon">🔐</span>
          <span className="text">Fully Secure Payment</span>
        </div>
        <div className="feature">
          <span className="icon">⚡</span>
          <span className="text">Fast Processing</span>
        </div>
        <div className="feature">
          <span className="icon">✅</span>
          <span className="text">Government Standards</span>
        </div>
        <div className="feature">
          <span className="icon">💬</span>
          <span className="text">Local Support 24/7</span>
        </div>
      </div>

      {/* Pay Button */}
      <button
        className="pay-button"
        onClick={handlePayment}
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="spinner">🔄</span>
            <span>Processing...</span>
          </>
        ) : (
          <>
            <span className="icon">💳</span>
            <span>Pay Now {formattedAmount}</span>
          </>
        )}
      </button>

      {/* Security Info */}
      <div className="security-info">
        <p>
          ✅ Payment system certified by Central Bank of Sudan standards<br />
          🔒 All information is protected with top-tier encryption<br />
          📞 For assistance: support@sudapay.sd
        </p>
      </div>

      {/* Styles */}
      <style jsx>{`
        .suda-payment-form {
          max-width: 600px;
          margin: 0 auto;
          padding: 20px;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          direction: ltr;
          text-align: left;
        }

        .payment-header {
          text-align: center;
          margin-bottom: 30px;
          padding-bottom: 20px;
          border-bottom: 2px solid #f0f0f0;
        }

        .payment-header h2 {
          font-size: 28px;
          color: #333;
          margin: 0 0 10px 0;
        }

        .subtitle {
          color: #666;
          margin: 0;
          font-size: 14px;
        }

        .payment-info-card {
          background: #f9f9f9;
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 25px;
        }

        .info-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 0;
          border-bottom: 1px solid #e0e0e0;
        }

        .info-row:last-child {
          border-bottom: none;
        }

        .label {
          font-weight: 600;
          color: #555;
          font-size: 14px;
        }

        .value {
          color: #333;
          font-weight: 500;
        }

        .amount {
          font-size: 18px;
          color: #27ae60;
          font-weight: bold;
        }

        .gateway {
          background: #e8f5e9;
          color: #27ae60;
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 13px;
          font-weight: 600;
        }

        .currency-selector {
          margin-bottom: 25px;
        }

        .currency-selector .label {
          display: block;
          margin-bottom: 12px;
          font-weight: 600;
          color: #333;
        }

        .currency-options {
          display: flex;
          gap: 12px;
        }

        .currency-btn {
          flex: 1;
          padding: 12px;
          border: 2px solid #e0e0e0;
          border-radius: 8px;
          background: white;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          font-weight: 600;
        }

        .currency-btn:hover:not(:disabled) {
          border-color: #27ae60;
          background: #f0f8f5;
        }

        .currency-btn.active {
          border-color: #27ae60;
          background: #e8f5e9;
          color: #27ae60;
        }

        .currency-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .symbol {
          font-size: 18px;
        }

        .badge {
          background: #27ae60;
          color: white;
          padding: 2px 6px;
          border-radius: 10px;
          font-size: 10px;
          margin-top: 4px;
        }

        .error-message {
          background: #ffebee;
          color: #c62828;
          padding: 12px 15px;
          border-radius: 8px;
          margin-bottom: 20px;
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 13px;
        }

        .error-message .icon {
          font-size: 16px;
        }

        .features {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 12px;
          margin-bottom: 25px;
        }

        .feature {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 12px;
          background: #f5f5f5;
          border-radius: 8px;
          font-size: 12px;
          text-align: center;
          gap: 6px;
        }

        .feature .icon {
          font-size: 20px;
        }

        .pay-button {
          width: 100%;
          padding: 16px;
          background: linear-gradient(135deg, #27ae60, #229954);
          color: white;
          border: none;
          border-radius: 8px;
          font-size: 16px;
          font-weight: 700;
          cursor: pointer;
          transition: all 0.3s ease;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 10px;
        }

        .pay-button:hover:not(:disabled) {
          background: linear-gradient(135deg, #229954, #1e8449);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
        }

        .pay-button:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .spinner {
          display: inline-block;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        .security-info {
          background: #e8f5e9;
          border: 1px solid #81c784;
          border-radius: 8px;
          padding: 12px;
          font-size: 11px;
          color: #2e7d32;
          line-height: 1.6;
          margin-top: 20px;
        }

        .security-info p {
          margin: 0;
        }

        /* Mobile Responsive */
        @media (max-width: 600px) {
          .suda-payment-form {
            padding: 15px;
          }

          .payment-header h2 {
            font-size: 22px;
          }

          .suda-payment-form {
            max-width: 100%;
          }
        }
      `}</style>
    </div>
  );
}

export default SudaPaymentForm;