import React from "react";
import "./TruckSpinner.css";

export default function TruckSpinner({ size = 100, className = "" }) {
  return (
    <div className={`truck-spinner ${className}`.trim()} role="status" aria-label="Loading">
      <svg
        width={size}
        height={size}
        viewBox="0 0 100 100"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect x="10" y="20" width="40" height="20" fill="#4CAF50" />
        <rect x="60" y="20" width="30" height="20" fill="#2196F3" />
        <circle cx="20" cy="40" r="10" fill="#FFC107" />
        <circle cx="70" cy="40" r="10" fill="#FFC107" />
        <animateTransform
          attributeName="transform"
          type="rotate"
          from="0 50 50"
          to="360 50 50"
          dur="2s"
          repeatCount="indefinite"
        />
      </svg>
    </div>
  );
}
