/**
 * BOT ROUTING IMPLEMENTATION GUIDE
 * Intelligent bot routing map
 *
 * This document outlines the complete routing structure for all AI bots in the GTS system.
 * 
 * ================================================================
 * ROUTING STRUCTURE
 * ================================================================
 * 
 * Base URL: /ai-bots
 * Hub Dashboard: /ai-bots/hub
 * 
 * All bot routes follow the pattern: /ai-bots/{bot-name}
 * 
 * ================================================================
 * PHASE 1: CORE BOTS ( ACTIVE)
 * ================================================================
 * 
 * 1. General Manager Bot
 *    Path: /ai-bots/general-manager
 *    Component: AIGeneralManagerControlPage
 *    Panel: GeneralManagerControlPanel
 *    Status:  ACTIVE
 *    Description: Executive oversight and strategic reporting
 * 
 * 2. Freight Broker Bot
 *    Path: /ai-bots/freight-broker (legacy)  /ai-bots/freight-broker-control (new)
 *    Component: AIFreightBroker or FreightBrokerControlPanel
 *    Panel: FreightBrokerControlPanel
 *    Status:  ACTIVE
 *    Description: Core freight brokerage and load management
 * 
 * 3. MapleLoad Canada Bot
 *    Path: /ai-bots/mapleload-canada
 *    Component: AIMapleLoadCanadaBot or MapleLoadControlPanel
 *    Panel: MapleLoadControlPanel
 *    Status:  ACTIVE
 *    Description: Canadian freight operations and compliance
 * 
 * 4. Executive Intelligence Bot
 *    Path: /ai-bots/executive-intelligence
 *    Component: AIExecutiveIntelligenceBot or ExecutiveIntelligenceControlPanel
 *    Panel: ExecutiveIntelligenceControlPanel
 *    Status:  ACTIVE
 *    Description: Executive dashboards and business intelligence
 * 
 * ================================================================
 * PHASE 2: OPERATIONAL BOTS ( IMPLEMENTATION)
 * ================================================================
 * 
 * 5. System Architect Bot ( IN DEVELOPMENT)
 *    Path: /ai-bots/system-architect
 *    Component: SystemArchitectControlPage (TO CREATE)
 *    Panel: SystemArchitectControlPanel (TO CREATE)
 *    Status:  PLANNED
 *    Description: Infrastructure and system design
 * 
 * 6. Data Coordinator Bot
 *    Path: /ai-bots/data-coordinator
 *    Component: AIDataCoordinatorControlPage
 *    Panel: DataCoordinatorControlPanel
 *    Status:  ACTIVE
 *    Description: Data pipeline, ETL, and quality management
 * 
 * 7. Freight Bookings Bot
 *    Path: /ai-bots/freight-bookings
 *    Component: AIFreightBookingsControlPage
 *    Panel: FreightBookingsControlPanel
 *    Status:  ACTIVE
 *    Description: Booking management and reservation system
 * 
 * 8. Finance Intelligence Bot
 *    Path: /ai-bots/finance-intelligence
 *    Component: AIFinanceControlPage
 *    Panel: FinanceControlPanel
 *    Status:  ACTIVE
 *    Description: Financial management and business operations
 * 
 * ================================================================
 * PHASE 3: ADMINISTRATIVE BOTS ( IN PROGRESS)
 * ================================================================
 * 
 * 9. Security Question Bot ( IN DEVELOPMENT)
 *    Path: /ai-bots/security-question
 *    Component: AISecurityControlPage
 *    Panel: SecurityControlPanel
 *    Status:  ACTIVE (BACKEND NOT ACTIVE)
 *    Description: Security management and access control
 * 
 * 10. Sales Intelligence Bot
 *     Path: /ai-bots/sales-intelligence
 *     Component: AISalesControlPage
 *     Panel: SalesControlPanel
 *     Status:  ACTIVE
 *     Description: Sales pipeline and CRM management
 * 
 * 11. Legal Counsel Bot
 *     Path: /ai-bots/legal-counsel
 *     Component: AILegalControlPage
 *     Panel: LegalControlPanel
 *     Status:  ACTIVE
 *     Description: Legal compliance and contract management
 * 
 * 12. Safety Manager Bot ( IN DEVELOPMENT)
 *     Path: /ai-bots/safety-manager
 *     Component: SafetyManagerControlPage (TO CREATE)
 *     Panel: SafetyManagerControlPanel (TO CREATE)
 *     Status:  PLANNED
 *     Description: Safety and incident management
 * 
 * ================================================================
 * PHASE 4: SUPPORT BOTS ( PLANNED)
 * ================================================================
 * 
 * 13. Partner Management Bot
 *     Path: /ai-bots/partner-management
 *     Component: AIPartnerManagementControlPage
 *     Panel: PartnerManagementControlPanel
 *     Status:  ACTIVE (BACKEND NOT ACTIVE)
 *     Description: Carrier partnerships and relationships
 * 
 * 14. Operations Management Bot ( IN DEVELOPMENT)
 *     Path: /ai-bots/operations-management
 *     Component: OperationsManagementControlPage (TO CREATE)
 *     Panel: OperationsManagementControlPanel (TO CREATE)
 *     Status:  PLANNED
 *     Description: Operational efficiency and workflow
 * 
 * 15. Document Intelligence Bot ( IN DEVELOPMENT)
 *     Path: /ai-bots/document-intelligence
 *     Component: DocumentIntelligenceControlPage (TO CREATE)
 *     Panel: DocumentIntelligenceControlPanel (TO CREATE)
 *     Status:  PLANNED
 *     Description: Document processing and management
 * 
 * 16. Customer Service Bot ( IN DEVELOPMENT)
 *     Path: /ai-bots/customer-service
 *     Component: CustomerServiceControlPage (TO CREATE)
 *     Panel: CustomerServiceControlPanel (TO CREATE)
 *     Status:  PLANNED
 *     Description: Customer support and service management
 * 
 * 17. Market Intelligence Bot ( IN DEVELOPMENT)
 *     Path: /ai-bots/market-intelligence
 *     Component: MarketIntelligenceControlPage (TO CREATE)
 *     Panel: MarketIntelligenceControlPanel (TO CREATE)
 *     Status:  PLANNED
 *     Description: Market analysis and competitive intelligence
 * 
 * ================================================================
 * FILE STRUCTURE
 * ================================================================
 * 
 * Frontend Pages:
 * frontend/src/pages/ai-bots/
 *    AIBotsHubDashboard.jsx                    # Central hub for all bots
 *    AIGeneralManagerControlPage.jsx           # General Manager wrapper
 *    wrappers/
 *       AIFreightBookingsControlPage.jsx      # Freight Bookings wrapper
 *       AIDataCoordinatorControlPage.jsx      # Data Coordinator wrapper
 *       AIFinanceControlPage.jsx              # Finance wrapper
 *       AISecurityControlPage.jsx             # Security wrapper
 *       AISalesControlPage.jsx                # Sales wrapper
 *       AILegalControlPage.jsx                # Legal wrapper
 *       AIPartnerManagementControlPage.jsx    # Partner Management wrapper
 * 
 * Control Panel Components:
 * frontend/src/components/bots/
 *    GeneralManagerControlPanel.jsx            # (TO CREATE)
 *    FreightBrokerControlPanel.jsx             #  CREATED
 *    MapleLoadControlPanel.jsx                 #  CREATED
 *    ExecutiveIntelligenceControlPanel.jsx     #  CREATED
 *    SystemArchitectControlPanel.jsx           # (TO CREATE)
 *    DataCoordinatorControlPanel.jsx           #  CREATED
 *    FreightBookingsControlPanel.jsx           #  CREATED
 *    FinanceControlPanel.jsx                   #  CREATED
 *    SecurityControlPanel.jsx                  #  CREATED
 *    SalesControlPanel.jsx                     #  CREATED
 *    LegalControlPanel.jsx                     #  CREATED
 *    SafetyManagerControlPanel.jsx             # (TO CREATE)
 *    PartnerManagementControlPanel.jsx         #  CREATED
 *    OperationsManagementControlPanel.jsx      # (TO CREATE)
 *    DocumentIntelligenceControlPanel.jsx      # (TO CREATE)
 *    CustomerServiceControlPanel.jsx           # (TO CREATE)
 *    MarketIntelligenceControlPanel.jsx        # (TO CREATE)
 * 
 * ================================================================
 * IMPLEMENTATION CHECKLIST
 * ================================================================
 * 
 * PHASE 1: CORE BOTS 
 *  General Manager Bot - Path + Wrapper + Component
 *  Freight Broker Bot - Path + Component (existing)
 *  MapleLoad Canada Bot - Path + Component (existing)
 *  Executive Intelligence Bot - Path + Component (existing)
 * 
 * PHASE 2: OPERATIONAL BOTS 
 *  System Architect Bot - Path configuration (PENDING COMPONENT)
 *  Data Coordinator Bot - Path + Wrapper + Component
 *  Freight Bookings Bot - Path + Wrapper + Component
 *  Finance Intelligence Bot - Path + Wrapper + Component
 * 
 * PHASE 3: ADMINISTRATIVE BOTS 
 *  Security Question Bot - Path + Wrapper + Component (BACKEND NOT ACTIVE)
 *  Sales Intelligence Bot - Path + Wrapper + Component
 *  Legal Counsel Bot - Path + Wrapper + Component
 *  Safety Manager Bot - Path configuration (PENDING COMPONENT)
 * 
 * PHASE 4: SUPPORT BOTS 
 *  Partner Management Bot - Path + Wrapper + Component (BACKEND NOT ACTIVE)
 *  Operations Management Bot - Planned
 *  Document Intelligence Bot - Planned
 *  Customer Service Bot - Planned
 *  Market Intelligence Bot - Planned
 * 
 * ================================================================
 * HOW TO ADD A NEW BOT
 * ================================================================
 * 
 * 1. Create the Control Panel Component:
 *    frontend/src/components/bots/{BotName}ControlPanel.jsx
 *    Follow the pattern from existing panels (4 tabs, sidebar, footer)
 * 
 * 2. Create the Page Wrapper:
 *    frontend/src/pages/ai-bots/wrappers/AI{BotName}ControlPage.jsx
 *    Simple wrapper that imports and renders the control panel
 * 
 * 3. Add Import in App.jsx:
 *    import AI{BotName}ControlPage from "./pages/ai-bots/wrappers/AI{BotName}ControlPage";
 * 
 * 4. Add Route in App.jsx:
 *    <Route
 *      path="/ai-bots/{bot-name}"
 *      element={
 *        <RequireAuth>
 *          <Layout>
 *            <AI{BotName}ControlPage />
 *          </Layout>
 *        </RequireAuth>
 *      }
 *    />
 * 
 * 5. Update AIBotsHubDashboard.jsx:
 *    Add bot to botsRegistry array with:
 *    - id, name, description, icon
 *    - path, status, phase
 *    - features array
 *    - controlPanel name
 * 
 * 6. Update index.js exports:
 *    frontend/src/components/bots/index.js
 *    Add: export { default as {BotName}ControlPanel } from "./{BotName}ControlPanel";
 * 
 * ================================================================
 * CONTROL PANEL ARCHITECTURE PATTERN
 * ================================================================
 * 
 * Every Control Panel includes:
 * 
 * - Header Section:
 *   - Bot icon and title
 *   - Arabic subtitle
 *   - Quick stats (key metrics)
 *   - Connection status indicator
 * 
 * - Tab Navigation:
 *   - 4 tabs with domain-specific content
 *   - Tab icons for quick identification
 *   - Active tab highlighting
 * 
 * - Main Content Area:
 *   - 3-column layout (main content 3/4, sidebar 1/4)
 *   - Responsive grid for smaller screens
 * 
 * - Right Sidebar:
 *   - Quick Actions buttons
 *   - Activity Log
 *   - Alerts/Status indicators
 * 
 * - Footer:
 *   - Version info
 *   - Last sync timestamp
 * 
 * - State Management:
 *   - useState for activeTab, panelData, loading, connected
 *   - useEffect for data fetching
 *   - useCallback for action handling
 *   - 30-second auto-refresh interval (15s for Security)
 * 
 * - API Integration:
 *   - axiosClient for API calls
 *   - Endpoints: /api/v1/ai/bots/available/{BOT_KEY}/status (GET)
 *   - Endpoints: /api/v1/ai/bots/available/{BOT_KEY}/run (POST)
 *   - Mock data mode for inactive backends
 * 
 * ================================================================
 * TESTING ROUTES
 * ================================================================
 * 
 * Hub Dashboard:
 * http://localhost:5173/ai-bots/hub
 * 
 * Individual Bots:
 * http://localhost:5173/ai-bots/general-manager
 * http://localhost:5173/ai-bots/freight-bookings
 * http://localhost:5173/ai-bots/data-coordinator
 * http://localhost:5173/ai-bots/finance-intelligence
 * http://localhost:5173/ai-bots/security-question
 * http://localhost:5173/ai-bots/sales-intelligence
 * http://localhost:5173/ai-bots/legal-counsel
 * http://localhost:5173/ai-bots/partner-management
 * 
 * ================================================================
 * NEXT STEPS
 * ================================================================
 * 
 * 1.  Create AIBotsHubDashboard.jsx
 * 2.  Create wrapper pages for all control panels
 * 3.  Add routes to App.jsx
 * 4.  Create missing Control Panel components:
 *    - GeneralManagerControlPanel
 *    - SystemArchitectControlPanel
 *    - SafetyManagerControlPanel
 *    - OperationsManagementControlPanel
 *    - DocumentIntelligenceControlPanel
 *    - CustomerServiceControlPanel
 *    - MarketIntelligenceControlPanel
 * 5.  Create wrapper pages for remaining bots
 * 6.  Implement backend API endpoints
 * 7.  Test all routes and connections
 */

export const BOT_ROUTES = {
    HUB: '/ai-bots/hub',

    // Phase 1: Core
    GENERAL_MANAGER: '/ai-bots/general-manager',
    FREIGHT_BROKER: '/ai-bots/freight-broker',
    MAPLELOAD_CANADA: '/ai-bots/mapleload-canada',
    EXECUTIVE_INTELLIGENCE: '/ai-bots/executive-intelligence',

    // Phase 2: Operational
    SYSTEM_ARCHITECT: '/ai-bots/system-architect',
    DATA_COORDINATOR: '/ai-bots/data-coordinator',
    FREIGHT_BOOKINGS: '/ai-bots/freight-bookings',
    FINANCE_INTELLIGENCE: '/ai-bots/finance-intelligence',

    // Phase 3: Administrative
    SECURITY_QUESTION: '/ai-bots/security-question',
    SALES_INTELLIGENCE: '/ai-bots/sales-intelligence',
    LEGAL_COUNSEL: '/ai-bots/legal-counsel',
    SAFETY_MANAGER: '/ai-bots/safety-manager',

    // Phase 4: Support
    PARTNER_MANAGEMENT: '/ai-bots/partner-management',
    OPERATIONS_MANAGEMENT: '/ai-bots/operations-management',
    DOCUMENT_INTELLIGENCE: '/ai-bots/document-intelligence',
    CUSTOMER_SERVICE: '/ai-bots/customer-service',
    MARKET_INTELLIGENCE: '/ai-bots/market-intelligence'
};
