/**
 * Freight Broker Bot - Canadian Logistics Control Panel
 * Comprehensive freight load board with Canadian cross-border support
 */
import { useState, useEffect } from "react";
import axios from "axios";
import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix for default markers not showing in leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl: "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

// City coordinates mapping for Canada and selected US cities
const cityCoordinates = {
  "Grande Cache": [53.93, -119.35],
  "Edmonton": [53.5461, -113.4938],
  "Calgary": [51.0447, -114.0719],
  "Vancouver": [49.2827, -123.1207],
  "Toronto": [43.6629, -79.3957],
  "Montreal": [45.5017, -73.5673],
  "Halifax": [44.6426, -63.2181],
  "Winnipeg": [49.8951, -97.1384],
  "Regina": [50.4452, -104.6189],
  "Quebec City": [46.8139, -71.2080],
  "Grand Island": [40.9250, -98.3468],
  "Edgeley": [48.7339, -99.1814],
  "Perris": [33.7803, -117.2289],
  "Buffalo": [42.8864, -78.8784],
  "Detroit": [42.3314, -83.0458],
  "Los Angeles": [34.0522, -118.2437],
  "Chicago": [41.8781, -87.6298],
  "Dallas": [32.7767, -96.7970],
  "Houston": [29.7604, -95.3698],
  "New York": [40.7128, -74.0060],
  "Boston": [42.3601, -71.0589],
  "Seattle": [47.6062, -122.3321],
  "Phoenix": [33.4484, -112.0742],
};

const getCityCoordinates = (cityName) => {
  const cleanCity = cityName.split(",")[0].trim();
  return cityCoordinates[cleanCity] || [51.5074, -0.1278]; // Default to somewhere visible
};

const FreightBrokerControl = () => {
  const [loading, setLoading] = useState(false);
  const [loads, setLoads] = useState([]);
  const [selectedLoad, setSelectedLoad] = useState(null);
  const [searchFilters, setSearchFilters] = useState({
    origin: "",
    destination: "",
    trailerType: "all",
    minWeight: 0,
    maxWeight: 100000
  });
  const [routes, setRoutes] = useState([
    { id: 1, trailer: "", pickup: "", dh_p: 0, dropoff: "", dh_d: 0, length: 0, weight: 0 }
  ]);

  const dailyFreeViews = 4;
  const [viewsLeft, setViewsLeft] = useState(dailyFreeViews);
  const [showSettings, setShowSettings] = useState(false);
  const [botSettings, setBotSettings] = useState({
    minRate: 1000,
    maxDistance: 2000,
    preferredTrailerTypes: [],
    autoFilterUSD: false,
    notificationsEnabled: true,
    defaultSortBy: 'distance'
  });

  const canadianProvinces = [
    "Alberta (AB)", "British Columbia (BC)", "Manitoba (MB)", 
    "New Brunswick (NB)", "Newfoundland and Labrador (NL)", 
    "Nova Scotia (NS)", "Ontario (ON)", "Prince Edward Island (PE)",
    "Quebec (QC)", "Saskatchewan (SK)", "Northwest Territories (NT)",
    "Nunavut (NU)", "Yukon (YT)"
  ];

  const trailerTypes = [
    "Van", "Flatbed", "Reefer", "Tanker", "Dry Bulk", "Step Deck", "Double Drop"
  ];

  useEffect(() => {
    fetchLoads();
  }, []);

  const fetchLoads = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/freight/canadian-loads', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        // Map API response to component format
        const formattedLoads = (data.loads || []).map(load => ({
          id: load.load_id,
          age: load.posted_age || '7h',
          pickup: `${load.origin_city}, ${load.origin_province}`,
          pickupDate: load.pickup_date,
          dropoff: `${load.destination_city}, ${load.destination_province}`,
          dropoffDate: load.dropoff_date,
          distance: load.distance_miles,
          trailer: load.trailer_type?.charAt(0) || 'V',
          weight: load.weight_lbs || 0,
          broker: load.broker_name,
          phone: load.broker_phone,
          email: load.broker_phone ? 'info@broker.com' : null,
          price: load.rate_cad,
          unlocked: load.unlocked || false
        }));
        setLoads(formattedLoads);
      } else {
        console.error('API error:', response.status);
        setLoads(mockLoads);
      }
    } catch (error) {
      console.error("Error fetching loads:", error);
      setLoads(mockLoads);
    } finally {
      setLoading(false);
    }
  };

  const handleAddRoute = () => {
    setRoutes([
      ...routes,
      { id: routes.length + 1, trailer: "", pickup: "", dh_p: 0, dropoff: "", dh_d: 0, length: 0, weight: 0 }
    ]);
  };

  const handleRemoveRoute = (id) => {
    setRoutes(routes.filter(r => r.id !== id));
  };

  const handleSearch = () => {
    fetchLoads();
  };

  const handleUnlockLoad = (loadId) => {
    if (viewsLeft > 0) {
      // Update the unlocked state for the load
      const updatedLoads = loads.map(load => 
        load.id === loadId ? { ...load, unlocked: true } : load
      );
      
      // Also update selectedLoad if it's the one being unlocked
      if (selectedLoad?.id === loadId) {
        setSelectedLoad({ ...selectedLoad, unlocked: true });
      }
      
      setLoads(updatedLoads);
      setViewsLeft(viewsLeft - 1);
    } else {
      alert('No free views remaining. Upgrade to unlock more loads.');
    }
  };

  const getTrailerIcon = (type) => {
    const icons = {
      'V': 'Van',
      'F': 'Flatbed',
      'R': 'Reefer',
      'T': 'Tanker',
      'SD': 'Step Deck',
      'DD': 'Double Drop'
    };
    return icons[type] || 'Van';
  };

  const formatCurrency = (amount) => {
    if (!amount || amount === '--') return '--';
    return `$${amount.toLocaleString('en-CA')}`;
  };

  const calculateProfit = (load) => {
    const rate = load.price || 0;
    const distance = load.distance || 0;
    const operatingCost = distance * 2.00;
    const profit = rate - operatingCost;
    return profit;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 to-blue-700 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold flex items-center gap-3">
                🚛 Freight Broker Bot
              </h1>
              <p className="text-blue-100 mt-2">Canadian Logistics Command Center</p>
            </div>
            <div className="flex items-center gap-4">
              <span className="bg-yellow-500 text-white px-3 py-1 rounded-full text-sm font-semibold">
                Daily Free Views: {viewsLeft}/{dailyFreeViews}
              </span>
              <button onClick={() => setShowSettings(!showSettings)} className="backdrop-blur-xl bg-white/10 text-blue-100 px-4 py-2 rounded-lg font-medium hover:bg-white/20 border border-white/20 transition-all">
                ⚙️ Bot Settings
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-6">
        {/* Route Builder */}
        <div className="backdrop-blur-xl bg-white/10 rounded-lg border border-white/20 p-6 mb-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold flex items-center gap-2">
              🧭 Route Builder - Canadian Freight
            </h2>
            <button onClick={handleAddRoute} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
              + Add Route
            </button>
          </div>
          <p className="text-gray-600 mb-4">Configure your shipping routes and preferences</p>
          
          <div className="space-y-4">
            {routes.map((route, index) => (
              <div key={route.id} className="grid grid-cols-1 md:grid-cols-12 gap-3 p-4 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10">
                <div className="md:col-span-2">
                  <label className="text-xs text-gray-400">Trailer Type</label>
                  <select className="w-full mt-1 px-3 py-2 border border-white/20 rounded-md bg-white/5 backdrop-blur-sm text-white">
                    <option className="bg-slate-800">Select Trailer</option>
                    {trailerTypes.map(type => (
                      <option key={type} className="bg-slate-800">{type}</option>
                    ))}
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="text-xs text-gray-400">Pick Up</label>
                  <select className="w-full mt-1 px-3 py-2 border border-white/20 rounded-md bg-white/5 backdrop-blur-sm text-white">
                    <option className="bg-slate-800">Select Province</option>
                    {canadianProvinces.map(prov => (
                      <option key={prov} className="bg-slate-800">{prov}</option>
                    ))}
                  </select>
                </div>
                <div className="md:col-span-1">
                  <label className="text-xs text-gray-400">DH-P (km)</label>
                  <input type="number" placeholder="km" className="w-full mt-1 px-3 py-2 border border-white/20 rounded-md bg-white/5 backdrop-blur-sm text-white placeholder-gray-500" />
                </div>
                <div className="md:col-span-2">
                  <label className="text-xs text-gray-400">Drop Off</label>
                  <select className="w-full mt-1 px-3 py-2 border border-white/20 rounded-md bg-white/5 backdrop-blur-sm text-white">
                    <option className="bg-slate-800">Select Province/State</option>
                    {canadianProvinces.map(prov => (
                      <option key={prov} className="bg-slate-800">{prov}</option>
                    ))}
                    <option className="bg-slate-800">Various US States</option>
                  </select>
                </div>
                <div className="md:col-span-1">
                  <label className="text-xs text-gray-400">DH-D (km)</label>
                  <input type="number" placeholder="km" className="w-full mt-1 px-3 py-2 border border-white/20 rounded-md bg-white/5 backdrop-blur-sm text-white placeholder-gray-500" />
                </div>
                <div className="md:col-span-1">
                  <label className="text-xs text-gray-400">Length (ft)</label>
                  <input type="number" className="w-full mt-1 px-3 py-2 border border-white/20 rounded-md bg-white/5 backdrop-blur-sm text-white" />
                </div>
                <div className="md:col-span-1">
                  <label className="text-xs text-gray-400">Weight (lbs)</label>
                  <input type="number" className="w-full mt-1 px-3 py-2 border border-white/20 rounded-md bg-white/5 backdrop-blur-sm text-white" />
                </div>
                <div className="md:col-span-2 flex items-end gap-2">
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex-1">
                    Search
                  </button>
                  {routes.length > 1 && (
                    <button 
                      onClick={() => handleRemoveRoute(route.id)}
                      className="border border-red-600/50 text-red-400 px-3 py-2 rounded-lg hover:bg-red-500/20 backdrop-blur-sm"
                    >
                      ×
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content - Load Board */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Load List */}
          <div className="lg:col-span-2">
            <div className="backdrop-blur-xl bg-white/10 rounded-lg border border-white/20 shadow-lg">
              <div className="p-6 border-b border-white/10">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold flex items-center gap-2 text-white">
                    📦 Available Loads - Canada/US Cross Border
                  </h2>
                  <span className="bg-white/10 backdrop-blur-sm text-gray-200 px-3 py-1 rounded-full text-sm border border-white/20">{loads.length} loads</span>
                </div>
                <div className="flex gap-2">
                  <input 
                    placeholder="Search origin..." 
                    className="flex-1 px-3 py-2 border border-white/20 rounded-md bg-white/5 backdrop-blur-sm text-white placeholder-gray-500"
                    value={searchFilters.origin}
                    onChange={(e) => setSearchFilters({...searchFilters, origin: e.target.value})}
                  />
                  <input 
                    placeholder="Search destination..."
                    className="flex-1 px-3 py-2 border border-white/20 rounded-md bg-white/5 backdrop-blur-sm text-white placeholder-gray-500"
                    value={searchFilters.destination}
                    onChange={(e) => setSearchFilters({...searchFilters, destination: e.target.value})}
                  />
                  <button onClick={handleSearch} className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700">
                    🔍 Search
                  </button>
                </div>
              </div>
              
              <div className="p-4">
                {loading ? (
                  <div className="space-y-4">
                    {[1,2,3].map(i => (
                      <div key={i} className="animate-pulse p-4 border rounded-lg">
                        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="space-y-3 max-h-[800px] overflow-y-auto">
                    {loads.map((load, index) => (
                      <div
                        key={index}
                        className={`p-4 border rounded-lg cursor-pointer transition-all backdrop-blur-sm ${
                          selectedLoad?.id === load.id ? 'bg-blue-500/30 border-blue-400' : 'border-white/20 bg-white/5 hover:bg-white/10'
                        }`}
                        onClick={() => setSelectedLoad(load)}
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center gap-2">
                            <span className="bg-white/10 backdrop-blur-sm text-gray-300 px-2 py-1 rounded text-xs border border-white/20">{load.age}</span>
                            <span className={`px-2 py-1 rounded text-xs font-semibold border backdrop-blur-sm ${
                              load.price ? 'bg-green-500/20 text-green-300 border-green-500/30' : 'bg-white/10 text-gray-300 border-white/20'
                            }`}>
                              {load.price ? formatCurrency(load.price) : '--'}
                            </span>
                          </div>
                          {viewsLeft > 0 && !load.unlocked && (
                            <button 
                              onClick={(e) => {
                                e.stopPropagation();
                                handleUnlockLoad(load.id);
                              }}
                              className="border border-blue-500/50 text-blue-300 px-3 py-1 rounded text-xs hover:bg-blue-500/20 backdrop-blur-sm"
                            >
                              Unlock
                            </button>
                          )}
                        </div>
                        
                        <div className="grid grid-cols-2 gap-2 mt-2">
                          <div className="flex items-start gap-1">
                            <span className="text-gray-400 mt-1">📍</span>
                            <div>
                              <p className="text-xs text-gray-400">Pick Up</p>
                              <p className="font-medium text-sm text-white">{load.pickup}</p>
                              <p className="text-xs text-gray-500">{load.pickupDate}</p>
                            </div>
                          </div>
                          <div className="flex items-start gap-1">
                            <span className="text-gray-400 mt-1">📍</span>
                            <div>
                              <p className="text-xs text-gray-400">Drop Off</p>
                              <p className="font-medium text-sm text-white">{load.dropoff}</p>
                              <p className="text-xs text-gray-500">{load.dropoffDate || '--'}</p>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex justify-between items-center mt-3 text-xs">
                          <div className="flex items-center gap-2">
                            <span className="bg-white/10 backdrop-blur-sm px-2 py-1 rounded text-gray-300 border border-white/20">{load.distance}mi</span>
                            <span className="bg-white/10 backdrop-blur-sm px-2 py-1 rounded text-gray-300 border border-white/20">{getTrailerIcon(load.trailer)}</span>
                            <span className="text-gray-400">{load.weight} lbs</span>
                          </div>
                          <span className="text-gray-400">{load.broker}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Load Details */}
          <div className="lg:col-span-1">
            {selectedLoad ? (
              <div className="backdrop-blur-xl bg-white/10 rounded-lg border border-white/20 p-6 space-y-4 shadow-lg">
                <h2 className="text-xl font-bold flex items-center gap-2 text-white">
                  🚛 Trip Details
                </h2>
                
                {/* Route Info */}
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-500/30 rounded-full flex items-center justify-center border border-blue-400/50">
                      📍
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">PICK UP</p>
                      <p className="font-medium text-white">{selectedLoad.pickup}</p>
                      <p className="text-sm text-gray-500">{selectedLoad.pickupDate}</p>
                    </div>
                  </div>
                  <div className="ml-4 h-6 border-l-2 border-dashed border-white/20"></div>
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-red-500/30 rounded-full flex items-center justify-center border border-red-400/50">
                      📍
                    </div>
                    <div>
                      <p className="text-xs text-gray-400">DROP OFF</p>
                      <p className="font-medium text-white">{selectedLoad.dropoff}</p>
                      <p className="text-sm text-gray-500">{selectedLoad.dropoffDate || '--'}</p>
                    </div>
                  </div>
                </div>

                {/* Map Display */}
                <div className="border-t border-white/10 pt-4">
                  <h4 className="font-semibold mb-3 text-white">🗺️ Route Map</h4>
                  <div className="rounded-lg overflow-hidden border border-white/20 shadow-lg" style={{ height: "300px" }}>
                    <MapContainer
                      center={[53.5, -113.5]}
                      zoom={4}
                      style={{ height: "100%", width: "100%" }}
                    >
                      <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                        attribution='&copy; CartoDB'
                      />
                      <Marker position={getCityCoordinates(selectedLoad.pickup)}>
                        <Popup>
                          <div className="text-sm">
                            <p className="font-semibold">Pick Up</p>
                            <p>{selectedLoad.pickup}</p>
                            <p className="text-xs text-gray-500">{selectedLoad.pickupDate}</p>
                          </div>
                        </Popup>
                      </Marker>
                      <Marker position={getCityCoordinates(selectedLoad.dropoff)}>
                        <Popup>
                          <div className="text-sm">
                            <p className="font-semibold">Drop Off</p>
                            <p>{selectedLoad.dropoff}</p>
                            <p className="text-xs text-gray-500">{selectedLoad.dropoffDate || '--'}</p>
                          </div>
                        </Popup>
                      </Marker>
                      <Polyline
                        positions={[
                          getCityCoordinates(selectedLoad.pickup),
                          getCityCoordinates(selectedLoad.dropoff),
                        ]}
                        color="#3B82F6"
                        weight={3}
                        opacity={0.7}
                        dashArray="5, 5"
                      />
                    </MapContainer>
                  </div>
                </div>

                <div className="border-t border-white/10 pt-4">
                  <h4 className="font-semibold mb-3 text-white">Load Specifications</h4>
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-2 bg-white/5 backdrop-blur-sm rounded border border-white/10">
                      <p className="text-xs text-gray-400">Distance</p>
                      <p className="font-bold text-white">{selectedLoad.distance} mi</p>
                    </div>
                    <div className="p-2 bg-white/5 backdrop-blur-sm rounded border border-white/10">
                      <p className="text-xs text-gray-400">Trailer</p>
                      <p className="font-bold text-white">{getTrailerIcon(selectedLoad.trailer)}</p>
                    </div>
                    <div className="p-2 bg-white/5 backdrop-blur-sm rounded border border-white/10">
                      <p className="text-xs text-gray-400">Weight</p>
                      <p className="font-bold text-white">{selectedLoad.weight} lbs</p>
                    </div>
                    <div className="p-2 bg-white/5 backdrop-blur-sm rounded border border-white/10">
                      <p className="text-xs text-gray-400">Length</p>
                      <p className="font-bold text-white">{selectedLoad.length || '--'} ft</p>
                    </div>
                  </div>
                </div>

                {selectedLoad.price && (
                  <div className="border-t border-white/10 pt-4">
                    <h4 className="font-semibold mb-3 text-white">Rate & Profit Analysis</h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Line Haul Rate</span>
                        <span className="font-bold text-green-400">
                          {formatCurrency(selectedLoad.price)} CAD
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Rate per Mile</span>
                        <span className="font-medium text-gray-300">
                          {selectedLoad.distance ? 
                            formatCurrency((selectedLoad.price / selectedLoad.distance).toFixed(2)) : '--'
                          }/mi
                        </span>
                      </div>
                      <div className="flex justify-between pt-2 border-t border-white/10">
                        <span className="font-semibold text-white">Est. Profit</span>
                        <span className={`font-bold ${
                          calculateProfit(selectedLoad) > 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {formatCurrency(calculateProfit(selectedLoad).toFixed(0))} CAD
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Broker Info */}
                <div className="border-t border-white/10 pt-4">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-white">Broker Information</h4>
                    {selectedLoad.unlocked && (
                      <span className="text-xs bg-green-500/30 text-green-300 px-2 py-1 rounded-full border border-green-500/50">🔓 Unlocked</span>
                    )}
                  </div>
                  <div className="space-y-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-3">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">🏢</span>
                      <div>
                        <p className="text-xs text-gray-400">Company</p>
                        <p className="font-semibold text-white">{selectedLoad.broker}</p>
                      </div>
                    </div>
                    {selectedLoad.phone && (
                      <div className="flex items-center gap-2">
                        <span className="text-xl">📞</span>
                        <div>
                          <p className="text-xs text-gray-400">Phone</p>
                          <a href={`tel:${selectedLoad.phone}`} className="font-semibold text-blue-400 hover:text-blue-300">
                            {selectedLoad.phone}
                          </a>
                        </div>
                      </div>
                    )}
                    {selectedLoad.email && (
                      <div className="flex items-center gap-2">
                        <span className="text-xl">📧</span>
                        <div>
                          <p className="text-xs text-gray-400">Email</p>
                          <a href={`mailto:${selectedLoad.email}`} className="font-semibold text-blue-400 hover:text-blue-300">
                            {selectedLoad.email}
                          </a>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 pt-4">
                  <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex-1">
                    ✓ Book Load
                  </button>
                  <button className="border border-white/20 px-4 py-2 rounded-lg hover:bg-white/10 backdrop-blur-sm flex-1">
                    📞 Contact
                  </button>
                </div>
              </div>
            ) : (
              <div className="backdrop-blur-xl bg-white/10 rounded-lg border border-white/20 p-6 text-center text-gray-300 shadow-lg">
                <div className="text-6xl mb-3">📦</div>
                <p>Select a load to view details</p>
                <p className="text-sm mt-2">Click on any load from the list to see full trip information</p>
              </div>
            )}
          </div>
        </div>

        {/* Recommended Loads */}
        <div className="backdrop-blur-xl bg-white/10 rounded-lg border border-white/20 p-6 mt-6 shadow-lg">
          <h2 className="text-xl font-bold flex items-center gap-2 mb-2 text-white">
            📈 AI Recommended Loads - Based on Your Search History
          </h2>
          <p className="text-gray-400 mb-4">Personalized matches for your equipment and routes</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {mockRecommendations.map((load, index) => (
              <div key={index} className="p-3 border border-white/20 rounded-lg bg-white/5 backdrop-blur-sm hover:bg-white/10 transition-all">
                <div className="flex justify-between items-start mb-2">
                  <span className="bg-white/10 backdrop-blur-sm text-gray-300 px-2 py-1 rounded text-xs border border-white/20">{load.age}</span>
                  <span className="bg-green-500/20 text-green-300 px-2 py-1 rounded text-xs font-semibold border border-green-500/30 backdrop-blur-sm">
                    {formatCurrency(load.price)} CAD
                  </span>
                </div>
                <p className="font-medium text-sm text-white">{load.pickup}</p>
                <p className="text-xs text-gray-400 mb-1">→ {load.dropoff}</p>
                <div className="flex justify-between text-xs text-gray-400 mt-2">
                  <span>{load.distance}mi</span>
                  <span>{load.trailer}</span>
                  <span>{load.weight} lbs</span>
                </div>
                <button className="w-full mt-3 border border-blue-500/50 text-blue-300 px-3 py-1 rounded text-sm hover:bg-blue-500/20 backdrop-blur-sm">
                  View Details
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bot Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="backdrop-blur-xl bg-white/10 rounded-lg border border-white/20 shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-gradient-to-r from-blue-900/50 to-blue-700/50 border-b border-white/10 p-6 flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                ⚙️ Bot Settings
              </h2>
              <button onClick={() => setShowSettings(false)} className="text-white hover:text-blue-300 text-2xl">
                ✕
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Rate Filtering */}
              <div className="backdrop-blur-sm bg-white/5 rounded-lg p-4 border border-white/10">
                <h3 className="text-lg font-semibold text-white mb-3">💰 Rate Filtering</h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-gray-400">Minimum Rate (CAD)</label>
                    <input
                      type="number"
                      value={botSettings.minRate}
                      onChange={(e) => setBotSettings({...botSettings, minRate: parseInt(e.target.value)})}
                      className="w-full mt-1 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400"
                    />
                  </div>
                </div>
              </div>

              {/* Distance Preferences */}
              <div className="backdrop-blur-sm bg-white/5 rounded-lg p-4 border border-white/10">
                <h3 className="text-lg font-semibold text-white mb-3">📏 Distance Preferences</h3>
                <div>
                  <label className="text-sm text-gray-400">Maximum Distance (miles)</label>
                  <input
                    type="number"
                    value={botSettings.maxDistance}
                    onChange={(e) => setBotSettings({...botSettings, maxDistance: parseInt(e.target.value)})}
                    className="w-full mt-1 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400"
                  />
                </div>
              </div>

              {/* Trailer Type Preferences */}
              <div className="backdrop-blur-sm bg-white/5 rounded-lg p-4 border border-white/10">
                <h3 className="text-lg font-semibold text-white mb-3">🚛 Preferred Trailer Types</h3>
                <div className="grid grid-cols-2 gap-3">
                  {trailerTypes.map(type => (
                    <label key={type} className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={botSettings.preferredTrailerTypes.includes(type)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setBotSettings({
                              ...botSettings,
                              preferredTrailerTypes: [...botSettings.preferredTrailerTypes, type]
                            });
                          } else {
                            setBotSettings({
                              ...botSettings,
                              preferredTrailerTypes: botSettings.preferredTrailerTypes.filter(t => t !== type)
                            });
                          }
                        }}
                        className="w-4 h-4 accent-blue-500 cursor-pointer"
                      />
                      <span className="text-gray-300">{type}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Sort Preferences */}
              <div className="backdrop-blur-sm bg-white/5 rounded-lg p-4 border border-white/10">
                <h3 className="text-lg font-semibold text-white mb-3">📊 Sort Preferences</h3>
                <select
                  value={botSettings.defaultSortBy}
                  onChange={(e) => setBotSettings({...botSettings, defaultSortBy: e.target.value})}
                  className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400"
                >
                  <option value="distance">Distance (Nearest First)</option>
                  <option value="price">Rate (Highest First)</option>
                  <option value="posted">Recently Posted</option>
                  <option value="profit">Profit (Estimated)</option>
                </select>
              </div>

              {/* Notifications */}
              <div className="backdrop-blur-sm bg-white/5 rounded-lg p-4 border border-white/10">
                <h3 className="text-lg font-semibold text-white mb-3">🔔 Notifications</h3>
                <label className="flex items-center gap-3 cursor-pointer">
                  <div className="relative inline-flex w-14 h-8 bg-gray-700 rounded-full">
                    <input
                      type="checkbox"
                      checked={botSettings.notificationsEnabled}
                      onChange={(e) => setBotSettings({...botSettings, notificationsEnabled: e.target.checked})}
                      className="sr-only peer"
                    />
                    <div className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform peer-checked:translate-x-6`}></div>
                  </div>
                  <span className="text-gray-300">Enable Load Notifications</span>
                </label>
              </div>

              {/* Auto Filter USD */}
              <div className="backdrop-blur-sm bg-white/5 rounded-lg p-4 border border-white/10">
                <h3 className="text-lg font-semibold text-white mb-3">🇺🇸 Cross-Border Filter</h3>
                <label className="flex items-center gap-3 cursor-pointer">
                  <div className="relative inline-flex w-14 h-8 bg-gray-700 rounded-full">
                    <input
                      type="checkbox"
                      checked={botSettings.autoFilterUSD}
                      onChange={(e) => setBotSettings({...botSettings, autoFilterUSD: e.target.checked})}
                      className="sr-only peer"
                    />
                    <div className={`absolute top-1 left-1 w-6 h-6 bg-white rounded-full transition-transform peer-checked:translate-x-6`}></div>
                  </div>
                  <span className="text-gray-300">Auto-hide USD Rates (Show CAD Only)</span>
                </label>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-white/10">
                <button
                  onClick={() => setShowSettings(false)}
                  className="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 font-medium transition-all"
                >
                  ✓ Save Settings
                </button>
                <button
                  onClick={() => setShowSettings(false)}
                  className="flex-1 border border-white/20 text-gray-300 px-4 py-2 rounded-lg hover:bg-white/10 font-medium transition-all"
                >
                  ✕ Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Mock Data - Canadian Cross Border Loads
const mockLoads = [
  {
    id: 1,
    age: "21h",
    pickup: "Grande Cache, AB",
    pickupDate: "Feb 12 12:57",
    dropoff: "Grand Island, NE",
    distance: 1619,
    trailer: "F",
    weight: 48000,
    broker: "Dispatch",
    phone: "(888) 650-4753",
    email: "loads@dispatch.com",
    price: 2425,
    unlocked: true
  },
  {
    id: 2,
    age: "7h",
    pickup: "Edmonton, AB",
    pickupDate: "Feb 17",
    dropoff: "Edgeley, ND",
    distance: 983,
    trailer: "SD",
    weight: 48000,
    broker: "Dispatch",
    phone: "(888) 650-4753",
    email: "loads@dispatch.com",
    price: 2425
  },
  {
    id: 3,
    age: "3h",
    pickup: "Edmonton, AB",
    pickupDate: "Feb 12",
    dropoff: "Perris, CA",
    distance: 1740,
    trailer: "R",
    weight: 44000,
    broker: "Dispatch",
    phone: "(888) 650-4753",
    email: "loads@dispatch.com",
    price: null
  },
  {
    id: 4,
    age: "7h",
    pickup: "Edmonton, AB",
    pickupDate: "Feb 24",
    dropoff: "Waterloo, NE",
    distance: 1431,
    trailer: "V",
    weight: 31337,
    broker: "United Transportation Services, Inc.",
    phone: "(780) 555-0147",
    email: "dispatch@utsinc.com",
    price: 2000
  },
  {
    id: 5,
    age: "7h",
    pickup: "Edmonton, AB",
    pickupDate: "Feb 20",
    dropoff: "Twin Falls, ID",
    distance: 1028,
    trailer: "V",
    weight: 31355,
    broker: "United Transportation Services, Inc.",
    phone: "(780) 555-0147",
    email: "dispatch@utsinc.com",
    price: 1800
  },
  {
    id: 6,
    age: "7h",
    pickup: "Edmonton, AB",
    pickupDate: "Feb 18",
    dropoff: "Idaho Falls, ID",
    distance: 880,
    trailer: "V",
    weight: 31337,
    broker: "United Transportation Services, Inc.",
    phone: "(780) 555-0147",
    email: "dispatch@utsinc.com",
    price: 1500
  }
];

const mockRecommendations = [
  {
    age: "17h",
    pickup: "Oakdale, LA",
    dropoff: "Kingsland, TX",
    distance: 423,
    trailer: "F",
    weight: 48000,
    price: 1150
  },
  {
    age: "7h",
    pickup: "Oakdale, LA",
    dropoff: "San Antonio, TX",
    distance: 402,
    trailer: "F",
    weight: 48000,
    price: 1150
  },
  {
    age: "3h",
    pickup: "Edmonton, AB",
    dropoff: "Butte, MT",
    distance: 654,
    trailer: "R",
    weight: 44000,
    price: 1400
  },
  {
    age: "7h",
    pickup: "Oakdale, LA",
    dropoff: "Corpus Christi, TX",
    distance: 427,
    trailer: "F",
    weight: 48000,
    price: 1150
  }
];

export default FreightBrokerControl;
