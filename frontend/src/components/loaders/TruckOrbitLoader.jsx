import React from "react";
import { Truck } from "lucide-react";
import "./truck-orbit-loader.css";

export default function TruckOrbitLoader({ text = "Loading user information..." }) {
    return (
        <div className="truckLoaderWrap">
            <div className="truckOrbit">
                <div className="orbitRing" />
                <div className="truckDot">
                    <Truck size={22} />
                </div>
            </div>
            <div className="truckLoaderText">{text}</div>
        </div>
    );
}
