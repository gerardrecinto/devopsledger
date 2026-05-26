import type React from "react";

type DashboardSummary = {
  decision_records: number;
  changed_resources: number;
  deployment_events: number;
  incident_correlations: number;
};

type ResourceTimelineItem = {
  id: string;
  decision_record_title: string;
  address: string | null;
  resource_type: string;
  provider: string | null;
  actions: string[];
  created_at: string;
};

const emptySummary: DashboardSummary = {
  decision_records: 0,
  changed_resources: 0,
  deployment_events: 0,
  incident_correlations: 0,
};

async function getJson<T>(path: string, fallback: T): Promise<T> {
  const apiUrl = process.env.API_URL || "http://localhost:8000";
  try {
    const response = await fetch(`${apiUrl}${path}`, { cache: "no-store" });
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export default async function Home() {
  const [summary, timeline] = await Promise.all([
    getJson<DashboardSummary>("/api/v1/dashboard", emptySummary),
    getJson<ResourceTimelineItem[]>("/api/v1/resources/timeline", []),
  ]);

  return (
    <main style={styles.page}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>DevOpsLedger</h1>
          <p style={styles.subtitle}>Operational memory for infrastructure changes</p>
        </div>
        <span style={styles.badge}>Offline-first CE</span>
      </header>

      <section style={styles.metrics} aria-label="Dashboard metrics">
        <Metric label="Decision records" value={summary.decision_records} />
        <Metric label="Changed resources" value={summary.changed_resources} />
        <Metric label="Deployments" value={summary.deployment_events} />
        <Metric label="Incident links" value={summary.incident_correlations} />
      </section>

      <section style={styles.section}>
        <div style={styles.sectionHeader}>
          <h2 style={styles.heading}>Changed resource timeline</h2>
        </div>
        <div style={styles.tableWrap}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>Resource</th>
                <th style={styles.th}>Action</th>
                <th style={styles.th}>Provider</th>
                <th style={styles.th}>Decision</th>
              </tr>
            </thead>
            <tbody>
              {timeline.length === 0 ? (
                <tr>
                  <td style={styles.empty} colSpan={4}>
                    No resource changes recorded yet.
                  </td>
                </tr>
              ) : (
                timeline.map((item) => (
                  <tr key={item.id}>
                    <td style={styles.td}>
                      <strong>{item.address || item.resource_type}</strong>
                      <span style={styles.muted}>{item.resource_type}</span>
                    </td>
                    <td style={styles.td}>{item.actions.join(", ")}</td>
                    <td style={styles.td}>{item.provider || "unknown"}</td>
                    <td style={styles.td}>{item.decision_record_title}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div style={styles.metric}>
      <span style={styles.metricValue}>{value}</span>
      <span style={styles.metricLabel}>{label}</span>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  page: {
    minHeight: "100vh",
    margin: 0,
    padding: "32px",
    fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    background: "#f7f8fa",
    color: "#17202a",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "16px",
    maxWidth: "1120px",
    margin: "0 auto 28px",
  },
  title: { margin: 0, fontSize: "32px", fontWeight: 700 },
  subtitle: { margin: "6px 0 0", color: "#5b6570" },
  badge: {
    border: "1px solid #b8c7d9",
    borderRadius: "6px",
    padding: "8px 10px",
    background: "#ffffff",
    color: "#2d5f8b",
    fontSize: "14px",
  },
  metrics: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "12px",
    maxWidth: "1120px",
    margin: "0 auto 28px",
  },
  metric: {
    border: "1px solid #d8dde3",
    borderRadius: "8px",
    padding: "18px",
    background: "#ffffff",
  },
  metricValue: { display: "block", fontSize: "28px", fontWeight: 700 },
  metricLabel: { display: "block", marginTop: "4px", color: "#5b6570" },
  section: { maxWidth: "1120px", margin: "0 auto" },
  sectionHeader: { display: "flex", alignItems: "center", marginBottom: "10px" },
  heading: { margin: 0, fontSize: "20px" },
  tableWrap: {
    overflowX: "auto",
    border: "1px solid #d8dde3",
    borderRadius: "8px",
    background: "#ffffff",
  },
  table: { width: "100%", borderCollapse: "collapse", minWidth: "720px" },
  th: {
    padding: "12px 14px",
    textAlign: "left",
    color: "#5b6570",
    borderBottom: "1px solid #d8dde3",
    fontSize: "13px",
  },
  td: { padding: "14px", borderBottom: "1px solid #edf0f2", verticalAlign: "top" },
  muted: { display: "block", marginTop: "4px", color: "#6d7781", fontSize: "13px" },
  empty: { padding: "28px 14px", color: "#6d7781", textAlign: "center" },
};
