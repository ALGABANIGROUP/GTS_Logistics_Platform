// frontend/src/pages/partner/PartnerDashboardPage.tsx

import React, { useEffect, useState } from "react";
import { getPartnerDashboard } from "../../services/partnerApi";

interface PartnerDashboardSummary {
  partnerId: string;
  totalClients: number;
  totalOrders: number;
  totalRevenue: number;
  totalPendingPayout: number;
  lastMonthRevenue: number;
  lastPayoutDate?: string | null;
}

const PartnerDashboardPage: React.FC = () => {
  const [data, setData] = useState<PartnerDashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadDashboard = async () => {
      try {
        const res = await getPartnerDashboard();
        if (!isMounted) return;
        setData(res);
      } catch (err: any) {
        if (!isMounted) return;
        const message =
          err?.response?.data?.detail ||
          err?.message ||
          "Failed to load partner dashboard.";
        setError(message);
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    loadDashboard();

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) {
    return (
      <div className="p-4 text-sm text-gray-600">
        Loading partner dashboard...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg">
        {error}
      </div>
    );
  }

  if (!data) {
    return (
      <div className="p-4 text-sm text-gray-500">
        No dashboard data available.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Top metrics cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border rounded-lg shadow-sm p-4">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            Active Clients
          </p>
          <p className="mt-2 text-2xl font-semibold text-gray-900">
            {data.totalClients}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Clients assigned to your partner ID
          </p>
        </div>

        <div className="bg-white border rounded-lg shadow-sm p-4">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            Total Orders
          </p>
          <p className="mt-2 text-2xl font-semibold text-gray-900">
            {data.totalOrders}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Orders created by your clients
          </p>
        </div>

        <div className="bg-white border rounded-lg shadow-sm p-4">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            Total Revenue (Your Share)
          </p>
          <p className="mt-2 text-2xl font-semibold text-emerald-600">
            {data.totalRevenue.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Accumulated partner revenue
          </p>
        </div>

        <div className="bg-white border rounded-lg shadow-sm p-4">
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">
            Pending Payouts
          </p>
          <p className="mt-2 text-2xl font-semibold text-amber-600">
            {data.totalPendingPayout.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Awaiting approval / transfer
          </p>
        </div>
      </div>

      {/* Secondary info */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-white border rounded-lg shadow-sm p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-2">
            Activity Snapshot
          </h2>
          <p className="text-sm text-gray-600">
            Use the navigation above to drill into your clients, orders,
            revenue breakdown and payout requests.
          </p>
        </div>

        <div className="bg-white border rounded-lg shadow-sm p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-2">
            Last Month Revenue
          </h2>
          <p className="text-sm text-gray-700">
            {data.lastMonthRevenue.toLocaleString(undefined, {
              minimumFractionDigits: 2,
              maximumFractionDigits: 2,
            })}
          </p>
        </div>

        <div className="bg-white border rounded-lg shadow-sm p-4">
          <h2 className="text-sm font-semibold text-gray-900 mb-2">
            Last Payout
          </h2>
          {data.lastPayoutDate ? (
            <p className="text-sm text-gray-700">
              Last payout processed on{" "}
              <span className="font-medium">{data.lastPayoutDate}</span>
            </p>
          ) : (
            <p className="text-sm text-gray-500">
              No payout has been processed yet.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default PartnerDashboardPage;
