import axios from 'axios';
import { API_BASE_URL } from '../config/env';

const API_BASE = String(API_BASE_URL || '').replace(/\/+$/, '');

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
