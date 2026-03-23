import { useEffect, useMemo, useState } from "react";
import axiosClient from "../../api/axiosClient";
import RequireAuth from "../../components/RequireAuth";

export default function TMSDashboard() {
    return (
        <RequireAuth requiredRole="manager">
            <div className="space-y-6">
                <h1 className="text-xl font-semibold text-white">TMS Dashboard</h1>
                <StatusCard />
                <BotsCard />
                <ActionsCard />
            </div>
        </RequireAuth>
    );
}

function StatusCard() {
    const [status, setStatus] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        let mounted = true;
        axiosClient
            .get("/api/v1/tms/status")
            .then((res) => mounted && setStatus(res.data))
            .catch((err) => mounted && setError(err?.response?.data || { error: "request_failed" }));
        return () => {
            mounted = false;
        };
    }, []);

    return (
        <div className="glass-panel p-4 border border-white/10">
            <div className="text-sm text-slate-200">System Status</div>
            <pre className="mt-2 text-xs text-slate-300 overflow-auto">
                {JSON.stringify(status || error || {}, null, 2)}
            </pre>
        </div>
    );
}

function BotsCard() {
    const [bots, setBots] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        let mounted = true;
        axiosClient
            .get("/api/v1/tms/bots/available")
            .then((res) => mounted && setBots(res.data?.bots || []))
            .catch((err) => mounted && setError(err?.response?.data || { error: "request_failed" }));
        return () => {
            mounted = false;
        };
    }, []);

    return (
        <div className="glass-panel p-4 border border-white/10">
            <div className="text-sm text-slate-200">Available Bots</div>
            {error ? (
                <pre className="mt-2 text-xs text-rose-300">{JSON.stringify(error, null, 2)}</pre>
            ) : (
                <ul className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2">
                    {bots.map((b) => (
                        <li key={b.name} className="border border-white/10 rounded px-3 py-2 text-sm text-slate-200">
                            <div className="font-medium">{b.display}</div>
                            <div className="text-xs text-slate-400">{b.name}</div>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

function ActionsCard() {
    const [shipmentId, setShipmentId] = useState("S12345");
    const [action, setAction] = useState("create");
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const actions = useMemo(
        () => [
            { key: "create", label: "Create" },
            { key: "dispatch", label: "Dispatch" },
            { key: "track", label: "Track" },
            { key: "close", label: "Close" },
        ],
        []
    );

    const runLifecycle = async () => {
        setError(null);
        setResult(null);
        try {
            const res = await axiosClient.post("/api/v1/tms/shipments/lifecycle", {
                shipment_id: shipmentId,
                action,
                data: {},
            });
            setResult(res.data);
        } catch (e) {
            setError(e?.response?.data || { error: "request_failed" });
        }
    };

    const runExecute = async () => {
        setError(null);
        setResult(null);
        const mapping = {
            create: { bot: "freight_broker", action: "create_shipment" },
            dispatch: { bot: "freight_broker", action: "dispatch" },
            track: { bot: "customer_service", action: "track_shipment" },
            close: { bot: "documents_manager", action: "close_shipment" },
        };
        try {
            const { bot, action: a } = mapping[action];
            const res = await axiosClient.post("/api/v1/tms/execute", {
                bot,
                action: a,
                payload: { shipment_id: shipmentId },
            });
            setResult(res.data);
        } catch (e) {
            setError(e?.response?.data || { error: "request_failed" });
        }
    };

    return (
        <div className="glass-panel p-4 border border-white/10">
            <div className="text-sm text-slate-200">Quick Actions</div>
            <div className="mt-3 flex flex-wrap items-end gap-3">
                <div>
                    <label className="block text-xs text-slate-400">Shipment ID</label>
                    <input
                        className="px-2 py-1 rounded bg-slate-900 text-slate-100 border border-white/10"
                        value={shipmentId}
                        onChange={(e) => setShipmentId(e.target.value)}
                    />
                </div>
                <div>
                    <label className="block text-xs text-slate-400">Action</label>
                    <select
                        className="px-2 py-1 rounded bg-slate-900 text-slate-100 border border-white/10"
                        value={action}
                        onChange={(e) => setAction(e.target.value)}
                    >
                        {actions.map((a) => (
                            <option key={a.key} value={a.key}>
                                {a.label}
                            </option>
                        ))}
                    </select>
                </div>
                <button onClick={runLifecycle} className="px-3 py-1 rounded bg-blue-600 text-white text-sm">
                    Run Lifecycle
                </button>
                <button onClick={runExecute} className="px-3 py-1 rounded bg-emerald-600 text-white text-sm">
                    Execute via TMS
                </button>
            </div>
            <div className="mt-3">
                {error ? (
                    <pre className="text-xs text-rose-300 overflow-auto">{JSON.stringify(error, null, 2)}</pre>
                ) : result ? (
                    <pre className="text-xs text-slate-300 overflow-auto">{JSON.stringify(result, null, 2)}</pre>
                ) : (
                    <div className="text-xs text-slate-400">Pick an action to run</div>
                )}
            </div>
        </div>
    );
}
