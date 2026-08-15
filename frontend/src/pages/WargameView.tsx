export default function WargameView() {
  return (
    <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2>War Gaming Engine</h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            COA-2 "Phased Block" — 500 Monte Carlo runs
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button className="btn btn--secondary btn--sm" id="btn-wg-all-runs">All Runs Heatmap</button>
          <button className="btn btn--secondary btn--sm" id="btn-wg-worst">Worst Case</button>
          <button className="btn btn--secondary btn--sm" id="btn-wg-median">Median</button>
          <button className="btn btn--primary btn--sm" id="btn-wg-run">Run Simulation</button>
        </div>
      </div>
      <div className="panel" style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <div style={{ fontSize: '3rem', marginBottom: '16px' }}>⚙</div>
          <h3 style={{ marginBottom: '8px' }}>War Gaming Engine</h3>
          <p style={{ fontSize: '0.85rem', maxWidth: '360px' }}>
            Full Monte Carlo simulation engine implemented in Phase 2.<br />
            SimPy DES + Mesa Multi-Agent Simulation with 500 parallel runs.
          </p>
          <button className="btn btn--primary" style={{ marginTop: '16px' }} id="btn-wg-phase2">Coming in Phase 2</button>
        </div>
      </div>
      <div className="panel">
        <h4 style={{ marginBottom: '8px' }}>SIMULATION STATISTICS (Demo Data)</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px', fontSize: '0.8rem' }}>
          {[['Success Rate', '84%', 'green'], ['Mean Casualties', '0.9', ''], ['P95 Timeline', '4.1h', ''], ['ROE Violations', '2%', 'green'], ['Fuel Efficiency', '72%', '']].map(([k, v, c]) => (
            <div key={k as string} className="stat-card">
              <div className="stat-card__value" style={{ fontSize: '1.5rem', color: c === 'green' ? 'var(--color-success)' : undefined }}>{v as string}</div>
              <div className="stat-card__label">{k as string}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
