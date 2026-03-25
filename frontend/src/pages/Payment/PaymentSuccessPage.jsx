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
                    throw new Error('Payment ID not found');
                }

                setLoading(true);
                const paymentData = await paymentApi.get(paymentId);
                setPayment(paymentData);
            } catch (err) {
                setError(err?.response?.data?.detail || err.message || 'Failed to load payment data');
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
            'Payment Receipt',
            '------------------------------',
            `Payment ID: ${payment.reference_id}`,
            `Transaction ID: ${payment.gateway_transaction_id || 'Not Available'}`,
            `Amount: ${formatAmount(payment.amount, payment.currency)}`,
            `Gateway: ${paymentApi.getGatewayName(payment.payment_gateway)}`,
            `Status: ${getStatusText(payment.status)}`,
            `Date: ${new Date(payment.created_at).toLocaleString()}`,
            `Invoice Number: #${payment.invoice_id}`,
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
                    <h1>Loading payment data</h1>
                    <p>Retrieving the latest available status from the system.</p>
                </div>
            </div>
        );
    }

    if (error || !payment) {
        return (
            <div className="payment-status-page">
                <div className="status-card">
                    <div className="status-icon">⚠️</div>
                    <h1>Failed to load payment data</h1>
                    <p>{error || 'An unexpected error occurred'}</p>
                    <div className="actions">
                        <button className="btn-primary" onClick={goToInvoice}>View invoice</button>
                        <button className="btn-secondary" onClick={() => navigate('/')}>Back to home</button>
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
                        label="Payment ID"
                        value={payment.reference_id}
                        action={(
                            <button className="copy-btn" onClick={() => copyToClipboard(payment.reference_id)}>
                                {copied ? 'Copied' : 'Copy'}
                            </button>
                        )}
                    />
                    <DetailRow label="Amount" value={formatAmount(payment.amount, payment.currency)} />
                    <DetailRow label="Gateway" value={paymentApi.getGatewayName(payment.payment_gateway)} />
                    <DetailRow label="Invoice Number" value={`#${payment.invoice_id}`} />
                    <DetailRow label="Status" value={getStatusText(payment.status)} />
                    <DetailRow label="Transaction ID" value={payment.gateway_transaction_id || 'Not available'} />
                    <DetailRow label="Date" value={new Date(payment.created_at).toLocaleString()} />
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
                    <h2>Next steps</h2>
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
                    <button className="btn-primary" onClick={goToInvoice}>View Invoice</button>
                    <button className="btn-secondary" onClick={downloadReceipt}>Download Receipt</button>
                    <button className="btn-secondary" onClick={() => navigate('/invoices')}>All Invoices</button>
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
        pending: 'Pending',
        processing: 'Processing',
        completed: 'Completed',
        paid: 'Paid',
        failed: 'Failed',
        cancelled: 'Cancelled',
        refunded: 'Refunded',
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
            title: 'Payment Successful',
            subtitle: 'Payment has been confirmed and its status updated in the system.',
            infoLine1: 'Payment confirmed from the platform.',
            infoLine2: 'All transactions are protected and recorded in the financial log.',
            infoLine3: 'You can now track the invoice or download the receipt.',
            steps: [
                { title: 'Payment Confirmation', description: 'The payment has been recorded as a completed transaction.' },
                { title: 'Invoice Update', description: 'The invoice is now considered paid in the system.' },
                { title: 'Keep Reference', description: 'Keep the payment ID and transaction ID for future reference.' },
            ],
        };
    }

    if (normalized === 'pending' || normalized === 'processing') {
        return {
            icon: '⏳',
            accentColor: '#b45309',
            infoBackground: '#fffbeb',
            infoColor: '#92400e',
            title: 'Payment Pending Confirmation',
            subtitle: 'Request received but final status not yet determined.',
            infoLine1: 'Payment may be waiting for gateway confirmation or webhook arrival.',
            infoLine2: 'Return to this page later or check the invoice.',
            infoLine3: 'Do not rely on this page as final proof until status is completed.',
            steps: [
                { title: 'Request Registration', description: 'Payment record created locally.' },
                { title: 'Waiting for Update', description: 'Waiting for gateway response or webhook notification.' },
                { title: 'Follow-up', description: 'Check the invoice later to confirm completion.' },
            ],
        };
    }

    return {
        icon: '❌',
        accentColor: '#b91c1c',
        infoBackground: '#fef2f2',
        infoColor: '#991b1b',
        title: 'Payment Incomplete',
        subtitle: 'Current status does not indicate a successful payment.',
        infoLine1: 'The transaction may have failed, been cancelled, or refunded.',
        infoLine2: 'Check the invoice or payment history for the reason.',
        infoLine3: 'If the amount was actually deducted, contact support for reconciliation.',
        steps: [
            { title: 'Review Status', description: 'Check current status and transaction references.' },
            { title: 'Verify Invoice', description: 'Ensure the invoice is no longer pending payment.' },
            { title: 'Contact Support', description: 'Use the payment ID if you need assistance.' },
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
