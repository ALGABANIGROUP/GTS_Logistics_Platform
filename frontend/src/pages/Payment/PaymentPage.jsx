/**
 * PaymentPage Component - صفحة الدفع الرئيسية
 * توفير تجربة دفع كاملة مع SUDAPAY
 * 
 * المميزات:
 * - عرض بيانات الفاتورة
 * - محرر نموذج الدفع
 * - معالجة الأخطاء
 * - دعم اللغة العربية
 * 
 * Routes:
 * - /payments/:invoiceId - الدفع للفاتورة
 * 
 * Author: GTS Development Team
 * Date: March 2026
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import SudaPaymentForm from '../../components/SudaPaymentForm';
import { readAuthToken } from '../../utils/authStorage';
import { useCurrencyStore } from '../../stores/useCurrencyStore';

/**
 * PaymentPage Component
 * صفحة الدفع الكاملة مع معلومات الفاتورة والنموذج
 */
export function PaymentPage() {
  const { invoiceId } = useParams();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const paymentStatus = searchParams.get('status');
  const paymentId = searchParams.get('payment_id');

  /**
   * Load Invoice Data - تحميل بيانات الفاتورة
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
          throw new Error('فشل تحميل بيانات الفاتورة');
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
   * Handle Payment Success - معالج النجاح
   */
  const handlePaymentSuccess = () => {
    console.log('✅ Payment successful!');
    navigate(`/payments/success?payment_id=${paymentId}&invoice_id=${invoiceId}`);
  };

  /**
   * Handle Payment Error - معالج الخطأ
   */
  const handlePaymentError = (errorMsg) => {
    console.error('❌ Payment error:', errorMsg);
    setError(errorMsg);
  };

  /**
   * Go Back - العودة للخلف
   */
  const goBack = () => {
    navigate('/invoices');
  };

  /* Loading State */
  if (loading) {
    return (
      <div className="payment-loading">
        <div className="loader">
          <span>📥</span>
          <p>جاري تحميل بيانات الفاتورة...</p>
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
          <h2>حدث خطأ</h2>
          <p>{error}</p>
          <button className="btn-back" onClick={goBack}>
            العودة للفواتير
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
          <h2>تم الدفع بنجاح!</h2>
          <p>تم استقبال دفعتك وجاري معالجتها</p>
          <div className="details">
            <p>معرف الدفعة: <strong>{paymentId}</strong></p>
            <p>الفاتورة: <strong>#{invoiceId}</strong></p>
          </div>
          <button className="btn-continue" onClick={() => navigate('/invoices')}>
            العودة للفواتير
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
          ← العودة
        </button>
        <h1>💳 الدفع</h1>
      </div>

      {/* Invoice Summary */}
      {invoice && (
        <div className="invoice-summary">
          <div className="summary-card">
            <h3>📋 ملخص الفاتورة</h3>

            <div className="summary-row">
              <span className="label">رقم الفاتورة:</span>
              <span className="value">#{invoice.id}</span>
            </div>

            <div className="summary-row">
              <span className="label">الشاحن:</span>
              <span className="value">{invoice.shipper_name || 'غير معروف'}</span>
            </div>

            <div className="summary-row">
              <span className="label">الحامل:</span>
              <span className="value">{invoice.carrier_name || 'غير معروف'}</span>
            </div>

            <div className="summary-row">
              <span className="label">الحالة:</span>
              <span className={`status-badge ${invoice.status}`}>
                {translateStatus(invoice.status)}
              </span>
            </div>

            <div className="summary-row total">
              <span className="label">المبلغ المستحق:</span>
              <span className="value">
                {formatAmount(invoice.total_amount, invoice.currency)}
              </span>
            </div>

            {invoice.notes && (
              <div className="summary-row notes">
                <span className="label">ملاحظات:</span>
                <span className="value">{invoice.notes}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Payment Form */}
      <div className="payment-form-section">
        {invoice && (
          <SudaPaymentForm
            invoiceId={invoice.id}
            amount={invoice.total_amount}
            currency={invoice.currency || 'SDG'}
            onSuccess={handlePaymentSuccess}
            onError={handlePaymentError}
          />
        )}
      </div>

      {/* Previous Error */}
      {error && (
        <div className="error-alert">
          <span className="icon">⚠️</span>
          <div className="content">
            <h4>تنبيه</h4>
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

      {/* FAQ Section */}
      <div className="faq-section">
        <h3>❓ الأسئلة الشائعة</h3>

        <div className="faq-item">
          <h4>كيف يتم الدفع؟</h4>
          <p>
            انقر على زر "الدفع الآن" لتحويلك إلى منصة SUDAPAY الآمنة.
            هناك ستتمكن من اختيار طريقة الدفع المفضلة لديك.
          </p>
        </div>

        <div className="faq-item">
          <h4>هل البيانات آمنة؟</h4>
          <p>
            نعم، جميع المعاملات محمية بتشفير من الدرجة العسكرية (TLS 1.3)
            وتتوافق مع معايير البنك المركزي السوداني.
          </p>
        </div>

        <div className="faq-item">
          <h4>ماذا لو فشل الدفع؟</h4>
          <p>
            يمكنك إعادة محاولة الدفع مرة أخرى. إذا استمرت المشكلة،
            تواصل مع فريق الدعم لدينا.
          </p>
        </div>

        <div className="faq-item">
          <h4>كم وقت تستغرق معالجة الدفع؟</h4>
          <p>
            عادة ما يتم تأكيد الدفع فوراً. قد تستغرق بعض الطرق وقتاً أطول
            قليلاً حسب الطريقة المختارة.
          </p>
        </div>
      </div>

      {/* Support Section */}
      <div className="support-section">
        <h3>📞 هل تحتاج للمساعدة؟</h3>
        <p>
          تواصل مع فريق الدعم على
          <a href="tel:+249123456789"> +249 123 456 789</a> أو
          <a href="mailto:support@gtslogistics.sd"> support@gtslogistics.sd</a>
        </p>
      </div>

      {/* Styles */}
      <style jsx>{`
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
 * Translate Status - ترجمة حالة الفاتورة
 */
function translateStatus(status) {
  const statusMap = {
    'draft': '♠️ مسودة',
    'sent': '📤 مرسلة',
    'pending': '⏳ معلقة',
    'paid': '✅ مدفوعة',
    'overdue': '⚠️ متأخرة',
    'cancelled': '❌ ملغاة',
    'refunded': '🔄 مسترجعة',
  };
  return statusMap[status] || status;
}

/**
 * Format Amount - تنسيق المبلغ
 */
function formatAmount(amount, currency = 'SDG') {
  // استخدام العملة الحالية من المتجر إذا لم يتم تحديد عملة
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
