import { useParams, Navigate } from "react-router-dom";

import ShipperDash from "./shipper/TMSDashboard";
import CarrierDash from "./carrier/TMSDashboard";
import BrokerDash from "./broker/TMSDashboard";
import AdminDash from "./admin/TMSDashboard";

export default function TMSDashboard() {
  const { role } = useParams();

  if (!role) return <Navigate to="/tms/shipper" replace />;

  switch (role) {
    case "shipper":
      return <ShipperDash />;
    case "carrier":
      return <CarrierDash />;
    case "broker":
      return <BrokerDash />;
    case "admin":
      return <AdminDash />;
    default:
      return <Navigate to="/tms/shipper" replace />;
  }
}
