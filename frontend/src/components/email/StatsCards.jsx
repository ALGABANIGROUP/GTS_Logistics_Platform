/* eslint-disable react/prop-types */
const cardBase =
  "rounded-2xl border border-white/10 bg-white/5 p-4 shadow-[0_12px_40px_rgba(15,23,42,0.18)]";

const formatPercent = (value) => `${Math.round((Number(value) || 0) * 100)}%`;

export default function StatsCards({ botStats, trends, decisions }) {
  const totalFeedback = botStats?.summary?.total_feedback || 0;
  const averageAccuracy = botStats?.summary?.average_accuracy || 0;
  const analyzedMessages = trends?.summary?.analyzed_messages || 0;
  const routedMessages = decisions?.summary?.routed_messages || 0;

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div className={cardBase}>
        <div className="text-xs uppercase tracking-[0.18em] text-slate-400">Bot Accuracy</div>
        <div className="mt-3 text-3xl font-semibold text-white">{formatPercent(averageAccuracy)}</div>
        <div className="mt-1 text-sm text-slate-300">Average measured accuracy across active bot feedback.</div>
      </div>
      <div className={cardBase}>
        <div className="text-xs uppercase tracking-[0.18em] text-slate-400">Feedback Volume</div>
        <div className="mt-3 text-3xl font-semibold text-white">{totalFeedback}</div>
        <div className="mt-1 text-sm text-slate-300">Validated learning events stored for routing decisions.</div>
      </div>
      <div className={cardBase}>
        <div className="text-xs uppercase tracking-[0.18em] text-slate-400">Analyzed Emails</div>
        <div className="mt-3 text-3xl font-semibold text-white">{analyzedMessages}</div>
        <div className="mt-1 text-sm text-slate-300">Messages with AI or heuristic analysis snapshots.</div>
      </div>
      <div className={cardBase}>
        <div className="text-xs uppercase tracking-[0.18em] text-slate-400">Routed Messages</div>
        <div className="mt-3 text-3xl font-semibold text-white">{routedMessages}</div>
        <div className="mt-1 text-sm text-slate-300">Messages routed through rule, AI, or mailbox defaults.</div>
      </div>
    </div>
  );
}
