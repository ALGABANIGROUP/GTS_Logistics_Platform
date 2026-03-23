import AIBotPage from "../../components/AIBotPage.jsx";

export default function AIMarketingManager() {
  return (
    <AIBotPage
      botKey="marketing_manager"
      title="Marketing Manager"
      description="Campaign operations, lead generation, ROI forecasting, customer segmentation, and promotion workflows."
      relatedLinks={[
        { label: "Sales Bot", href: "/ai-bots/sales-team" },
        { label: "Information Coordinator", href: "/ai-bots/information-coordinator" },
      ]}
    />
  );
}
