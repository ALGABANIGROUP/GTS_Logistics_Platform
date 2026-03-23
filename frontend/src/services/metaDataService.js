// src/services/metaDataService.js
import http from './http';

const META_API_BASE = '/api/v1/meta';

export const metaDataService = {
  getTrailerTypes: async () => {
    try {
      const response = await http.get(`${META_API_BASE}/trailer-types`);
      return response.data || [];
    } catch (error) {
      console.error('Failed to fetch trailer types:', error);
      return [];
    }
  },

  getLocations: async () => {
    try {
      const response = await http.get(`${META_API_BASE}/locations`);
      return response.data || [];
    } catch (error) {
      console.error('Failed to fetch locations:', error);
      return [];
    }
  }
};
