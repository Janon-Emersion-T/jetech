import Fastify from "fastify";

const app = Fastify({ logger: false });
const jobs = [];

app.get("/health", async () => ({
  status: "online",
  service: "jarvis-automation-node",
}));

app.get("/jobs", async () => ({
  items: jobs,
}));

app.post("/jobs/browser-preview", async (request) => {
  const payload = request.body || {};
  const job = {
    id: `job-${jobs.length + 1}`,
    type: "browser_preview",
    status: "queued",
    targetUrl: payload.targetUrl || "",
    createdAt: new Date().toISOString(),
    note:
      "Playwright execution is intentionally deferred until VPS/browser credentials and live automation flows are provided.",
  };
  jobs.unshift(job);
  return { item: job };
});

app.listen({ host: "127.0.0.1", port: 9200 }).catch((error) => {
  console.error(error);
  process.exit(1);
});
