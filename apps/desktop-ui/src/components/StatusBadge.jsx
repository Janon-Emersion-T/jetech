const toneMap = {
  ok: "bg-emerald-400/15 text-emerald-200 ring-1 ring-emerald-300/20",
  warn: "bg-amber-400/15 text-amber-100 ring-1 ring-amber-300/20",
  danger: "bg-rose-400/15 text-rose-100 ring-1 ring-rose-300/20",
  info: "bg-sky-400/15 text-sky-100 ring-1 ring-sky-300/20",
};

export function StatusBadge({ label, tone = "info" }) {
  return (
    <span className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${toneMap[tone] || toneMap.info}`}>
      {label}
    </span>
  );
}
