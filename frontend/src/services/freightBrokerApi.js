import { createShipment, listShipments } from "./shipmentsApi";

const normalizeShipmentItems = (response) => {
    if (Array.isArray(response)) return response;
    if (Array.isArray(response?.items)) return response.items;
    return [];
};

export const getShipments = async (params = {}) => {
    const response = await listShipments(params);
    const items = normalizeShipmentItems(response);
    return {
        items,
        total: response?.total ?? items.length,
    };
};

export const getRecentShipments = async (limit = 5) => {
    const response = await listShipments({ limit });
    const items = normalizeShipmentItems(response).slice(0, limit);
    return {
        items,
        total: response?.total ?? items.length,
    };
};

export const createFreightShipment = async (payload) => createShipment(payload);

const freightBrokerApi = {
    getShipments,
    getRecentShipments,
    createShipment: createFreightShipment,
};

export default freightBrokerApi;
