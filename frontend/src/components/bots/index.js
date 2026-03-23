/**
 * Bot Control Components - Index
 * Export all bot control interface components
 */

// Main interface
export { default as BotControlInterface } from "./BotControlInterface";

// Header and navigation
export { default as BotHeader } from "./BotHeader";
export { default as BotTabs } from "./BotTabs";
export { default as StatusBar } from "./StatusBar";

// Tab components
export { default as DashboardTab } from "./tabs/DashboardTab";
export { default as ExecuteTab } from "./tabs/ExecuteTab";
export { default as ScheduleTab } from "./tabs/ScheduleTab";
export { default as AnalyticsTab } from "./tabs/AnalyticsTab";
export { default as ConfigTab } from "./tabs/ConfigTab";
export { default as LogsTab } from "./tabs/LogsTab";

// Specialized Bot Interfaces
export { default as MapleLoadCanadaInterface } from "./MapleLoadCanadaInterface";
export { default as ExecutiveIntelligenceInterface } from "./ExecutiveIntelligenceInterface";
export { default as MaintenanceDevInterface } from "./MaintenanceDevInterface";
export { default as FreightBookingsInterface } from "./FreightBookingsInterface";
export { default as FreightBrokerDashboard } from "./FreightBrokerDashboard";

// Specialized Bot Control Panels (New Architecture)
export { default as FreightBrokerControlPanel } from "./FreightBrokerControlPanel";
export { default as ExecutiveIntelligenceControlPanel } from "./ExecutiveIntelligenceControlPanel";
export { default as DevMaintenanceControlPanel } from "./DevMaintenanceControlPanel";
export { default as MapleLoadControlPanel } from "./MapleLoadControlPanel";
export { default as FreightBookingsControlPanel } from "./FreightBookingsControlPanel";
export { default as DataCoordinatorControlPanel } from "./DataCoordinatorControlPanel";
export { default as FinanceControlPanel } from "./FinanceControlPanel";
export { default as SecurityControlPanel } from "./SecurityControlPanel";
export { default as SalesControlPanel } from "./SalesControlPanel";
export { default as LegalControlPanel } from "./LegalControlPanel";
export { default as PartnerManagementControlPanel } from "./PartnerManagementControlPanel";
export { default as GeneralManagerControlPanel } from "./GeneralManagerControlPanel";
