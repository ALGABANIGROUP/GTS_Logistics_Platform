/**
 * PaymentFailedPage Component - Payment failure page
 * Displays error message and available options
 * 
 * Features:
 * - Display failure reason
 * - Retry options
 * - Technical support information
 * - English language support
 * 
 * Routes:
 * - /payments/failed - Failure page
 * 
 * Author: GTS Development Team
 * Date: March 2026
 */

import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

/**
 * PaymentFailedPage Component
 * Page to display payment failure with options
 */
export function PaymentFailedPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const paymentId = searchParams.get('payment_id');
    const invoiceId = searchParams.get('invoice_id');
    const reason = searchParams.get('reason') || 'Payment incomplete';

    const [retrying, setRetrying] = useState(false);
    const [openFaq, setOpenFaq] = useState(0);

    /**
     * Handle Retry Payment
     */
    const handleRetry = async () => {
        setRetrying(true);
        try {
            // Navigate back to payment page
            navigate(`/payments/${invoiceId}`);
        } catch (err) {
            console.error('Error retrying payment:', err);
            setRetrying(false);
        }
    };

    /**
     * Get Error Details
     */
    const getErrorDetails = () => {
        const errorMap = {
            'insufficient_funds': {
                title: 'Insufficient Funds',
                description: 'Your balance is insufficient to complete this transaction. Please ensure sufficient funds and try again.',
                icon: '💰',
                actions: ['Try another payment method', 'Add funds', 'Go back'],
            },
            'card_declined': {
                title: 'Card Declined',
                description: 'Your card was declined by the bank. This may be due to security reasons or other issues. Contact your bank for details.',
                icon: '🚫',
                actions: ['Try another card', 'Contact your bank', 'Go back'],
            },
            'expired_card': {
                title: 'Expired Card',
                description: 'Your card has expired. Please use a valid card.',
                icon: '📆',
                actions: ['Use another card', 'Go back'],
            },
            'network_error': {
                title: 'Network Error',
                description: 'A connection error occurred with the payment server. Please try again.',
                icon: '🌐',
                actions: ['Retry', 'Go back'],
            },
            'timeout': {
                title: 'Timeout',
                description: 'The transaction took too long to complete. Please try again.',
                icon: '⏱️',
                actions: ['Retry', 'Go back'],
            },
            'cancelled': {
                title: 'Payment Cancelled',
                description: 'Payment was cancelled. You can retry at any time.',
                icon: '❌',
                actions: ['Retry', 'Go back'],
            },
        };
        return errorMap[reason] || {
            title: 'Payment Failed',
            description: reason || 'An error occurred while processing payment.',
            icon: '❌',
            actions: ['Retry', 'Go back'],
        };
    };

    const errorDetails = getErrorDetails();
    const faqItems = [
        {
            question: 'Why was my payment declined?',
            answer: 'Payment may be declined due to several reasons: insufficient funds, incorrect card details, or bank security measures.',
        },
        {
            question: 'Will the amount be deducted from my account?',
            answer: 'No, if payment fails, no amount is deducted. All failed attempts leave no impact on your account.',
        },
        {
            question: 'How do I know if payment was successful?',
            answer: 'A success confirmation page will appear upon completion. You will also receive an email confirmation.',
        },
        {
            question: 'Can I pay in another currency?',
            answer: 'Yes, we support multiple currencies including Sudanese Pound (SDG) and US Dollar (USD).',
        },
    ];

    return (
        <div className="payment-failed-page">
            {/* Background Gradient */}
            <div className="background"></div>

            {/* Content */}
            <div className="failed-container">
                <div className="failed-card">
                    {/* Icon */}
                    <div className="failed-icon">
                        {errorDetails.icon}
                    </div>

                    {/* Title */}
                    <h1>{errorDetails.title}</h1>

                    {/* Description */}
                    <p className="description">
                        {errorDetails.description}
                    </p>

                    {/* Error Details */}
                    <div className="error-details">
                        {paymentId && (
                            <div className="detail">
                                <span className="label">Payment ID:</span>
                                <span className="value">{paymentId}</span>
                            </div>
                        )}
                        {invoiceId && (
                            <div className="detail">
                                <span className="label">Invoice Number:</span>
                                <span className="value">#{invoiceId}</span>
                            </div>
                        )}
                        <div className="detail">
                            <span className="label">Reason:</span>
                            <span className="value">{reason}</span>
                        </div>
                        <div className="detail">
                            <span className="label">Date & Time:</span>
                            <span className="value">
                                {new Date().toLocaleString()}
                            </span>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="actions">
                        <button
                            className="btn-retry"
                            onClick={handleRetry}
                            disabled={retrying}
                        >
                            {retrying ? '⏳ Retrying...' : '🔄 Retry'}
                        </button>
                        <button
                            className="btn-alt1"
                            onClick={() => navigate(`/payments/${invoiceId}`)}
                        >
                            💳 Try another payment method
                        </button>
                        <button
                            className="btn-alt2"
                            onClick={() => navigate('/invoices')}
                        >
                            📋 Back to Invoices
                        </button>
                    </div>

                    {/* Support Section */}
                    <div className="support-section">
                        <h3>📞 Need Help?</h3>
                        <p>
                            If the problem persists, please contact our support team:
                        </p>
                        <div className="support-contacts">
                            <a href="mailto:support@gtslogistics.sd" className="support-link">
                                📧 support@gtslogistics.sd
                            </a>
                            <a href="tel:+249123456789" className="support-link">
                                📞 +249 123 456 789
                            </a>
                            <a href="https://wa.me/249123456789" className="support-link">
                                💬 Contact via WhatsApp
                            </a>
                        </div>
                    </div>

                    {/* Tips */}
                    <div className="tips-section">
                        <h4>💡 Helpful Tips:</h4>
                        <ul>
                            <li>✓ Check your internet connection</li>
                            <li>✓ Verify payment details (amount, currency)</li>
                            <li>✓ Ensure sufficient funds</li>
                            <li>✓ Try a different browser if issue persists</li>
                            <li>✓ Clear browser cache and cookies</li>
                        </ul>
                    </div>
                </div>

                {/* FAQ */}
                <div className="faq-section">
                    <h3>❓ Frequently Asked Questions</h3>

                    <div className="faq-items">
                        {faqItems.map((item, index) => (
                            <div key={item.question} className="faq-item">
                                <button
                                    type="button"
                                    className="faq-toggle"
                                    onClick={() => setOpenFaq((current) => (current === index ? -1 : index))}
                                    aria-expanded={openFaq === index}
                                >
                                    {item.question}
                                </button>
                                {openFaq === index ? (
                                    <div className="faq-content">
                                        {item.answer}
                                    </div>
                                ) : null}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Styles */}
            <style>{`
        .payment-failed-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          direction: ltr;
          text-align: left;
        }

        .failed-container {
          max-width: 900px;
          width: 100%;
        }

        .failed-card {
          background: white;
          border-radius: 20px;
          padding: 40px;
          box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
          text-align: center;
          margin-bottom: 30px;
        }


        .failed-icon {
          font-size: 80px;
          margin-bottom: 20px;
          animation: shake 0.5s ease-in-out;
        }

        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          25% { transform: translateX(-10px); }
          75% { transform: translateX(10px); }
        }

        .failed-card h1 {
          font-size: 32px;
          color: #c62828;
          margin: 0 0 15px 0;
        }

        .description {
          color: #666;
          font-size: 16px;
          line-height: 1.6;
          margin: 0 0 25px 0;
        }

        .error-details {
          background: #f5f5f5;
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 25px;
          text-align: left;
        }

        .detail {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 10px 0;
          border-bottom: 1px solid #e0e0e0;
        }

        .detail:last-child {
          border-bottom: none;
        }

        .detail .label {
          font-weight: 600;
          color: #666;
          font-size: 13px;
        }

        .detail .value {
          color: #333;
          font-size: 13px;
        }

        .actions {
          display: flex;
          flex-direction: column;
          gap: 12px;
          margin-bottom: 25px;
        }

        button {
          padding: 14px 24px;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .btn-retry {
          background: linear-gradient(135deg, #c62828, #b71c1c);
          color: white;
        }

        .btn-retry:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(198, 40, 40, 0.3);
        }

        .btn-retry:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }

        .btn-alt1 {
          background: #fff3e0;
          color: #e65100;
        }

        .btn-alt1:hover {
          background: #ffe0b2;
        }

        .btn-alt2 {
          background: #e0e0e0;
          color: #333;
        }

        .btn-alt2:hover {
          background: #d0d0d0;
        }

        .support-section {
          background: #e3f2fd;
          border: 2px solid #1976d2;
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 20px;
        }

        .support-section h3 {
          margin: 0 0 12px 0;
          color: #1565c0;
          font-size: 16px;
        }

        .support-section p {
          margin: 0 0 15px 0;
          color: #555;
          font-size: 13px;
        }

        .support-contacts {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }

        .support-link {
          display: inline-block;
          color: #1976d2;
          text-decoration: none;
          padding: 8px 0;
          font-weight: 600;
          transition: all 0.3s ease;
        }

        .support-link:hover {
          color: #1565c0;
          text-decoration: underline;
        }

        .tips-section {
          background: #f5f5f5;
          border-radius: 12px;
          padding: 20px;
          margin-bottom: 0;
          text-align: left;
        }

        .tips-section h4 {
          margin: 0 0 15px 0;
          color: #333;
          font-size: 14px;
        }

        .tips-section ul {
          list-style: none;
          padding: 0;
          margin: 0;
        }

        .tips-section li {
          padding: 8px 0;
          color: #666;
          font-size: 13px;
        }

        .faq-section {
          background: white;
          border-radius: 16px;
          padding: 30px;
          box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
        }

        .faq-section h3 {
          margin: 0 0 20px 0;
          font-size: 18px;
          color: #333;
        }

        .faq-items {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .faq-item {
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          overflow: hidden;
        }

        .faq-toggle {
          width: 100%;
          padding: 15px;
          background: #f9f9f9;
          border: none;
          cursor: pointer;
          text-align: left;
          font-weight: 600;
          color: #333;
          transition: all 0.3s ease;
        }

        .faq-toggle:hover {
          background: #f0f0f0;
        }

        .faq-content {
          padding: 15px;
          color: #666;
          font-size: 13px;
          line-height: 1.6;
          background: white;
          display: none;
        }

        .faq-item:hover .faq-content {
          display: block;
        }

        /* Mobile Responsive */
        @media (max-width: 700px) {
          .failed-card {
            padding: 25px;
          }

          .failed-card h1 {
            font-size: 24px;
          }

          .failed-icon {
            font-size: 60px;
          }

          .actions {
            gap: 10px;
          }

          button {
            width: 100%;
            font-size: 13px;
          }

          .detail {
            flex-direction: column;
            align-items: flex-start;
            gap: 5px;
          }
        }
      `}</style>
        </div>
    );
}

export default PaymentFailedPage;
