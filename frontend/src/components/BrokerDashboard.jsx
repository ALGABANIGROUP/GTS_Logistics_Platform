// frontend/src/components/BrokerDashboard.jsx

import React, { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";

const BrokerDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await axiosClient.get("/dashboard/freight-dashboard/summary");
        setDashboardData(res.data);
      } catch (error) {
        console.error("❌ Failed to fetch dashboard data:", error);
      }
    };

    fetchDashboard();
  }, []);

  if (!dashboardData) return <div>📊 Loading Dashboard...</div>;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div className="bg-white p-4 rounded shadow text-center">
        <h4 className="text-sm text-gray-500">Total Shipments</h4>
        <p className="text-2xl font-bold">{dashboardData.total_shipments}</p>
      </div>
      <div className="bg-yellow-100 p-4 rounded shadow text-center">
        <h4 className="text-sm text-gray-500">On The Way</h4>
        <p className="text-xl font-bold text-yellow-700">{dashboardData.on_the_way}</p>
      </div>
      <div className="bg-red-100 p-4 rounded shadow text-center">
        <h4 className="text-sm text-gray-500">Delayed</h4>
        <p className="text-xl font-bold text-red-700">{dashboardData.delayed_shipments}</p>
      </div>
      <div className="bg-blue-100 p-4 rounded shadow text-center">
        <h4 className="text-sm text-gray-500">Estimated Time</h4>
        <p className="text-xl font-bold text-blue-700">{dashboardData.estimated_time}</p>
      </div>
      <div className="bg-orange-100 p-4 rounded shadow text-center">
        <h4 className="text-sm text-gray-500">Active Alerts</h4>
        <p className="text-xl font-bold text-orange-700">{dashboardData.active_alerts}</p>
      </div>
    </div>
  );
};

export default BrokerDashboard;
