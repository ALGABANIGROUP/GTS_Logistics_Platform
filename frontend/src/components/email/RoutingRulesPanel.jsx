/* eslint-disable react/prop-types */
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  assignBotToMailbox,
  createRoutingRule,
  deleteRoutingRule,
  getAssignedBot,
  getRoutingRules,
  manuallyRouteMessage,
  updateRoutingRule,
} from "../../services/emailCenterApi";

const CONDITION_FIELDS = [
  { value: "all", label: "Subject + Body + Sender + Recipients" },
  { value: "subject", label: "Subject" },
  { value: "body", label: "Body" },
  { value: "sender", label: "Sender" },
  { value: "recipients", label: "Recipients" },
];

const CONDITION_OPERATORS = [
  { value: "contains", label: "Contains" },
  { value: "equals", label: "Equals" },
  { value: "starts_with", label: "Starts with" },
  { value: "ends_with", label: "Ends with" },
  { value: "regex", label: "Regex" },
  { value: "in", label: "In list" },
  { value: "not_contains", label: "Does not contain" },
  { value: "not_equals", label: "Does not equal" },
];

const ACTION_TYPES = [
  { value: "process", label: "Process" },
  { value: "forward", label: "Forward" },
  { value: "reply", label: "Reply" },
  { value: "ignore", label: "Ignore" },
  { value: "tag", label: "Tag" },
  { value: "assign", label: "Assign" },
  { value: "escalate", label: "Escalate" },
];

const DEFAULT_BOTS = [
  { key: "finance_bot", name: "Finance Bot" },
  { key: "customer_service", name: "Customer Service" },
  { key: "legal_bot", name: "Legal Bot" },
  { key: "operations_manager", name: "Operations Manager" },
  { key: "freight_broker", name: "Freight Broker" },
];

const emptyForm = {
  bot_key: "",
  condition_field: "all",
  condition_operator: "contains",
  condition_value: "",
  condition_match_all: false,
  action_type: "process",
  action_config: "",
  priority: 0,
  is_active: true,
};

const normalizeRulePayload = (formData) => {
  let actionConfig;
  if (formData.action_config && String(formData.action_config).trim()) {
    actionConfig = JSON.parse(formData.action_config);
  }

  return {
    bot_key: formData.bot_key || null,
    condition_field: formData.condition_field,
    condition_operator: formData.condition_operator,
    condition_value: formData.condition_value,
    condition_match_all: Boolean(formData.condition_match_all),
    action_type: formData.action_type,
    action_config: actionConfig,
    priority: Number(formData.priority) || 0,
    is_active: Boolean(formData.is_active),
  };
};

const RuleModal = ({ initialRule, onClose, onSave }) => {
  const [formData, setFormData] = useState(() => ({
    ...emptyForm,
    ...(initialRule
      ? {
          ...initialRule,
          bot_key: initialRule.bot_key || "",
          condition_value:
            typeof initialRule.condition_value === "string"
              ? initialRule.condition_value
              : JSON.stringify(initialRule.condition_value ?? ""),
          action_config: initialRule.action_config
            ? JSON.stringify(initialRule.action_config, null, 2)
            : "",
        }
      : {}),
  }));
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();
    try {
      setError("");
      await onSave(normalizeRulePayload(formData));
    } catch (err) {
      setError(err?.message || "Failed to save rule.");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4">
      <div className="w-full max-w-3xl rounded-2xl border border-white/10 bg-slate-950 p-5 shadow-2xl">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-lg font-semibold text-white">
              {initialRule ? "Edit routing rule" : "Create routing rule"}
            </div>
            <div className="text-xs text-slate-400">
              Define routing logic for the selected mailbox.
            </div>
          </div>
          <button
            onClick={onClose}
            className="rounded-lg border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-200 hover:bg-white/10"
          >
            Close
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <label className="space-y-1 text-xs text-slate-300">
              <span>Bot override</span>
              <select
                value={formData.bot_key}
                onChange={(event) => setFormData((prev) => ({ ...prev, bot_key: event.target.value }))}
                className="w-full rounded-lg border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-white"
              >
                <option value="">Use mailbox assigned bot</option>
                {DEFAULT_BOTS.map((bot) => (
                  <option key={bot.key} value={bot.key}>
                    {bot.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-1 text-xs text-slate-300">
              <span>Priority</span>
              <input
                type="number"
                min="0"
                value={formData.priority}
                onChange={(event) =>
                  setFormData((prev) => ({ ...prev, priority: event.target.value }))
                }
                className="w-full rounded-lg border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-white"
              />
            </label>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <label className="space-y-1 text-xs text-slate-300">
              <span>Field</span>
              <select
                value={formData.condition_field}
                onChange={(event) =>
                  setFormData((prev) => ({ ...prev, condition_field: event.target.value }))
                }
                className="w-full rounded-lg border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-white"
              >
                {CONDITION_FIELDS.map((field) => (
                  <option key={field.value} value={field.value}>
                    {field.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-1 text-xs text-slate-300">
              <span>Operator</span>
              <select
                value={formData.condition_operator}
                onChange={(event) =>
                  setFormData((prev) => ({ ...prev, condition_operator: event.target.value }))
                }
                className="w-full rounded-lg border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-white"
              >
                {CONDITION_OPERATORS.map((operator) => (
                  <option key={operator.value} value={operator.value}>
                    {operator.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-1 text-xs text-slate-300">
              <span>Action</span>
              <select
                value={formData.action_type}
                onChange={(event) =>
                  setFormData((prev) => ({ ...prev, action_type: event.target.value }))
                }
                className="w-full rounded-lg border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-white"
              >
                {ACTION_TYPES.map((action) => (
                  <option key={action.value} value={action.value}>
                    {action.label}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="space-y-1 text-xs text-slate-300">
            <span>Condition value</span>
            <textarea
              value={formData.condition_value}
              onChange={(event) =>
                setFormData((prev) => ({ ...prev, condition_value: event.target.value }))
              }
              className="min-h-[90px] w-full rounded-lg border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-white"
              placeholder="Example: invoice"
            />
          </label>

          <label className="space-y-1 text-xs text-slate-300">
            <span>Action config (JSON, optional)</span>
            <textarea
              value={formData.action_config}
              onChange={(event) =>
                setFormData((prev) => ({ ...prev, action_config: event.target.value }))
              }
              className="min-h-[110px] w-full rounded-lg border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-white"
              placeholder='Example: {"user_id": 42}'
            />
          </label>

          <div className="flex flex-wrap items-center gap-4 text-xs text-slate-300">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.condition_match_all}
                onChange={(event) =>
                  setFormData((prev) => ({ ...prev, condition_match_all: event.target.checked }))
                }
              />
              Match all values
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.is_active}
                onChange={(event) =>
                  setFormData((prev) => ({ ...prev, is_active: event.target.checked }))
                }
              />
              Active
            </label>
          </div>

          {error ? (
            <div className="rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-100">
              {error}
            </div>
          ) : null}

          <div className="flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-slate-200 hover:bg-white/10"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-400"
            >
              {initialRule ? "Save changes" : "Create rule"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const RoutingRulesPanel = ({ mailbox, isAdmin, selectedMessageId }) => {
  const [rules, setRules] = useState([]);
  const [assignedBot, setAssignedBot] = useState("");
  const [botConfigText, setBotConfigText] = useState("{}");
  const [loading, setLoading] = useState(false);
  const [savingBot, setSavingBot] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [editingRule, setEditingRule] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const mailboxId = mailbox?.id;

  const selectedBotLabel = useMemo(() => {
    const match = DEFAULT_BOTS.find((bot) => bot.key === assignedBot);
    return match?.name || assignedBot || "No bot assigned";
  }, [assignedBot]);

  const loadData = useCallback(async () => {
    if (!mailboxId) return;
    setLoading(true);
    setError("");
    try {
      const [botResponse, rulesResponse] = await Promise.all([
        getAssignedBot(mailboxId),
        getRoutingRules(mailboxId),
      ]);
      setAssignedBot(botResponse?.assigned_bot_key || "");
      setBotConfigText(JSON.stringify(botResponse?.bot_config || {}, null, 2));
      setRules(Array.isArray(rulesResponse?.rules) ? rulesResponse.rules : []);
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to load routing rules.");
    } finally {
      setLoading(false);
    }
  }, [mailboxId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSaveAssignedBot = async () => {
    if (!mailboxId) return;
    try {
      setSavingBot(true);
      setError("");
      setSuccess("");
      const parsedConfig = botConfigText.trim() ? JSON.parse(botConfigText) : {};
      await assignBotToMailbox(mailboxId, assignedBot || null, parsedConfig);
      setSuccess("Mailbox bot assignment updated.");
      await loadData();
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to save mailbox bot assignment.");
    } finally {
      setSavingBot(false);
    }
  };

  const handleSaveRule = async (payload) => {
    if (!mailboxId) return;
    if (editingRule) {
      await updateRoutingRule(editingRule.id, payload);
      setEditingRule(null);
    } else {
      await createRoutingRule(mailboxId, payload);
      setShowCreateModal(false);
    }
    await loadData();
    setSuccess("Routing rule saved.");
  };

  const handleDeleteRule = async (ruleId) => {
    if (!window.confirm("Delete this routing rule?")) return;
    try {
      setError("");
      setSuccess("");
      await deleteRoutingRule(ruleId);
      await loadData();
      setSuccess("Routing rule deleted.");
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to delete rule.");
    }
  };

  const handleToggleRule = async (rule) => {
    try {
      setError("");
      setSuccess("");
      await updateRoutingRule(rule.id, { is_active: !rule.is_active });
      await loadData();
      setSuccess("Routing rule updated.");
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to update rule.");
    }
  };

  const handleManualRoute = async () => {
    if (!selectedMessageId) {
      setError("Select a message first to trigger manual routing.");
      return;
    }
    try {
      setError("");
      setSuccess("");
      const result = await manuallyRouteMessage(selectedMessageId);
      setSuccess(
        result?.assigned_bot
          ? `Manual routing completed. Assigned bot: ${result.assigned_bot}.`
          : "Manual routing completed with no bot assignment."
      );
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || "Failed to trigger manual routing.");
    }
  };

  if (!mailboxId) {
    return (
      <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-slate-300">
        Select a mailbox to manage routing rules.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="grid gap-4 lg:grid-cols-[320px_minmax(0,1fr)]">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="text-sm font-semibold text-white">Mailbox bot assignment</div>
          <div className="mt-1 text-xs text-slate-400">
            Assign a default bot for unmatched messages in {mailbox.email_address}.
          </div>

          <div className="mt-4 space-y-3">
            <label className="space-y-1 text-xs text-slate-300">
              <span>Default bot</span>
              <select
                value={assignedBot}
                onChange={(event) => setAssignedBot(event.target.value)}
                disabled={!isAdmin}
                className="w-full rounded-lg border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-white disabled:opacity-60"
              >
                <option value="">No default bot</option>
                {DEFAULT_BOTS.map((bot) => (
                  <option key={bot.key} value={bot.key}>
                    {bot.name}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-1 text-xs text-slate-300">
              <span>Bot config (JSON)</span>
              <textarea
                value={botConfigText}
                onChange={(event) => setBotConfigText(event.target.value)}
                disabled={!isAdmin}
                className="min-h-[120px] w-full rounded-lg border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-white disabled:opacity-60"
              />
            </label>

            <div className="rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2 text-xs text-slate-300">
              Current bot: <span className="font-semibold text-white">{selectedBotLabel}</span>
            </div>

            {isAdmin ? (
              <button
                onClick={handleSaveAssignedBot}
                disabled={savingBot}
                className="w-full rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-400 disabled:opacity-60"
              >
                {savingBot ? "Saving..." : "Save mailbox bot"}
              </button>
            ) : (
              <div className="rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-400">
                Read-only view. Only email admins can change mailbox bot assignments.
              </div>
            )}

            <button
              onClick={handleManualRoute}
              disabled={!isAdmin || !selectedMessageId}
              className="w-full rounded-lg border border-emerald-400/30 bg-emerald-500/10 px-4 py-2 text-sm font-semibold text-emerald-100 hover:bg-emerald-500/20 disabled:opacity-60"
            >
              Run manual routing for selected message
            </button>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="text-sm font-semibold text-white">Routing rules</div>
              <div className="text-xs text-slate-400">
                Rules are evaluated from lowest priority number to highest.
              </div>
            </div>
            {isAdmin ? (
              <button
                onClick={() => {
                  setEditingRule(null);
                  setShowCreateModal(true);
                }}
                className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white hover:bg-sky-400"
              >
                New rule
              </button>
            ) : null}
          </div>

          {error ? (
            <div className="mt-4 rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-100">
              {error}
            </div>
          ) : null}

          {success ? (
            <div className="mt-4 rounded-lg border border-emerald-400/30 bg-emerald-500/10 px-3 py-2 text-xs text-emerald-100">
              {success}
            </div>
          ) : null}

          {loading ? (
            <div className="mt-4 rounded-xl border border-white/10 bg-slate-950/60 px-3 py-6 text-sm text-slate-300">
              Loading routing rules...
            </div>
          ) : rules.length === 0 ? (
            <div className="mt-4 rounded-xl border border-dashed border-white/10 bg-slate-950/60 px-3 py-6 text-sm text-slate-400">
              No routing rules defined for this mailbox yet.
            </div>
          ) : (
            <div className="mt-4 space-y-3">
              {rules.map((rule) => (
                <div
                  key={rule.id}
                  className={`rounded-xl border px-4 py-3 ${
                    rule.is_active
                      ? "border-sky-400/20 bg-sky-500/5"
                      : "border-white/10 bg-slate-950/60"
                  }`}
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="space-y-2">
                      <div className="flex flex-wrap items-center gap-2 text-[11px] uppercase tracking-wide text-slate-400">
                        <span className="rounded-full border border-white/10 px-2 py-0.5">
                          Priority {rule.priority}
                        </span>
                        <span className="rounded-full border border-white/10 px-2 py-0.5">
                          {rule.is_active ? "Active" : "Inactive"}
                        </span>
                        <span className="rounded-full border border-white/10 px-2 py-0.5">
                          {rule.bot_key || "Mailbox default bot"}
                        </span>
                      </div>

                      <div className="text-sm text-white">
                        If <span className="font-semibold">{rule.condition_field}</span>{" "}
                        <span className="text-sky-300">{rule.condition_operator}</span>{" "}
                        <span className="font-mono text-slate-300">
                          {typeof rule.condition_value === "string"
                            ? rule.condition_value
                            : JSON.stringify(rule.condition_value)}
                        </span>
                      </div>

                      <div className="text-xs text-slate-400">
                        Action: <span className="text-slate-200">{rule.action_type}</span>
                        {rule.action_config ? (
                          <span className="ml-2 font-mono text-slate-300">
                            {JSON.stringify(rule.action_config)}
                          </span>
                        ) : null}
                      </div>

                      <div className="text-[11px] text-slate-500">
                        Matched {rule.times_matched || 0} times
                        {rule.last_matched_at ? ` • Last match ${new Date(rule.last_matched_at).toLocaleString()}` : ""}
                      </div>
                    </div>

                    {isAdmin ? (
                      <div className="flex flex-wrap items-center gap-2">
                        <button
                          onClick={() => handleToggleRule(rule)}
                          className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-200 hover:bg-white/10"
                        >
                          {rule.is_active ? "Disable" : "Enable"}
                        </button>
                        <button
                          onClick={() => setEditingRule(rule)}
                          className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-200 hover:bg-white/10"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDeleteRule(rule.id)}
                          className="rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-1.5 text-xs text-rose-100 hover:bg-rose-500/20"
                        >
                          Delete
                        </button>
                      </div>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {(showCreateModal || editingRule) && (
        <RuleModal
          initialRule={editingRule}
          onClose={() => {
            setEditingRule(null);
            setShowCreateModal(false);
          }}
          onSave={handleSaveRule}
        />
      )}
    </div>
  );
};

export default RoutingRulesPanel;
