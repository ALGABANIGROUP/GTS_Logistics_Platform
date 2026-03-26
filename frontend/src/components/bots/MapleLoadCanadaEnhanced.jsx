import React, { useEffect, useMemo, useState } from "react";
import { RefreshCw, PlusCircle, Search, Database } from "lucide-react";
import axiosClient from "../../api/axiosClient";
import "./MapleLoadCanadaControl.css";

const defaultSearch = {
    origin: "",
    destination: "",
    weight: "",
    commodity: "",
    date_from: "",
    date_to: "",
    max_rate: "",
};

const defaultPost = {
    origin: "",
    destination: "",
    equipment: "Van",
    weight: "",
    rate: "",
};

const MapleLoadCanadaEnhanced = () => {
    const botEndpoint = "/api/v1/ai/bots/mapleload-canada";
    const [botStatus, setBotStatus] = useState(null);
    const [searchParams, setSearchParams] = useState(defaultSearch);
    const [postData, setPostData] = useState(defaultPost);
    const [loads, setLoads] = useState([]);
    const [submitting, setSubmitting] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [message, setMessage] = useState("");

    const fetchStatus = async () => {
        const response = await axiosClient.get(`${botEndpoint}/status`);
        setBotStatus(response?.data?.data || response?.data || null);
    };

    const searchFreight = async (params = searchParams, background = false) => {
        if (!background) setLoading(true);
        setError("");
        try {
            const response = await axiosClient.post(`${botEndpoint}/search-freight`, params);
            setLoads(Array.isArray(response?.data?.loads) ? response.data.loads : []);
        } catch (err) {
            setLoads([]);
            setError(err?.response?.data?.detail || err?.message || "Failed to load Canadian freight data.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        Promise.all([fetchStatus(), searchFreight(defaultSearch)])
            .catch((err) => {
                setError(err?.response?.data?.detail || err?.message || "Failed to initialize MapleLoad Canada.");
                setLoading(false);
            });
    }, []);

    const handlePostLoad = async () => {
        setSubmitting(true);
        setMessage("");
        setError("");
        try {
            const response = await axiosClient.post("/truckerpath/post-load", {
                shipment_info: {
                    origin: postData.origin,
                    destination: postData.destination,
                    equipment: postData.equipment,
                    weight: postData.weight,
                    rate: postData.rate,
                    currency: "CAD",
                },
                contact_info: {},
            });
            if (!response?.data?.ok) {
                throw new Error(response?.data?.detail || "Failed to post load");
            }
            setMessage("Load submitted to the configured freight channel.");
            setPostData(defaultPost);
        } catch (err) {
            setError(err?.response?.data?.detail || err?.message || "Failed to post load.");
        } finally {
            setSubmitting(false);
        }
    };

    const summary = useMemo(() => {
        const total = loads.length;
        const avgRate = total
            ? Math.round(loads.reduce((sum, load) => sum + Number(String(load.rate || 0).replace(/[^0-9.]/g, "") || 0), 0) / total)
            : 0;
        return { total, avgRate };
    }, [loads]);

    return (
        <div className="mapleload-canada-control">
            <div className="control-header mapleload-unified">
                <div className="header-main">
                    <div className="header-title">
                        <span className="header-icon">
                            <img src="/canada-maple-leaf.svg" alt="Canada Maple Leaf" style={{ width: "50px", height: "50px" }} />
                        </span>
                        <div>
                            <h1>MapleLoad Canada</h1>
                            <p className="bot-description">Live Canadian freight sourcing and posting workspace</p>
                            <div className="version-badge">
                                {botStatus?.display_name || "MapleLoad Canada"} {botStatus?.version ? `v${botStatus.version}` : ""}
                            </div>
                        </div>
                    </div>
                    <button className="execute-btn orange" onClick={() => searchFreight(searchParams, true)} disabled={loading}>
                        <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
                        Refresh
                    </button>
                </div>
            </div>

            <main className="control-content space-y-6">
                {error ? <div className="result-panel error">{error}</div> : null}
                {message ? <div className="result-panel success">{message}</div> : null}

                <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div className="result-panel">
                        <div className="content-header">
                            <h2><Search size={18} /> Search Canadian Freight</h2>
                            <p>Uses the mounted MapleLoad Canada dashboard endpoint.</p>
                        </div>
                        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                            <input value={searchParams.origin} onChange={(e) => setSearchParams((prev) => ({ ...prev, origin: e.target.value }))} placeholder="Origin" />
                            <input value={searchParams.destination} onChange={(e) => setSearchParams((prev) => ({ ...prev, destination: e.target.value }))} placeholder="Destination" />
                            <input value={searchParams.weight} onChange={(e) => setSearchParams((prev) => ({ ...prev, weight: e.target.value }))} placeholder="Weight" />
                            <input value={searchParams.commodity} onChange={(e) => setSearchParams((prev) => ({ ...prev, commodity: e.target.value }))} placeholder="Commodity" />
                        </div>
                        <button className="execute-btn blue mt-4" onClick={() => searchFreight(searchParams)} disabled={loading}>
                            {loading ? "Searching..." : "Search Freight"}
                        </button>
                    </div>

                    <div className="result-panel">
                        <div className="content-header">
                            <h2><PlusCircle size={18} /> Post Load</h2>
                            <p>Posts through the configured freight board integration.</p>
                        </div>
                        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
                            <input value={postData.origin} onChange={(e) => setPostData((prev) => ({ ...prev, origin: e.target.value }))} placeholder="Origin" />
                            <input value={postData.destination} onChange={(e) => setPostData((prev) => ({ ...prev, destination: e.target.value }))} placeholder="Destination" />
                            <select value={postData.equipment} onChange={(e) => setPostData((prev) => ({ ...prev, equipment: e.target.value }))}>
                                <option value="Van">Van</option>
                                <option value="Flatbed">Flatbed</option>
                                <option value="Reefer">Reefer</option>
                                <option value="Step Deck">Step Deck</option>
                            </select>
                            <input value={postData.weight} onChange={(e) => setPostData((prev) => ({ ...prev, weight: e.target.value }))} placeholder="Weight" />
                            <input value={postData.rate} onChange={(e) => setPostData((prev) => ({ ...prev, rate: e.target.value }))} placeholder="Rate (CAD)" />
                        </div>
                        <button className="execute-btn green mt-4" onClick={handlePostLoad} disabled={submitting}>
                            {submitting ? "Posting..." : "Post Load"}
                        </button>
                    </div>
                </div>

                <div className="result-panel">
                    <div className="content-header">
                        <h2><Database size={18} /> Marketplace Snapshot</h2>
                        <p>{summary.total} loads returned{summary.total ? `, average rate CAD ${summary.avgRate}` : ""}</p>
                    </div>
                    {loading ? (
                        <div className="text-slate-300">Loading Canadian freight...</div>
                    ) : loads.length === 0 ? (
                        <div className="text-slate-400">No live Canadian loads matched the current filters.</div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full min-w-[720px]">
                                <thead>
                                    <tr>
                                        <th>Origin</th>
                                        <th>Destination</th>
                                        <th>Weight</th>
                                        <th>Commodity</th>
                                        <th>Rate</th>
                                        <th>Posted By</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {loads.map((load) => (
                                        <tr key={load.id}>
                                            <td>{load.origin}</td>
                                            <td>{load.destination}</td>
                                            <td>{load.weight || "-"}</td>
                                            <td>{load.commodity || "-"}</td>
                                            <td>{load.rate || "-"}</td>
                                            <td>{load.posted_by || "MapleLoad Canada"}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
};

export default MapleLoadCanadaEnhanced;
