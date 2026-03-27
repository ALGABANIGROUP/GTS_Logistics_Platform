import { useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "../contexts/AuthContext.jsx";
import { useRefreshSubscription } from "../contexts/UiActionsContext.jsx";
import SystemReadinessGate from "../components/SystemReadinessGate.jsx";
import RoutingRulesPanel from "../components/email/RoutingRulesPanel.jsx";
import EmailAIDashboard from "./EmailAIDashboard.jsx";
import {
  approveMessage,
  createMailbox,
  deleteMailbox,
  getMyMessage,
  getThread,
  listMailboxes,
  listMailboxRequests,
  listMessages,
  listMyMailboxes,
  listMyMessages,
  pollMailboxes,
  requestMailbox,
  approveMailboxRequest,
  rejectMailboxRequest,
  sendMessage,
  setGlobalMode,
  setMailboxMode,
  updateThread,
  updateMailbox,
} from "../services/emailCenterApi";

const MODE_OPTIONS = ["BOT", "HUMAN"];
const AUTO_REFRESH_MS = 15000;
const formatShortDate = (value) => {
  if (!value) return "n/a";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleTimeString();
};

const formatDate = (value) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
};

const EMAIL_SYNC_ROLES = new Set(["super_admin", "owner"]);

const buildSyncMessage = (result) => {
  if (!result || typeof result !== "object") {
    return "Mailbox sync completed.";
  }

  const checked = Number(result.mailboxes_checked || 0);
  const polled = Number(result.mailboxes_polled || 0);
  const processed = Number(result.processed || 0);
  const failed = Number(result.mailboxes_failed || 0);
  const skipped = result.skipped || {};
  const parts = [
    `Checked ${checked} mailbox${checked === 1 ? "" : "es"}`,
    `polled ${polled}`,
    `imported ${processed} message${processed === 1 ? "" : "s"}`,
  ];

  const missingHost = Number(skipped.missing_imap_host || 0);
  const missingCreds = Number(skipped.missing_credentials || 0);
  if (missingHost > 0) parts.push(`${missingHost} missing IMAP host`);
  if (missingCreds > 0) parts.push(`${missingCreds} missing credentials`);
  if (failed > 0) parts.push(`${failed} failed`);

  return `${parts.join(", ")}.`;
};

const Emails = () => {
  const { user, role: authRole, authReady, isAuthenticated } = useAuth();
  const role = (authRole || user?.effective_role || user?.role || "")
    .toString()
    .toLowerCase();
  // Match role hierarchy: owner/super_admin/admin can manage system mailboxes.
  const isAdmin = role === "super_admin" || role === "owner" || role === "admin";
  const canPollMailboxes = EMAIL_SYNC_ROLES.has(role);

  const [mailboxes, setMailboxes] = useState([]);
  const [selectedMailbox, setSelectedMailbox] = useState(null);
  const [messages, setMessages] = useState([]);
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [messageDetail, setMessageDetail] = useState(null);
  const [thread, setThread] = useState(null);
  const [threadMessages, setThreadMessages] = useState([]);
  const [threadDraft, setThreadDraft] = useState({
    status: "open",
    tags: "",
    priority: "",
    assigned_to_user_id: "",
  });
  const [composeOpen, setComposeOpen] = useState(false);
  const [composeForm, setComposeForm] = useState({
    to: "",
    subject: "",
    body: "",
    send: true,
  });
  const [mailboxForm, setMailboxForm] = useState({
    email_address: "",
    display_name: "",
    mode: "HUMAN",
    inbound_enabled: true,
    outbound_enabled: true,
    imap_host: "mail.gabanilogistics.com",
    imap_port: 993,
    imap_user: "",
    imap_ssl: true,
    smtp_host: "mail.gabanilogistics.com",
    smtp_port: 465,
    smtp_user: "",
    smtp_ssl: true,
  });
  const [mailboxRequests, setMailboxRequests] = useState([]);
  const [requestForm, setRequestForm] = useState({
    requested_email: "",
    desired_mode: "HUMAN",
    package_name: "",
  });
  const [activeTab, setActiveTab] = useState("inbox");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const mailboxArray = Array.isArray(mailboxes)
    ? mailboxes
    : Array.isArray(mailboxes?.mailboxes)
      ? mailboxes.mailboxes
      : Array.isArray(mailboxes?.data)
        ? mailboxes.data
        : [];
  const visibleMailboxes = useMemo(() => {
    if (!isAdmin) return mailboxArray;
    return mailboxArray.filter((mailbox) => mailbox.package_scope === "SYSTEM" && mailbox.is_enabled);
  }, [isAdmin, mailboxArray]);

  const mailboxMode = useMemo(() => selectedMailbox?.mode || "BOT", [selectedMailbox]);
  const canManageMailbox =
    isAdmin || (selectedMailbox?.owner_user_id && user?.id === selectedMailbox.owner_user_id);
  const setErrorState = (type, message) => {
    setError({ type, message });
  };

  const loadMailboxes = async () => {
    const data = isAdmin ? await listMailboxes() : await listMyMailboxes();
    setMailboxes(Array.isArray(data) ? data : []);
    const filtered = isAdmin
      ? data.filter((mailbox) => mailbox.package_scope === "SYSTEM" && mailbox.is_enabled)
      : data;
    if (!selectedMailbox && filtered.length > 0) {
      setSelectedMailbox(filtered[0]);
      return;
    }
    if (selectedMailbox && !filtered.find((mailbox) => mailbox.id === selectedMailbox.id)) {
      setSelectedMailbox(filtered[0] || null);
    }
  };

  const loadRequests = async () => {
    if (!isAdmin) return;
    const data = await listMailboxRequests();
    setMailboxRequests(data);
  };

  const loadMessages = async (mailboxId, options = {}) => {
    if (!mailboxId) return;
    const data = isAdmin
      ? await listMessages(mailboxId, { limit: 50 })
      : await listMyMessages(mailboxId, { limit: 50 });
    setMessages(data);
    if (!options.preserveSelection) {
      setSelectedMessage(null);
      setMessageDetail(null);
      setThread(null);
      setThreadMessages([]);
      return;
    }
    if (selectedMessage && !data.find((msg) => msg.id === selectedMessage.id)) {
      setSelectedMessage(null);
      setMessageDetail(null);
      setThread(null);
      setThreadMessages([]);
    }
  };

  useEffect(() => {
    if (!authReady || !isAuthenticated) {
      return undefined;
    }

    let mounted = true;
    const bootstrap = async () => {
      try {
        setLoading(true);
        await loadMailboxes();
        await loadRequests();
      } catch (err) {
        if (mounted) {
          const status = err?.response?.status;
          const message =
            err?.response?.data?.detail || err?.message || "Failed to load mailboxes.";
          setErrorState(status === 403 ? "forbidden" : "error", message);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };
    bootstrap();
    return () => {
      mounted = false;
    };
  }, [authReady, isAuthenticated, isAdmin]);

  useEffect(() => {
    if (!selectedMailbox?.id) return;
    loadMessages(selectedMailbox.id).catch((err) => {
      const status = err?.response?.status;
      const message =
        err?.response?.data?.detail || err?.message || "Failed to load messages.";
      setErrorState(status === 403 ? "forbidden" : "error", message);
    });
  }, [selectedMailbox?.id]);

  const refreshInFlight = useRef(false);
  useEffect(() => {
    if (!selectedMailbox?.id) return;
    let active = true;
    const tick = async () => {
      if (!active || refreshInFlight.current || document.hidden) return;
      refreshInFlight.current = true;
      try {
        if (canPollMailboxes) {
          await pollMailboxes();
        }
        await loadMessages(selectedMailbox.id, { preserveSelection: true });
      } catch (err) {
        const status = err?.response?.status;
        const message =
          err?.response?.data?.detail || err?.message || "Auto refresh failed.";
        setErrorState(status === 403 ? "forbidden" : "error", message);
      } finally {
        refreshInFlight.current = false;
      }
    };
    const timer = setInterval(tick, AUTO_REFRESH_MS);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [canPollMailboxes, selectedMailbox?.id]);

  useEffect(() => {
    if (!selectedMailbox) return;
    setMailboxForm((prev) => ({
      ...prev,
      email_address: selectedMailbox.email_address || prev.email_address,
      display_name: selectedMailbox.display_name || "",
      mode: selectedMailbox.mode || "HUMAN",
      inbound_enabled: selectedMailbox.inbound_enabled ?? true,
      outbound_enabled: selectedMailbox.outbound_enabled ?? true,
      imap_host: selectedMailbox.imap_host || prev.imap_host,
      imap_port: selectedMailbox.imap_port || prev.imap_port,
      imap_user: selectedMailbox.imap_user || selectedMailbox.email_address || "",
      imap_ssl: selectedMailbox.imap_ssl ?? true,
      smtp_host: selectedMailbox.smtp_host || prev.smtp_host,
      smtp_port: selectedMailbox.smtp_port || prev.smtp_port,
      smtp_user: selectedMailbox.smtp_user || selectedMailbox.email_address || "",
      smtp_ssl: selectedMailbox.smtp_ssl ?? true,
    }));
  }, [selectedMailbox?.id]);

  const refreshAll = () => {
    setError(null);
    loadMailboxes()
      .then(() => {
        if (selectedMailbox?.id) {
          return loadMessages(selectedMailbox.id);
        }
        return null;
      })
      .catch((err) => {
        const status = err?.response?.status;
        const message =
          err?.response?.data?.detail || err?.message || "Failed to refresh mailboxes.";
        setErrorState(status === 403 ? "forbidden" : "error", message);
      });

    loadRequests().catch((err) => {
      const status = err?.response?.status;
      const message =
        err?.response?.data?.detail || err?.message || "Failed to refresh requests.";
      setErrorState(status === 403 ? "forbidden" : "error", message);
    });
  };

  useRefreshSubscription(() => {
    refreshAll();
  });

  const handleSelectMailbox = (mailbox) => {
    setSelectedMailbox(mailbox);
    setMailboxForm((prev) => ({
      ...prev,
      email_address: mailbox.email_address || prev.email_address,
      display_name: mailbox.display_name || "",
      mode: mailbox.mode || "HUMAN",
      inbound_enabled: mailbox.inbound_enabled ?? true,
      outbound_enabled: mailbox.outbound_enabled ?? true,
      imap_host: mailbox.imap_host || prev.imap_host,
      imap_port: mailbox.imap_port || prev.imap_port,
      imap_user: mailbox.imap_user || mailbox.email_address || "",
      imap_ssl: mailbox.imap_ssl ?? true,
      smtp_host: mailbox.smtp_host || prev.smtp_host,
      smtp_port: mailbox.smtp_port || prev.smtp_port,
      smtp_user: mailbox.smtp_user || mailbox.email_address || "",
      smtp_ssl: mailbox.smtp_ssl ?? true,
    }));
  };

  const handleSelectMessage = async (message) => {
    setSelectedMessage(message);
    setMessageDetail(null);
    setThread(null);
    setThreadMessages([]);

    try {
      if (isAdmin) {
        if (message?.thread_id) {
          const data = await getThread(message.thread_id);
          setThread(data.thread);
          setThreadMessages(data.messages || []);
          setThreadDraft({
            status: data.thread?.status || "open",
            tags: (data.thread?.tags || []).join(", "),
            priority: data.thread?.priority || "",
            assigned_to_user_id: data.thread?.assigned_to_user_id || "",
          });
          return;
        }

        setMessageDetail(message);
        return;
      }

      const detail = await getMyMessage(message.id);
      setMessageDetail(detail);
    } catch (err) {
      const status = err?.response?.status;
      const messageText =
        err?.response?.data?.detail || err?.message || "Failed to load message.";
      setErrorState(status === 403 ? "forbidden" : "error", messageText);
    }
  };

  const handleMailboxModeChange = async (mode) => {
    if (!selectedMailbox) return;
    try {
      const updated = await setMailboxMode(selectedMailbox.id, mode);
      setMailboxes((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
      setSelectedMailbox(updated);
    } catch {
      setErrorState("error", "Failed to update mailbox mode.");
    }
  };

  const handleGlobalModeChange = async (mode) => {
    try {
      await setGlobalMode(mode);
      await loadMailboxes();
    } catch {
      setErrorState("error", "Failed to update global mode.");
    }
  };

  const handleSync = async () => {
    if (!canPollMailboxes) {
      setErrorState("forbidden", "Pull Now requires owner or super admin access.");
      return;
    }
    try {
      const result = await pollMailboxes();
      await loadMessages(selectedMailbox?.id, { preserveSelection: true });
      if (selectedMessage?.thread_id) {
        const data = await getThread(selectedMessage.thread_id);
        setThread(data.thread);
        setThreadMessages(data.messages || []);
      }
      setErrorState("info", buildSyncMessage(result));
    } catch (err) {
      const status = err?.response?.status;
      const message =
        err?.response?.data?.detail || err?.message || "Failed to sync mailboxes.";
      setErrorState(status === 403 ? "forbidden" : "error", message);
    }
  };

  const handleThreadSave = async () => {
    if (!thread?.id) return;
    try {
      const payload = {
        status: threadDraft.status || "open",
        priority: threadDraft.priority || null,
        assigned_to_user_id: threadDraft.assigned_to_user_id
          ? Number(threadDraft.assigned_to_user_id)
          : null,
        tags: threadDraft.tags
          ? threadDraft.tags.split(",").map((tag) => tag.trim()).filter(Boolean)
          : [],
      };
      const updated = await updateThread(thread.id, payload);
      setThread(updated);
    } catch {
      setErrorState("error", "Failed to update thread.");
    }
  };

  const handleApprove = async (messageId) => {
    try {
      await approveMessage(messageId);
      if (selectedMessage?.thread_id) {
        const data = await getThread(selectedMessage.thread_id);
        setThread(data.thread);
        setThreadMessages(data.messages || []);
      }
    } catch {
      setErrorState("error", "Failed to approve message.");
    }
  };

  const handleSend = async () => {
    if (!selectedMailbox) return;
    try {
      const payload = {
        mailbox_id: selectedMailbox.id,
        to: composeForm.to.split(",").map((v) => v.trim()).filter(Boolean),
        subject: composeForm.subject,
        body: composeForm.body,
        html: false,
        send: composeForm.send,
      };
      await sendMessage(payload);
      setComposeForm({ to: "", subject: "", body: "", send: true });
      setComposeOpen(false);
      await loadMessages(selectedMailbox.id);
    } catch {
      setErrorState("error", "Failed to send message.");
    }
  };

  const handleCreateMailbox = async () => {
    try {
      if (!isAdmin) {
        const result = await requestMailbox({
          requested_email: requestForm.requested_email,
          desired_mode: requestForm.desired_mode || "HUMAN",
          package_name: requestForm.package_name || undefined,
        });
        setRequestForm({ requested_email: "", desired_mode: "HUMAN", package_name: "" });
        await loadRequests();
        setErrorState(
          "info",
          `Mailbox request submitted (status: ${result?.status || "pending"}).`
        );
        return;
      }

      const payload = {
        ...mailboxForm,
        mode: mailboxForm.mode || "HUMAN",
        imap_port: Number(mailboxForm.imap_port) || 993,
        smtp_port: Number(mailboxForm.smtp_port) || 465,
      };

      const created = await createMailbox(payload);

      await loadMailboxes();
      setSelectedMailbox(created);
    } catch (err) {
      console.error(err);
      setErrorState("error", "Failed to save mailbox settings.");
    }
  };

  const handleUpdateMailbox = async () => {
    if (!selectedMailbox) return;
    try {
      const payload = {
        display_name: mailboxForm.display_name || selectedMailbox.display_name,
        mode: mailboxForm.mode || selectedMailbox.mode,
        inbound_enabled: mailboxForm.inbound_enabled,
        outbound_enabled: mailboxForm.outbound_enabled,
        imap_host: mailboxForm.imap_host,
        imap_port: Number(mailboxForm.imap_port) || 993,
        imap_user: mailboxForm.imap_user,
        imap_ssl: mailboxForm.imap_ssl,
        smtp_host: mailboxForm.smtp_host,
        smtp_port: Number(mailboxForm.smtp_port) || 465,
        smtp_user: mailboxForm.smtp_user,
        smtp_ssl: mailboxForm.smtp_ssl,
      };

      const updated = await updateMailbox(selectedMailbox.id, payload);
      setMailboxes((prev) => prev.map((m) => (m.id === updated.id ? updated : m)));
      setSelectedMailbox(updated);
    } catch (err) {
      console.error(err);
      setErrorState("error", "Failed to update mailbox.");
    }
  };

  const handleDeleteMailbox = async () => {
    if (!selectedMailbox) return;
    if (!isAdmin) return;
    try {
      await deleteMailbox(selectedMailbox.id);
      setSelectedMailbox(null);
      await loadMailboxes();
    } catch (err) {
      console.error(err);
      setErrorState("error", "Failed to delete mailbox.");
    }
  };

  const handleApproveRequest = async (requestId) => {
    try {
      await approveMailboxRequest(requestId);
      await loadRequests();
      await loadMailboxes();
    } catch (err) {
      console.error(err);
      setErrorState("error", "Failed to approve request.");
    }
  };

  const handleRejectRequest = async (requestId) => {
    try {
      await rejectMailboxRequest(requestId);
      await loadRequests();
    } catch (err) {
      console.error(err);
      setErrorState("error", "Failed to reject request.");
    }
  };

  return (
    <SystemReadinessGate>
      <div className="space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="text-2xl font-semibold text-white">Email Command Center</div>
            <div className="text-sm text-slate-300">
              Human and bot inboxes with approvals, routing, and audit history.
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="rounded-lg border border-white/10 bg-white/10 px-3 py-1.5 text-xs font-semibold text-white hover:bg-white/15"
              onClick={handleSync}
              disabled={!canPollMailboxes}
              title={!canPollMailboxes ? "Pull Now requires owner or super admin access." : undefined}
            >
              Pull Now
            </button>
            <button
              className="rounded-lg border border-white/10 bg-white/10 px-3 py-1.5 text-xs font-semibold text-white hover:bg-white/15"
              onClick={() => setComposeOpen(true)}
            >
              Compose
            </button>
          </div>
        </div>

        {error?.message ? (
          <div
            className={`rounded-xl border px-3 py-2 text-xs ${error.type === "info"
              ? "border-emerald-400/30 bg-emerald-500/10 text-emerald-100"
              : error.type === "forbidden"
                ? "border-amber-400/30 bg-amber-500/10 text-amber-100"
                : "border-red-500/30 bg-red-500/10 text-red-100"
              }`}
          >
            {error.message}
          </div>
        ) : null}

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setActiveTab("inbox")}
            className={`rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${
              activeTab === "inbox"
                ? "border-sky-400/40 bg-sky-500/10 text-white"
                : "border-white/10 bg-white/5 text-slate-300 hover:bg-white/10"
            }`}
          >
            Inbox
          </button>
          <button
            onClick={() => setActiveTab("rules")}
            className={`rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${
              activeTab === "rules"
                ? "border-sky-400/40 bg-sky-500/10 text-white"
                : "border-white/10 bg-white/5 text-slate-300 hover:bg-white/10"
            }`}
          >
            Routing Rules
          </button>
          {isAdmin ? (
            <button
              onClick={() => setActiveTab("ai-dashboard")}
              className={`rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${
                activeTab === "ai-dashboard"
                  ? "border-sky-400/40 bg-sky-500/10 text-white"
                  : "border-white/10 bg-white/5 text-slate-300 hover:bg-white/10"
              }`}
            >
              AI Dashboard
            </button>
          ) : null}
          {isAdmin ? (
            <button
              onClick={() => setActiveTab("requests")}
              className={`rounded-lg border px-3 py-1.5 text-xs font-semibold transition ${
                activeTab === "requests"
                  ? "border-sky-400/40 bg-sky-500/10 text-white"
                  : "border-white/10 bg-white/5 text-slate-300 hover:bg-white/10"
              }`}
            >
              Requests
            </button>
          ) : null}
        </div>

        {loading ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-slate-200">
            Loading mailboxes...
          </div>
        ) : activeTab === "rules" ? (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-[240px_minmax(0,1fr)]">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Mailboxes
              </div>
              <div className="mt-3 space-y-2">
                {visibleMailboxes.map((mailbox) => (
                  <button
                    key={mailbox.id}
                    onClick={() => handleSelectMailbox(mailbox)}
                    className={`w-full rounded-xl border px-3 py-2 text-left text-sm transition ${
                      selectedMailbox?.id === mailbox.id
                        ? "border-sky-400/40 bg-sky-500/10 text-white"
                        : "border-white/10 bg-white/5 text-slate-200 hover:bg-white/10"
                    }`}
                  >
                    <div className="font-semibold">{mailbox.display_name || mailbox.email_address}</div>
                    <div className="text-[11px] text-slate-400">{mailbox.email_address}</div>
                    <div className="mt-1 text-[10px] text-slate-500">
                      Owner #{mailbox.owner_user_id || "n/a"} · Mode {mailbox.mode}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <RoutingRulesPanel
              mailbox={selectedMailbox}
              isAdmin={isAdmin}
              selectedMessageId={selectedMessage?.id || null}
            />
          </div>
        ) : activeTab === "ai-dashboard" && isAdmin ? (
          <EmailAIDashboard embedded />
        ) : activeTab === "requests" && isAdmin ? null : (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-[240px_minmax(0,1fr)_minmax(0,1.1fr)]">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Mailboxes
              </div>
              <div className="mt-3 space-y-2">
                {visibleMailboxes.map((mailbox) => (
                  <button
                    key={mailbox.id}
                    onClick={() => handleSelectMailbox(mailbox)}
                    className={`w-full rounded-xl border px-3 py-2 text-left text-sm transition ${selectedMailbox?.id === mailbox.id
                      ? "border-sky-400/40 bg-sky-500/10 text-white"
                      : "border-white/10 bg-white/5 text-slate-200 hover:bg-white/10"
                      }`}
                  >
                    <div className="font-semibold">{mailbox.display_name || mailbox.email_address}</div>
                    <div className="text-[11px] text-slate-400">{mailbox.email_address}</div>
                    <div className="mt-2 flex flex-wrap items-center gap-2 text-[10px] uppercase text-slate-300">
                      <span className="inline-flex rounded-full border border-white/10 px-2 py-0.5">
                        {mailbox.mode}
                      </span>
                      <span className="inline-flex rounded-full border border-white/10 px-2 py-0.5">
                        {mailbox.is_enabled ? "Active" : "Disabled"}
                      </span>
                      {mailbox.outbound_only ? (
                        <span className="inline-flex rounded-full border border-amber-400/40 px-2 py-0.5 text-amber-200">
                          Outbound only
                        </span>
                      ) : null}
                    </div>
                    <div className="mt-1 text-[10px] text-slate-500">
                      Last polled: {formatShortDate(mailbox.last_polled_at)}
                    </div>
                    <div className="mt-1 text-[10px] text-slate-400">
                      Messages: {mailbox.message_count ?? 0} &middot; Threads: {mailbox.thread_count ?? 0}
                    </div>
                    {mailbox.last_error ? (
                      <div className="mt-1 text-[10px] text-rose-200">
                        Last error: {mailbox.last_error}
                      </div>
                    ) : null}
                  </button>
                ))}
              </div>

              {isAdmin ? (
                <div className="mt-4 border-t border-white/10 pt-4">
                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                    Global Mode
                  </div>
                  <div className="mt-2 flex gap-2">
                    {MODE_OPTIONS.map((mode) => (
                      <button
                        key={mode}
                        onClick={() => handleGlobalModeChange(mode)}
                        className="flex-1 rounded-lg border border-white/10 bg-white/5 px-2 py-1 text-[11px] font-semibold text-slate-200 hover:bg-white/10"
                      >
                        {mode}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}

              <div className="mt-4 border-t border-white/10 pt-4 space-y-3">
                <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  {isAdmin ? "Mailbox Settings (Admin)" : "Request Mailbox"}
                </div>

                {isAdmin ? (
                  <>
                    <input
                      value={mailboxForm.email_address}
                      onChange={(e) =>
                        setMailboxForm((prev) => ({ ...prev, email_address: e.target.value }))
                      }
                      placeholder="mailbox@domain.com"
                      className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                    />
                    <input
                      value={mailboxForm.display_name}
                      onChange={(e) =>
                        setMailboxForm((prev) => ({ ...prev, display_name: e.target.value }))
                      }
                      placeholder="Display name"
                      className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                    />
                    <select
                      value={mailboxForm.mode}
                      onChange={(e) =>
                        setMailboxForm((prev) => ({ ...prev, mode: e.target.value }))
                      }
                      className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                    >
                      <option value="HUMAN">HUMAN</option>
                      <option value="BOT">BOT</option>
                    </select>

                    <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-300">
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={mailboxForm.inbound_enabled}
                          onChange={(e) =>
                            setMailboxForm((prev) => ({
                              ...prev,
                              inbound_enabled: e.target.checked,
                            }))
                          }
                        />
                        Inbound
                      </label>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={mailboxForm.outbound_enabled}
                          onChange={(e) =>
                            setMailboxForm((prev) => ({
                              ...prev,
                              outbound_enabled: e.target.checked,
                            }))
                          }
                        />
                        Outbound
                      </label>
                    </div>

                    <div className="grid grid-cols-2 gap-2">
                      <input
                        value={mailboxForm.imap_host}
                        onChange={(e) =>
                          setMailboxForm((prev) => ({ ...prev, imap_host: e.target.value }))
                        }
                        placeholder="IMAP host"
                        className="rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                      />
                      <input
                        value={mailboxForm.imap_port}
                        onChange={(e) =>
                          setMailboxForm((prev) => ({ ...prev, imap_port: e.target.value }))
                        }
                        placeholder="IMAP port"
                        className="rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                      />
                    </div>
                    <input
                      value={mailboxForm.imap_user}
                      onChange={(e) =>
                        setMailboxForm((prev) => ({ ...prev, imap_user: e.target.value }))
                      }
                      placeholder="IMAP user"
                      className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                    />
                    <label className="flex items-center gap-2 text-[11px] text-slate-300">
                      <input
                        type="checkbox"
                        checked={mailboxForm.imap_ssl}
                        onChange={(e) =>
                          setMailboxForm((prev) => ({ ...prev, imap_ssl: e.target.checked }))
                        }
                      />
                      IMAP SSL/TLS
                    </label>

                    <div className="grid grid-cols-2 gap-2">
                      <input
                        value={mailboxForm.smtp_host}
                        onChange={(e) =>
                          setMailboxForm((prev) => ({ ...prev, smtp_host: e.target.value }))
                        }
                        placeholder="SMTP host"
                        className="rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                      />
                      <input
                        value={mailboxForm.smtp_port}
                        onChange={(e) =>
                          setMailboxForm((prev) => ({ ...prev, smtp_port: e.target.value }))
                        }
                        placeholder="SMTP port"
                        className="rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                      />
                    </div>
                    <input
                      value={mailboxForm.smtp_user}
                      onChange={(e) =>
                        setMailboxForm((prev) => ({ ...prev, smtp_user: e.target.value }))
                      }
                      placeholder="SMTP user"
                      className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                    />
                    <label className="flex items-center gap-2 text-[11px] text-slate-300">
                      <input
                        type="checkbox"
                        checked={mailboxForm.smtp_ssl}
                        onChange={(e) =>
                          setMailboxForm((prev) => ({ ...prev, smtp_ssl: e.target.checked }))
                        }
                      />
                      SMTP SSL/TLS
                    </label>
                  </>
                ) : (
                  <>
                    <input
                      value={requestForm.requested_email}
                      onChange={(e) =>
                        setRequestForm((prev) => ({ ...prev, requested_email: e.target.value }))
                      }
                      placeholder="request@domain.com"
                      className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                    />
                    <select
                      value={requestForm.desired_mode}
                      onChange={(e) =>
                        setRequestForm((prev) => ({ ...prev, desired_mode: e.target.value }))
                      }
                      className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                    >
                      <option value="HUMAN">HUMAN</option>
                      <option value="BOT">BOT</option>
                    </select>
                    <input
                      value={requestForm.package_name}
                      onChange={(e) =>
                        setRequestForm((prev) => ({ ...prev, package_name: e.target.value }))
                      }
                      placeholder="Package (optional)"
                      className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                    />
                  </>
                )}

                <div className="flex flex-col gap-2">
                  <button
                    onClick={handleCreateMailbox}
                    className="rounded-lg bg-sky-500 px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-sky-400"
                  >
                    {isAdmin ? "Create Mailbox" : "Request Mailbox"}
                  </button>
                  {isAdmin && selectedMailbox ? (
                    <button
                      onClick={handleUpdateMailbox}
                      disabled={!canManageMailbox}
                      className="rounded-lg border border-white/10 bg-white/10 px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-white/20 disabled:opacity-60"
                    >
                      Update Selected
                    </button>
                  ) : null}
                  {isAdmin && selectedMailbox ? (
                    <button
                      onClick={handleDeleteMailbox}
                      className="rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-1.5 text-[11px] font-semibold text-rose-200 hover:bg-rose-500/20"
                    >
                      Delete Selected
                    </button>
                  ) : null}
                </div>
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-semibold text-white">
                    {selectedMailbox?.display_name || "Messages"}
                  </div>
                  <div className="text-xs text-slate-400">
                    Mode: {mailboxMode}
                  </div>
                </div>
                <select
                  className="rounded-md border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                  value={mailboxMode}
                  onChange={(e) => handleMailboxModeChange(e.target.value)}
                  disabled={!canManageMailbox}
                >
                  {MODE_OPTIONS.map((mode) => (
                    <option key={mode} value={mode}>
                      {mode}
                    </option>
                  ))}
                </select>
              </div>

              <div className="mt-3 space-y-2">
                {messages.length === 0 ? (
                  <div className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300">
                    No messages yet.
                  </div>
                ) : (
                  messages.map((message) => (
                    <button
                      key={message.id}
                      onClick={() => handleSelectMessage(message)}
                      className={`w-full rounded-xl border px-3 py-2 text-left text-xs transition ${selectedMessage?.id === message.id
                        ? "border-sky-400/40 bg-sky-500/10 text-white"
                        : "border-white/10 bg-white/5 text-slate-200 hover:bg-white/10"
                        }`}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="font-semibold">{message.subject || "(no subject)"}</div>
                        {message.requires_approval ? (
                          <span className="rounded-full border border-amber-400/40 bg-amber-500/10 px-2 py-0.5 text-[10px] text-amber-200">
                            Approval
                          </span>
                        ) : null}
                      </div>
                      <div className="mt-1 text-[11px] text-slate-400">
                        {message.from_email || message.to_emails?.join(", ")}
                      </div>
                      <div className="mt-1 text-[10px] text-slate-500">
                        {formatDate(message.created_at)}
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              {thread && isAdmin ? (
                <>
                  <div className="text-sm font-semibold text-white">
                    {thread.subject || "Thread"}
                  </div>
                  <div className="mt-1 text-xs text-slate-400">
                    Last update: {formatDate(thread.last_message_at)}
                  </div>

                  <div className="mt-4 grid gap-3 text-xs text-slate-200">
                    <label className="space-y-1">
                      <span className="text-[11px] text-slate-400">Status</span>
                      <input
                        className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                        value={threadDraft.status}
                        onChange={(e) => setThreadDraft((prev) => ({ ...prev, status: e.target.value }))}
                      />
                    </label>
                    <label className="space-y-1">
                      <span className="text-[11px] text-slate-400">Tags</span>
                      <input
                        className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                        value={threadDraft.tags}
                        onChange={(e) => setThreadDraft((prev) => ({ ...prev, tags: e.target.value }))}
                        placeholder="urgent, finance"
                      />
                    </label>
                    <label className="space-y-1">
                      <span className="text-[11px] text-slate-400">Priority</span>
                      <input
                        className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                        value={threadDraft.priority}
                        onChange={(e) => setThreadDraft((prev) => ({ ...prev, priority: e.target.value }))}
                      />
                    </label>
                    <label className="space-y-1">
                      <span className="text-[11px] text-slate-400">Assigned User ID</span>
                      <input
                        className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-2 py-1 text-xs text-white"
                        value={threadDraft.assigned_to_user_id}
                        onChange={(e) =>
                          setThreadDraft((prev) => ({ ...prev, assigned_to_user_id: e.target.value }))
                        }
                      />
                    </label>
                    <button
                      onClick={handleThreadSave}
                      className="rounded-lg border border-sky-400/40 bg-sky-500/10 px-3 py-2 text-xs font-semibold text-sky-100 hover:bg-sky-500/20"
                    >
                      Save Thread
                    </button>
                  </div>

                  <div className="mt-4 space-y-3">
                    {threadMessages.map((msg) => (
                      <div key={msg.id} className="glass-card p-3">
                        <div className="flex items-center justify-between text-[11px] text-slate-400">
                          <span>{msg.direction?.toUpperCase()}</span>
                          <span>{formatDate(msg.created_at)}</span>
                        </div>
                        <div className="mt-2 text-sm text-white">{msg.subject || "(no subject)"}</div>
                        <div className="mt-2 text-xs text-slate-200 whitespace-pre-wrap">
                          {msg.body_text || msg.body_html || ""}
                        </div>
                        {msg.requires_approval ? (
                          <button
                            className="mt-3 rounded-lg border border-amber-400/40 bg-amber-500/10 px-3 py-1 text-[11px] font-semibold text-amber-200 hover:bg-amber-500/20"
                            onClick={() => handleApprove(msg.id)}
                          >
                            Approve and Send
                          </button>
                        ) : null}
                      </div>
                    ))}
                  </div>
                </>
              ) : messageDetail ? (
                <div className="space-y-3">
                  <div className="text-sm font-semibold text-white">
                    {messageDetail.subject || "(no subject)"}
                  </div>
                  <div className="text-xs text-slate-400">
                    From: {messageDetail.from_email || "Unknown"}
                  </div>
                  <div className="text-xs text-slate-400">
                    Received: {formatDate(messageDetail.received_at || messageDetail.created_at)}
                  </div>
                  <div className="glass-card p-3 text-xs text-slate-200">
                    {messageDetail.body_preview || "No preview available."}
                  </div>
                </div>
              ) : (
                <div className="text-xs text-slate-400">Select a message to view details.</div>
              )}
            </div>
          </div>
        )}

        {composeOpen && activeTab === "inbox" ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="text-sm font-semibold text-white">Compose Message</div>
            <div className="mt-3 grid gap-3 text-xs text-slate-200">
              <input
                className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-3 py-2 text-xs text-white"
                placeholder="To (comma separated)"
                value={composeForm.to}
                onChange={(e) => setComposeForm((prev) => ({ ...prev, to: e.target.value }))}
              />
              <input
                className="w-full rounded-lg border border-white/10 bg-slate-900/60 px-3 py-2 text-xs text-white"
                placeholder="Subject"
                value={composeForm.subject}
                onChange={(e) => setComposeForm((prev) => ({ ...prev, subject: e.target.value }))}
              />
              <textarea
                className="min-h-[120px] w-full rounded-lg border border-white/10 bg-slate-900/60 px-3 py-2 text-xs text-white"
                placeholder="Message body"
                value={composeForm.body}
                onChange={(e) => setComposeForm((prev) => ({ ...prev, body: e.target.value }))}
              />
              <label className="flex items-center gap-2 text-[11px] text-slate-300">
                <input
                  type="checkbox"
                  checked={composeForm.send}
                  onChange={(e) => setComposeForm((prev) => ({ ...prev, send: e.target.checked }))}
                />
                Send immediately (unchecked = draft)
              </label>
              <div className="flex items-center gap-2">
                <button
                  onClick={handleSend}
                  className="rounded-lg border border-emerald-400/40 bg-emerald-500/10 px-3 py-2 text-xs font-semibold text-emerald-100 hover:bg-emerald-500/20"
                >
                  Submit
                </button>
                <button
                  onClick={() => setComposeOpen(false)}
                  className="rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-xs font-semibold text-slate-200 hover:bg-white/10"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        ) : null}
        {isAdmin && activeTab === "requests" ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
            <div className="text-sm font-semibold text-white">Pending mailbox requests</div>
            <div className="mt-3 space-y-2">
              {mailboxRequests.length === 0 ? (
                <div className="text-xs text-slate-400">No pending requests.</div>
              ) : (
                mailboxRequests
                  .filter((req) => req.status === "pending")
                  .map((req) => (
                    <div
                      key={req.id}
                      className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-white/10 bg-slate-950/60 px-3 py-2 text-xs text-slate-200"
                    >
                      <div>
                        <div className="font-semibold">{req.requested_email}</div>
                        <div className="text-[11px] text-slate-400">
                          Requested by #{req.requester_user_id} · {req.desired_mode}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleApproveRequest(req.id)}
                          className="rounded-lg border border-emerald-400/40 bg-emerald-500/10 px-2 py-1 text-[11px] font-semibold text-emerald-100 hover:bg-emerald-500/20"
                        >
                          Approve
                        </button>
                        <button
                          onClick={() => handleRejectRequest(req.id)}
                          className="rounded-lg border border-rose-400/40 bg-rose-500/10 px-2 py-1 text-[11px] font-semibold text-rose-100 hover:bg-rose-500/20"
                        >
                          Reject
                        </button>
                      </div>
                    </div>
                  ))
              )}
            </div>
          </div>
        ) : null}
      </div>
    </SystemReadinessGate>
  );
};

export default Emails;
