import AIBotPage from "../../components/AIBotPage.jsx";

export default function AICollaborationEngine() {
  return (
    <AIBotPage
      botKey="operations_manager"
      title="Collaboration Engine"
      description="Multi-bot workflows coordinated by Operations Manager."
      relatedLinks={[{ label: "Operations", href: "/operations" }]}
    />
  );
}
