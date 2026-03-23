import React from "react";

export default function RootLayout({
  sidebar,
  topbar,
  footer,
  children,
  className = "",
  contentClassName = "",
}) {
  return (
    <div className={`root-layout ${className}`.trim()}>
      {sidebar}
      <div className="root-main">
        {topbar ? <header className="glass-topbar">{topbar}</header> : null}
        <main className={`root-content ${contentClassName}`.trim()}>
          {children}
        </main>
        {footer ? (
          <footer className="glass-topbar glass-footer">{footer}</footer>
        ) : null}
      </div>
    </div>
  );
}

RootLayout.displayName = "RootLayout";
