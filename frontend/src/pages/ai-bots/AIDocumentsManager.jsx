import AIBotPage from "../../components/AIBotPage.jsx";

export default function AIDocumentsManager() {
  return (
    <AIBotPage
      botKey="documents_manager"
      title="Documents Manager Bot"
      description="Document compliance and renewal tracking."
      relatedLinks={[{ label: "Documents", href: "/documents" }, { label: "Upload", href: "/documents/upload" }]}
    />
  );
}
