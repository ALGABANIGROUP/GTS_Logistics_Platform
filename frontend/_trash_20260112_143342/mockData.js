export const generateMockShipments = (count = 10) => {
    const shipments = [];
    const saudiCities = [
        { name: 'Riyadh', lat: 24.7136, lng: 46.6753 },
        { name: 'Jeddah', lat: 21.4858, lng: 39.1925 },
        { name: 'Dammam', lat: 26.4207, lng: 50.0888 },
        { name: 'Mecca', lat: 21.3891, lng: 39.8579 },
        { name: 'Medina', lat: 24.5247, lng: 39.5692 },
        { name: 'Tabuk', lat: 28.3835, lng: 36.5662 },
        { name: 'Abha', lat: 18.2465, lng: 42.5117 },
        { name: 'Hail', lat: 27.5114, lng: 41.7208 },
        { name: 'Al Jouf', lat: 29.7858, lng: 40.0999 },
        { name: 'Najran', lat: 17.5656, lng: 44.2289 }
    ];
    const statuses = ['in_transit', 'picked_up', 'delivered', 'assigned', 'created'];
    const customers = [
        'Saudi Tech Solutions',
        'Al Rajhi Transport',
        'National Food Distributors',
        'Gulf Electronics',
        'Arabian Construction Co.',
        'Medina Trading',
        'Jeddah Import Export',
        'Riyadh Pharmaceuticals',
        'Eastern Province Logistics',
        'Western Region Supplies'
    ];
    const drivers = [
        { id: 'DRV001', name: 'Ahmed Al-Mansour', phone: '+966500123456' },
        { id: 'DRV002', name: 'Mohammed Al-Ghamdi', phone: '+966501234567' },
        { id: 'DRV003', name: 'Khalid Al-Otaibi', phone: '+966502345678' },
        { id: 'DRV004', name: 'Saeed Al-Zahrani', phone: '+966503456789' },
        { id: 'DRV005', name: 'Ali Al-Shammari', phone: '+966504567890' }
    ];
    for (let i = 1; i <= count; i++) {
        const pickupCity = saudiCities[Math.floor(Math.random() * saudiCities.length)];
        let deliveryCity;
        do {
            deliveryCity = saudiCities[Math.floor(Math.random() * saudiCities.length)];
        } while (deliveryCity.name === pickupCity.name);
        const status = statuses[Math.floor(Math.random() * statuses.length)];
        const customer = customers[Math.floor(Math.random() * customers.length)];
        const driver = drivers[Math.floor(Math.random() * drivers.length)];
        const progress = Math.random();
        const currentLat = pickupCity.lat + (deliveryCity.lat - pickupCity.lat) * progress;
        const currentLng = pickupCity.lng + (deliveryCity.lng - pickupCity.lng) * progress;
        const lat = currentLat + (Math.random() * 0.1 - 0.05);
        const lng = currentLng + (Math.random() * 0.1 - 0.05);
        shipments.push({
            id: `SHIP${String(i).padStart(3, '0')}`,
            customer,
            pickup: `${pickupCity.name} - Main District`,
            delivery: `${deliveryCity.name} - Industrial Area`,
            status,
            driver_id: driver.id,
            created_at: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
            estimated_delivery: new Date(Date.now() + Math.random() * 3 * 24 * 60 * 60 * 1000).toISOString(),
            weight: `${Math.floor(Math.random() * 5000) + 500} kg`,
            value: `${Math.floor(Math.random() * 50000) + 5000} SAR`,
            pickup_location: { lat: pickupCity.lat, lng: pickupCity.lng, address: `${pickupCity.name}, Saudi Arabia` },
            delivery_location: { lat: deliveryCity.lat, lng: deliveryCity.lng, address: `${deliveryCity.name}, Saudi Arabia` },
            tracking_info: { latitude: lat.toFixed(6), longitude: lng.toFixed(6), speed: `${Math.floor(Math.random() * 60) + 40} km/h`, heading: Math.floor(Math.random() * 360), last_update: new Date().toISOString(), battery_level: Math.floor(Math.random() * 50) + 50 },
            driver_info: { ...driver, vehicle: ['Mercedes Actros', 'Volvo FH', 'MAN TGX', 'Scania R-series'][Math.floor(Math.random() * 4)], rating: (Math.random() * 2 + 3).toFixed(1), completed_shipments: Math.floor(Math.random() * 200) + 50 }
        });
    }
    return shipments;
};
