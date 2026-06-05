import { PanelCard } from "../components/PanelCard";
import { StatusBadge } from "../components/StatusBadge";

export function ApprovalsPanel({ approvals = [], onCreateDemoApproval }) {
  return (
    <PanelCard
      title="Approvals"
      subtitle="Production, legal, and purchase actions must wait for strict WhatsApp approval tokens."
      actions={
        <button
          className="rounded-full bg-accent px-4 py-2 text-sm font-semibold text-slate-950 transition hover:opacity-90"
          onClick={onCreateDemoApproval}
        >
          Create Sample Approval
        </button>
      }
    >
      <div className="space-y-3">
        {approvals.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-line/80 p-6 text-sm text-slate-400">
            No pending approvals.
          </div>
        ) : (
          approvals.map((approval) => (
            <div key={approval.id} className="rounded-2xl border border-line/60 bg-slate-950/20 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="font-semibold text-slate-50">{approval.token}</div>
                <StatusBadge label={approval.status} tone={approval.status === "pending" ? "warn" : "ok"} />
              </div>
              <p className="mt-2 text-sm text-slate-300">{approval.action_summary}</p>
              <p className="mt-2 text-xs text-slate-500">
                Approve format: `APPROVE {approval.token}` | Reject format: `REJECT {approval.token}`
              </p>
            </div>
          ))
        )}
      </div>
    </PanelCard>
  );
}
