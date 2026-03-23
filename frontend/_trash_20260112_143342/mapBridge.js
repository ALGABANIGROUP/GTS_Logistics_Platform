class GTSMapBridge {
    constructor() {
        this.connected = false;
        this.mapInstance = null;
        this.eventListeners = {};
        this.initialize();
    }
    async initialize() {
        try {
            await this.connectToExistingSystem();
            this.setupEventListeners();
            console.log('✅ GTS Map Bridge initialized successfully');
        } catch (error) {
            console.error('❌ Failed to initialize map bridge:', error);
            this.setupMockSystem();
        }
    }
    async connectToExistingSystem() {
        this.ws = new WebSocket('ws://localhost:5000/ws/tracking');
        return new Promise((resolve, reject) => {
            this.ws.onopen = () => { this.connected = true; resolve(); };
            this.ws.onerror = (error) => { reject(error); };
            this.ws.onmessage = (event) => { this.handleIncomingMessage(event.data); };
        });
    }
    handleIncomingMessage(data) {
        try {
            const message = JSON.parse(data);
            if (message.type && this.eventListeners[message.type]) {
                this.eventListeners[message.type].forEach(callback => { callback(message.data); });
            }
            switch (message.type) {
                case 'location_update': this.handleLocationUpdate(message.data); break;
                case 'shipment_update': this.handleShipmentUpdate(message.data); break;
                case 'system_status': this.handleSystemStatus(message.data); break;
            }
        } catch (error) { }
    }
    handleLocationUpdate(data) {
        if (this.mapInstance && this.mapInstance.updateLocation) {
            this.mapInstance.updateLocation(data);
        }
        this.emit('locationUpdated', data);
    }
    handleShipmentUpdate(data) { this.emit('shipmentUpdated', data); }
    handleSystemStatus(data) { this.emit('systemStatus', data); }
    centerOnLocation(lat, lng, zoom = 14) {
        if (this.mapInstance && this.mapInstance.centerOn) {
            this.mapInstance.centerOn(lat, lng, zoom);
        }
        this.emit('mapCentered', { lat, lng, zoom });
    }
    addShipmentMarker(shipment) {
        if (this.mapInstance && this.mapInstance.addMarker) {
            this.mapInstance.addMarker(shipment);
        }
        this.emit('markerAdded', shipment);
    }
    updateShipmentMarker(shipmentId, updates) {
        if (this.mapInstance && this.mapInstance.updateMarker) {
            this.mapInstance.updateMarker(shipmentId, updates);
        }
        this.emit('markerUpdated', { shipmentId, ...updates });
    }
    removeShipmentMarker(shipmentId) {
        if (this.mapInstance && this.mapInstance.removeMarker) {
            this.mapInstance.removeMarker(shipmentId);
        }
        this.emit('markerRemoved', shipmentId);
    }
    on(event, callback) {
        if (!this.eventListeners[event]) {
            this.eventListeners[event] = [];
        }
        this.eventListeners[event].push(callback);
    }
    off(event, callback) {
        if (this.eventListeners[event]) {
            this.eventListeners[event] = this.eventListeners[event].filter(cb => cb !== callback);
        }
    }
    emit(event, data) {
        if (this.eventListeners[event]) {
            this.eventListeners[event].forEach(callback => { callback(data); });
        }
    }
    setupMockSystem() {
        this.connected = false;
        this.mockInterval = setInterval(() => {
            this.emit('mock_location_update', {
                shipment_id: 'SHIP' + Math.floor(Math.random() * 100),
                latitude: 24.7136 + (Math.random() * 0.1 - 0.05),
                longitude: 46.6753 + (Math.random() * 0.1 - 0.05),
                speed: Math.floor(Math.random() * 60) + 40,
                timestamp: new Date().toISOString()
            });
        }, 3000);
    }
    getSystemInfo() {
        return {
            connected: this.connected,
            hasMap: !!this.mapInstance,
            system: 'GTS Existing Map System',
            version: '2.0',
            mode: this.connected ? 'live' : 'mock'
        };
    }
    destroy() {
        if (this.ws) { this.ws.close(); }
        if (this.mockInterval) { clearInterval(this.mockInterval); }
        this.eventListeners = {};
    }
}
const mapBridge = new GTSMapBridge();
window.GTSMapBridge = mapBridge;
export default mapBridge;
