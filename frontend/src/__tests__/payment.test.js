import { describe, it, expect, vi, beforeEach } from 'vitest';
import axiosClient from '../api/axiosClient';
import paymentApi from '../api/paymentApi';

vi.mock('../api/axiosClient', () => ({
    default: {
        post: vi.fn(),
        get: vi.fn(),
    },
}));

describe('paymentApi helpers', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('formats amounts with configured currency', () => {
        const formatted = paymentApi.formatAmount(5000, 'SDG');

        expect(typeof formatted).toBe('string');
        expect(formatted.length).toBeGreaterThan(0);
    });

    it('returns known gateway names', () => {
        expect(paymentApi.getGatewayName('sudapay')).toContain('SUDAPAY');
        expect(paymentApi.getGatewayName('stripe')).toBe('Stripe');
        expect(paymentApi.getGatewayName('paypal')).toBe('PayPal');
        expect(paymentApi.getGatewayName('other_gateway')).toBe('other_gateway');
    });

    it('returns known payment status metadata', () => {
        const status = paymentApi.getPaymentStatus('completed');

        expect(status.label).toContain('مكتمل');
        expect(status.color).toBe('success');
    });

    it('handles unknown status safely', () => {
        const status = paymentApi.getPaymentStatus('unknown_status');

        expect(status.icon).toBe('❓');
    });

    it('creates payment via API', async () => {
        axiosClient.post.mockResolvedValue({ data: { id: 1, status: 'pending' } });

        const result = await paymentApi.create({
            invoice_id: 123,
            amount: 1000,
            currency: 'SDG',
            gateway: 'sudapay',
            description: 'test',
        });

        expect(axiosClient.post).toHaveBeenCalledWith('/api/v1/payments/create', {
            invoice_id: 123,
            amount: 1000,
            currency: 'SDG',
            gateway: 'sudapay',
            description: 'test',
        });
        expect(result.id).toBe(1);
    });

    it('uses defaults for create/refund/history helpers', async () => {
        axiosClient.post
            .mockResolvedValueOnce({ data: { id: 2 } })
            .mockResolvedValueOnce({ data: { status: 'refunded' } });
        axiosClient.get.mockResolvedValueOnce({ data: { items: [], total: 0, limit: 50, offset: 0 } });

        await paymentApi.create({
            invoice_id: 321,
            amount: 250,
            description: 'default-path',
        });
        await paymentApi.refund(18);
        await paymentApi.getUserHistory();

        expect(axiosClient.post).toHaveBeenNthCalledWith(1, '/api/v1/payments/create', {
            invoice_id: 321,
            amount: 250,
            currency: 'SDG',
            gateway: 'sudapay',
            description: 'default-path',
        });
        expect(axiosClient.post).toHaveBeenNthCalledWith(2, '/api/v1/payments/18/refund', {
            amount: undefined,
            reason: 'Customer request',
        });
        expect(axiosClient.get).toHaveBeenCalledWith('/api/v1/payments/user/history?limit=50&offset=0');
    });

    it('confirms and refunds payments via API', async () => {
        axiosClient.post
            .mockResolvedValueOnce({ data: { status: 'completed' } })
            .mockResolvedValueOnce({ data: { status: 'refunded' } });

        const confirmResult = await paymentApi.confirm(77, { gateway_transaction_id: 'gtx-1' });
        const refundResult = await paymentApi.refund(77, { amount: 50, reason: 'duplicate' });

        expect(axiosClient.post).toHaveBeenNthCalledWith(1, '/api/v1/payments/77/confirm', {
            gateway_transaction_id: 'gtx-1',
        });
        expect(axiosClient.post).toHaveBeenNthCalledWith(2, '/api/v1/payments/77/refund', {
            amount: 50,
            reason: 'duplicate',
        });
        expect(confirmResult.status).toBe('completed');
        expect(refundResult.status).toBe('refunded');
    });

    it('fetches payment and invoice payment history', async () => {
        axiosClient.get
            .mockResolvedValueOnce({ data: { id: 5 } })
            .mockResolvedValueOnce({ data: [{ id: 8 }] })
            .mockResolvedValueOnce({ data: { items: [{ id: 11 }], total: 1, limit: 10, offset: 20 } });

        const payment = await paymentApi.get(5);
        const invoicePayments = await paymentApi.getInvoicePayments(9);
        const history = await paymentApi.getUserHistory({ limit: 10, offset: 20 });

        expect(axiosClient.get).toHaveBeenNthCalledWith(1, '/api/v1/payments/5');
        expect(axiosClient.get).toHaveBeenNthCalledWith(2, '/api/v1/payments/invoice/9');
        expect(axiosClient.get).toHaveBeenNthCalledWith(3, '/api/v1/payments/user/history?limit=10&offset=20');
        expect(payment.id).toBe(5);
        expect(invoicePayments).toHaveLength(1);
        expect(history.items).toHaveLength(1);
        expect(history.total).toBe(1);
    });

    it('returns empty arrays when invoice/history data is missing', async () => {
        axiosClient.get
            .mockResolvedValueOnce({})
            .mockResolvedValueOnce({ data: null });

        const invoicePayments = await paymentApi.getInvoicePayments(44);
        const history = await paymentApi.getUserHistory({ limit: 1, offset: 0 });

        expect(invoicePayments).toEqual([]);
        expect(history).toEqual([]);
    });

    it('handles sudapay success and failure handlers', async () => {
        const getSpy = vi.spyOn(paymentApi, 'get').mockResolvedValue({ status: 'completed' });

        const success = await paymentApi.handleSudapaySuccess(22);
        const failure = await paymentApi.handleSudapayFailure(22, 'declined');

        expect(getSpy).toHaveBeenCalledWith(22);
        expect(success.status).toBe('completed');
        expect(failure.status).toBe('failed');
        expect(failure.reason).toBe('declined');

        getSpy.mockRestore();
    });

    it('uses default failure reason for sudapay failure handler', async () => {
        const result = await paymentApi.handleSudapayFailure(55);

        expect(result.status).toBe('failed');
        expect(result.reason).toBe('Unknown error');
    });

    it('propagates API errors through catch blocks', async () => {
        const error = new Error('network');
        axiosClient.post.mockRejectedValue(error);
        axiosClient.get.mockRejectedValue(error);

        await expect(paymentApi.create({ invoice_id: 1, amount: 10, description: 'x' })).rejects.toThrow('network');
        await expect(paymentApi.confirm(1)).rejects.toThrow('network');
        await expect(paymentApi.refund(1)).rejects.toThrow('network');
        await expect(paymentApi.get(1)).rejects.toThrow('network');
        await expect(paymentApi.getInvoicePayments(1)).rejects.toThrow('network');
        await expect(paymentApi.getUserHistory()).rejects.toThrow('network');
    });

    it('propagates response.data style API errors through each method', async () => {
        const apiError = { response: { data: { code: 'bad_request' } }, message: 'fallback' };

        axiosClient.post
            .mockRejectedValueOnce(apiError)
            .mockRejectedValueOnce(apiError)
            .mockRejectedValueOnce(apiError);
        axiosClient.get
            .mockRejectedValueOnce(apiError)
            .mockRejectedValueOnce(apiError)
            .mockRejectedValueOnce(apiError);

        await expect(paymentApi.confirm(10)).rejects.toEqual(apiError);
        await expect(paymentApi.refund(10)).rejects.toEqual(apiError);
        await expect(paymentApi.create({ invoice_id: 9, amount: 5, description: 'e' })).rejects.toEqual(apiError);
        await expect(paymentApi.get(10)).rejects.toEqual(apiError);
        await expect(paymentApi.getInvoicePayments(10)).rejects.toEqual(apiError);
        await expect(paymentApi.getUserHistory({ limit: 5 })).rejects.toEqual(apiError);
    });

    it('propagates sudapay success failure when confirm throws', async () => {
        const getSpy = vi.spyOn(paymentApi, 'get').mockRejectedValue(new Error('confirm-failed'));

        await expect(paymentApi.handleSudapaySuccess(3)).rejects.toThrow('confirm-failed');

        getSpy.mockRestore();
    });

    it('handles rejected API objects that carry response.data', async () => {
        const apiError = { response: { data: { detail: 'bad request' } }, message: 'fallback message' };
        axiosClient.post.mockRejectedValue(apiError);

        await expect(
            paymentApi.create({ invoice_id: 999, amount: 1, description: 'err' })
        ).rejects.toEqual(apiError);
    });

    it('throws when sudapay failure logger itself throws (catch branch)', async () => {
        const logSpy = vi.spyOn(console, 'log').mockImplementationOnce(() => {
            throw new Error('log failed');
        });

        await expect(paymentApi.handleSudapayFailure(77)).rejects.toThrow('log failed');

        logSpy.mockRestore();
    });
});
