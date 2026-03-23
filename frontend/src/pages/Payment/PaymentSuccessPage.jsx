import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import paymentApi from '../../api/paymentApi';

export function PaymentSuccessPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();

    const paymentId = searchParams.get('payment_id');
    const invoiceId = searchParams.get('invoice_id');

    const [payment, setPayment] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [copied, setCopied] = useState(false);

    useEffect(() => {
        const loadPayment = async () => {
            try {
                if (!paymentId) {
                    throw new Error('معرف الدفعة غير موجود');
                }

                setLoading(true);
                const paymentData = await paymentApi.get(paymentId);
                setPayment(paymentData);
            } catch (err) {
                setError(err?.response?.data?.detail || err.message || 'فشل تحميل بيانات الدفعة');
            } finally {
                setLoading(false);
            }
        };

        loadPayment();
    }, [paymentId]);

    const goToInvoice = () => {
        if (invoiceId) {
            navigate(`/invoices/${invoiceId}`);
            return;
        }
        navigate('/invoices');
    };

    const copyToClipboard = async (text) => {
        if (!text) {
            return;
        }
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const downloadReceipt = () => {
        if (!payment) {
            return;
        }

        const receipt = [
            'إيصال الدفع',
            '------------------------------',
            `معرف الدفعة: ${payment.reference_id}`,
            `معرف العملية: ${payment.gateway_transaction_id || 'غير متوفر'}`,
            `المبلغ: ${formatAmount(payment.amount, payment.currency)}`,
            `البوابة: ${paymentApi.getGatewayName(payment.payment_gateway)}`,
            `الحالة: ${getStatusText(payment.status)}`,
            `التاريخ: ${new Date(payment.created_at).toLocaleString('ar-SD')}`,
            `رقم الفاتورة: #${payment.invoice_id}`,
        ].join('\n');

        const element = document.createElement('a');
        element.setAttribute('href', `data:text/plain;charset=utf-8,${encodeURIComponent(receipt)}`);
        element.setAttribute('download', `receipt-${payment.reference_id}.txt`);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    if (loading) {
        return (
            <div className="payment-status-page">
                <div className="status-card">
                    <div className="status-icon">⏳</div>
                    <h1>جاري تحميل بيانات الدفع</h1>
                    <p>نسترجع آخر حالة متاحة من النظام.</p>
                </div>
            </div>
        );
    }

    if (error || !payment) {
        return (
            <div className="payment-status-page">
                <div className="status-card">
                    <div className="status-icon">⚠️</div>
                    <h1>تعذر تحميل بيانات الدفع</h1>
                    <p>{error || 'حدث خطأ غير متوقع'}</p>
                    <div className="actions">
                        <button className="btn-primary" onClick={goToInvoice}>عرض الفاتورة</button>
                        <button className="btn-secondary" onClick={() => navigate('/')}>العودة للرئيسية</button>
                    </div>
                </div>
            </div>
        );
    }

    const statusMeta = getStatusMeta(payment.status);

    return (
        <div className="payment-status-page">
            <div className="status-card">
                <div className="status-icon" style={{ color: statusMeta.accentColor }}>
                    {statusMeta.icon}
                </div>
                <h1 style={{ color: statusMeta.accentColor }}>{statusMeta.title}</h1>
                <p className="subtitle">{statusMeta.subtitle}</p>

                <div className="payment-details">
                    <DetailRow
                        label="معرف الدفعة"
                        value={payment.reference_id}
                        action={(
                            <button className="copy-btn" onClick={() => copyToClipboard(payment.reference_id)}>
                                {copied ? 'تم النسخ' : 'نسخ'}
                            </button>
                        )}
                    />
                    <DetailRow label="المبلغ" value={formatAmount(payment.amount, payment.currency)} />
                    <DetailRow label="البوابة" value={paymentApi.getGatewayName(payment.payment_gateway)} />
                    <DetailRow label="رقم الفاتورة" value={`#${payment.invoice_id}`} />
                    <DetailRow label="الحالة" value={getStatusText(payment.status)} />
                    <DetailRow label="معرف العملية" value={payment.gateway_transaction_id || 'غير متوفر'} />
                    <DetailRow label="التاريخ" value={new Date(payment.created_at).toLocaleString('ar-SD')} />
                </div>

                <div
                    className="info-box"
                    style={{
                        background: statusMeta.infoBackground,
                        borderColor: statusMeta.accentColor,
                        color: statusMeta.infoColor,
                    }}
                >
                    <p>{statusMeta.infoLine1}</p>
                    <p>{statusMeta.infoLine2}</p>
                    <p>{statusMeta.infoLine3}</p>
                </div>

                <div className="next-steps">
                    <h2>الخطوات التالية</h2>
                    {statusMeta.steps.map((step, index) => (
                        <div key={step.title} className="step-row">
                            <span className="step-number">{index + 1}</span>
                            <div>
                                <div className="step-title">{step.title}</div>
                                <div className="step-description">{step.description}</div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="actions">
                    <button className="btn-primary" onClick={goToInvoice}>عرض الفاتورة</button>
                    <button className="btn-secondary" onClick={downloadReceipt}>تحميل الإيصال</button>
                    <button className="btn-secondary" onClick={() => navigate('/invoices')}>كل الفواتير</button>
                </div>
            </div>

            <style jsx>{`
                .payment-status-page {
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 24px;
                    background: linear-gradient(180deg, #f5f7fa 0%, #e8eef5 100%);
                    direction: rtl;
                }

                .status-card {
                    width: min(760px, 100%);
                    background: #fff;
                    border-radius: 20px;
                    box-shadow: 0 16px 48px rgba(15, 23, 42, 0.12);
                    padding: 32px;
                    text-align: right;
                }

                .status-icon {
                    font-size: 64px;
                    margin-bottom: 12px;
                    text-align: center;
                }

                h1 {
                    margin: 0 0 8px;
                    text-align: center;
                }

                .subtitle {
                    margin: 0 0 24px;
                    color: #475569;
                    text-align: center;
                }

                .payment-details {
                    display: grid;
                    gap: 12px;
                    background: #f8fafc;
                    border-radius: 14px;
                    padding: 18px;
                }

                .detail-row {
                    display: flex;
                    justify-content: space-between;
                    gap: 16px;
                    align-items: center;
                    border-bottom: 1px solid #e2e8f0;
                    padding-bottom: 10px;
                }

                .detail-row:last-child {
                    border-bottom: none;
                    padding-bottom: 0;
                }

                .detail-label {
                    color: #64748b;
                    font-weight: 600;
                }

                .detail-value {
                    color: #0f172a;
                    font-weight: 500;
                    word-break: break-word;
                }

                .detail-value-group {
                    display: flex;
                    gap: 10px;
                    align-items: center;
                }

                .copy-btn,
                .btn-primary,
                .btn-secondary {
                    border: none;
                    border-radius: 10px;
                    padding: 10px 16px;
                    cursor: pointer;
                    font-weight: 600;
                }

                .copy-btn {
                    background: #e2e8f0;
                    color: #0f172a;
                }

                .info-box {
                    margin-top: 20px;
                    border: 2px solid;
                    border-radius: 14px;
                    padding: 16px;
                }

                .info-box p {
                    margin: 0 0 8px;
                }

                .info-box p:last-child {
                    margin-bottom: 0;
                }

                .next-steps {
                    margin-top: 20px;
                    background: #fff;
                    border: 1px solid #e2e8f0;
                    border-radius: 14px;
                    padding: 18px;
                }

                .next-steps h2 {
                    margin: 0 0 16px;
                    font-size: 20px;
                }

                .step-row {
                    display: flex;
                    gap: 12px;
                    align-items: flex-start;
                    margin-bottom: 14px;
                }

                .step-row:last-child {
                    margin-bottom: 0;
                }

                .step-number {
                    width: 32px;
                    height: 32px;
                    border-radius: 999px;
                    background: #0f172a;
                    color: #fff;
                    display: inline-flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 700;
                    flex-shrink: 0;
                }

                .step-title {
                    font-weight: 700;
                    color: #0f172a;
                    margin-bottom: 4px;
                }

                .step-description {
                    color: #475569;
                }

                .actions {
                    display: flex;
                    gap: 12px;
                    justify-content: center;
                    flex-wrap: wrap;
                    margin-top: 24px;
                }

                .btn-primary {
                    background: #0f766e;
                    color: #fff;
                }

                .btn-secondary {
                    background: #e2e8f0;
                    color: #0f172a;
                }

                @media (max-width: 640px) {
                    .status-card {
                        padding: 20px;
                    }

                    .detail-row {
                        flex-direction: column;
                        align-items: flex-start;
                    }

                    .detail-value-group {
                        width: 100%;
                        justify-content: space-between;
                    }

                    .actions {
                        flex-direction: column;
                    }
                }
            `}</style>
        </div>
    );
}

function DetailRow({ label, value, action = null }) {
    return (
        <div className="detail-row">
            <span className="detail-label">{label}</span>
            <div className="detail-value-group">
                <span className="detail-value">{value}</span>
                {action}
            </div>
        </div>
    );
}

function getStatusText(status) {
    const statusMap = {
        pending: 'قيد الانتظار',
        processing: 'جاري المعالجة',
        completed: 'مكتمل',
        paid: 'مدفوع',
        failed: 'فشل',
        cancelled: 'ملغى',
        refunded: 'مسترجع',
    };
    return statusMap[status] || status;
}

function getStatusMeta(status) {
    const normalized = String(status || 'pending').toLowerCase();

    if (normalized === 'completed' || normalized === 'paid') {
        return {
            icon: '✅',
            accentColor: '#15803d',
            infoBackground: '#ecfdf5',
            infoColor: '#166534',
            title: 'تم الدفع بنجاح',
            subtitle: 'تم تأكيد الدفع وتحديث حالته في النظام.',
            infoLine1: 'تم تأكيد الدفع من المنصة.',
            infoLine2: 'جميع المعاملات محمية ومثبتة في السجل المالي.',
            infoLine3: 'يمكنك الآن متابعة الفاتورة أو تنزيل الإيصال.',
            steps: [
                { title: 'تأكيد الدفع', description: 'تم تسجيل الدفعة كعملية مكتملة.' },
                { title: 'تحديث الفاتورة', description: 'يتم اعتبار الفاتورة مدفوعة في النظام.' },
                { title: 'الاحتفاظ بالمرجع', description: 'احتفظ بمعرف الدفعة ومعرف العملية عند الحاجة.' },
            ],
        };
    }

    if (normalized === 'pending' || normalized === 'processing') {
        return {
            icon: '⏳',
            accentColor: '#b45309',
            infoBackground: '#fffbeb',
            infoColor: '#92400e',
            title: 'الدفع قيد التأكيد',
            subtitle: 'تم استلام الطلب لكن الحالة النهائية لم تُحسم بعد.',
            infoLine1: 'قد يكون الدفع بانتظار تأكيد البوابة أو وصول webhook.',
            infoLine2: 'ارجع لهذه الصفحة لاحقًا أو راجع الفاتورة.',
            infoLine3: 'لا تعتمد هذه الصفحة كإثبات نهائي حتى تصبح الحالة مكتملة.',
            steps: [
                { title: 'تسجيل الطلب', description: 'تم إنشاء سجل الدفع محليًا.' },
                { title: 'انتظار التحديث', description: 'ننتظر رد البوابة أو إشعار الويبهوك.' },
                { title: 'المتابعة', description: 'راجع الفاتورة لاحقًا للتأكد من اكتمال العملية.' },
            ],
        };
    }

    return {
        icon: '❌',
        accentColor: '#b91c1c',
        infoBackground: '#fef2f2',
        infoColor: '#991b1b',
        title: 'الدفع غير مكتمل',
        subtitle: 'الحالة الحالية لا تشير إلى عملية دفع ناجحة.',
        infoLine1: 'قد تكون العملية فشلت أو ألغيت أو تم استرجاعها.',
        infoLine2: 'راجع الفاتورة أو سجل المدفوعات لمعرفة السبب.',
        infoLine3: 'إذا تم الخصم فعليًا فتواصل مع الدعم لإجراء المطابقة.',
        steps: [
            { title: 'مراجعة الحالة', description: 'تحقق من الحالة الحالية ومراجع العملية.' },
            { title: 'التحقق من الفاتورة', description: 'تأكد أن الفاتورة لم تعد بانتظار السداد.' },
            { title: 'التواصل مع الدعم', description: 'استخدم معرف الدفعة إذا احتجت للمساعدة.' },
        ],
    };
}

function formatAmount(amount, currency = 'SDG') {
    return new Intl.NumberFormat('ar-SD', {
        style: 'currency',
        currency,
        minimumFractionDigits: 2,
    }).format(amount);
}

export default PaymentSuccessPage;
