export default function Home() {
  return (
    <main style={{ fontFamily: "system-ui, sans-serif", maxWidth: 800, margin: "0 auto", padding: "2rem" }}>
      <h1>DevOpsLedger</h1>
      <p>Operational memory layer for GitOps teams.</p>
      <p>
        Every infrastructure change becomes a decision record: intent, diff, risk,
        approval, rollback readiness, deployment, and learning.
      </p>
      <section>
        <h2>Self-hosted. No required SaaS. No telemetry.</h2>
        <ul>
          <li>Runs entirely on-prem</li>
          <li>All integrations optional and disabled by default</li>
          <li>Open source</li>
          <li>Works in air-gapped environments</li>
        </ul>
      </section>
      <section>
        <h2>Status</h2>
        <p>Early development. API at <code>/health</code>.</p>
      </section>
    </main>
  );
}
