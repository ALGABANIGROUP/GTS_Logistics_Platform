import axiosClient from "../api/axiosClient";

const fleetSafetyApi = {
  getConfig: () => axiosClient.get("/api/v1/fleet/config"),
  getDashboard: () => axiosClient.get("/api/v1/fleet/dashboard"),
  listDrivers: (params = {}) => axiosClient.get("/api/v1/fleet/drivers", { params }),
  createDriver: (payload) => axiosClient.post("/api/v1/fleet/drivers", payload),
  updateDriver: (driverId, payload) => axiosClient.patch(`/api/v1/fleet/drivers/${driverId}`, payload),
  deleteDriver: (driverId) => axiosClient.delete(`/api/v1/fleet/drivers/${driverId}`),
  listVehicles: (params = {}) => axiosClient.get("/api/v1/fleet/vehicles", { params }),
  createVehicle: (payload) => axiosClient.post("/api/v1/fleet/vehicles", payload),
  updateVehicle: (vehicleId, payload) => axiosClient.patch(`/api/v1/fleet/vehicles/${vehicleId}`, payload),
  deleteVehicle: (vehicleId) => axiosClient.delete(`/api/v1/fleet/vehicles/${vehicleId}`),
  listAssignments: () => axiosClient.get("/api/v1/fleet/assignments"),
  createAssignment: (payload) => axiosClient.post("/api/v1/fleet/assignments", payload),
  unassignDriver: (driverId) => axiosClient.post(`/api/v1/fleet/assignments/${driverId}/unassign`),
  listIncidents: (params = {}) => axiosClient.get("/api/v1/fleet/incidents", { params }),
  getIncident: (incidentId) => axiosClient.get(`/api/v1/fleet/incidents/${incidentId}`),
  createIncident: (payload) => axiosClient.post("/api/v1/fleet/incidents", payload),
  updateIncident: (incidentId, payload) => axiosClient.patch(`/api/v1/fleet/incidents/${incidentId}`, payload),
  deleteIncident: (incidentId) => axiosClient.delete(`/api/v1/fleet/incidents/${incidentId}`),
  getLiveMapData: () => axiosClient.get("/api/v1/fleet/live/map-data"),
  updateVehicleLocation: (vehicleId, payload) => axiosClient.post(`/api/v1/fleet/live/vehicles/${vehicleId}/location`, payload),
  updateDriverLocation: (driverId, payload) => axiosClient.post(`/api/v1/fleet/live/drivers/${driverId}/location`, payload),
  getVehicleTrack: (vehicleId, hours = 24) => axiosClient.get(`/api/v1/fleet/live/vehicles/${vehicleId}/track`, { params: { hours } }),
  getDriverTrack: (driverId, hours = 24) => axiosClient.get(`/api/v1/fleet/live/drivers/${driverId}/track`, { params: { hours } }),
};

export default fleetSafetyApi;
