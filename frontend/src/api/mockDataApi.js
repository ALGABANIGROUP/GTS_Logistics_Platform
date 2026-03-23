import axiosClient from "./axiosClient";

export const mockDrivers = [
  {
    id: 101,
    name: "John Smith",
    phone: "+1 (555) 123-4567",
    email: "john.smith@example.com",
    photo: null,
    rating: 4.8,
    experience: 8,
    license: "CDL-A",
    vehicle_id: 201,
    company_id: 301,
    current_location: {
      lat: 40.7128,
      lng: -74.006,
      city: "New York",
      state: "NY",
      updated_at: "2026-03-18T14:30:00Z",
    },
    status: "available",
    completed_trips: 1240,
  },
  {
    id: 102,
    name: "Maria Garcia",
    phone: "+1 (555) 234-5678",
    email: "maria.garcia@example.com",
    photo: null,
    rating: 4.9,
    experience: 12,
    license: "CDL-A",
    vehicle_id: 202,
    company_id: 301,
    current_location: {
      lat: 34.0522,
      lng: -118.2437,
      city: "Los Angeles",
      state: "CA",
      updated_at: "2026-03-18T14:25:00Z",
    },
    status: "on_trip",
    completed_trips: 2150,
  },
  {
    id: 103,
    name: "David Chen",
    phone: "+1 (555) 345-6789",
    email: "david.chen@example.com",
    photo: null,
    rating: 4.7,
    experience: 5,
    license: "CDL-B",
    vehicle_id: 203,
    company_id: 301,
    current_location: {
      lat: 41.8781,
      lng: -87.6298,
      city: "Chicago",
      state: "IL",
      updated_at: "2026-03-18T14:20:00Z",
    },
    status: "available",
    completed_trips: 850,
  },
  {
    id: 104,
    name: "Sarah Johnson",
    phone: "+1 (555) 456-7890",
    email: "sarah.j@example.com",
    photo: null,
    rating: 4.6,
    experience: 6,
    license: "CDL-A",
    vehicle_id: 204,
    company_id: 303,
    current_location: {
      lat: 29.7604,
      lng: -95.3698,
      city: "Houston",
      state: "TX",
      updated_at: "2026-03-18T14:15:00Z",
    },
    status: "on_trip",
    completed_trips: 980,
  },
  {
    id: 105,
    name: "Michael Brown",
    phone: "+1 (555) 567-8901",
    email: "michael.b@example.com",
    photo: null,
    rating: 4.9,
    experience: 15,
    license: "CDL-A",
    vehicle_id: 205,
    company_id: 304,
    current_location: {
      lat: 39.9526,
      lng: -75.1652,
      city: "Philadelphia",
      state: "PA",
      updated_at: "2026-03-18T14:10:00Z",
    },
    status: "available",
    completed_trips: 3200,
  },
  {
    id: 106,
    name: "Liam Tremblay",
    phone: "+1 (555) 678-9012",
    email: "liam.t@example.ca",
    photo: null,
    rating: 4.8,
    experience: 9,
    license: "AZ",
    vehicle_id: 206,
    company_id: 302,
    current_location: {
      lat: 44.5,
      lng: -76.5,
      city: "Kingston",
      state: "ON",
      updated_at: "2026-03-18T14:30:00Z",
    },
    status: "on_trip",
    completed_trips: 1410,
  },
  {
    id: 107,
    name: "Noah Martin",
    phone: "+1 (555) 765-4321",
    email: "noah.m@example.ca",
    photo: null,
    rating: 4.5,
    experience: 7,
    license: "AZ",
    vehicle_id: 207,
    company_id: 302,
    current_location: {
      lat: 43.6532,
      lng: -79.3832,
      city: "Toronto",
      state: "ON",
      updated_at: "2026-03-18T14:12:00Z",
    },
    status: "available",
    completed_trips: 990,
  },
];

export const mockCompanies = [
  {
    id: 301,
    name: "US Express Logistics",
    logo: null,
    address: "123 Industrial Ave, Chicago, IL 60607",
    phone: "+1 (312) 555-0100",
    email: "dispatch@usexpress.com",
    website: "www.usexpress.com",
    founded: 2010,
    fleet_size: 45,
    drivers: [101, 102, 103],
    headquarters: { lat: 41.8781, lng: -87.6298, city: "Chicago", state: "IL" },
    service_areas: ["Midwest", "East Coast", "South"],
    rating: 4.7,
  },
  {
    id: 302,
    name: "Canada Freight Masters",
    logo: null,
    address: "456 King St W, Toronto, ON M5V 1K4",
    phone: "+1 (416) 555-0200",
    email: "dispatch@canadafreight.ca",
    website: "www.canadafreight.ca",
    founded: 2008,
    fleet_size: 32,
    drivers: [106, 107],
    headquarters: { lat: 43.6532, lng: -79.3832, city: "Toronto", state: "ON" },
    service_areas: ["Ontario", "Quebec", "Western Canada"],
    rating: 4.8,
  },
  {
    id: 303,
    name: "Pacific Coast Carriers",
    logo: null,
    address: "789 Harbor Blvd, Los Angeles, CA 90015",
    phone: "+1 (213) 555-0300",
    email: "ops@pacificcoast.com",
    website: "www.pacificcoast.com",
    founded: 2015,
    fleet_size: 28,
    drivers: [104],
    headquarters: { lat: 34.0522, lng: -118.2437, city: "Los Angeles", state: "CA" },
    service_areas: ["West Coast", "Southwest", "Pacific Northwest"],
    rating: 4.6,
  },
  {
    id: 304,
    name: "East Coast Transport",
    logo: null,
    address: "321 Atlantic Ave, New York, NY 10001",
    phone: "+1 (212) 555-0400",
    email: "dispatch@eastcoast.com",
    website: "www.eastcoast.com",
    founded: 2012,
    fleet_size: 38,
    drivers: [105],
    headquarters: { lat: 40.7128, lng: -74.006, city: "New York", state: "NY" },
    service_areas: ["Northeast", "Mid-Atlantic", "Southeast"],
    rating: 4.5,
  },
  {
    id: 305,
    name: "Southern Haulers",
    logo: null,
    address: "567 Dixie Rd, Atlanta, GA 30303",
    phone: "+1 (404) 555-0500",
    email: "ops@southernhaulers.com",
    website: "www.southernhaulers.com",
    founded: 2011,
    fleet_size: 25,
    drivers: [],
    headquarters: { lat: 33.749, lng: -84.388, city: "Atlanta", state: "GA" },
    service_areas: ["Southeast", "Texas", "Gulf Coast"],
    rating: 4.4,
  },
];

export const mockTenants = [
  {
    id: "gts-toronto",
    name: "GTS Logistics",
    type: "tenant",
    location: { lat: 43.6532, lng: -79.3832, city: "Toronto", state: "ON", country: "Canada" },
    contact: { phone: "+1 (416) 555-0100", email: "info@gts.com", website: "www.gts.com" },
    stats: { drivers: 25, vehicles: 30, active_shipments: 12 },
    status: "active",
  },
  {
    id: "us-express-tenant",
    name: "US Express Freight",
    type: "tenant",
    location: { lat: 41.8781, lng: -87.6298, city: "Chicago", state: "IL", country: "USA" },
    contact: { phone: "+1 (312) 555-0200", email: "dispatch@usexpress.com", website: "www.usexpress.com" },
    stats: { drivers: 42, vehicles: 55, active_shipments: 28 },
    status: "active",
  },
  {
    id: "canada-haulers-tenant",
    name: "Canada Haulers",
    type: "tenant",
    location: { lat: 45.5017, lng: -73.5673, city: "Montreal", state: "QC", country: "Canada" },
    contact: { phone: "+1 (514) 555-0300", email: "ops@canadahaulers.ca", website: "www.canadahaulers.ca" },
    stats: { drivers: 18, vehicles: 22, active_shipments: 9 },
    status: "active",
  },
];

export const mockBrokers = [
  {
    id: 101,
    name: "North American Freight Brokers",
    type: "broker",
    location: { lat: 40.7128, lng: -74.006, city: "New York", state: "NY", country: "USA" },
    contact: { phone: "+1 (212) 555-1000", email: "broker@nafreight.com", website: "www.nafreight.com" },
    stats: { loads_posted: 450, active_loads: 78 },
    rating: 4.8,
    status: "active",
  },
  {
    id: 102,
    name: "Trans-Canada Logistics",
    type: "broker",
    location: { lat: 49.2827, lng: -123.1207, city: "Vancouver", state: "BC", country: "Canada" },
    contact: { phone: "+1 (604) 555-2000", email: "dispatch@tclogistics.ca", website: "www.tclogistics.ca" },
    stats: { loads_posted: 320, active_loads: 45 },
    rating: 4.6,
    status: "active",
  },
  {
    id: 103,
    name: "Midwest Freight Solutions",
    type: "broker",
    location: { lat: 41.8781, lng: -87.6298, city: "Chicago", state: "IL", country: "USA" },
    contact: { phone: "+1 (312) 555-3000", email: "info@midwestfreight.com", website: "www.midwestfreight.com" },
    stats: { loads_posted: 280, active_loads: 52 },
    rating: 4.5,
    status: "active",
  },
];

export const mockCarriers = [
  {
    id: 201,
    name: "Swift Transportation",
    type: "carrier",
    location: { lat: 33.4484, lng: -112.074, city: "Phoenix", state: "AZ", country: "USA" },
    contact: { phone: "+1 (602) 555-4000", email: "dispatch@swift.com", website: "www.swift.com" },
    stats: { fleet_size: 150, available_trucks: 45, active_shipments: 120 },
    rating: 4.7,
    status: "active",
  },
  {
    id: 202,
    name: "Knight-Swift",
    type: "carrier",
    location: { lat: 32.7767, lng: -96.797, city: "Dallas", state: "TX", country: "USA" },
    contact: { phone: "+1 (214) 555-5000", email: "ops@knightswift.com", website: "www.knightswift.com" },
    stats: { fleet_size: 220, available_trucks: 68, active_shipments: 180 },
    rating: 4.8,
    status: "active",
  },
  {
    id: 203,
    name: "Bison Transport",
    type: "carrier",
    location: { lat: 49.8951, lng: -97.1384, city: "Winnipeg", state: "MB", country: "Canada" },
    contact: { phone: "+1 (204) 555-6000", email: "dispatch@bison.ca", website: "www.bison.ca" },
    stats: { fleet_size: 85, available_trucks: 22, active_shipments: 58 },
    rating: 4.9,
    status: "active",
  },
];

export const mockVehicles = [
  {
    id: 201,
    plate: "USA-1234",
    type: "Semi-Trailer",
    model: "Freightliner Cascadia",
    year: 2023,
    capacity: 40000,
    fuel_type: "Diesel",
    driver_id: 101,
    company_id: 301,
    last_maintenance: "2026-03-01",
    next_maintenance: "2026-04-01",
    status: "active",
  },
  {
    id: 202,
    plate: "USA-5678",
    type: "Flatbed",
    model: "Peterbilt 579",
    year: 2022,
    capacity: 48000,
    fuel_type: "Diesel",
    driver_id: 102,
    company_id: 301,
    last_maintenance: "2026-02-15",
    next_maintenance: "2026-03-15",
    status: "maintenance",
  },
  {
    id: 206,
    plate: "CAN-7890",
    type: "Semi-Trailer",
    model: "Kenworth T680",
    year: 2023,
    capacity: 42000,
    fuel_type: "Diesel",
    driver_id: 106,
    company_id: 302,
    last_maintenance: "2026-03-05",
    next_maintenance: "2026-04-05",
    status: "active",
  },
];

export const mockShipments = [
  {
    id: 4001,
    reference: "US-2026-001",
    status: "in_transit",
    driver_id: 101,
    vehicle_id: 201,
    company_id: 301,
    origin: {
      city: "Chicago",
      state: "IL",
      address: "123 Industrial Ave",
      lat: 41.8781,
      lng: -87.6298,
      country: "US",
    },
    destination: {
      city: "New York",
      state: "NY",
      address: "456 Broadway",
      lat: 40.7128,
      lng: -74.006,
      country: "US",
    },
    current_location: {
      lat: 40.5,
      lng: -80.2,
      updated_at: "2026-03-18T14:35:00Z",
      speed: 65,
      description: "Near Pittsburgh corridor",
    },
    cargo: {
      type: "Electronics",
      weight: 2500,
      dimensions: "10x8x6 ft",
      value: 75000,
    },
    pickup_date: "2026-03-18T08:00:00Z",
    eta: "2026-03-19T14:00:00Z",
    progress: 0.65,
    route: [
      [41.8781, -87.6298],
      [41.5, -86],
      [41.2, -84.5],
      [40.8, -82],
      [40.5, -80.2],
      [40.2, -78.5],
      [40.7128, -74.006],
    ],
  },
  {
    id: 4002,
    reference: "CA-2026-002",
    status: "in_transit",
    driver_id: 106,
    vehicle_id: 206,
    company_id: 302,
    origin: {
      city: "Toronto",
      state: "ON",
      address: "456 King St W",
      lat: 43.6532,
      lng: -79.3832,
      country: "CA",
    },
    destination: {
      city: "Montreal",
      state: "QC",
      address: "789 St Catherine St",
      lat: 45.5017,
      lng: -73.5673,
      country: "CA",
    },
    current_location: {
      lat: 44.5,
      lng: -76.5,
      updated_at: "2026-03-18T14:30:00Z",
      speed: 70,
      description: "Highway 401 eastbound",
    },
    cargo: {
      type: "Automotive Parts",
      weight: 3200,
      dimensions: "12x8x6 ft",
      value: 45000,
    },
    pickup_date: "2026-03-18T09:00:00Z",
    eta: "2026-03-19T10:00:00Z",
    progress: 0.45,
    route: [
      [43.6532, -79.3832],
      [44, -78.5],
      [44.5, -77.5],
      [44.5, -76.5],
      [45, -75],
      [45.5017, -73.5673],
    ],
  },
  {
    id: 4003,
    reference: "US-2026-003",
    status: "pending",
    driver_id: null,
    vehicle_id: null,
    company_id: 303,
    origin: {
      city: "Los Angeles",
      state: "CA",
      address: "789 Harbor Blvd",
      lat: 34.0522,
      lng: -118.2437,
      country: "US",
    },
    destination: {
      city: "San Francisco",
      state: "CA",
      address: "321 Market St",
      lat: 37.7749,
      lng: -122.4194,
      country: "US",
    },
    current_location: {
      lat: 34.0522,
      lng: -118.2437,
      updated_at: "2026-03-18T14:00:00Z",
      speed: 0,
      description: "Awaiting dispatch in Los Angeles",
    },
    cargo: {
      type: "Medical Supplies",
      weight: 1800,
      dimensions: "8x6x4 ft",
      value: 120000,
    },
    pickup_date: "2026-03-19T08:00:00Z",
    eta: "2026-03-20T12:00:00Z",
    progress: 0,
    route: [
      [34.0522, -118.2437],
      [35, -120],
      [36.5, -121.5],
      [37.7749, -122.4194],
    ],
  },
];

export const getMockDrivers = () => mockDrivers;
export const getMockCompanies = () => mockCompanies;
export const getMockShipments = () => mockShipments;
export const getMockVehicles = () => mockVehicles;

function normalizeDriversResponse(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.drivers)) return data.drivers;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function normalizeCompaniesResponse(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.companies)) return data.companies;
  if (Array.isArray(data?.data)) return data.data;
  return [];
}

function normalizeMapEntitiesResponse(data) {
  return {
    tenants: Array.isArray(data?.tenants) ? data.tenants : [],
    brokers: Array.isArray(data?.brokers) ? data.brokers : [],
    carriers: Array.isArray(data?.carriers) ? data.carriers : [],
    drivers: Array.isArray(data?.drivers) ? data.drivers : [],
    shipments: Array.isArray(data?.shipments) ? data.shipments : [],
  };
}

export const getAllMapData = async ({ shipments = [] } = {}) => {
  try {
    const [entitiesRes, driversRes, companiesRes] = await Promise.all([
      axiosClient.get("/api/v1/map/entities").catch(() => ({ data: {} })),
      axiosClient.get("/api/v1/drivers", { params: { limit: 50 } }).catch(() => ({ data: {} })),
      axiosClient.get("/api/v1/companies", { params: { limit: 20 } }).catch(() => ({ data: {} })),
    ]);

    const liveEntities = normalizeMapEntitiesResponse(entitiesRes.data);
    const liveDrivers = normalizeDriversResponse(driversRes.data);
    const liveCompanies = normalizeCompaniesResponse(companiesRes.data);
    const mergedShipments = shipments.length > 0 ? [...shipments, ...mockShipments] : liveEntities.shipments.length ? liveEntities.shipments : mockShipments;
    const mergedDrivers = liveEntities.drivers.length > 0 ? liveEntities.drivers : liveDrivers.length > 0 ? liveDrivers : mockDrivers;
    const mergedTenants = liveEntities.tenants.length > 0 ? liveEntities.tenants : mockTenants;
    const mergedBrokers = liveEntities.brokers.length > 0 ? liveEntities.brokers : mockBrokers;
    const mergedCarriers = liveEntities.carriers.length > 0 ? liveEntities.carriers : mockCarriers;
    const mergedCompanies = liveCompanies.length > 0 ? liveCompanies : mergedTenants.length > 0 ? mergedTenants : mockCompanies;

    return {
      tenants: mergedTenants,
      brokers: mergedBrokers,
      carriers: mergedCarriers,
      shipments: mergedShipments,
      drivers: mergedDrivers,
      companies: mergedCompanies,
      vehicles: mockVehicles,
    };
  } catch {
    return {
      tenants: mockTenants,
      brokers: mockBrokers,
      carriers: mockCarriers,
      shipments: shipments.length > 0 ? [...shipments, ...mockShipments] : mockShipments,
      drivers: mockDrivers,
      companies: mockTenants,
      vehicles: mockVehicles,
    };
  }
};
