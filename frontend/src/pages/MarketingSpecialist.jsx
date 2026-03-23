
import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";
import {
  PieChart, Pie, Cell, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid, Legend, ResponsiveContainer, BarChart, Bar
} from "recharts";

// Try to use Card if available, else fallback to div
let Card = ({ children, className = "" }) => <div className={`bg-white shadow p-4 rounded ${className}`}>{children}</div>;
let CardHeader = ({ children }) => <div className="mb-2">{children}</div>;
let CardTitle = ({ children, className = "" }) => <h3 className={`text-xl font-semibold ${className}`}>{children}</h3>;
let CardContent = ({ children }) => <div>{children}</div>;
try {
  // eslint-disable-next-line
  Card = require("../components/ui/card").Card || Card;
  CardHeader = require("../components/ui/card").CardHeader || CardHeader;
  CardTitle = require("../components/ui/card").CardTitle || CardTitle;
  CardContent = require("../components/ui/card").CardContent || CardContent;
} catch { }

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff8042", "#8dd1e1"];

const MarketingSpecialist = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await axiosClient.get("/ai/marketing/overview");
        setData(res.data);
        setError(null);
      } catch (err) {
        setError("Failed to load marketing data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <h2 className="text-2xl font-bold mb-4">📢 AI Marketing Specialist</h2>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, index) => (
              <div key={index} className="h-24 w-full bg-gray-200 animate-pulse rounded" />
            ))}
          </div>
          <div className="h-64 w-full bg-gray-200 animate-pulse rounded" />
          <div className="h-64 w-full bg-gray-200 animate-pulse rounded" />
          <div className="h-32 w-full bg-gray-200 animate-pulse rounded" />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <h2 className="text-2xl font-bold mb-4">📢 AI Marketing Specialist</h2>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded" role="alert">
          <strong className="font-bold">Error:</strong>
          <span className="block sm:inline"> {error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h2 className="text-2xl font-bold mb-4">📢 AI Marketing Specialist</h2>

      {data && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Campaigns</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{data.campaigns}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Leads</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{data.leads.toLocaleString()}</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Conversion Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">{data.conversion_rate}%</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Budget Spent</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">${data.budget.toLocaleString()}</p>
              </CardContent>
            </Card>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Pie Chart */}
            <Card>
              <CardHeader>
                <CardTitle>🎯 Campaign Type Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={data.campaign_types} dataKey="value" nameKey="type" cx="50%" cy="50%" outerRadius={100} label>
                      {data.campaign_types.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Line Chart */}
            <Card>
              <CardHeader>
                <CardTitle>📈 Campaign Performance Over Time</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={data.performance}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="clicks" stroke="#8884d8" name="Clicks" />
                    <Line type="monotone" dataKey="conversions" stroke="#82ca9d" name="Conversions" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Bar Chart for Campaign Comparison */}
          <Card>
            <CardHeader>
              <CardTitle>📊 Campaign Leads by Type</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={data.campaign_types}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="value" fill="#8884d8" name="Leads Generated" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* AI Suggestions */}
          <Card>
            <CardHeader>
              <CardTitle>🤖 AI Recommendations</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2">
                {data.recommendations.map((item, index) => (
                  <li key={index} className="flex items-start">
                    <span className="inline-block w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3"></span>
                    <span className="text-gray-700">{item}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

        </div>
      )}
    </div>
  );
};

export default MarketingSpecialist;
