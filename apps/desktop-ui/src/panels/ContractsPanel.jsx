import { PanelCard } from "../components/PanelCard";

export function ContractsPanel({ contracts }) {
  return (
    <PanelCard title="Service Contracts" subtitle="Integration boundaries between desktop, Python, Rust, and Node services.">
      <pre className="overflow-auto rounded-2xl border border-line/60 bg-slate-950/40 p-4 text-xs leading-6 text-slate-300">
        {JSON.stringify(contracts, null, 2)}
      </pre>
    </PanelCard>
  );
}
