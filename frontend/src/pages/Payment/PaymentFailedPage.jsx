/**
 * PaymentFailedPage Component - صفحة فشل الدفع
 * عرض رسالة الخطأ والخيارات المتاحة
 * 
 * المميزات:
 * - عرض سبب الفشل
 * - خيارات إعادة المحاولة
 * - معلومات الدعم الفني
 * - دعم اللغة العربية
 * 
 * Routes:
 * - /payments/failed - صفحة الفشل
 * 
 * Author: GTS Development Team
 * Date: March 2026
 */

import React, { useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

/**
 * PaymentFailedPage Component
 * صفحة عرض فشل العملية مع الخيارات
 */
export function PaymentFailedPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const paymentId = searchParams.get('payment_id');
    const invoiceId = searchParams.get('invoice_id');
    const reason = searchParams.get('reason') || 'الدفع غير مكتمل';

    const [retrying, setRetrying] = useState(false);

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
                title: 'رصيد غير كافي',
                description: 'يبدو أن رصيدك غير كافي لإتمام هذه العملية. يرجى التأكد من وجود رصيد كافي والمحاولة مرة أخرى.',
                icon: '💰',
                actions: ['محاولة طريقة دفع أخرى', 'إضافة رصيد', 'العودة'],
            },
            'card_declined': {
                title: 'تم رفض البطاقة',
                description: 'تم رفض البطاقة من قبل البنك. قد يكون السبب أمان أو مشكلة أخرى. تواصل مع البنك لمزيد من التفاصيل.',
                icon: '🚫',
                actions: ['محاولة بطاقة أخرى', 'التواصل مع البنك', 'العودة'],
            },
            'expired_card': {
                title: 'البطاقة منتهية الصلاحية',
                description: 'بطاقتك منتهية الصلاحية. يرجى استخدام بطاقة صحيحة.',
                icon: '📆',
                actions: ['استخدام بطاقة أخرى', 'العودة'],
            },
            'network_error': {
                title: 'خطأ في الاتصال',
                description: 'حدث خطأ في الاتصال بخادم الدفع. يرجى المحاولة مرة أخرى.',
                icon: '🌐',
                actions: ['إعادة المحاولة', 'العودة'],
            },
            'timeout': {
                title: 'انتهت المهلة الزمنية',
                description: 'استغرقت العملية وقتاً طويلاً جداً. يرجى المحاولة مرة أخرى.',
                icon: '⏱️',
                actions: ['إعادة المحاولة', 'العودة'],
            },
            'cancelled': {
                title: 'تم إلغاء الدفع',
                description: 'تم إلغاء عملية الدفع. يمكنك إعادة المحاولة في أي وقت.',
                icon: '❌',
                actions: ['إعادة المحاولة', 'العودة'],
            },
        };
        return errorMap[reason] || {
            title: 'فشل الدفع',
            description: reason || 'حدث خطأ أثناء معالجة الدفع.',
            icon: '❌',
            actions: ['إعادة المحاولة', 'العودة'],
        };
    };

    const errorDetails = getErrorDetails();

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
                                <span className="label">معرف الدفعة:</span>
                                <span className="value">{paymentId}</span>
                            </div>
                        )}
                        {invoiceId && (
                            <div className="detail">
                                <span className="label">رقم الفاتورة:</span>
                                <span className="value">#{invoiceId}</span>
                            </div>
                        )}
                        <div className="detail">
                            <span className="label">السبب:</span>
                            <span className="value">{reason}</span>
                        </div>
                        <div className="detail">
                            <span className="label">التاريخ والوقت:</span>
                            <span className="value">
                                {new Date().toLocaleString('ar-SD')}
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
                            {retrying ? '⏳ جاري المحاولة...' : '🔄 إعادة المحاولة'}
                        </button>
                        <button
                            className="btn-alt1"
                            onClick={() => navigate(`/payments/${invoiceId}`)}
                        >
                            💳 محاولة طريقة دفع أخرى
                        </button>
                        <button
                            className="btn-alt2"
                            onClick={() => navigate('/invoices')}
                        >
                            📋 العودة للفواتير
                        </button>
                    </div>

                    {/* Support Section */}
                    <div className="support-section">
                        <h3>📞 هل تحتاج للمساعدة؟</h3>
                        <p>
                            إذا استمرت المشكلة، يرجى التواصل مع فريق الدعم:
                        </p>
                        <div className="support-contacts">
                            <a href="mailto:support@gtslogistics.sd" className="support-link">
                                📧 support@gtslogistics.sd
                            </a>
                            <a href="tel:+249123456789" className="support-link">
                                📞 +249 123 456 789
                            </a>
                            <a href="https://wa.me/249123456789" className="support-link">
                                💬 تواصل عبر WhatsApp
                            </a>
                        </div>
                    </div>

                    {/* Tips */}
                    <div className="tips-section">
                        <h4>💡 نصائح للمساعدة:</h4>
                        <ul>
                            <li>✓ تأكد من اتصالك بالإنترنت</li>
                            <li>✓ تحقق من بيانات الدفعة (المبلغ، العملة)</li>
                            <li>✓ تأكد من أن لديك رصيد كافي</li>
                            <li>✓ حاول من متصفح آخر إذا استمرت المشكلة</li>
                            <li>✓ امسح ذاكرة التخزين المؤقت للمتصفح</li>
                        </ul>
                    </div>
                </div>

                {/* FAQ */}
                <div className="faq-section">
                    <h3>❓ أسئلة متكررة</h3>

                    <div className="faq-items">
                        <div className="faq-item">
                            <button className="faq-toggle">
                                لماذا تم رفض الدفع؟
                            </button>
                            <div className="faq-content">
                                قد يكون الرفض بسبب عدة أسباب منها: رصيد غير كافي،
                                بيانات بطاقة غير صحيحة، أو إجراءات أمان من البنك.
                            </div>
                        </div>

                        <div className="faq-item">
                            <button className="faq-toggle">
                                هل سيتم خصم المبلغ من حسابي؟
                            </button>
                            <div className="faq-content">
                                لا، عند فشل الدفع لا يتم خصم أي مبلغ. جميع المحاولات الفاشلة
                                لا تترك اثراً على حسابك.
                            </div>
                        </div>

                        <div className="faq-item">
                            <button className="faq-toggle">
                                كيف أعرف أن الدفع نجح؟
                            </button>
                            <div className="faq-content">
                                ستظهر صفحة تأكيد النجاح عند اكتمال الدفع. كما ستتلقى
                                بريداً إلكترونياً بتأكيد العملية.
                            </div>
                        </div>

                        <div className="faq-item">
                            <button className="faq-toggle">
                                هل يمكن استخدام عملة أخرى للدفع؟
                            </button>
                            <div className="faq-content">
                                نعم، نحن ندعم الدفع بعملات متعددة منها الجنيه السوداني (SDG)
                                والدولار الأمريكي (USD).
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Styles */}
            <style jsx>{`
        .payment-failed-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          direction: rtl;
          text-align: right;
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
          text-align: right;
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
          text-align: right;
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
          text-align: right;
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
