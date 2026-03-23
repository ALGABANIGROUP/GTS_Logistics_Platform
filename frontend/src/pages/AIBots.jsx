import React, { useState, useEffect } from "react";
import AIBotsDashboard from "../components/AIBotsDashboard.jsx";
import AIBotsPanelEnhanced from "../components/AIBotsPanelEnhanced.jsx";

/**
 * AI Bots Page - Integrated System
 *
 * Supports:
 * - New system: bot allocation by subscription and role
 * - Legacy system: show all bots (for compatibility)
 */
export default function AIBots() {
  const [useEnhanced, setUseEnhanced] = useState(true);

  // You can switch between both systems as needed
  useEffect(() => {
    // Check whether a flag exists in localStorage
    const legacy = localStorage.getItem('use_legacy_bots_panel');
    if (legacy === 'true') {
      setUseEnhanced(false);
    }
  }, []);

  // Use new system by default
  return useEnhanced ? <AIBotsPanelEnhanced /> : <AIBotsDashboard />;
}
