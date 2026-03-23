import React, { useEffect, useMemo, useState } from "react";
import { FaBalanceScale, FaFileContract, FaRobot, FaShieldAlt } from "react-icons/fa";
import { listCarriers } from "../../services/carriersApi";
import legalConsultantApi from "../../services/legalConsultantApi";

const panelStyle = {
    background: "rgba(15, 23, 42, 0.72)",
    border: "1px solid rgba(148, 163, 184, 0.18)",
    borderRadius: "18px",
    backdropFilter: "blur(16px)",
};

const fieldStyle = {
    width: "100%",
    padding: "12px 14px",
    background: "#0f172a",
    border: "1px solid #334155",
    borderRadius: "10px",
    color: "white",
    fontSize: "14px",
};

const labelStyle = {
    display: "block",
    marginBottom: "8px",
    color: "#cbd5e1",
    fontSize: "13px",
};

const normalizeReviewSections = (review) => {
    if (!review || typeof review !== "object") return [];

    return Object.entries(review)
        .filter(([, value]) => value !== null && value !== undefined && value !== "")
        .map(([key, value]) => ({ key, value }));
};

const CarriersContracts = () => {
    const [carriers, setCarriers] = useState([]);
    const [selectedCarrierId, setSelectedCarrierId] = useState("");
    const [contractType, setContractType] = useState("carrier_service_agreement");
    const [serviceScope, setServiceScope] = useState("Dedicated regional freight coverage with SLA commitments.");
    const [paymentTerms, setPaymentTerms] = useState("Net 30 with detention and fuel surcharge review.");
    const [notes, setNotes] = useState("Review indemnity, liability caps, and termination wording.");
    const [review, setReview] = useState(null);
    const [legalStats, setLegalStats] = useState({});
    const [loading, setLoading] = useState(true);
    const [reviewing, setReviewing] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                const [carrierResponse, statsResponse] = await Promise.all([
                    listCarriers({ per_page: 50 }),
                    legalConsultantApi.getLegalStats().catch(() => ({})),
                ]);
                setCarriers(carrierResponse.items || []);
                setLegalStats(statsResponse || {});
            } catch (err) {
                console.error("Failed to load carrier contracts workspace:", err);
                setError("Failed to load carrier and legal data.");
            } finally {
                setLoading(false);
            }
        };

        load();
    }, []);

    const selectedCarrier = useMemo(
        () => carriers.find((carrier) => String(carrier.id) === String(selectedCarrierId)) || null,
        [carriers, selectedCarrierId]
    );

    const reviewSections = useMemo(() => normalizeReviewSections(review), [review]);

    const handleReview = async () => {
        if (!selectedCarrier) {
            setError("Select a carrier before requesting a legal review.");
            return;
        }

        try {
            setReviewing(true);
            setError("");
            const response = await legalConsultantApi.reviewCarrierContract({
                carrier: selectedCarrier,
                contractType,
                serviceScope,
                paymentTerms,
                notes,
            });
            setReview(response);
        } catch (err) {
            console.error("Failed to review contract:", err);
            setError("The AI Legal Consultant review request failed.");
        } finally {
            setReviewing(false);
        }
    };

    if (loading) {
        return <div style={{ padding: "32px", color: "#cbd5e1" }}>Loading contracts workspace...</div>;
    }

    return (
        <div style={{ padding: "24px", color: "white" }}>
            <div style={{ marginBottom: "24px" }}>
                <h1 style={{ fontSize: "28px", margin: 0 }}>Carrier Contracts</h1>
                <p style={{ color: "#94a3b8", marginTop: "8px" }}>
                    Contract review and risk analysis are handled by the AI Legal Consultant.
                </p>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, minmax(0, 1fr))", gap: "16px", marginBottom: "24px" }}>
                <div style={{ ...panelStyle, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>Carriers Available</div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px" }}>
                        <span style={{ fontSize: "28px", fontWeight: 700 }}>{carriers.length}</span>
                        <FaFileContract style={{ color: "#10b981", fontSize: "24px" }} />
                    </div>
                </div>
                <div style={{ ...panelStyle, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>Verified Carriers</div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px" }}>
                        <span style={{ fontSize: "28px", fontWeight: 700 }}>{carriers.filter((item) => item.is_verified).length}</span>
                        <FaShieldAlt style={{ color: "#38bdf8", fontSize: "24px" }} />
                    </div>
                </div>
                <div style={{ ...panelStyle, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>Legal Reviews</div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px" }}>
                        <span style={{ fontSize: "28px", fontWeight: 700 }}>{legalStats.total_reviews ?? legalStats.total ?? 0}</span>
                        <FaRobot style={{ color: "#f59e0b", fontSize: "24px" }} />
                    </div>
                </div>
                <div style={{ ...panelStyle, padding: "18px" }}>
                    <div style={{ color: "#94a3b8", fontSize: "12px" }}>Compliance Checks</div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "10px" }}>
                        <span style={{ fontSize: "28px", fontWeight: 700 }}>{legalStats.compliance_checks ?? 0}</span>
                        <FaBalanceScale style={{ color: "#fb7185", fontSize: "24px" }} />
                    </div>
                </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: "24px" }}>
                <div style={{ ...panelStyle, padding: "22px" }}>
                    <h2 style={{ marginTop: 0, marginBottom: "18px", fontSize: "18px" }}>Draft Review Request</h2>

                    <div style={{ marginBottom: "16px" }}>
                        <label style={labelStyle}>Carrier</label>
                        <select value={selectedCarrierId} onChange={(e) => setSelectedCarrierId(e.target.value)} style={fieldStyle}>
                            <option value="">Select a carrier</option>
                            {carriers.map((carrier) => (
                                <option key={carrier.id} value={carrier.id}>
                                    {carrier.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div style={{ marginBottom: "16px" }}>
                        <label style={labelStyle}>Contract Type</label>
                        <select value={contractType} onChange={(e) => setContractType(e.target.value)} style={fieldStyle}>
                            <option value="carrier_service_agreement">Carrier Service Agreement</option>
                            <option value="lane_commitment">Lane Commitment</option>
                            <option value="broker_carrier_addendum">Broker Carrier Addendum</option>
                        </select>
                    </div>

                    <div style={{ marginBottom: "16px" }}>
                        <label style={labelStyle}>Service Scope</label>
                        <textarea value={serviceScope} onChange={(e) => setServiceScope(e.target.value)} rows={4} style={fieldStyle} />
                    </div>

                    <div style={{ marginBottom: "16px" }}>
                        <label style={labelStyle}>Payment Terms</label>
                        <textarea value={paymentTerms} onChange={(e) => setPaymentTerms(e.target.value)} rows={3} style={fieldStyle} />
                    </div>

                    <div style={{ marginBottom: "16px" }}>
                        <label style={labelStyle}>Review Focus</label>
                        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={4} style={fieldStyle} />
                    </div>

                    {error ? (
                        <div style={{ marginBottom: "14px", color: "#fca5a5", background: "rgba(127, 29, 29, 0.35)", border: "1px solid rgba(248, 113, 113, 0.3)", padding: "12px", borderRadius: "12px" }}>
                            {error}
                        </div>
                    ) : null}

                    <button
                        onClick={handleReview}
                        disabled={reviewing}
                        style={{
                            padding: "12px 18px",
                            background: reviewing ? "#475569" : "#f59e0b",
                            border: "none",
                            borderRadius: "10px",
                            color: "white",
                            cursor: reviewing ? "default" : "pointer",
                            fontWeight: 600,
                        }}
                    >
                        {reviewing ? "Reviewing with AI Legal Consultant..." : "Run Legal Review"}
                    </button>
                </div>

                <div style={{ ...panelStyle, padding: "22px" }}>
                    <h2 style={{ marginTop: 0, marginBottom: "18px", fontSize: "18px" }}>AI Legal Consultant Output</h2>
                    {reviewSections.length === 0 ? (
                        <div style={{ color: "#94a3b8", lineHeight: 1.6 }}>
                            Select a carrier and send the draft to the AI Legal Consultant. The review summary, risk notes, and compliance guidance will appear here.
                        </div>
                    ) : (
                        <div style={{ display: "grid", gap: "14px" }}>
                            {reviewSections.map((section) => (
                                <div key={section.key} style={{ background: "rgba(15, 23, 42, 0.92)", border: "1px solid rgba(51, 65, 85, 1)", borderRadius: "14px", padding: "14px" }}>
                                    <div style={{ color: "#f8fafc", fontWeight: 700, marginBottom: "8px", textTransform: "capitalize" }}>
                                        {section.key.replace(/_/g, " ")}
                                    </div>
                                    <div style={{ color: "#cbd5e1", whiteSpace: "pre-wrap", lineHeight: 1.6, fontSize: "14px" }}>
                                        {typeof section.value === "object" ? JSON.stringify(section.value, null, 2) : String(section.value)}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default CarriersContracts;
