import RequireAuth from "../../components/RequireAuth";
import MarketingSpecialist from "../MarketingSpecialist";

export default function MarketingBot() {
  return (
    <RequireAuth roles={["admin", "owner", "super_admin"]}>
      <MarketingSpecialist />
    </RequireAuth>
  );
}
