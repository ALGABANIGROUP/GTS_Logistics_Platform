/**
 * maps.js - OpenStreetMap with Leaflet (Replacement for Google Maps)
 * Uses UnifiedShipmentMap component for rendering
 * WebSocket support for real-time location updates
 */

import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

let map;
let safetyMarkers = [];
let truckMarkers = [];
let weatherMarkers = [];
let socket;
let safetyLayer, truckLayer, weatherLayer;

/**
 * Initialize Leaflet map with OpenStreetMap tiles
 */
export function initMap(mapElementId = 'map') {
  const mapElement = document.getElementById(mapElementId);

  if (!mapElement) {
    console.warn(`Map element with ID "${mapElementId}" not found`);
    return;
  }

  // Initialize Leaflet map
  map = L.map(mapElementId).setView([37.7749, -122.4194], 5);

  // Add OpenStreetMap tiles
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }).addTo(map);

  // Create layer groups for organization
  safetyLayer = L.layerGroup().addTo(map);
  truckLayer = L.layerGroup().addTo(map);
  weatherLayer = L.layerGroup().addTo(map);

  // Add layer control
  L.control.layers({}, {
    'Safety Reports': safetyLayer,
    'Trucks': truckLayer,
    'Weather': weatherLayer
  }).addTo(map);

  fetchSafetyReports();
  fetchWeatherTraffic();
  setupWebSocket();
}

/**
 * Fetch safety reports from API
 */
async function fetchSafetyReports() {
  try {
    const response = await fetch('/safety-reports/map');
    const data = await response.json();
    updateSafetyMarkers(data.map_data || []);
  } catch (error) {
    console.error('Error fetching safety reports:', error);
  }
}

/**
 * Update safety markers on map
 */
function updateSafetyMarkers(safetyReports) {
  safetyLayer.clearLayers();

  safetyReports.forEach((report) => {
    const redIcon = L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
    });

    const marker = L.marker([report.latitude, report.longitude], { icon: redIcon })
      .bindPopup(`<strong>${report.report_type}</strong><br>${report.description}`)
      .addTo(safetyLayer);
  });
}

/**
 * Fetch weather and traffic data
 */
async function fetchWeatherTraffic() {
  try {
    const response = await fetch('/safety/weather-traffic?lat=37.7749&lon=-122.4194');
    const data = await response.json();
    updateWeatherMarkers(data.weather);
  } catch (error) {
    console.error('Error fetching weather and traffic data:', error);
  }
}

/**
 * Update weather markers on map
 */
function updateWeatherMarkers(weatherData) {
  weatherLayer.clearLayers();

  if (weatherData && weatherData.coord) {
    const yellowIcon = L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-yellow.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
    });

    const marker = L.marker([weatherData.coord.lat, weatherData.coord.lon], { icon: yellowIcon })
      .bindPopup(`<strong>Weather</strong><br>${weatherData.weather?.[0]?.description}<br>Temp: ${weatherData.main?.temp}°C`)
      .addTo(weatherLayer);
  }
}

/**
 * Setup WebSocket for real-time truck tracking
 */
function setupWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/truck-locations`;

  socket = new WebSocket(wsUrl);

  socket.onopen = () => {
    console.log('✅ Connected to truck tracking WebSocket');
  };

  socket.onmessage = function (event) {
    try {
      const truckData = JSON.parse(event.data);
      updateTruckMarkers([truckData]);
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  };

  socket.onclose = function () {
    console.warn('❌ WebSocket closed, attempting to reconnect...');
    setTimeout(setupWebSocket, 5000);
  };

  socket.onerror = function (error) {
    console.error('WebSocket error:', error);
  };
}

/**
 * Update truck markers on map
 */
function updateTruckMarkers(truckData) {
  truckLayer.clearLayers();

  truckData.forEach((truck) => {
    const blueIcon = L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
    });

    const marker = L.marker([truck.latitude, truck.longitude], { icon: blueIcon })
      .bindPopup(`<strong>Truck ID: ${truck.id}</strong><br>Status: ${truck.status}<br>Speed: ${truck.speed || 'N/A'} km/h`)
      .addTo(truckLayer);
  });
}

/**
 * No longer needed - using OpenStreetMap instead of Google Maps
 * This function is kept for backward compatibility
 */
export function loadGoogleMapsAPI(apiKey) {
  return new Promise((resolve) => {
    console.info('ℹ️ Google Maps API loading disabled. Using OpenStreetMap with Leaflet instead.');
    resolve();
  });
}

/**
 * Cleanup function
 */
export function destroyMap() {
  if (socket) {
    socket.close();
    socket = null;
  }
  if (map) {
    map.remove();
    map = null;
  }
}
