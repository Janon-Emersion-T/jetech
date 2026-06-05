import { PanelCard } from "../components/PanelCard";
import { StatusBadge } from "../components/StatusBadge";

export function ProjectsPanel({ projects = [] }) {
  return (
    <PanelCard title="Client Projects" subtitle="Tenant-isolated projects with deployment readiness metadata.">
      <div className="space-y-3">
        {projects.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-line/80 p-6 text-sm text-slate-400">
            No projects recorded yet.
          </div>
        ) : (
          projects.map((project) => (
            <div key={project.id} className="rounded-2xl border border-line/60 bg-slate-950/20 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h3 className="text-base font-semibold text-slate-50">{project.name}</h3>
                  <p className="text-sm text-slate-400">{project.stack || "Stack not set"}</p>
                </div>
                <StatusBadge label={project.status} tone={project.status === "active" ? "ok" : "info"} />
              </div>
              <div className="mt-3 grid gap-3 text-sm text-slate-300 md:grid-cols-4">
                <div>Container: {project.container_name || "planned"}</div>
                <div>Database: {project.database_name || "planned"}</div>
                <div>Ingress: {project.ingress_host || "planned"}</div>
                <div>SSL: {project.ssl_status || "pending"}</div>
              </div>
            </div>
          ))
        )}
      </div>
    </PanelCard>
  );
}
