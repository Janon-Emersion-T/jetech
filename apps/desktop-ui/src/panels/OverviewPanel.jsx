import { PanelCard } from "../components/PanelCard";
import { StatusBadge } from "../components/StatusBadge";

function SummaryStat({ label, value, note }) {
  return (
    <div className="rounded-2xl border border-line/60 bg-slate-950/20 p-4">
      <div className="text-xs uppercase tracking-[0.2em] text-slate-400">{label}</div>
      <div className="mt-2 text-2xl font-semibold text-slate-50">{value}</div>
      <div className="mt-1 text-sm text-slate-400">{note}</div>
    </div>
  );
}

export function OverviewPanel({ overview }) {
  const reports = overview.reports || {};
  const stopState = overview.emergency_stop_active ? "Active" : "Ready";

  return (
    <div className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr]">
      <PanelCard
        title="Operations Readiness"
        subtitle="Local-first execution with explicit production approval controls."
      >
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <SummaryStat label="Customers" value={overview.customer_count} note="Lifecycle records owned by LKProfessionals" />
          <SummaryStat label="Projects" value={overview.project_count} note="Each project isolated for compute, DB, logs, and backups" />
          <SummaryStat label="Pending Approvals" value={overview.pending_approvals} note="Strict token confirmation required" />
          <SummaryStat label="Emergency State" value={stopState} note="STOP JARVIS immediately pauses guarded execution" />
        </div>
      </PanelCard>

      <PanelCard title="Latest Reporting" subtitle="Prepared for future WhatsApp delivery cadence.">
        <div className="space-y-3">
          {["critical", "hourly", "daily", "weekly"].map((kind) => (
            <div key={kind} className="rounded-2xl border border-line/60 bg-slate-950/20 p-4">
              <div className="flex items-center justify-between">
                <div className="text-sm font-medium capitalize text-slate-100">{kind}</div>
                <StatusBadge
                  label={reports[kind]?.status || "missing"}
                  tone={reports[kind] ? "ok" : "warn"}
                />
              </div>
              <p className="mt-2 text-sm text-slate-400">
                {reports[kind]?.summary || "No report recorded yet."}
              </p>
            </div>
          ))}
        </div>
      </PanelCard>
    </div>
  );
}
