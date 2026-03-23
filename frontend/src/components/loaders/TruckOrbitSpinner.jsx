import React from "react";

export default function TruckOrbitSpinner({
  size = 72,
  text = "Loading...",
  speed = 1.2,
}) {
  const radius = Math.round(size * 0.34);

  return (
    <div className="truck-orbit-wrap">
      <div
        className="truck-orbit"
        style={{
          width: size,
          height: size,
          ["--orbit-radius"]: `${radius}px`,
          ["--orbit-duration"]: `${speed}s`,
        }}
        role="status"
        aria-label="Loading"
      >
        <svg className="truck-orbit-ring" viewBox="0 0 100 100" aria-hidden="true">
          <circle cx="50" cy="50" r="42" />
        </svg>

        <div className="truck-orbit-glow" />

        <div className="truck-orbit-carrier">
          <div className="truck-orbit-truck">
            <svg viewBox="0 0 64 64" aria-hidden="true">
              <path d="M6 18c0-2.2 1.8-4 4-4h24c2.2 0 4 1.8 4 4v22H6V18z" />
              <path d="M38 24h10c1 0 2 .4 2.7 1.2l6.1 6.8c.8.9 1.2 2 1.2 3.2V40H38V24z" />
              <path d="M14.5 46.5a5.5 5.5 0 1 0 0 .1z" />
              <path d="M49.5 46.5a5.5 5.5 0 1 0 0 .1z" />
              <path d="M6 40h52v4H6z" />
            </svg>
          </div>
        </div>
      </div>

      {text ? <div className="truck-orbit-text">{text}</div> : null}
    </div>
  );
}
