// Importing React hooks and necessary libraries
import { useEffect, useState, useRef } from "react";
import axiosClient from "../api/axiosClient";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid, Legend
} from "recharts";
import Navbar from "../components/Navbar"; // Top Navigation Bar
import { API_BASE_URL } from "../config/env";
import { getDocumentLogoDataUrl } from "../utils/documentBranding";
import { exportWorkbookXml, openPrintDocument } from "../utils/exportUtils";

const API_ROOT = String(API_BASE_URL || "").replace(/\/+$/, "");
const FREIGHT_UPDATES_WS_URL = (() => {
  try {
    const parsed = new URL(API_ROOT);
    const protocol = parsed.protocol === "https:" ? "wss" : "ws";
    return `${protocol}://${parsed.host}/ws/freight/updates`;
  } catch {
    return "";
  }
})();

const CustomerDashboard = () => {
  // State declarations
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [range, setRange] = useState("month");
  const [stateFilter, setStateFilter] = useState("");
  const socketRef = useRef(null);
  const [userInput, setUserInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);

  // Fetch data from API on load or when filters change
  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axiosClient.get("/ai/freight/overview", {
          params: {
            range,
            ...(stateFilter ? { state: stateFilter } : {}),
          },
        });
        setData(res.data);
      } catch {
        console.error("Error fetching freight broker data");
      }
      setLoading(false);
    };
    fetchData();
  }, [range, stateFilter]);

  // WebSocket connection for real-time updates
  useEffect(() => {
    if (!FREIGHT_UPDATES_WS_URL) return undefined;

    socketRef.current = new WebSocket(FREIGHT_UPDATES_WS_URL);
    socketRef.current.onmessage = (event) => {
      const liveData = JSON.parse(event.data);
      setData((prev) => prev ? { ...prev, ...liveData } : liveData);
    };
    return () => socketRef.current?.close();
  }, []);

  // Export dashboard data to Excel
  const handleExportExcel = async () => {
    if (!data) return;

    exportWorkbookXml({
      fileName: "Freight_Report.xls",
      sheets: [
        {
          name: "Summary",
          headers: ["Metric", "Value"],
          rows: [
            ["Total Shipments", data.total_shipments],
            ["Avg Revenue per Load", data.avg_revenue_per_load],
            ["Total Revenue", data.total_revenue],
          ],
        },
        {
          name: "Top Carriers",
          headers: Object.keys(data.top_carriers?.[0] || {}),
          rows: (data.top_carriers || []).map((row) => Object.values(row || {})),
        },
        {
          name: "Shipments by State",
          headers: Object.keys(data.shipments_by_state?.[0] || {}),
          rows: (data.shipments_by_state || []).map((row) => Object.values(row || {})),
        },
        {
          name: "Load Trends",
          headers: Object.keys(data.load_trends?.[0] || {}),
          rows: (data.load_trends || []).map((row) => Object.values(row || {})),
        },
      ],
    });
  };

  // Export the dashboard view to PDF
  const handleExportPDF = async () => {
    const logoDataUrl = await getDocumentLogoDataUrl();
    openPrintDocument({
      title: "Freight Report",
      subtitle: `Generated: ${new Date().toLocaleString()}`,
      logoDataUrl,
      sections: [
        {
          type: "list",
          title: "Summary",
          items: [
            `Total Shipments: ${data?.total_shipments ?? 0}`,
            `Avg Revenue per Load: ${data?.avg_revenue_per_load ?? 0}`,
            `Total Revenue: ${data?.total_revenue ?? 0}`,
          ],
        },
        {
          type: "table",
          title: "Top Carriers",
          headers: Object.keys(data?.top_carriers?.[0] || {}),
          rows: (data?.top_carriers || []).map((row) => Object.values(row || {})),
        },
        {
          type: "table",
          title: "Shipments by State",
          headers: Object.keys(data?.shipments_by_state?.[0] || {}),
          rows: (data?.shipments_by_state || []).map((row) => Object.values(row || {})),
        },
        {
          type: "list",
          title: "AI Recommendations",
          items: data?.recommendations || [],
        },
      ],
    });
  };

  // Send a message to the AI assistant
  const handleSendMessage = async () => {
    if (!userInput) return;
    const userMsg = { sender: "You", text: userInput };
    setChatHistory([...chatHistory, userMsg]);
    setUserInput("");
    try {
      const res = await axiosClient.post("/support/ai", { message: userInput });
      const botMsg = { sender: "AI", text: res.data.reply };
      setChatHistory(prev => [...prev, botMsg]);
    } catch {
      const errMsg = { sender: "AI", text: "Error getting response from AI." };
      setChatHistory(prev => [...prev, errMsg]);
    }
  };

  return (
    <div className="bg-gray-100 min-h-screen">
      <Navbar />
      <div className="flex" id="freight-dashboard">
        <div className="flex-1 p-6">
          <h2 className="text-2xl font-bold mb-4">📦 Customer Dashboard + AI Assistant</h2>

          {/* Filters */}
          <div className="flex flex-wrap gap-4 items-center mb-6">
            <div>
              <label className="font-semibold mr-2">Date Range:</label>
              <select
                className="border px-3 py-1 rounded"
                value={range}
                onChange={(e) => setRange(e.target.value)}
              >
                <option value="day">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
              </select>
            </div>

            <div>
              <label className="font-semibold mr-2">State:</label>
              <input
                type="text"
                placeholder="e.g. Texas"
                className="border px-3 py-1 rounded"
                value={stateFilter}
                onChange={(e) => setStateFilter(e.target.value)}
              />
            </div>

            <div className="ml-auto flex gap-3">
              <button onClick={handleExportExcel} className="bg-green-600 text-white px-3 py-1 rounded">Export Excel</button>
              <button onClick={handleExportPDF} className="bg-blue-600 text-white px-3 py-1 rounded">Export PDF</button>
            </div>
          </div>

          {/* Loading Spinner */}
          {loading && <p>Loading data...</p>}

          {/* Dashboard Content */}
          {!loading && data && (
            <div className="space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white shadow p-4 rounded">
                  <h3 className="text-lg font-semibold">Total Shipments</h3>
                  <p className="text-xl">{data.total_shipments}</p>
                </div>
                <div className="bg-white shadow p-4 rounded">
                  <h3 className="text-lg font-semibold">Avg Revenue per Load</h3>
                  <p className="text-xl">${data.avg_revenue_per_load}</p>
                </div>
                <div className="bg-white shadow p-4 rounded">
                  <h3 className="text-lg font-semibold">Total Revenue</h3>
                  <p className="text-xl">${data.total_revenue}</p>
                </div>
              </div>

              {/* Top Carriers List */}
              <div className="bg-white shadow p-4 rounded">
                <h3 className="text-xl font-semibold mb-2">🚛 Top Carriers</h3>
                <ul className="list-disc ml-6">
                  {data.top_carriers.map((carrier, index) => (
                    <li key={index}>
                      {carrier.name} – {carrier.success_rate}% success ({carrier.loads} loads)
                    </li>
                  ))}
                </ul>
              </div>

              {/* Shipments by State - Bar Chart */}
              <div className="bg-white shadow p-4 rounded">
                <h3 className="text-xl font-semibold mb-2">📍 Shipments by State</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={data.shipments_by_state}>
                    <XAxis dataKey="state" />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Load Trends - Line Chart */}
              <div className="bg-white shadow p-4 rounded">
                <h3 className="text-xl font-semibold mb-2">📈 Load Volume Trends</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.load_trends}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="volume" stroke="#8884d8" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* AI Recommendations */}
              <div className="bg-white shadow p-4 rounded">
                <h3 className="text-xl font-semibold mb-2">🤖 AI Recommendations</h3>
                <ul className="list-disc ml-6 text-blue-700">
                  {data.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>

              {/* AI Chat Assistant */}
              <div className="bg-white shadow p-4 rounded">
                <h3 className="text-xl font-semibold mb-2">💬 Customer Support Chat (AI)</h3>
                <div className="h-64 overflow-y-auto border p-3 mb-3 bg-gray-50 rounded">
                  {chatHistory.map((msg, index) => (
                    <p key={index} className={msg.sender === "You" ? "text-right" : "text-left text-blue-600"}>
                      <strong>{msg.sender}:</strong> {msg.text}
                    </p>
                  ))}
                </div>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Ask a question..."
                    className="border px-3 py-2 rounded flex-1"
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                  />
                  <button onClick={handleSendMessage} className="bg-indigo-600 text-white px-4 py-2 rounded">Send</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CustomerDashboard;
