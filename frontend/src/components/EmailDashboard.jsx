import { useState } from "react";
import EmailList from "./EmailList";
import EmailDetail from "./EmailDetail";

const EmailDashboard = () => {
  const [selectedEmail, setSelectedEmail] = useState(null);

  return (
    <div className="grid grid-cols-3 h-screen">
      <div className="col-span-1 border-r p-4 overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">📬 Inbox</h2>
        <EmailList onSelect={setSelectedEmail} />
      </div>
      <div className="col-span-2 p-4">
        <EmailDetail email={selectedEmail} />
      </div>
    </div>
  );
};

export default EmailDashboard;
