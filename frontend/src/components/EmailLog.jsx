import { useEffect, useState } from "react";
import { API_BASE_URL } from "../config/env";

const API_ROOT = String(API_BASE_URL || "").replace(/\/+$/, "");

const EmailLog = () => {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch(`${API_ROOT}/emails/logs`)
      .then((res) => res.json())
      .then((data) => setLogs(data));
  }, []);

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">📨 Email Log</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full table-auto border text-sm">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-2 py-1 border">Bot</th>
              <th className="px-2 py-1 border">From</th>
              <th className="px-2 py-1 border">Subject</th>
              <th className="px-2 py-1 border">Reply</th>
              <th className="px-2 py-1 border">Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log, i) => (
              <tr key={i}>
                <td className="border px-2 py-1 text-blue-700 font-semibold">{log.bot}</td>
                <td className="border px-2 py-1">{log.from}</td>
                <td className="border px-2 py-1">{log.subject}</td>
                <td className="border px-2 py-1 text-green-700">{log.reply?.slice(0, 60)}...</td>
                <td className="border px-2 py-1 text-gray-500">{log.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default EmailLog;
