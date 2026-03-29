import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { getTrailerTypes, getShipmentTypes, getLocations } from '../services/metaDataApi';

vi.mock('../config/env', () => ({
    API_BASE_URL: 'https://api.gtsdispatcher.com',
}));

vi.mock('axios', () => ({
    default: {
        get: vi.fn(),
    },
}));

describe('metaDataApi service', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('fetches trailer types', async () => {
        axios.get.mockResolvedValueOnce({ data: ['flatbed', 'reefer'] });

        const result = await getTrailerTypes();

        expect(axios.get).toHaveBeenCalledWith('https://api.gtsdispatcher.com/meta/trailer_types');
        expect(result).toEqual(['flatbed', 'reefer']);
    });

    it('fetches shipment types', async () => {
        axios.get.mockResolvedValueOnce({ data: ['LTL', 'FTL'] });

        const result = await getShipmentTypes();

        expect(axios.get).toHaveBeenCalledWith('https://api.gtsdispatcher.com/meta/shipment_types');
        expect(result).toEqual(['LTL', 'FTL']);
    });

    it('fetches locations', async () => {
        axios.get.mockResolvedValueOnce({ data: ['Khartoum', 'Port Sudan'] });

        const result = await getLocations();

        expect(axios.get).toHaveBeenCalledWith('https://api.gtsdispatcher.com/meta/locations');
        expect(result).toEqual(['Khartoum', 'Port Sudan']);
    });
});
