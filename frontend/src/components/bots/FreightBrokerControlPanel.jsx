import React, { useState, useEffect } from "react";

const FreightBrokerControlPanel = () => {
    const [loads, setLoads] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchLoads = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch("/api/v1/freight/canadian-loads?active=true");
            if (!response.ok) {
                if (response.status === 503) {
                    throw new Error("Freight service temporarily unavailable");
                }
                throw new Error("Failed to fetch loads");
            }

            const data = await response.json();
            setLoads(data.loads || []);
        } catch (err) {
            setError(err.message);
            setLoads([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLoads();
    }, []);

    if (loading) {
        return <div>Loading freight loads...</div>;
    }

    if (error) {
        return (
            <div>
                Error: {error} <button onClick={fetchLoads}>Retry</button>
            </div>
        );
    }

    return (
        <div className="freight-broker-panel">
            <h2>Active Canadian Loads</h2>
            <div className="loads-list">
                {loads.map((load) => (
                    <div key={load.id} className="load-card">
                        <h3>
                            {load.origin} to {load.destination}
                        </h3>
                        <p>Rate: ${load.rate}</p>
                        <p>Distance: {load.distance} km</p>
                        <button>Book Now</button>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default FreightBrokerControlPanel;
