import { useEffect, useState } from "react";

function Safety() {
    const [incidents, setIncidents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchIncidents = async () => {
            try {
                const response = await fetch("http://127.0.0.1:8000/safety/incidents");
                if (response.ok) {
                    const data = await response.json();
                    setIncidents(data);
                } else {
                    console.error("Failed to fetch incidents:", response.status);
                }
            } catch (error) {
                console.error("Error fetching incidents:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchIncidents();
    }, []);

    return (
        <div>
            <h2 className="text-xl font-bold mb-4">🛡️ Safety Incident Reports</h2>
            {loading && <p>Loading...</p>}
            {!loading && incidents.length === 0 && <p>No incidents reported.</p>}
            {!loading && incidents.length > 0 && (
                <div className="space-y-4">
                    {incidents.map((incident) => (
                        <div key={incident.id} className="bg-white p-4 shadow rounded">
                            <h3 className="text-lg font-semibold">{incident.title}</h3>
                            <p className="text-sm text-gray-600">Reported at: {new Date(incident.reported_at).toLocaleString()}</p>
                            <p><strong>Location:</strong> {incident.location}</p>
                            <p><strong>Severity:</strong> {incident.severity}</p>
                            <p><strong>Status:</strong> {incident.resolved ? "✅ Resolved" : "❌ Unresolved"}</p>
                            <p className="mt-2 text-sm">{incident.description}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default Safety;
