import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import axiosClient from "../api/axiosClient";
import SystemReadinessGate from "./SystemReadinessGate.jsx";

const APPROVED_BOT_CATALOG = {
  customer_service: {
    name: "AI Customer Service",
    description: "Customer support and request intake.",
    route: "/ai-bots/customer-service",
  },
  documents_manager: {
    name: "AI Documents Manager",
    description: "Document processing and compliance workflows.",
    route: "/ai-bots/documents",
  },
  general_manager: {
    name: "AI General Manager",
    description: "Executive oversight and strategic reporting.",
    route: "/ai-bots/general-manager",
  },
  payment_bot: {
    name: "Payment Gateway Dashboard",
    description: "Secure payment processing, invoice management, and finance bot integration.",
    route: "/ai-bots/payment",
  },
  information_coordinator: {
    name: "AI Information Coordinator",
    description: "Knowledge routing and intelligence coordination.",
    route: "/ai-bots/information",
  },
  intelligence_bot: {
    name: "AI Intelligence Bot",
    description: "Strategic analysis and executive insights.",
    route: "/ai-bots/control?bot=intelligence_bot",
  },
  legal_bot: {
    name: "AI Legal Consultant",
    description: "Legal review and compliance guidance.",
    route: "/ai-bots/legal",
  },
  maintenance_dev: {
    name: "AI Dev Maintenance Bot (CTO)",
    description: "System maintenance, CTO fixes, and health checks.",
    route: "/ai-bots/maintenance-dashboard",
  },
  marketing_manager: {
    name: "AI Marketing Manager",
    description: "Campaign orchestration and growth analytics.",
    route: "/admin/ai/marketing-bot",
  },
  partner_manager: {
    name: "AI Partner Manager",
    description: "Partner operations workflows, alliance management, and carrier partnerships.",
    route: "/ai-bots/partner-management",
  },
  mapleload_bot: {
    name: "AI MapleLoad Canada",
    description: "Canadian market intelligence and load matching.",
    route: "/ai-bots/mapleload-canada",
  },
  operations_manager_bot: {
    name: "AI Operations Manager",
    description: "Operational workflow coordination.",
    route: "/ai-bots/operations",
  },
  safety_manager_bot: {
    name: "AI Safety Manager",
    description: "Safety compliance and incident tracking.",
    route: "/ai-bots/safety_manager",
  },
  sales_bot: {
    name: "AI Sales Bot",
    description: "Sales analytics and pipeline support.",
    route: "/ai-bots/sales",
  },
  security_manager_bot: {
    name: "AI Security Manager",
    description: "Security monitoring and threat response.",
    route: "/ai-bots/security_manager",
  },
  system_manager_bot: {
    name: "AI System Manager",
    description: "System health monitoring and optimization.",
    route: "/ai-bots/system-admin",
  },
  ai_dispatcher: {
    name: "AI Dispatcher",
    description: "Intelligent task distribution and routing.",
    route: "/ai-bots/aid-dispatcher",
  },
  trainer_bot: {
    name: "AI Trainer Bot",
    description: "Training and simulation orchestration for bot readiness.",
    route: "/ai-bots/control",
  },
  freight_broker: {
    name: "AI Freight Broker",
    description: "Core freight brokerage and load management.",
    route: "/ai-bots/freight",
  },
};

const REQUIRED_VISIBLE_BOTS = [
  { botKey: "payment_bot", canRun: true, reasonCodes: [] },
  { botKey: "marketing_manager", canRun: true, reasonCodes: [] },
  { botKey: "partner_manager", canRun: true, reasonCodes: [] },
  { botKey: "maintenance_dev", canRun: true, reasonCodes: [] },
  { botKey: "security_manager_bot", canRun: true, reasonCodes: [] },
  { botKey: "trainer_bot", canRun: true, reasonCodes: [] },
];

const BOT_ALIASES = {
  general_manager: "general_manager",
  payment_bot: "payment_bot",
  payment: "payment_bot",
  payment_gateway: "payment_bot",
  information_coordinator: "information_coordinator",
  intelligence_bot: "intelligence_bot",
  executive_intelligence: "intelligence_bot",
  legal_bot: "legal_bot",
  legal_consultant: "legal_bot",
  legal_counsel: "legal_bot",
  maintenance_dev: "maintenance_dev",
  maintenance_dev_cto: "maintenance_dev",
  dev_maintenance: "maintenance_dev",
  documents_manager: "documents_manager",
  customer_service: "customer_service",
  operations_manager: "operations_manager_bot",
  operations_bot: "operations_manager_bot",
  operations_manager_bot: "operations_manager_bot",
  safety_manager: "safety_manager_bot",
  safety_bot: "safety_manager_bot",
  safety_manager_bot: "safety_manager_bot",
  security_manager: "security_manager_bot",
  security_bot: "security_manager_bot",
  security_manager_bot: "security_manager_bot",
  system_admin: "system_manager_bot",
  system_manager: "system_manager_bot",
  system_bot: "system_manager_bot",
  system_manager_bot: "system_manager_bot",
  mapleload: "mapleload_bot",
  mapleload_canada: "mapleload_bot",
  mapleload_bot: "mapleload_bot",
  sales: "sales_bot",
  sales_team: "sales_bot",
  sales_bot: "sales_bot",
  marketing_manager: "marketing_manager",
  ai_marketing_manager: "marketing_manager",
  partner_manager: "partner_manager",
  partner_management: "partner_manager",
  ai_partner_manager: "partner_manager",
  ai_dispatcher: "ai_dispatcher",
  aid_dispatcher: "ai_dispatcher",
  dispatcher: "ai_dispatcher",
  trainer_bot: "trainer_bot",
  trainer: "trainer_bot",
  training_bot: "trainer_bot",
  freight_broker: "freight_broker",
  freight: "freight_broker",
  freight_broker_bot: "freight_broker",
  freightbroker: "freight_broker",
};

const normalizeBotKey = (value) => {
  const raw = String(value || "").trim();
  if (!raw) return "";
  return raw.toLowerCase().replace(/[^a-z0-9_]/g, "_");
};

const resolveBotKey = (value) => {
  const normalized = normalizeBotKey(value);
  if (!normalized) return "";
  const canonical = BOT_ALIASES[normalized] || normalized;
  return APPROVED_BOT_CATALOG[canonical] ? canonical : "";
};

const buildIcon = (botKey) => {
  if (!botKey) return "AI";
  const parts = String(botKey).split("_").filter(Boolean);
  const initials = parts.map((part) => part[0]?.toUpperCase() || "").join("");
  return initials.slice(0, 4) || "AI";
};

const buildRoute = (botKey) => {
  const base = APPROVED_BOT_CATALOG[botKey]?.route || "/ai-bots/control";
  if (base === "/ai-bots/control") {
    return `${base}?bot=${encodeURIComponent(botKey)}`;
  }
  return base;
};

const renderReason = (code) =>
  String(code || "")
    .replace(/_/g, " ")
    .toLowerCase();

const ActionButton = ({ to, disabled, label }) => {
  if (disabled) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full border border-slate-600/60 bg-slate-800/40 px-3 py-1 text-slate-400">
        {label}
      </span>
    );
  }

  return (
    <Link
      to={to}
      className="inline-flex items-center gap-1 rounded-full border border-slate-600/70 bg-slate-800/70 px-3 py-1 text-slate-100 transition hover:border-sky-400/60 hover:text-sky-100"
    >
      {label}
    </Link>
  );
};

const BotCard = ({ bot, actionLabel }) => {
  const canRun = Boolean(bot.canRun);
  const reasonCodes = bot.reasonCodes || [];
  const isAlias = Boolean(bot.isAlias);

  return (
    <div className="group rounded-3xl border border-slate-700/60 bg-slate-900/60 p-5 shadow-2xl shadow-black/40 backdrop-blur-xl transition duration-200 hover:border-sky-400/50 hover:bg-slate-900/70">
      <div className="flex items-start gap-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-800 text-[11px] font-semibold uppercase tracking-wide text-slate-50 shadow-inner shadow-black/40">
          {bot.icon}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <div className="truncate text-base font-semibold text-slate-50">
              {bot.title}
            </div>
            {isAlias ? (
              <span className="rounded-full border border-blue-400/30 bg-blue-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-blue-100">
                Alias
              </span>
            ) : null}
            <span
              className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${canRun
                ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-100"
                : "border-rose-400/30 bg-rose-500/10 text-rose-100"
                }`}
            >
              {canRun ? "Active" : "Blocked"}
            </span>
          </div>
          <div className="mt-1 line-clamp-2 text-sm text-slate-300">
            {bot.desc}
          </div>

          {reasonCodes.length ? (
            <div className="mt-2 flex flex-wrap gap-2 text-[10px] uppercase tracking-wide text-rose-200/80">
              {reasonCodes.map((code) => (
                <span
                  key={`${bot.botKey}-${code}`}
                  className="rounded-full border border-rose-400/30 bg-rose-500/10 px-2 py-0.5"
                >
                  {renderReason(code)}
                </span>
              ))}
            </div>
          ) : null}

          <div className="mt-4 flex flex-wrap items-center gap-2 text-xs font-semibold">
            <ActionButton
              to={bot.path}
              disabled={!canRun}
              label={actionLabel.control}
            />
            <ActionButton
              to={`${bot.path}${bot.path.includes("?") ? "&" : "?"}quick=1`}
              disabled={!canRun}
              label={actionLabel.quick}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default function AIBotsDashboard() {
  const [bots, setBots] = useState([]);
  const [aliases, setAliases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [offline, setOffline] = useState(false);

  const actionLabel = useMemo(
    () => ({ control: "Control Panel", quick: "Quick Run" }),
    []
  );

  useEffect(() => {
    let active = true;

    const loadBots = async () => {
      try {
        setLoading(true);
        const res = await axiosClient.get("/api/v1/bots/available");
        const payload = res?.data || {};
        const list = Array.isArray(payload?.bots) ? payload.bots : [];
        const aliasList = Array.isArray(payload?.aliases) ? payload.aliases : [];

        if (!active) return;

        const mapped = list.reduce((acc, bot) => {
          const rawKey = bot.bot_key || bot.botKey || bot.name;
          const botKey = resolveBotKey(rawKey);
          if (!botKey || acc.has(botKey)) return acc;
          const config = APPROVED_BOT_CATALOG[botKey];
          acc.set(botKey, {
            botKey,
            title: config?.name || bot.display_name || bot.name || botKey,
            desc: config?.description || bot.description || "AI assistant",
            icon: buildIcon(botKey),
            path: buildRoute(botKey),
            canRun: bot.can_run,
            reasonCodes: bot.reason_codes || [],
            category: bot.category || "",
          });
          return acc;
        }, new Map());

        const mappedAliases = aliasList
          .map((alias) => {
            const aliasKey = alias.alias_key || alias.aliasKey;
            const targetKey = resolveBotKey(alias.bot_key || alias.botKey);
            if (!aliasKey || !targetKey) return null;
            if (mapped.has(targetKey)) return null;
            return {
              botKey: aliasKey,
              title: alias.display_name || aliasKey,
              desc: `Alias for ${targetKey}`,
              icon: buildIcon(aliasKey),
              path: buildRoute(targetKey),
              canRun: alias.can_run,
              reasonCodes: alias.reason_codes || [],
              isAlias: true,
            };
          })
          .filter(Boolean);

        REQUIRED_VISIBLE_BOTS.forEach((forcedBot) => {
          if (mapped.has(forcedBot.botKey)) return;
          const config = APPROVED_BOT_CATALOG[forcedBot.botKey];
          if (!config) return;
          mapped.set(forcedBot.botKey, {
            botKey: forcedBot.botKey,
            title: config.name,
            desc: config.description,
            icon: buildIcon(forcedBot.botKey),
            path: buildRoute(forcedBot.botKey),
            canRun: forcedBot.canRun,
            reasonCodes: forcedBot.reasonCodes,
            category: "",
          });
        });

        setBots(Array.from(mapped.values()));
        setAliases(mappedAliases);
      } catch (err) {
        if (active) {
          setBots([]);
          setAliases([]);
          setOffline(true);
        }
      } finally {
        if (active) setLoading(false);
      }
    };

    loadBots();
    return () => {
      active = false;
    };
  }, []);

  const total = bots.length + aliases.length;

  return (
    <SystemReadinessGate>
      <div className="space-y-5">
        <div className="flex flex-col gap-2 rounded-3xl border border-slate-700/60 bg-slate-900/60 p-5 shadow-2xl shadow-black/40 backdrop-blur-xl">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-xl font-semibold text-slate-50">AI Bots Panel</div>
              <div className="mt-1 text-sm text-slate-300">
                Run operational and strategic assistants from a unified view.
              </div>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <span className="rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 font-semibold text-emerald-100">
                {loading ? "Loading" : `${total} available`}
              </span>
            </div>
          </div>
        </div>

        {offline ? (
          <div className="rounded-3xl border border-amber-400/30 bg-amber-500/10 p-6 text-sm text-amber-100 shadow-2xl shadow-black/40 backdrop-blur-xl">
            <div className="flex items-center gap-3">
              <div className="text-amber-100">
                <strong>AI Bots service is currently unavailable</strong>
              </div>
            </div>
            <div className="mt-2 text-amber-200/80">
              The bots health check endpoint is not responding. You can still view the dashboard UI, but bot execution may not work properly.
            </div>
          </div>
        ) : loading ? (
          <div className="rounded-3xl border border-slate-700/60 bg-slate-900/60 p-6 text-sm text-slate-200 shadow-2xl shadow-black/40 backdrop-blur-xl">
            Loading bots...
          </div>
        ) : total === 0 ? (
          <div className="rounded-3xl border border-slate-700/60 bg-slate-900/60 p-6 text-sm text-slate-200 shadow-2xl shadow-black/40 backdrop-blur-xl">
            No bots available for your role.
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {bots.map((bot) => (
                <BotCard key={bot.botKey || bot.path} bot={bot} actionLabel={actionLabel} />
              ))}
            </div>
            {aliases.length ? (
              <div className="space-y-3">
                <div className="text-xs uppercase tracking-wide text-slate-300/80">
                  Aliases
                </div>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {aliases.map((alias) => (
                    <BotCard
                      key={alias.botKey || alias.path}
                      bot={alias}
                      actionLabel={actionLabel}
                    />
                  ))}
                </div>
              </div>
            ) : null}
          </>
        )}
      </div>
    </SystemReadinessGate>
  );
}
