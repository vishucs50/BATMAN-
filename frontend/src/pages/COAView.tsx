// COA Comparison View — Phase 0 skeleton (full AI in Phase 1)
const coas = [
  { num: 1, name: 'Bold Cordon', style: 'bold', success: 71, cas: '1.8 (σ=1.1)', time: '2.5h', risk: 'HIGH', topRisk: 'N-flank escape P=0.31', fuel: 85 },
  { num: 2, name: 'Phased Block', style: 'balanced', success: 84, cas: '0.9 (σ=0.7)', time: '3.2h', risk: 'MEDIUM', topRisk: 'Timing delay P=0.18', fuel: 72, recommended: true },
  { num: 3, name: 'Aerial First', style: 'cautious', success: 67, cas: '2.1 (σ=1.4)', time: '2.0h', risk: 'HIGH', topRisk: 'Weather window P=0.39', fuel: 90 },
]
export default function COAView() {
  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px', height: '100%', overflow: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2>Course of Action Comparison</h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>Mission: CI-KARGIL-2026-0815 • 500 Monte Carlo runs per COA</p>
        </div>
        <button className="btn btn--primary" id="btn-generate-new-coas">Generate New COAs</button>
      </div>
      <div className="grid-3">
        {coas.map(c => (
          <div key={c.num} className={`coa-card coa-card--${c.style} ${c.recommended ? 'coa-card--selected' : ''}`} id={`coa-card-${c.num}`}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3>COA-{c.num}: "{c.name}"</h3>
              {c.recommended && <span className="badge badge--amber">★ RECOMMENDED</span>}
            </div>
            <div className="divider" />
            {[['Success Rate', `${c.success}%`], ['Exp. Casualties', c.cas], ['Timeline', c.time], ['Fuel Used', `${c.fuel}%`]].map(([k, v]) => (
              <div key={k as string} className="coa-metric">
                <span>{k as string}</span>
                <span className="coa-metric-value">{v as string}</span>
              </div>
            ))}
            <div className="divider" />
            <div>
              <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>TOP RISK</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--color-danger)' }}>{c.topRisk}</div>
            </div>
            <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
              <button className="btn btn--secondary btn--sm" style={{ flex: 1 }} id={`btn-simulate-coa${c.num}`}>SIMULATE</button>
              <button className={`btn btn--sm ${c.recommended ? 'btn--primary' : 'btn--secondary'}`} style={{ flex: 1 }} id={`btn-select-coa${c.num}`}>
                {c.recommended ? 'SELECT ★' : 'SELECT'}
              </button>
            </div>
          </div>
        ))}
      </div>
      <div className="panel">
        <h4 style={{ marginBottom: '8px' }}>AI REASONING — Why COA-2 is recommended</h4>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          <div><strong style={{ color: 'var(--text-primary)' }}>Primary:</strong> Highest success rate (84%) across 500 simulation runs</div>
          <div><strong style={{ color: 'var(--text-primary)' }}>Trade-off:</strong> 42 min longer than COA-1 (acceptable for reduced casualty risk)</div>
          <div><strong style={{ color: 'var(--text-primary)' }}>Precedent:</strong> Similar to CI-BARAMULLA-2024 [OUTCOME: SUCCESS]</div>
        </div>
        <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
          <button className="btn btn--secondary btn--sm" id="btn-expand-reasoning">Expand Reasoning</button>
          <button className="btn btn--secondary btn--sm" id="btn-show-simulation">Show Simulation</button>
          <button className="btn btn--secondary btn--sm" id="btn-adjust-weights">Adjust Weights</button>
          <div style={{ flex: 1 }} />
          <button className="btn btn--primary" id="btn-approve-coa2">APPROVE COA-2</button>
        </div>
      </div>
    </div>
  )
}
