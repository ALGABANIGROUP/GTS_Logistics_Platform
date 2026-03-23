// frontend/src/pages/SafetyManager.jsx
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import axiosClient from '../api/axiosClient';

const SafetyManager = () => {
  const { user, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [incidents, setIncidents] = useState([]);
  const [compliance, setCompliance] = useState(null);
  const [risks, setRisks] = useState(null);
  const [weather, setWeather] = useState(null);
  const [weatherError, setWeatherError] = useState(null);
  const [reportForm, setReportForm] = useState({
    incident_type: 'slip_trip_fall',
    severity: 'moderate',
    description: '',
    location: '',
    reporter: user?.email || '',
    injured_persons: [],
    witnesses: []
  });

  useEffect(() => {
    fetchDashboard();
    fetchWeather();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const response = await axiosClient.get('/api/v1/safety/dashboard');
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIncidents = async () => {
    try {
      const response = await axiosClient.get('/api/v1/safety/incidents/statistics');
      setIncidents(response.data);
    } catch (error) {
      console.error('Error fetching incidents:', error);
    }
  };

  const fetchCompliance = async () => {
    try {
      const response = await axiosClient.get('/api/v1/safety/compliance/check');
      setCompliance(response.data);
    } catch (error) {
      console.error('Error fetching compliance:', error);
    }
  };

  const fetchRisks = async () => {
    try {
      const response = await axiosClient.get('/api/v1/safety/risks/assess');
      setRisks(response.data);
    } catch (error) {
      console.error('Error fetching risks:', error);
    }
  };

  const fetchWeather = async () => {
    try {
      // Get weather for user's registered location (for fleet tracking)
      // NOT current GPS location - the weather should match where the fleet operates
      const userCity = user?.city || user?.address?.city || user?.location?.city || 'Vancouver';
      const response = await axiosClient.get('/api/v1/weather/current', {
        params: { city: userCity, units: 'metric' },
      });
      setWeather(response.data);
      setWeatherError(null);
    } catch (error) {
      console.error('Error fetching weather:', error);
      setWeatherError('Weather unavailable');
    }
  };

  const handleReportIncident = async (e) => {
    e.preventDefault();
    try {
      await axiosClient.post('/api/v1/safety/incidents/report', reportForm);
      alert('✅ Incident reported successfully!');
      setReportForm({
        incident_type: 'slip_trip_fall',
        severity: 'moderate',
        description: '',
        location: '',
        reporter: user?.email || '',
        injured_persons: [],
        witnesses: []
      });
      fetchDashboard();
    } catch (error) {
      alert('❌ Error reporting incident: ' + error.message);
    }
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'incidents') fetchIncidents();
    if (tab === 'compliance') fetchCompliance();
    if (tab === 'risks') fetchRisks();
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">🔐</div>
          <p className="text-white text-2xl font-bold">Please login to access Safety Manager</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin inline-block">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full"></div>
          </div>
          <p className="text-white text-xl mt-4">⏳ Loading Safety Dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800">
      {/* Top Navigation */}
      <div className="bg-slate-950 border-b border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-xl font-bold">🛡️</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">Safety Manager Bot</h1>
              <p className="text-xs text-slate-400">🏭 Comprehensive Workplace Safety</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-slate-300 font-semibold">{user?.email}</p>
            <p className="text-xs text-slate-500">{new Date().toLocaleDateString()}</p>
          </div>
        </div>
      </div>

      {/* Dashboard Stats Cards */}
      {dashboard && (
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {/* Safety Score */}
            <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-xl p-6 text-white shadow-lg hover:shadow-2xl hover:scale-105 hover:bg-slate-700/50 transition">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-blue-300 text-xs font-bold uppercase tracking-wide">Safety Score</p>
                  <p className="text-5xl font-black mt-2">{dashboard.safety_score || 0}</p>
                </div>
                <span className="text-5xl">📊</span>
              </div>
              <div className="w-full bg-slate-700/50 rounded-full h-2 overflow-hidden">
                <div className="h-full bg-blue-500" style={{ width: `${dashboard.safety_score || 0}%` }}></div>
              </div>
            </div>

            {/* Days Without Accident */}
            <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-xl p-6 text-white shadow-lg hover:shadow-2xl hover:scale-105 hover:bg-slate-700/50 transition">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-emerald-300 text-xs font-bold uppercase tracking-wide">Days Without Accident</p>
                  <p className="text-5xl font-black mt-2">{dashboard.days_without_accident || 0}</p>
                  <p className="text-xs text-emerald-400 mt-2">🎯 Great Safety Record</p>
                </div>
                <span className="text-5xl">✅</span>
              </div>
            </div>

            {/* Compliance Rate */}
            <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-xl p-6 text-white shadow-lg hover:shadow-2xl hover:scale-105 hover:bg-slate-700/50 transition">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <p className="text-purple-300 text-xs font-bold uppercase tracking-wide">Compliance Rate</p>
                  <p className="text-5xl font-black mt-2">{dashboard.compliance_rate || 0}%</p>
                </div>
                <span className="text-5xl">📋</span>
              </div>
              <div className="w-full bg-slate-700/50 rounded-full h-2 overflow-hidden">
                <div className="h-full bg-purple-500" style={{ width: `${dashboard.compliance_rate || 0}%` }}></div>
              </div>
            </div>

            {/* Total Incidents */}
            <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-xl p-6 text-white shadow-lg hover:shadow-2xl hover:scale-105 hover:bg-slate-700/50 transition">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-red-300 text-xs font-bold uppercase tracking-wide">Total Incidents</p>
                  <p className="text-5xl font-black mt-2">{dashboard.total_incidents || 0}</p>
                  <p className="text-xs text-red-400 mt-2">📅 Today: {dashboard.incidents_today || 0}</p>
                </div>
                <span className="text-5xl">⚠️</span>
              </div>
            </div>

            {/* Weather Snapshot */}
            <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-xl p-6 text-white shadow-lg hover:shadow-2xl hover:scale-105 hover:bg-slate-700/50 transition">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-cyan-300 text-xs font-bold uppercase tracking-wide">Weather</p>
                  <p className="text-3xl font-black mt-2">
                    {weather?.temp != null ? `${Math.round(weather.temp)}°C` : '--'}
                  </p>
                  <p className="text-xs text-cyan-200 mt-2">
                    {weather?.description || weatherError || 'Loading...'}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    {weather?.location?.name || 'Riyadh'}
                  </p>
                </div>
                <span className="text-5xl">🌤️</span>
              </div>
            </div>
          </div>

          {/* Risk & Alerts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Risk Level */}
            <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-xl p-8 shadow-lg">
              <h3 className="text-xl font-bold text-white mb-8 flex items-center">
                <span className="w-3 h-3 bg-red-500 rounded-full mr-3 animate-pulse"></span>
                Current Risk Level
              </h3>
              <div className="text-center">
                <div className={`inline-block px-10 py-5 rounded-lg text-3xl font-black backdrop-blur-sm ${dashboard.risk_level === 'HIGH' ? 'bg-white/10 text-red-200 border border-white/20' :
                  dashboard.risk_level === 'MEDIUM' ? 'bg-white/10 text-yellow-200 border border-white/20' :
                    'bg-white/10 text-green-200 border border-white/20'
                  }`}>
                  🎯 {dashboard.risk_level || 'UNKNOWN'}
                </div>
              </div>
            </div>

            {/* Active Alerts */}
            <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-xl p-8 shadow-lg">
              <h3 className="text-xl font-bold text-white mb-6 flex items-center">
                <span className="w-3 h-3 bg-blue-500 rounded-full mr-3 animate-pulse"></span>
                Active Alerts ({dashboard.active_alerts?.length || 0})
              </h3>
              {dashboard.active_alerts && dashboard.active_alerts.length > 0 ? (
                <ul className="space-y-3 max-h-48 overflow-y-auto">
                  {dashboard.active_alerts.slice(0, 5).map((alert, idx) => (
                    <li key={idx} className="bg-slate-700/50 backdrop-blur-sm rounded-lg p-4 flex items-start space-x-3 hover:bg-slate-600/50 transition border border-slate-600/30">
                      <span className="text-xl mt-1">🔔</span>
                      <span className="text-sm text-slate-200">{alert}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="bg-green-500/10 backdrop-blur-sm rounded-lg p-6 text-center border border-green-500/30">
                  <p className="text-green-200 font-semibold">✅ No active alerts - All systems normal!</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="bg-gradient-to-r from-slate-800 to-slate-900 border-y border-slate-700 sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex space-x-1 overflow-x-auto">
            {[
              { id: 'dashboard', label: '📊 Dashboard' },
              { id: 'report', label: '📝 Report Incident' },
              { id: 'incidents', label: '📋 Incidents' },
              { id: 'compliance', label: '✅ Compliance' },
              { id: 'risks', label: '⚠️ Risks' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => handleTabChange(tab.id)}
                className={`px-6 py-4 font-bold text-sm whitespace-nowrap border-b-2 transition ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-400 bg-slate-700'
                  : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div className="max-w-7xl mx-auto px-6 py-8 min-h-96">
        {/* Report Tab */}
        {activeTab === 'report' && (
          <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-2xl p-10 shadow-2xl">
            <h2 className="text-4xl font-black text-white mb-10">📝 Report New Incident</h2>
            <form onSubmit={handleReportIncident} className="space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Incident Type */}
                <div>
                  <label className="block text-sm font-bold text-slate-300 mb-3 uppercase tracking-wide">Incident Type</label>
                  <select
                    value={reportForm.incident_type}
                    onChange={(e) => setReportForm({ ...reportForm, incident_type: e.target.value })}
                    className="w-full bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 rounded-lg px-5 py-3 text-white font-semibold focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  >
                    <option value="slip_trip_fall">🚫 Slip, Trip, Fall</option>
                    <option value="equipment_accident">⚙️ Equipment Accident</option>
                    <option value="vehicle_accident">🚗 Vehicle Accident</option>
                    <option value="fire">🔥 Fire</option>
                    <option value="chemical_spill">🧪 Chemical Spill</option>
                  </select>
                </div>

                {/* Severity */}
                <div>
                  <label className="block text-sm font-bold text-slate-300 mb-3 uppercase tracking-wide">Severity Level</label>
                  <select
                    value={reportForm.severity}
                    onChange={(e) => setReportForm({ ...reportForm, severity: e.target.value })}
                    className="w-full bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 rounded-lg px-5 py-3 text-white font-semibold focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  >
                    <option value="minor">⚪ Minor</option>
                    <option value="moderate">🟡 Moderate</option>
                    <option value="major">🟠 Major</option>
                    <option value="critical">🔴 Critical</option>
                    <option value="fatal">⚫ Fatal</option>
                  </select>
                </div>

                {/* Location */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-bold text-slate-300 mb-3 uppercase tracking-wide">📍 Location</label>
                  <input
                    type="text"
                    value={reportForm.location}
                    onChange={(e) => setReportForm({ ...reportForm, location: e.target.value })}
                    placeholder="e.g., Warehouse Section A, Office Building 2"
                    className="w-full bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 rounded-lg px-5 py-3 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  />
                </div>

                {/* Description */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-bold text-slate-300 mb-3 uppercase tracking-wide">📝 Description</label>
                  <textarea
                    value={reportForm.description}
                    onChange={(e) => setReportForm({ ...reportForm, description: e.target.value })}
                    placeholder="Describe the incident in detail... What happened? Who was involved? What was the immediate cause?"
                    rows="6"
                    className="w-full bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 rounded-lg px-5 py-3 text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition resize-none"
                  />
                </div>

                {/* Reporter */}
                <div className="md:col-span-2">
                  <label className="block text-sm font-bold text-slate-300 mb-3 uppercase tracking-wide">👤 Reporter</label>
                  <input
                    type="text"
                    value={reportForm.reporter || user?.email}
                    onChange={(e) => setReportForm({ ...reportForm, reporter: e.target.value })}
                    className="w-full bg-slate-700/50 backdrop-blur-sm border border-slate-600/50 rounded-lg px-5 py-3 text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full bg-blue-600/80 hover:bg-blue-500/80 backdrop-blur-sm text-white font-black py-5 rounded-lg transition shadow-lg hover:shadow-2xl transform hover:scale-[1.02] border border-blue-500/50"
              >
                ✅ SUBMIT INCIDENT REPORT
              </button>
            </form>
          </div>
        )}

        {/* Incidents Tab */}
        {activeTab === 'incidents' && incidents && (
          <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-2xl overflow-hidden shadow-2xl">
            <div className="bg-slate-900/50 backdrop-blur-sm px-10 py-8 border-b border-slate-600/50">
              <h2 className="text-3xl font-black text-white">📊 Incident Statistics</h2>
            </div>
            <div className="p-10">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
                {/* By Type */}
                <div>
                  <h3 className="text-2xl font-bold text-white mb-8 pb-3 border-b border-blue-500/50">By Type</h3>
                  {incidents.by_type ? (
                    <div className="space-y-3">
                      {Object.entries(incidents.by_type).map(([type, count]) => (
                        <div key={type} className="bg-slate-700/40 backdrop-blur-sm rounded-lg p-5 flex justify-between items-center hover:bg-white/10 transition border border-slate-600/30">
                          <span className="text-slate-200 font-bold capitalize">{type.replace(/_/g, ' ')}</span>
                          <span className="bg-white/10 text-blue-200 px-4 py-2 rounded-full font-black text-lg border border-white/20">{count}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-slate-400 text-center py-8">📭 No data available</p>
                  )}
                </div>

                {/* By Severity */}
                <div>
                  <h3 className="text-2xl font-bold text-white mb-8 pb-3 border-b border-red-500/50">By Severity</h3>
                  {incidents.by_severity ? (
                    <div className="space-y-3">
                      {Object.entries(incidents.by_severity).map(([severity, count]) => (
                        <div key={severity} className="bg-slate-700/40 backdrop-blur-sm rounded-lg p-5 flex justify-between items-center hover:bg-white/10 transition border border-slate-600/30">
                          <span className={`px-4 py-2 rounded-lg font-bold text-sm backdrop-blur-sm ${severity === 'minor' ? 'bg-white/10 text-yellow-200 border border-white/20' :
                            severity === 'moderate' ? 'bg-white/10 text-orange-200 border border-white/20' :
                              severity === 'major' ? 'bg-white/10 text-red-200 border border-white/20' :
                                'bg-white/10 text-red-200 border border-white/20'
                            }`}>
                            {severity.toUpperCase()}
                          </span>
                          <span className="bg-white/10 text-red-200 px-4 py-2 rounded-full font-black text-lg border border-white/20">{count}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-slate-400 text-center py-8">📭 No data available</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Compliance Tab */}
        {activeTab === 'compliance' && compliance && (
          <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-2xl overflow-hidden shadow-2xl">
            <div className="bg-white/10 backdrop-blur-sm px-10 py-8 border-b border-white/20">
              <h2 className="text-3xl font-black text-white">✅ Compliance Status</h2>
            </div>
            <div className="p-10">
              {/* Overall Rate */}
              <div className="mb-12 bg-slate-700/40 backdrop-blur-sm rounded-xl p-8 border border-slate-600/30">
                <div className="flex justify-between items-end mb-6">
                  <span className="text-2xl font-bold text-white">Overall Compliance Rate</span>
                  <span className="text-5xl font-black text-purple-400">{compliance.compliance_rate?.toFixed(1) || 0}%</span>
                </div>
                <div className="w-full bg-slate-600/50 rounded-full h-5 overflow-hidden border border-purple-500/30">
                  <div className="h-full bg-purple-500/80" style={{ width: `${compliance.compliance_rate || 0}%` }}></div>
                </div>
              </div>

              {/* Frameworks */}
              {compliance.compliance_by_framework && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {Object.entries(compliance.compliance_by_framework).map(([framework, data]) => (
                    <div key={framework} className="bg-slate-700/40 backdrop-blur-sm rounded-xl p-8 hover:bg-slate-600/40 transition border-l-4 border-purple-500/70 border border-slate-600/30">
                      <h3 className="font-black text-white mb-6 text-lg">{framework}</h3>
                      <div className="space-y-4">
                        <div className="flex justify-between items-center bg-slate-800/50 rounded-lg p-4">
                          <span className="text-green-400 font-bold">✅ Compliant:</span>
                          <span className="font-black text-white text-2xl">{data.compliant}</span>
                        </div>
                        <div className="flex justify-between items-center bg-slate-800/50 rounded-lg p-4">
                          <span className="text-red-400 font-bold">❌ Non-Compliant:</span>
                          <span className="font-black text-white text-2xl">{data.non_compliant}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Risks Tab */}
        {activeTab === 'risks' && risks && (
          <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-600/50 rounded-2xl overflow-hidden shadow-2xl">
            <div className="bg-white/10 backdrop-blur-sm px-10 py-8 border-b border-white/20">
              <h2 className="text-3xl font-black text-white">⚠️ Risk Assessment</h2>
            </div>
            <div className="p-10">
              {risks.high_risk_areas && risks.high_risk_areas.length > 0 ? (
                <div className="space-y-6">
                  {risks.high_risk_areas.map((area, idx) => (
                    <div key={idx} className="bg-slate-700/40 backdrop-blur-sm rounded-xl p-8 hover:bg-slate-600/40 transition border-l-4 border-red-500/70 shadow-lg border border-slate-600/30">
                      <div className="flex justify-between items-start mb-6">
                        <div className="flex-1">
                          <h3 className="font-black text-white text-xl">{area.location || area.area}</h3>
                          <p className="text-slate-300 text-sm mt-2 font-semibold">🎯 {area.hazard || area.risk}</p>
                        </div>
                        <span className={`px-6 py-3 rounded-lg font-black text-sm backdrop-blur-sm ${area.risk_level === 'HIGH' ? 'bg-white/10 text-red-200 border border-white/20' :
                          area.risk_level === 'MEDIUM' ? 'bg-white/10 text-yellow-200 border border-white/20' :
                            'bg-white/10 text-green-200 border border-white/20'
                          }`}>
                          {area.risk_level}
                        </span>
                      </div>
                      {area.mitigation_strategy && (
                        <div className="bg-white/10 backdrop-blur-sm rounded-lg p-5 border-l-4 border-white/20 border border-white/20">
                          <p className="text-blue-200">
                            <span className="font-black text-blue-300">💡 Mitigation Strategy: </span>{area.mitigation_strategy}
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-20 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                  <p className="text-6xl mb-6">✅</p>
                  <p className="text-green-200 text-2xl font-black">No high-risk areas identified!</p>
                  <p className="text-green-300 mt-2">All work areas are within safe parameters.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SafetyManager;
