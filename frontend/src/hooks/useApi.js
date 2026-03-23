import { useState, useEffect, useCallback } from 'react';
import axiosClient from "../api/axiosClient.js";

const unwrap = async (request) => {
    const response = await request;
    return response?.data;
};

export const useApi = (apiCall, initialData = null, immediate = true) => {
    const [data, setData] = useState(initialData);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const execute = useCallback(async (...args) => {
        try {
            setLoading(true);
            setError(null);
            const result = await apiCall(...args);
            setData(result);
            return result;
        } catch (err) {
            setError(err);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [apiCall]);

    useEffect(() => {
        if (immediate) {
            execute();
        }
    }, [execute, immediate]);

    return { data, loading, error, execute, setData };
};

// Shipments hook
export const useShipments = (params = {}, immediate = true) => {
    return useApi(() => unwrap(axiosClient.get("/tms/shipments", { params })), [], immediate);
};

// LoadBoard hook
export const useLoadBoard = (params = {}, immediate = true) => {
    return useApi(() => unwrap(axiosClient.get("/loadboard/loads", { params })), [], immediate);
};

// Statistics hook
export const useStatistics = (params = {}, immediate = true) => {
    return useApi(() => unwrap(axiosClient.get("/statistics/overview", { params })), null, immediate);
};

// User profile hook
export const useUserProfile = (immediate = true) => {
    return useApi(() => unwrap(axiosClient.get("/users/profile")), null, immediate);
};
