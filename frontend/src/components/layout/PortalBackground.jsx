import React from "react";
import bg from "../../assets/PortalLanding-DLRewip6.png";
import "./PortalBackground.css";

export default function PortalBackground({ children }) {
  return (
    <div
      className="portal-background"
      style={{
        backgroundImage: `url(${bg})`,
      }}
    >
      <div className="portal-background__overlay" />
      <div className="portal-background__content">{children}</div>
    </div>
  );
}
