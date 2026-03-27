/**
 * PaymentPage Component - Main Payment Page
 * Provide invoice payment instructions without Sudapay
 * 
 * Features:
 * - Display invoice data
 * - Payment form editor
 * - Error handling
 * - English language support
 * 
 * Routes:
 * - /payments/:invoiceId - Payment for invoice
 * 
 * Author: GTS Development Team
 * Date: March 2026
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { readAuthToken } from '../../utils/authStorage';
import { useCurrencyStore } from '../../stores/useCurrencyStore';

/**
 * PaymentPage Component
 * Complete payment page with invoice information and form
 */
export function PaymentPage() {
  const { invoiceId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedMethod, setSelectedMethod] = useState('stripe');

  const paymentStatus = searchParams.get('status');
  const paymentId = searchParams.get('payment_id');

  /**
   * Load Invoice Data
   */
  useEffect(() => {
    const loadInvoice = async () => {
      try {
        setLoading(true);
        console.log('📥 Loading invoice:', invoiceId);

        // Fetch invoice from backend
        const response = await fetch(`/api/v1/invoices/${invoiceId}`, {
          headers: {
            'Authorization': `Bearer ${readAuthToken() || ''}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to load invoice data');
        }

        const data = await response.json();
        setInvoice(data);
        console.log('✅ Invoice loaded:', data);

      } catch (err) {
        console.error('❌ Error loading invoice:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    if (invoiceId) {
      loadInvoice();
    }
  }, [invoiceId]);

  /**
   * Handle Payment Success
   */
  const handlePaymentSuccess = () => {
    console.log('✅ Payment successful!');
    navigate(`/payments/success?payment_id=${paymentId}&invoice_id=${invoiceId}`);
  };

  /**
   * Handle Payment Error
   */
  const handlePaymentError = (errorMsg) => {
    console.error('❌ Payment error:', errorMsg);
    setError(errorMsg);
  };

  /**
   * Go Back
   */
  const goBack = () => {
    navigate('/invoices');
  };

  /**
   * Copy Bank Details to Clipboard
   */
  const copyToClipboard = async () => {
    const bankDetails = `
Account Holder: Gabani Transport Solutions LLC
Account Number: 200116499651
Institution/Transit: 621 / 16001
SWIFT/BIC: TRWICAW1XXX
Bank: Wise Payments Canada Inc.
Reference: Invoice #${invoiceId}
    `.trim();

    try {
      await navigator.clipboard.writeText(bankDetails);
      alert('Bank details copied to clipboard!');
    } catch (err) {
      console.error('Failed to copy:', err);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = bankDetails;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      alert('Bank details copied to clipboard!');
    }
  };

  /* Loading State */
  if (loading) {
    return (
      <div className="payment-loading">
        <div className="loader">
          <span>📥</span>
          <p>Loading invoice data...</p>
        </div>
      </div>
    );
  }

  /* Error State */
  if (!invoice && error) {
    return (
      <div className="payment-error">
        <div className="error-card">
          <span className="icon">❌</span>
          <h2>An error occurred</h2>
          <p>{error}</p>
          <button className="btn-back" onClick={goBack}>
            Back to invoices
          </button>
        </div>
      </div>
    );
  }

  /* Payment Success Message */
  if (paymentStatus === 'success') {
    return (
      <div className="payment-success">
        <div className="success-card">
          <span className="icon">✅</span>
          <h2>Payment successful!</h2>
          <p>Your payment has been received and is being processed</p>
          <div className="details">
            <p>Payment ID: <strong>{paymentId}</strong></p>
            <p>Invoice: <strong>#{invoiceId}</strong></p>
          </div>
          <button className="btn-continue" onClick={() => navigate('/invoices')}>
            Back to invoices
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="payment-page">
      {/* Header */}
      <div className="page-header">
        <button className="btn-back" onClick={goBack}>
          ← Back
        </button>
        <h1>💳 Payment</h1>
      </div>

      {/* Invoice Summary */}
      {invoice && (
        <div className="invoice-summary">
          <div className="summary-card">
            <h3>📋 Invoice summary</h3>

            <div className="summary-row">
              <span className="label">Invoice number:</span>
              <span className="value">#{invoice.id}</span>
            </div>

            <div className="summary-row">
              <span className="label">Shipper:</span>
              <span className="value">{invoice.shipper_name || 'Unknown'}</span>
            </div>

            <div className="summary-row">
              <span className="label">Carrier:</span>
              <span className="value">{invoice.carrier_name || 'Unknown'}</span>
            </div>

            <div className="summary-row">
              <span className="label">Status:</span>
              <span className={`status-badge ${invoice.status}`}>
                {translateStatus(invoice.status)}
              </span>
            </div>

            <div className="summary-row total">
              <span className="label">Amount due:</span>
              <span className="value">
                {formatAmount(invoice.total_amount, invoice.currency)}
              </span>
            </div>

            {invoice.notes && (
              <div className="summary-row notes">
                <span className="label">Notes:</span>
                <span className="value">{invoice.notes}</span>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="payment-form-section">
        <div className="invoice-summary">
          <div className="summary-card">
            <h3>Online gateway removed</h3>
            <p>
              Sudapay has been removed from GTS. Use the bank transfer details below or contact finance
              support to arrange payment.
            </p>
          </div>
        </div>
      </div>

      {/* Stripe Climate Section */}
      {selectedMethod === 'stripe' && invoice && (
        <div className="stripe-climate-section">
          <div className="climate-card">
            <div className="climate-header">
              <div className="climate-icon">
                <span>🌍</span>
              </div>
              <div className="climate-info">
                <h3>Stripe Climate</h3>
                <p>You're helping fund next-generation carbon removal technology.</p>
              </div>
            </div>
            <div className="climate-progress">
              <div className="progress-bar">
                <div className="progress-fill"></div>
              </div>
              <span className="progress-text">1% contribution</span>
            </div>
            <div className="climate-features">
              <span className="feature">✓ Permanent carbon removal</span>
              <span className="separator">•</span>
              <span className="feature">✓ Verified projects</span>
              <span className="separator">•</span>
              <span className="feature">✓ Transparent reporting</span>
            </div>
            <div className="climate-breakdown">
              <div className="breakdown-row">
                <span className="breakdown-label">Your payment:</span>
                <span className="breakdown-value">{formatAmount(invoice.total_amount, invoice.currency)}</span>
              </div>
              <div className="breakdown-row">
                <span className="breakdown-label">Climate contribution (1%):</span>
                <span className="breakdown-value climate-amount">{formatAmount(invoice.total_amount * 0.01, invoice.currency)}</span>
              </div>
              <div className="breakdown-row total">
                <span className="breakdown-label">Total:</span>
                <span className="breakdown-value">{formatAmount(invoice.total_amount, invoice.currency)}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Previous Error */}
      {error && (
        <div className="error-alert">
          <span className="icon">⚠️</span>
          <div className="content">
            <h4>Warning</h4>
            <p>{error}</p>
          </div>
          <button
            className="close-btn"
            onClick={() => setError(null)}
          >
            ×
          </button>
        </div>
      )}

      {/* Bank Transfer Section */}
      <div className="bank-transfer-section">
        <h3>🏦 Bank Transfer (Wire Transfer)</h3>
        <p className="bank-transfer-description">
          Make a direct bank transfer to our account. Your invoice will be marked as paid once we receive the funds.
        </p>

        <div className="bank-details-card">
          <div className="bank-detail-row">
            <span className="bank-label">Account Holder:</span>
            <span className="bank-value">Gabani Transport Solutions LLC</span>
          </div>
          <div className="bank-detail-row">
            <span className="bank-label">Account Number:</span>
            <span className="bank-value">200116499651</span>
          </div>
          <div className="bank-detail-row">
            <span className="bank-label">Institution/Transit:</span>
            <span className="bank-value">621 / 16001</span>
          </div>
          <div className="bank-detail-row">
            <span className="bank-label">SWIFT/BIC:</span>
            <span className="bank-value">TRWICAW1XXX</span>
          </div>
          <div className="bank-detail-row">
            <span className="bank-label">Bank:</span>
            <span className="bank-value">Wise Payments Canada Inc.</span>
          </div>
          <div className="bank-warning">
            <p className="warning-text">⚠️ Important: Please include your invoice number in the transfer reference.</p>
          </div>
        </div>

        <button
          onClick={copyToClipboard}
          className="copy-bank-details-btn"
        >
          📋 Copy Bank Details
        </button>
      </div>

      {/* FAQ Section */}
      <div className="faq-section">
        <h3>❓ Frequently Asked Questions</h3>

        <div className="faq-item">
          <h4>How is payment made?</h4>
          <p>
            Online Sudapay checkout has been removed. Use bank transfer or contact finance support
            for an approved payment method.
          </p>
        </div>

        <div className="faq-item">
          <h4>Is the data secure?</h4>
          <p>
            Yes, all transactions are protected with military-grade encryption (TLS 1.3)
            and comply with the standards of the Central Bank of Sudan.
          </p>
        </div>

        <div className="faq-item">
          <h4>What if payment fails?</h4>
          <p>
            You can retry the payment again. If the problem persists,
            contact our support team.
          </p>
        </div>

        <div className="faq-item">
          <h4>How long does payment processing take?</h4>
          <p>
            Usually, payment is confirmed immediately. Some methods may take a bit longer
            depending on the selected method.
          </p>
        </div>
      </div>

      {/* Support Section */}
      <div className="support-section">
        <h3>📞 Need help?</h3>
        <p>
          Contact our support team at
          <a href="tel:+249123456789"> +249 123 456 789</a> or
          <a href="mailto:support@gtslogistics.sd"> support@gtslogistics.sd</a>
        </p>
      </div>

      {/* Styles */}
      <style>{`
        .payment-page {
          max-width: 1000px;
          margin: 0 auto;
          padding: 20px;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          direction: rtl;
          text-align: right;
        }

        .page-header {
          display: flex;
          align-items: center;
          gap: 15px;
          margin-bottom: 30px;
          padding-bottom: 20px;
          border-bottom: 2px solid #f0f0f0;
        }

        .btn-back {
          background: none;
          border: none;
          font-size: 18px;
          cursor: pointer;
          color: #666;
          transition: color 0.3s ease;
        }

        .btn-back:hover {
          color: #333;
        }

        .page-header h1 {
          margin: 0;
          flex: 1;
          font-size: 28px;
          color: #333;
        }

        .invoice-summary {
          margin-bottom: 40px;
        }

        .summary-card {
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 12px;
          padding: 25px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }


        .summary-card h3 {
          margin: 0 0 20px 0;
          font-size: 18px;
          color: #333;
        }

        .summary-row {
          display: flex;
          justify-content: space-between;
          padding: 15px 0;
          border-bottom: 1px solid #f0f0f0;
        }

        .summary-row:last-child {
          border-bottom: none;
        }

        .summary-row.total {
          background: #f9f9f9;
          padding: 15px;
          margin: 10px -25px -25px -25px;
          border-radius: 0 0 12px 12px;
          font-weight: bold;
          font-size: 16px;
        }

        .summary-row.notes .value {
          text-align: left;
          max-width: 400px;
        }

        .label {
          font-weight: 600;
          color: #666;
        }

        .value {
          color: #333;
          font-weight: 500;
        }

        .status-badge {
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 12px;
          font-weight: 600;
          background: #e0e0e0;
          color: #666;
        }

        .status-badge.paid {
          background: #e8f5e9;
          color: #27ae60;
        }

        .status-badge.pending {
          background: #fff3e0;
          color: #f57c00;
        }

        .status-badge.cancelled {
          background: #ffebee;
          color: #c62828;
        }

        .payment-form-section {
          margin-bottom: 40px;
        }

        .error-alert {
          background: #ffebee;
          border-left: 4px solid #c62828;
          padding: 15px;
          border-radius: 8px;
          display: flex;
          gap: 15px;
          align-items: flex-start;
          margin-bottom: 20px;
        }

        .error-alert .icon {
          font-size: 20px;
          flex-shrink: 0;
        }

        .error-alert .content {
          flex: 1;
        }

        .error-alert h4 {
          margin: 0 0 5px 0;
          color: #c62828;
        }

        .error-alert p {
          margin: 0;
          color: #a00;
        }

        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: #c62828;
          flex-shrink: 0;
        }

        .bank-transfer-section {
          margin-bottom: 40px;
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 12px;
          padding: 25px;
          box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }

        .bank-transfer-section h3 {
          margin: 0 0 15px 0;
          font-size: 18px;
          color: #333;
        }

        .bank-transfer-description {
          color: #666;
          margin-bottom: 20px;
          line-height: 1.5;
        }

        .bank-details-card {
          background: #f8f9fa;
          border-radius: 8px;
          padding: 20px;
          margin-bottom: 20px;
        }

        .bank-detail-row {
          display: flex;
          justify-content: space-between;
          padding: 8px 0;
          border-bottom: 1px solid #e9ecef;
        }

        .bank-detail-row:last-child {
          border-bottom: none;
        }

        .bank-label {
          font-weight: 600;
          color: #495057;
        }

        .bank-value {
          color: #212529;
          font-family: monospace;
          font-weight: 500;
        }

        .bank-warning {
          margin-top: 15px;
          padding-top: 15px;
          border-top: 1px solid #dee2e6;
        }

        .warning-text {
          color: #856404;
          background: #fff3cd;
          padding: 10px;
          border-radius: 4px;
          border: 1px solid #ffeaa7;
          margin: 0;
          font-size: 14px;
        }

        .copy-bank-details-btn {
          width: 100%;
          padding: 12px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 6px;
          font-size: 16px;
          cursor: pointer;
          transition: background-color 0.3s ease;
        }

        .copy-bank-details-btn:hover {
          background: #0056b3;
        }

        .stripe-climate-section {
          margin-bottom: 40px;
        }

        .climate-card {
          background: linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(16, 185, 129, 0.1) 100%);
          border: 1px solid rgba(34, 197, 94, 0.3);
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 4px 12px rgba(34, 197, 94, 0.1);
        }

        .climate-header {
          display: flex;
          align-items: flex-start;
          gap: 15px;
          margin-bottom: 15px;
        }

        .climate-icon {
          width: 40px;
          height: 40px;
          background: rgba(34, 197, 94, 0.2);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;
        }

        .climate-icon span {
          font-size: 20px;
        }

        .climate-info h3 {
          margin: 0 0 5px 0;
          font-size: 18px;
          color: white;
          font-weight: 600;
        }

        .climate-info p {
          margin: 0;
          color: #10b981;
          font-size: 14px;
          line-height: 1.4;
        }

        .climate-progress {
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 15px;
        }

        .progress-bar {
          flex: 1;
          height: 8px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 4px;
          overflow: hidden;
        }

        .progress-fill {
          width: 100%;
          height: 100%;
          background: #22c55e;
          border-radius: 4px;
        }

        .progress-text {
          color: #10b981;
          font-size: 12px;
          font-weight: 600;
          white-space: nowrap;
        }

        .climate-features {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-bottom: 15px;
          font-size: 12px;
          color: #6b7280;
        }

        .feature {
          color: #10b981;
          font-weight: 500;
        }

        .separator {
          color: #9ca3af;
        }

        .climate-breakdown {
          border-top: 1px solid rgba(34, 197, 94, 0.2);
          padding-top: 15px;
        }

        .breakdown-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 4px 0;
          font-size: 12px;
        }

        .breakdown-row.total {
          border-top: 1px solid rgba(34, 197, 94, 0.3);
          padding-top: 8px;
          margin-top: 8px;
          font-weight: 600;
          font-size: 14px;
        }

        .breakdown-label {
          color: #9ca3af;
        }

        .breakdown-value {
          color: white;
          font-weight: 500;
        }

        .climate-amount {
          color: #10b981 !important;
        }

        .faq-section {
          background: #f5f5f5;
          padding: 30px;
          border-radius: 12px;
          margin-bottom: 30px;
        }

        .faq-section h3 {
          margin: 0 0 20px 0;
          font-size: 20px;
          color: #333;
        }

        .faq-item {
          background: white;
          padding: 15px;
          margin-bottom: 15px;
          border-radius: 8px;
          border-left: 3px solid #27ae60;
        }

        .faq-item h4 {
          margin: 0 0 8px 0;
          color: #333;
          font-size: 14px;
        }

        .faq-item p {
          margin: 0;
          color: #666;
          font-size: 13px;
          line-height: 1.6;
        }

        .support-section {
          background: linear-gradient(135deg, #27ae60, #229954);
          color: white;
          padding: 30px;
          border-radius: 12px;
          text-align: center;
        }

        .support-section h3 {
          margin: 0 0 15px 0;
          font-size: 20px;
        }

        .support-section p {
          margin: 0;
          font-size: 14px;
          line-height: 1.8;
        }

        .support-section a {
          color: white;
          font-weight: 600;
          text-decoration: none;
        }

        .support-section a:hover {
          text-decoration: underline;
        }

        .payment-loading,
        .payment-error {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 400px;
        }

        .loader,
        .error-card,
        .success-card {
          text-align: center;
        }

        .loader span,
        .error-card .icon,
        .success-card .icon {
          font-size: 48px;
          display: block;
          margin-bottom: 15px;
        }

        .success-card {
          background: #e8f5e9;
          border: 2px solid #27ae60;
          padding: 40px;
          border-radius: 12px;
          max-width: 500px;
        }

        .success-card h2 {
          color: #27ae60;
          margin: 15px 0;
        }

        .details {
          background: white;
          padding: 15px;
          border-radius: 8px;
          margin: 20px 0;
          text-align: right;
        }

        .details p {
          margin: 8px 0;
          color: #666;
        }

        .btn-continue {
          background: #27ae60;
          color: white;
          border: none;
          padding: 12px 30px;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          transition: all 0.3s ease;
        }

        .btn-continue:hover {
          background: #229954;
          transform: translateY(-2px);
        }

        /* Mobile Responsive */
        @media (max-width: 768px) {
          .payment-page {
            padding: 15px;
          }

          .page-header {
            flex-direction: column;
            align-items: flex-start;
          }

          .invoice-summary,
          .faq-section,
          .support-section {
            margin-bottom: 25px;
          }

          .summary-card {
            padding: 15px;
          }
        }
      `}</style>
    </div>
  );
}

/**
 * Helper Functions
 */

/**
 * Translate Status - Translate invoice status
 */
function translateStatus(status) {
  const statusMap = {
    'draft': '♠️ Draft',
    'sent': '📤 Sent',
    'pending': '⏳ Pending',
    'paid': '✅ Paid',
    'overdue': '⚠️ Overdue',
    'cancelled': '❌ Cancelled',
    'refunded': '🔄 Refunded',
  };
  return statusMap[status] || status;
}

/**
 * Format Amount - Format amount
 */
function formatAmount(amount, currency = 'SDG') {
  // Use current currency from store if no currency specified
  const currentCurrency = currency || useCurrencyStore.getState().currency;
  const locale = useCurrencyStore.getState().currencyLocale;

  const formatter = new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currentCurrency,
    minimumFractionDigits: 2,
  });
  return formatter.format(amount);
}

export default PaymentPage;
