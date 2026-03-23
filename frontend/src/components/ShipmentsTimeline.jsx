import React from "react";

const formatTimestamp = (value) => {
  if (!value) return "Unknown time";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Unknown time";
  return date.toLocaleString();
};

const renderDetails = (payload) => {
  if (!payload) return null;
  if (payload.changes) {
    return Object.entries(payload.changes).map(([key, diff]) => (
      <div key={key} className="text-xs text-slate-500">
        {key}: {String(diff?.from ?? "")} {"->"} {String(diff?.to ?? "")}
      </div>
    ));
  }
  if (payload.from || payload.to) {
    return (
      <div className="text-xs text-slate-500">
        {String(payload.from ?? "")} {"->"} {String(payload.to ?? "")}
      </div>
    );
  }
  if (payload.status) {
    return (
      <div className="text-xs text-slate-500">Status: {payload.status}</div>
    );
  }
  return null;
};

export default function ShipmentsTimeline({ shipment, events, loading }) {
  if (!shipment) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-500">
        Select a shipment to view the timeline.
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-800">
            Shipment Timeline #{shipment.id}
          </h2>
          <p className="text-xs text-slate-500">
            {shipment.pickup_location || "Unknown pickup"} {"->"}{" "}
            {shipment.dropoff_location || "Unknown dropoff"}
          </p>
        </div>
      </div>

      {loading ? (
        <p className="text-sm text-slate-500">Loading timeline...</p>
      ) : events.length === 0 ? (
        <p className="text-sm text-slate-500">No timeline events yet.</p>
      ) : (
        <ul className="space-y-3">
          {events.map((event) => (
            <li key={event.id} className="rounded-lg border border-slate-100 bg-slate-50 p-3">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-slate-700">{event.event_type}</span>
                <span className="text-xs text-slate-400">
                  {formatTimestamp(event.created_at)}
                </span>
              </div>
              {renderDetails(event.payload)}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
