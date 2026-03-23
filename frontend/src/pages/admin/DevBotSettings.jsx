import RequireAuth from "../../components/RequireAuth";
import DevBotSettingsPage from "../DevBotSettings";

export default function DevBotSettings() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <DevBotSettingsPage />
    </RequireAuth>
  );
}
