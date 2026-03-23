import RequireAuth from "../../components/RequireAuth";
import { SupportTicketList } from "../../components/SupportTickets";

export default function SupportTickets() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-semibold text-slate-900">Support Tickets</h1>
          <p className="mt-2 text-sm text-slate-600">
            Centralized view of support queue activity, ticket state, and response workflow.
          </p>
        </div>
        <SupportTicketList />
      </div>
    </RequireAuth>
  );
}
