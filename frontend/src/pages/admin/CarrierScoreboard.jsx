import RequireAuth from "../../components/RequireAuth";
import PartnerManagementControlPanel from "../../components/bots/PartnerManagementControlPanel";

export default function CarrierScoreboard() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h1 className="text-2xl font-semibold text-slate-900">Carrier Scoreboard</h1>
          <p className="mt-2 text-sm text-slate-600">
            Live carrier relationship metrics, partner health, onboarding, and compliance
            signals from the partner management control panel.
          </p>
        </div>
        <PartnerManagementControlPanel />
      </div>
    </RequireAuth>
  );
}
