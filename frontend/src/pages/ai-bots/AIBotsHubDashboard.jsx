import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { BOTS_REGISTRY, TIER_ORDER } from "../../config/botsRegistry";

const TIER_LABELS = {
  Basic: "Starter",
  Growth: "Growth",
  Professional: "Professional",
  Enterprise: "Enterprise",
  Marketing: "Marketing",
  Management: "Management",
  Training: "Training",
};

const TIER_BADGES = {
  Basic: "🚀 Starter",
  Growth: "📈 Growth",
  Professional: "💼 Professional",
  Enterprise: "🏢 Enterprise",
  Marketing: "📢 Marketing",
  Management: "🤝 Management",
  Training: "🎓 Training",
};

export default function AIBotsHubDashboard() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTier, setSelectedTier] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const navigate = useNavigate();

  const botsData = Array.isArray(BOTS_REGISTRY) && BOTS_REGISTRY.length > 0 ? BOTS_REGISTRY : [];

  const filteredBots = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase();

    return botsData
      .filter((bot) => {
        const matchesTier = selectedTier === "all" || bot.tier === selectedTier;
        const matchesStatus = filterStatus === "all" || bot.status === filterStatus;
        if (!matchesTier || !matchesStatus) return false;
        if (!needle) return true;

        return (
          bot.name.toLowerCase().includes(needle) ||
          bot.description.toLowerCase().includes(needle) ||
          String(bot.key || "").toLowerCase().includes(needle) ||
          (Array.isArray(bot.aliases) && bot.aliases.some((alias) => alias.toLowerCase().includes(needle)))
        );
      })
      .sort((a, b) => a.order - b.order);
  }, [botsData, filterStatus, searchTerm, selectedTier]);

  const botsByTier = useMemo(
    () =>
      filteredBots.reduce((acc, bot) => {
        if (!acc[bot.tier]) acc[bot.tier] = [];
        acc[bot.tier].push(bot);
        return acc;
      }, {}),
    [filteredBots]
  );

  const activeCount = botsData.filter((bot) => bot.status === "active").length;
  const inactiveCount = botsData.filter((bot) => bot.status === "inactive").length;

  return (
    <div className="min-h-screen bg-gray-100 px-4 py-8 dark:bg-gray-900">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8">
          <h1 className="mb-2 text-4xl font-bold text-gray-900 dark:text-white">AI Bots Hub</h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Plan: Enterprise | Available Bots: {activeCount} of {botsData.length}
          </p>
        </div>

        <div className="mb-8 rounded-xl border border-gray-200 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800">
          <div className="flex flex-wrap gap-4">
            <div className="min-w-64 flex-1">
              <input
                type="text"
                placeholder="Search bots by name, description, key, or alias..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
            </div>
            <select
              value={selectedTier}
              onChange={(e) => setSelectedTier(e.target.value)}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            >
              <option value="all">All Tiers ({botsData.length})</option>
              {TIER_ORDER.map((tier) => (
                <option key={tier} value={tier}>
                  {TIER_LABELS[tier] || tier}
                </option>
              ))}
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-gray-900 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
            >
              <option value="all">All Status</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>
        </div>

        <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-4">
          <div className="rounded-lg border border-green-200 bg-white p-4 dark:border-green-800 dark:bg-gray-800">
            <p className="text-sm text-gray-600 dark:text-gray-400">Active Bots</p>
            <p className="text-3xl font-bold text-green-600">{activeCount}</p>
          </div>
          <div className="rounded-lg border border-yellow-200 bg-white p-4 dark:border-yellow-800 dark:bg-gray-800">
            <p className="text-sm text-gray-600 dark:text-gray-400">In Development</p>
            <p className="text-3xl font-bold text-yellow-600">{inactiveCount}</p>
          </div>
          <div className="rounded-lg border border-blue-200 bg-white p-4 dark:border-blue-800 dark:bg-gray-800">
            <p className="text-sm text-gray-600 dark:text-gray-400">Total Bots</p>
            <p className="text-3xl font-bold text-blue-600">{botsData.length}</p>
          </div>
          <div className="rounded-lg border border-purple-200 bg-white p-4 dark:border-purple-800 dark:bg-gray-800">
            <p className="text-sm text-gray-600 dark:text-gray-400">Showing</p>
            <p className="text-3xl font-bold text-purple-600">{filteredBots.length}</p>
          </div>
        </div>

        {TIER_ORDER.map((tier) => {
          const tierBots = botsByTier[tier];
          if (!tierBots?.length) return null;

          return (
            <div key={tier} className="mb-12">
              <div className="mb-6 flex items-center gap-3">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {TIER_BADGES[tier] || tier}
                </h2>
                <span className="rounded-full bg-gray-200 px-3 py-1 text-sm text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                  {tierBots.length} bot{tierBots.length !== 1 ? "s" : ""}
                </span>
              </div>

              <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                {tierBots.map((bot) => (
                  <button
                    key={bot.id}
                    onClick={() => navigate(bot.path)}
                    disabled={bot.status !== "active"}
                    className={`rounded-xl border border-gray-200 bg-white p-6 text-left shadow-lg transition-all dark:border-gray-700 dark:bg-gray-800 ${
                      bot.status === "active"
                        ? "hover:border-blue-500 hover:shadow-xl"
                        : "cursor-not-allowed opacity-60"
                    }`}
                  >
                    <div className="mb-4 flex items-start justify-between">
                      <div className="text-4xl">{bot.icon || "🤖"}</div>
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-medium ${
                          bot.status === "active"
                            ? "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300"
                            : "bg-gray-100 text-gray-500 dark:bg-gray-700 dark:text-gray-400"
                        }`}
                      >
                        {bot.status === "active" ? "Active" : "Inactive"}
                      </span>
                    </div>

                    <h3 className="mb-2 text-xl font-bold text-gray-900 dark:text-white">{bot.name}</h3>
                    <p className="mb-4 text-sm text-gray-600 dark:text-gray-400">{bot.description}</p>

                    <div className="mb-4">
                      <div className="flex flex-wrap gap-2">
                        {bot.features.slice(0, 3).map((feature, idx) => (
                          <span
                            key={`${bot.key}-${idx}`}
                            className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-700 dark:bg-gray-700 dark:text-gray-300"
                          >
                            {feature}
                          </span>
                        ))}
                        {bot.features.length > 3 && (
                          <span className="rounded bg-gray-100 px-2 py-1 text-xs text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                            +{bot.features.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 text-sm font-medium text-blue-600 dark:text-blue-400">
                      <span>Launch Control Panel</span>
                      <span>→</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          );
        })}

        {filteredBots.length === 0 && (
          <div className="py-12 text-center">
            <p className="text-lg text-gray-600 dark:text-gray-400">
              No bots found matching your search criteria
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
