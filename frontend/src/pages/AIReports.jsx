import { useEffect, useState } from "react";
import { API_BASE_URL } from "../config/env";

const API_ROOT = String(API_BASE_URL || "").replace(/\/+$/, "");

const AIReports = () => {
  const [reports, setReports] = useState([]);
  const [type, setType] = useState("Weekly");
  const [loading, setLoading] = useState(false);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_ROOT}/ai/general/reports/${type}`);
      if (!res.ok) throw new Error("Failed to load reports");
      const data = await res.json();
      setReports(data);
    } catch (err) {
      console.error(err);
      setReports([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [type]);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">🤖 AI Reports – {type}</h1>

      <div className="flex gap-2 mb-4">
        {["Daily", "Weekly", "Monthly", "Yearly"].map((t) => (
          <button
            key={t}
            onClick={() => setType(t)}
            className={`px-3 py-1 rounded ${type === t ? "bg-blue-600 text-white" : "bg-gray-200"}`}
          >
            {t}
          </button>
        ))}
      </div>

      {loading ? (
        <p>Loading reports...</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white rounded shadow text-sm">
            <thead className="bg-gray-100">
              <tr>
                <th className="p-2 text-left">Bot Name</th>
                <th className="p-2 text-left">Summary</th>
                <th className="p-2 text-left">Status</th>
                <th className="p-2 text-left">Date</th>
                <th className="p-2 text-left">Details</th>
              </tr>
            </thead>
            <tbody>
              {reports.map((r) => (
                <tr key={r.id} className="border-t">
                  <td className="p-2 font-medium">{r.bot_name}</td>
                  <td className="p-2">{r.summary}</td>
                  <td className={`p-2 ${r.status === "active" ? "text-green-700" : "text-red-600"}`}>
                    {r.status}
                  </td>
                  <td className="p-2 text-gray-500">
                    {new Date(r.date).toLocaleString()}
                  </td>
                  <td className="p-2 whitespace-pre-wrap text-xs">
                    {JSON.stringify(r.details, null, 2)}
                  </td>
                </tr>
              ))}
              {reports.length === 0 && (
                <tr>
                  <td colSpan="5" className="p-4 text-center text-gray-400">
                    No reports found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default AIReports;
