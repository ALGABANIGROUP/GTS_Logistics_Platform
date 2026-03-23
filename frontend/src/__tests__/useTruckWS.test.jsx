import { describe, it, expect, vi, beforeEach } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { useTruckWS } from '../hooks/useTruckWS';

const closeMock = vi.fn();
let capturedHandlers = null;

vi.mock('../utils/wsClient', () => ({
    connectTruckLocationsWS: vi.fn((handlers) => {
        capturedHandlers = handlers;
        return { close: closeMock };
    }),
}));

describe('useTruckWS', () => {
    beforeEach(() => {
        closeMock.mockReset();
        capturedHandlers = null;
    });

    it('updates positions on truck_positions messages', () => {
        const { result } = renderHook(() => useTruckWS());

        expect(result.current.positions).toEqual([]);

        act(() => {
            capturedHandlers.onMessage({
                type: 'truck_positions',
                data: [{ id: 'truck-1', lat: 15.5, lng: 32.5 }],
            });
        });

        expect(result.current.positions).toEqual([{ id: 'truck-1', lat: 15.5, lng: 32.5 }]);
    });

    it('ignores non-position payloads and closes socket on unmount', () => {
        const { result, unmount } = renderHook(() => useTruckWS());

        act(() => {
            capturedHandlers.onMessage({ type: 'ping', data: [] });
        });

        expect(result.current.positions).toEqual([]);

        unmount();

        expect(closeMock).toHaveBeenCalledTimes(1);
    });

    it('ignores truck_positions payload when data is not an array', () => {
        const { result } = renderHook(() => useTruckWS());

        act(() => {
            capturedHandlers.onMessage({
                type: 'truck_positions',
                data: { id: 'single-object' },
            });
        });

        expect(result.current.positions).toEqual([]);
    });

    it('does not crash when socket close throws during cleanup', () => {
        closeMock.mockImplementationOnce(() => {
            throw new Error('close failed');
        });

        const { unmount } = renderHook(() => useTruckWS());

        expect(() => unmount()).not.toThrow();
    });
});
