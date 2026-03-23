import { useSearchParams } from "react-router-dom";
import AIBotPage from "../../components/AIBotPage.jsx";
import AILegalConsultant from "./AILegalConsultant.jsx";
import AIDispatcherControl from "./AIDispatcherControl.jsx";
import AISecurityManager from "./AISecurityManager.jsx";
import AISalesBotControl from "./AISalesBotControl.jsx";
import AIMarketingManager from "./AIMarketingManager.jsx";
import AIMaintenanceDev from "./AIMaintenanceDev.jsx";
import AITrainerBot from "./AITrainerBot.jsx";
import AIOperationsManager from "./AIOperationsManager.jsx";
import AIInformationCoordinator from "./AIInformationCoordinator.jsx";
import AISystemAdmin from "./AISystemAdmin.jsx";
import AIGeneralManager from "./AIGeneralManager.jsx";
import AIIntelligenceBot from "./AIIntelligenceBot.jsx";
import PaymentBotDashboard from "./PaymentBotDashboard.jsx";
import AIPartnerManagementControlPage from "./wrappers/AIPartnerManagementControlPage.jsx";
import SUDAPayBotDashboard from "./SUDAPayBotDashboard.jsx";
import FreightBrokerControlPanel from "../../components/bots/FreightBrokerControlPanel.jsx";

const DEFAULT_BOT = "operations_manager_bot";

export default function AIBotControl() {
  const [searchParams] = useSearchParams();
  const requestedBot = (searchParams.get("bot") || "").trim();
  const mode = (searchParams.get("mode") || "").trim().toLowerCase();
  const botKey = requestedBot || DEFAULT_BOT;

  const normalized = botKey.toLowerCase();
  const aliases = {
    operations_manager: "operations_manager_bot",
    operations_bot: "operations_manager_bot",
    payment_bot: "payment_bot",
    payment_gateway: "payment_bot",
    finance: "finance_bot",
    bot_finance: "finance_bot",
    partner: "partner_manager",
    partner_management: "partner_manager",
    ai_partner_manager: "partner_manager",
    sudapay: "sudapay",
    payment: "payment_bot",
    mapleload_canada: "mapleload_bot",
    mapleload: "mapleload_bot",
    trainer: "trainer_bot",
    training_bot: "trainer_bot",
    info: "information_coordinator",
    information: "information_coordinator",
    system_manager: "system_manager_bot",
    system_bot: "system_manager_bot",
    system_admin: "system_manager_bot",
  };
  const canonicalBotKey = aliases[normalized] || botKey;
  const isDevMaintenance =
    normalized === "dev_maintenance" || normalized === "maintenance_dev";
  const isExecutiveIntelligence =
    normalized === "executive_intelligence" ||
    normalized === "executive-intelligence";
  const isIntelligenceBot =
    normalized === "intelligence_bot" ||
    normalized === "intelligence" ||
    normalized === "market_intelligence";
  const isGeneralManager = normalized === "general_manager";
  const isLegalConsultant =
    normalized === "legal_consultant" ||
    normalized === "legal-bot" ||
    normalized === "legal_bot" ||
    normalized === "legal";
  const isDispatcher =
    normalized === "ai_dispatcher" ||
    normalized === "aid_dispatcher" ||
    normalized === "dispatcher";
  const isSecurity =
    normalized === "security_bot" ||
    normalized === "security-manager" ||
    normalized === "security_manager" ||
    normalized === "security_manager_bot";
  const isSales =
    normalized === "sales_bot" ||
    normalized === "sales-team" ||
    normalized === "sales_team";
  const isFinance =
    normalized === "finance_bot" ||
    normalized === "bot_finance" ||
    normalized === "finance";
  const isSudapay =
    normalized === "sudapay" ||
    normalized === "sudapay_gateway";
  const isPayment =
    normalized === "payment" ||
    normalized === "payment_bot" ||
    normalized === "payment_gateway";
  const isPartnerManager =
    normalized === "partner_manager" ||
    normalized === "partner_management" ||
    normalized === "partner" ||
    normalized === "ai_partner_manager";
  const isMarketing =
    normalized === "marketing_manager" ||
    normalized === "marketing_manager_bot" ||
    normalized === "marketing_bot";
  const isFreightBroker =
    normalized === "freight_broker" ||
    normalized === "freight-broker" ||
    normalized === "freight" ||
    normalized === "freight_broker_bot" ||
    normalized === "freightbroker";
  const isOperations =
    normalized === "operations_manager" ||
    normalized === "operations_manager_bot" ||
    normalized === "operations_bot";
  const isTrainer =
    normalized === "trainer_bot" ||
    normalized === "trainer" ||
    normalized === "training_bot";
  const isInformationCoordinator =
    normalized === "information_coordinator" ||
    normalized === "information-coordinator" ||
    normalized === "info" ||
    normalized === "information";
  const isSystemManager =
    normalized === "system_bot" ||
    normalized === "system_manager" ||
    normalized === "system_manager_bot" ||
    normalized === "system_admin";

  if (isDevMaintenance) {
    return <AIMaintenanceDev botKey={canonicalBotKey} />;
  }
  if (isOperations) {
    return <AIOperationsManager botKey={canonicalBotKey} />;
  }
  if (isGeneralManager) {
    return <AIGeneralManager botKey="general_manager" />;
  }
  if (isIntelligenceBot || isExecutiveIntelligence) {
    return <AIIntelligenceBot botKey="intelligence_bot" />;
  }
  if (isLegalConsultant) {
    return <AILegalConsultant mode={mode || "active"} />;
  }
  if (isDispatcher) {
    return <AIDispatcherControl botKey={canonicalBotKey} />;
  }
  if (isSecurity) {
    return <AISecurityManager botKey={canonicalBotKey} />;
  }
  if (isSales) {
    return <AISalesBotControl botKey={canonicalBotKey} />;
  }
  if (isFinance) {
    return (
      <AIBotPage
        botKey="finance_bot"
        title="AI Finance Bot"
        description="Financial analysis, revenue tracking, expense management, and invoice processing."
        mode={mode || "active"}
      />
    );
  }
  if (isPayment) {
    return <PaymentBotDashboard />;
  }
  if (isSudapay) {
    return <SUDAPayBotDashboard />;
  }
  if (isPartnerManager) {
    return <AIPartnerManagementControlPage />;
  }
  if (isMarketing) {
    return <AIMarketingManager botKey={canonicalBotKey} />;
  }
  if (isFreightBroker) {
    if (mode === "advanced") {
      return (
        <AIBotPage
          botKey={canonicalBotKey}
          title="Freight Broker Advanced Settings"
          description="Run commands, inspect status, and review bot configuration."
          mode={mode}
        />
      );
    }
    return <FreightBrokerControlPanel mode={mode || "active"} />;
  }
  if (isTrainer) {
    return <AITrainerBot botKey={canonicalBotKey} />;
  }
  if (isInformationCoordinator) {
    return <AIInformationCoordinator botKey={canonicalBotKey} />;
  }
  if (isSystemManager) {
    return <AISystemAdmin botKey={canonicalBotKey} />;
  }

  return (
    <AIBotPage
      botKey={canonicalBotKey}
      title="AI Bot Control"
      description="Run and inspect any registered bot using the unified API."
      mode={mode || "active"}
    />
  );
}
