import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { getTrailerTypes, getShipmentTypes, getLocations } from '../services/metaDataApi';

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

        expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/meta/trailer_types');
        expect(result).toEqual(['flatbed', 'reefer']);
    });

    it('fetches shipment types', async () => {
        axios.get.mockResolvedValueOnce({ data: ['LTL', 'FTL'] });

        const result = await getShipmentTypes();

        expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/meta/shipment_types');
        expect(result).toEqual(['LTL', 'FTL']);
    });

    it('fetches locations', async () => {
        axios.get.mockResolvedValueOnce({ data: ['Khartoum', 'Port Sudan'] });

        const result = await getLocations();

        expect(axios.get).toHaveBeenCalledWith('http://localhost:8000/meta/locations');
        expect(result).toEqual(['Khartoum', 'Port Sudan']);
    });
});
