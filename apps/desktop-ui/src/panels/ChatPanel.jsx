import { PanelCard } from "../components/PanelCard";

export function ChatPanel({ messages, input, onInputChange, onSend, loading }) {
  return (
    <PanelCard title="Brain Console" subtitle="Operational chat backed by decision memory and business context.">
      <div className="grid gap-4">
        <div className="max-h-[26rem] space-y-3 overflow-auto rounded-2xl border border-line/60 bg-slate-950/20 p-4">
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`rounded-2xl px-4 py-3 text-sm ${
                message.role === "user"
                  ? "ml-auto max-w-[80%] bg-accent/20 text-sky-50"
                  : "max-w-[85%] bg-slate-900/80 text-slate-200"
              }`}
            >
              {message.text}
            </div>
          ))}
        </div>
        <div className="flex gap-3">
          <input
            value={input}
            onChange={(event) => onInputChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                onSend();
              }
            }}
            className="flex-1 rounded-2xl border border-line/80 bg-slate-950/20 px-4 py-3 text-sm text-slate-100 outline-none ring-0 placeholder:text-slate-500"
            placeholder="Ask Jarvis about projects, approvals, or deployments..."
          />
          <button
            onClick={onSend}
            disabled={loading}
            className="rounded-2xl bg-accent px-5 py-3 text-sm font-semibold text-slate-950 transition disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>
    </PanelCard>
  );
}
