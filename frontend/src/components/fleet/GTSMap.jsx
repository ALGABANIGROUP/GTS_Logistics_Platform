import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-defaulticon-compatibility';
import 'leaflet-defaulticon-compatibility/dist/leaflet-defaulticon-compatibility.css';

const GTSMap = ({
    truckLocations = [],
    center = [24.7136, 46.6753], // Riyadh
    zoom = 10,
    height = '400px',
    onTruckSelect
}) => {
    const mapContainerRef = useRef(null);
    const mapRef = useRef(null);
    const markersRef = useRef({});
    const [mapReady, setMapReady] = useState(false);

    // Initialize map - only once
    useEffect(() => {
        if (!mapContainerRef.current || mapRef.current) return;

        // Create map
        const map = L.map(mapContainerRef.current, {
            center: center,
            zoom: zoom,
            maxBounds: L.latLngBounds(
                [16.0, 34.0], // Southwest Saudi Arabia
                [32.0, 56.0]  // Northeast Saudi Arabia
            ),
            maxBoundsViscosity: 1.0,
            zoomControl: true
        });

        // Add OpenStreetMap as base layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            maxZoom: 19,
            minZoom: 6
        }).addTo(map);

        // Add optional layers
        // CartoDB for better styling
        L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a>',
            maxZoom: 19
        }).addTo(map);

        mapRef.current = map;
        setMapReady(true);

        // Add controls
        L.control.scale({ imperial: false }).addTo(map);

        // Cleanup
        return () => {
            if (map) {
                map.remove();
                mapRef.current = null;
            }
        };
    }, []);

    // Update map center when it changes
    useEffect(() => {
        if (mapRef.current && center) {
            mapRef.current.setView(center, zoom);
        }
    }, [center, zoom]);

    // Update vehicles on the map
    useEffect(() => {
        if (!mapRef.current || !mapReady) return;

        const map = mapRef.current;
        const markers = markersRef.current;

        // Create custom truck icon
        const createTruckIcon = (status, isSelected = false) => {
            const color = status === 'moving' ? '#1976d2' :
                status === 'stopped' ? '#f44336' :
                    status === 'idle' ? '#ff9800' : '#757575';

            const size = isSelected ? 40 : 32;
            const border = isSelected ? '3px solid #ffeb3b' : '2px solid white';

            return L.divIcon({
                html: `
          <div style="
            background-color: ${color};
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            border: ${border};
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            cursor: pointer;
            transition: all 0.3s;
          ">
            🚚
          </div>
        `,
                iconSize: [size, size],
                iconAnchor: [size / 2, size / 2],
                popupAnchor: [0, -size / 2]
            });
        };

        // Update or add markers
        truckLocations.forEach(truck => {
            if (!truck.latitude || !truck.longitude) return;

            const lat = parseFloat(truck.latitude);
            const lng = parseFloat(truck.longitude);
            const position = [lat, lng];

            if (markers[truck.id]) {
                // Update existing marker
                markers[truck.id].setLatLng(position);

                // Update icon if status changes
                const currentStatus = markers[truck.id].options.status;
                if (currentStatus !== truck.status) {
                    const isSelected = markers[truck.id].options.isSelected;
                    markers[truck.id].setIcon(createTruckIcon(truck.status, isSelected));
                    markers[truck.id].options.status = truck.status;
                }
            } else {
                // Create new marker
                const icon = createTruckIcon(truck.status || 'idle', false);
                const marker = L.marker(position, {
                    icon: icon,
                    status: truck.status,
                    isSelected: false,
                    truckId: truck.id
                }).addTo(map);

                // Add popup
                const popupContent = `
          <div style="min-width: 220px; font-family: Arial, sans-serif;">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
              <div style="
                width: 12px;
                height: 12px;
                background-color: ${truck.status === 'moving' ? '#1976d2' : '#f44336'};
                border-radius: 50%;
                margin-right: 8px;
              "></div>
              <strong style="font-size: 16px;">${truck.truck_number || truck.id}</strong>
            </div>
            
            <div style="margin-bottom: 6px;">
              <span style="color: #666;">Driver:</span>
              <strong> ${truck.driver_name || 'Unknown'}</strong>
            </div>
            
            <div style="margin-bottom: 6px;">
              <span style="color: #666;">Status:</span>
              <strong style="color: ${truck.status === 'moving' ? '#1976d2' : '#f44336'}">
                ${truck.status === 'moving' ? 'Moving' : 'Stopped'}
              </strong>
            </div>
            
            ${truck.speed ? `
            <div style="margin-bottom: 6px;">
              <span style="color: #666;">Speed:</span>
              <strong> ${truck.speed}</strong>
            </div>
            ` : ''}
            
            ${truck.last_update ? `
            <div style="margin-bottom: 8px;">
              <span style="color: #666;">Last update:</span>
              <br/>
              <small>${new Date(truck.last_update).toLocaleString('en-US')}</small>
            </div>
            ` : ''}
            
            <button onclick="window.selectTruck('${truck.id}')" 
              style="
                background-color: #1976d2;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
                margin-top: 8px;
              ">
              View details
            </button>
          </div>
        `;

                marker.bindPopup(popupContent);

                // Add click handler
                marker.on('click', () => {
                    if (onTruckSelect) {
                        onTruckSelect(truck);
                    }

                    // Highlight selected marker
                    Object.values(markers).forEach(m => {
                        if (m.options.truckId === truck.id) {
                            m.setIcon(createTruckIcon(truck.status, true));
                            m.options.isSelected = true;
                        } else {
                            m.setIcon(createTruckIcon(m.options.status, false));
                            m.options.isSelected = false;
                        }
                    });
                });

                markers[truck.id] = marker;
            }
        });

        // Remove missing markers
        Object.keys(markers).forEach(id => {
            if (!truckLocations.find(t => t.id === id)) {
                map.removeLayer(markers[id]);
                delete markers[id];
            }
        });

        markersRef.current = markers;

    }, [truckLocations, mapReady, onTruckSelect]);

    // Helper function for global display
    useEffect(() => {
        window.selectTruck = (truckId) => {
            const truck = truckLocations.find(t => t.id === truckId);
            if (truck && onTruckSelect) {
                onTruckSelect(truck);
            }
        };
    }, [truckLocations, onTruckSelect]);

    return (
        <div style={{
            position: 'relative',
            height: height,
            borderRadius: '8px',
            overflow: 'hidden',
            border: '1px solid #e0e0e0'
        }}>
            {/* Map container */}
            <div
                ref={mapContainerRef}
                style={{
                    height: '100%',
                    width: '100%'
                }}
            />

            {/* Map info */}
            {mapReady && (
                <>
                    {/* Map legend */}
                    <div style={{
                        position: 'absolute',
                        top: '10px',
                        right: '10px',
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        padding: '8px 12px',
                        borderRadius: '6px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                        zIndex: 1000,
                        maxWidth: '200px'
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                            <div style={{
                                width: '10px',
                                height: '10px',
                                backgroundColor: '#1976d2',
                                borderRadius: '50%',
                                marginRight: '6px'
                            }}></div>
                            <span style={{ fontSize: '13px', fontWeight: 'bold' }}>Moving</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
                            <div style={{
                                width: '10px',
                                height: '10px',
                                backgroundColor: '#f44336',
                                borderRadius: '50%',
                                marginRight: '6px'
                            }}></div>
                            <span style={{ fontSize: '13px', fontWeight: 'bold' }}>Stopped</span>
                        </div>
                        <div style={{
                            fontSize: '11px',
                            color: '#666',
                            marginTop: '4px',
                            borderTop: '1px solid #eee',
                            paddingTop: '4px'
                        }}>
                            OpenStreetMap • {truckLocations.length} vehicles
                        </div>
                    </div>

                    {/* Bottom stats */}
                    <div style={{
                        position: 'absolute',
                        bottom: '10px',
                        left: '10px',
                        backgroundColor: 'rgba(255, 255, 255, 0.95)',
                        padding: '6px 10px',
                        borderRadius: '6px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
                        zIndex: 1000
                    }}>
                        <div style={{ fontSize: '12px', display: 'flex', alignItems: 'center' }}>
                            <span style={{ marginRight: '4px' }}>📍</span>
                            <span>Center: {center[0].toFixed(4)}, {center[1].toFixed(4)}</span>
                        </div>
                    </div>
                </>
            )}

            {/* Loading state */}
            {!mapReady && (
                <div style={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: 'rgba(255, 255, 255, 0.9)',
                    zIndex: 2000,
                    borderRadius: '8px'
                }}>
                    <div style={{ textAlign: 'center' }}>
                        <div style={{
                            width: '50px',
                            height: '50px',
                            border: '4px solid #f3f3f3',
                            borderTop: '4px solid #1976d2',
                            borderRadius: '50%',
                            animation: 'spin 1s linear infinite',
                            margin: '0 auto 16px auto'
                        }}></div>
                        <style>{`
              @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
              }
            `}</style>
                        <p style={{ margin: 0, color: '#1976d2', fontWeight: 'bold' }}>
                            Loading map system...
                        </p>
                        <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#666' }}>
                            OpenStreetMap • Free to use
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default GTSMap;
