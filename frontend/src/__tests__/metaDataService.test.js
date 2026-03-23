import { describe, it, expect, vi, beforeEach } from 'vitest';
import { metaDataService } from '../services/metaDataService';
import http from '../services/http';

vi.mock('../services/http', () => ({
    default: {
        get: vi.fn(),
    },
}));

describe('metaDataService', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('returns trailer types on success', async () => {
        http.get.mockResolvedValueOnce({ data: ['flatbed', 'reefer'] });

        const result = await metaDataService.getTrailerTypes();

        expect(http.get).toHaveBeenCalledWith('/api/v1/meta/trailer-types');
        expect(result).toEqual(['flatbed', 'reefer']);
    });

    it('returns empty array when trailer types data is missing', async () => {
        http.get.mockResolvedValueOnce({});

        const result = await metaDataService.getTrailerTypes();

        expect(result).toEqual([]);
    });

    it('returns empty array when trailer types request fails', async () => {
        http.get.mockRejectedValueOnce(new Error('network error'));

        const result = await metaDataService.getTrailerTypes();

        expect(result).toEqual([]);
    });

    it('returns locations on success', async () => {
        http.get.mockResolvedValueOnce({ data: ['Khartoum', 'Port Sudan'] });

        const result = await metaDataService.getLocations();

        expect(http.get).toHaveBeenCalledWith('/api/v1/meta/locations');
        expect(result).toEqual(['Khartoum', 'Port Sudan']);
    });

    it('returns empty array when locations data is missing or request fails', async () => {
        http.get.mockResolvedValueOnce({});
        const missingData = await metaDataService.getLocations();

        http.get.mockRejectedValueOnce(new Error('api down'));
        const failed = await metaDataService.getLocations();

        expect(missingData).toEqual([]);
        expect(failed).toEqual([]);
    });
});
