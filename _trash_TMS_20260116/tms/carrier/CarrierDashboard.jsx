import React, { useState, useEffect } from 'react';

const CarrierDashboard = () => {
    const [availableLoads, setAvailableLoads] = useState([]);
    const [myBids, setMyBids] = useState([]);

    useEffect(() => {
        // Fetch available shipments from the current Load Board
        fetch('/api/load-board/available-loads')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    setAvailableLoads(data.loads);
                }
            });
        // Fetch my bids
        fetch('/api/load-board/my-bids')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    setMyBids(data.bids);
                }
            });
    }, []);

    const placeBid = (loadId, amount) => {
        // Submit a bid via the current Load Board
        fetch('/api/load-board/place-bid', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                load_id: loadId,
                amount: amount,
                carrier_id: 'current_user_id'
            })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Bid submitted successfully');
                }
            });
    };

    return (
        <div>
            <h2>Carrier Dashboard</h2>
            <div>
                <h3>Available Shipments ({availableLoads.length})</h3>
                {availableLoads.map(load => (
                    <div key={load.id}>
                        <p>From: {load.from} To: {load.to}</p>
                        <p>Weight: {load.weight}</p>
                        <button onClick={() => placeBid(load.id, load.estimated_price)}>
                            Submit Bid
                        </button>
                    </div>
                ))}
            </div>
            <div>
                <h3>My Bids ({myBids.length})</h3>
                {myBids.map(bid => (
                    <div key={bid.id}>
                        <p>Shipment: {bid.load_id}</p>
                        <p>My Bid: {bid.amount} SAR</p>
                        <p>Status: {bid.status}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default CarrierDashboard;
