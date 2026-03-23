import axios from 'axios';

const API_BASE = globalThis.process?.env?.REACT_APP_API_URL || 'http://localhost:8000';

export const getTrailerTypes = async () => {
  const res = await axios.get(`${API_BASE}/meta/trailer_types`);
  return res.data;
};

export const getShipmentTypes = async () => {
  const res = await axios.get(`${API_BASE}/meta/shipment_types`);
  return res.data;
};

export const getLocations = async () => {
  const res = await axios.get(`${API_BASE}/meta/locations`);
  return res.data;
};
