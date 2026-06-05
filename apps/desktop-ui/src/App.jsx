import { useEffect, useState } from "react";
import { AlertTriangle, Bot, FolderKanban, LayoutDashboard, ScrollText, ShieldCheck } from "lucide-react";
import { apiGet, apiPost } from "./lib/api";
import { OverviewPanel } from "./panels/OverviewPanel";
import { ProjectsPanel } from "./panels/ProjectsPanel";
import { ApprovalsPanel } from "./panels/ApprovalsPanel";
import { ChatPanel } from "./panels/ChatPanel";
import { ContractsPanel } from "./panels/ContractsPanel";
import { StatusBadge } from "./components/StatusBadge";

const navItems = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "projects", label: "Projects", icon: FolderKanban },
  { id: "approvals", label: "Approvals", icon: ShieldCheck },
  { id: "chat", label: "Brain", icon: Bot },
  { id: "contracts", label: "Contracts", icon: ScrollText },
];

const startupMessage = {
  role: "jarvis",
  text:
    "Jarvis v2 is online. The desktop is now focused on business operations, approval discipline, and deployment-safe project management.",
};

function App() {
  const [activeView, setActiveView] = useState("overview");
  const [overview, setOverview] = useState({
    customer_count: 0,
    project_count: 0,
    pending_approvals: 0,
    emergency_stop_active: false,
    reports: {},
  });
  const [projects, setProjects] = useState([]);
  const [approvals, setApprovals] = useState([]);
  const [contracts, setContracts] = useState({});
  const [messages, setMessages] = useState([startupMessage]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function loadDashboard() {
    try {
      const [overviewData, projectsData, approvalsData, contractsData] = await Promise.all([
        apiGet("/api/v1/system/overview"),
        apiGet("/api/v1/projects"),
        apiGet("/api/v1/approvals/pending"),
        apiGet("/api/v1/contracts"),
      ]);
      setOverview(overviewData);
      setProjects(projectsData.items || []);
      setApprovals(approvalsData.items || []);
      setContracts(contractsData);
      setError("");
    } catch (loadError) {
      setError(loadError.message);
    }
  }

  useEffect(() => {
    loadDashboard();
    const timer = window.setInterval(loadDashboard, 20000);
    return () => window.clearInterval(timer);
  }, []);

  async function handleSend() {
    const trimmed = input.trim();
    if (!trimmed) {
      return;
    }
    setLoading(true);
    setMessages((current) => [...current, { role: "user", text: trimmed }]);
    setInput("");

    try {
      const data = await apiPost("/api/v1/chat", { message: trimmed });
      setMessages((current) => [...current, { role: "jarvis", text: data.response }]);
      setError("");
    } catch (sendError) {
      setMessages((current) => [
        ...current,
        { role: "jarvis", text: "The brain API is unavailable right now. Check local services." },
      ]);
      setError(sendError.message);
    } finally {
      setLoading(false);
    }
  }

  async function createSampleApproval() {
    try {
      await apiPost("/api/v1/approvals/request", {
        action_type: "production_deploy",
        action_summary: "Deploy LKProfessionals demo build to staging review environment.",
        risk_level: "high",
        target_environment: "staging",
      });
      await loadDashboard();
      await window.jarvisDesktop?.notify?.({
        title: "Jarvis Approval Created",
        body: "A new approval token is waiting for confirmation.",
      });
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  const activeNav = navItems.find((item) => item.id === activeView);

  return (
    <div className="min-h-screen bg-transparent text-slate-100">
      <div className="mx-auto grid min-h-screen max-w-[1600px] gap-6 p-6 lg:grid-cols-[280px_1fr]">
        <aside className="rounded-[2rem] border border-line/70 bg-panel/85 p-5 shadow-glow backdrop-blur">
          <div>
            <div className="text-xs uppercase tracking-[0.25em] text-accent">LKProfessionals</div>
            <h1 className="mt-3 text-3xl font-semibold text-white">Jarvis v2</h1>
            <p className="mt-3 text-sm leading-6 text-slate-400">
              Local-first business operating system with guarded automation and approval discipline.
            </p>
          </div>

          <div className="mt-6 rounded-3xl border border-line/70 bg-slate-950/20 p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-300">Emergency stop</span>
              <StatusBadge
                label={overview.emergency_stop_active ? "active" : "ready"}
                tone={overview.emergency_stop_active ? "danger" : "ok"}
              />
            </div>
            <p className="mt-3 text-sm text-slate-500">
              Accepts strict command `STOP JARVIS` and blocks protected execution until resumed.
            </p>
          </div>

          <nav className="mt-6 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = item.id === activeView;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveView(item.id)}
                  className={`flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left transition ${
                    isActive
                      ? "bg-accent text-slate-950"
                      : "bg-transparent text-slate-300 hover:bg-slate-900/50"
                  }`}
                >
                  <Icon size={18} />
                  <span className="font-medium">{item.label}</span>
                </button>
              );
            })}
          </nav>
        </aside>

        <main className="space-y-6">
          <header className="rounded-[2rem] border border-line/70 bg-panel/70 px-6 py-5 backdrop-blur">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <div className="text-xs uppercase tracking-[0.2em] text-slate-500">Active View</div>
                <div className="mt-2 flex items-center gap-3">
                  {activeNav ? <activeNav.icon size={22} className="text-accent" /> : null}
                  <h2 className="text-2xl font-semibold text-white">{activeNav?.label}</h2>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <StatusBadge label="Brain API local" tone="ok" />
                <StatusBadge label="K3s-ready design" tone="info" />
              </div>
            </div>
            {error ? (
              <div className="mt-4 flex items-center gap-3 rounded-2xl border border-rose-400/20 bg-rose-400/10 px-4 py-3 text-sm text-rose-100">
                <AlertTriangle size={16} />
                <span>{error}</span>
              </div>
            ) : null}
          </header>

          {activeView === "overview" ? <OverviewPanel overview={overview} /> : null}
          {activeView === "projects" ? <ProjectsPanel projects={projects} /> : null}
          {activeView === "approvals" ? (
            <ApprovalsPanel approvals={approvals} onCreateDemoApproval={createSampleApproval} />
          ) : null}
          {activeView === "chat" ? (
            <ChatPanel
              messages={messages}
              input={input}
              onInputChange={setInput}
              onSend={handleSend}
              loading={loading}
            />
          ) : null}
          {activeView === "contracts" ? <ContractsPanel contracts={contracts} /> : null}
        </main>
      </div>
    </div>
  );
}

export default App;
