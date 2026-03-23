import AIBotPage from "../../components/AIBotPage.jsx";

export default function AIFreightBroker() {
  return (
    <AIBotPage
      botKey="freight_broker"
      title="Freight Broker Bot"
      description="Carrier brokerage, rate intelligence, shipment booking, and freight tracking."
      relatedLinks={[{ label: "Operations Manager", href: "/ai-bots/operations-manager" }]}
    />
  );
}
