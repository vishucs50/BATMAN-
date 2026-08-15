import BatmanMap from '../components/map/BatmanMap'

// Inline stat and alert components for Phase 0

const stats = [
  { label: 'Active Units', value: '12', sub: '11 operational' },
  { label: 'Threat Prob.', value: '87%', sub: 'HIGH confidence', accent: true },
  { label: 'Mission Phase', value: '2 / 4', sub: 'Cordon' },
  { label: 'H+ Time', value: '02:47', sub: 'elapsed', mono: true },
]

const alerts = [
  { type: 'warning', title: 'Comms Degraded', msg: 'Sector-3 ↔ HQ — 12min ago' },
  { type: 'success', title: 'ALPHA: Objective Reached', msg: '08min ago' },
  { type: 'info',    title: 'Weather Update', msg: 'Visibility report in 30min' },
]

export default function CommandView() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gridTemplateRows: '1fr 180px', height: '100%', gap: '8px', padding: '8px', overflow: 'hidden' }}>

      {/* ── MAP (main) ─────────────────────────────────────── */}
      <div style={{ gridRow: '1', gridColumn: '1', borderRadius: '8px', overflow: 'hidden', background: '#0d1117' }}>
        <BatmanMap center={[76.9, 34.2]} zoom={10} />
      </div>

      {/* ── RIGHT PANEL ────────────────────────────────────── */}
      <div style={{ gridRow: '1', gridColumn: '2', display: 'flex', flexDirection: 'column', gap: '8px', overflow: 'hidden' }}>

        {/* Situation Summary */}
        <div className="panel" style={{ flex: 'none' }}>
          <div className="panel-header">
            <h4>SITUATION</h4>
            <span className="badge badge--red">HIGH THREAT</span>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            {stats.map(s => (
              <div key={s.label} className="stat-card">
                <div className="stat-card__value" style={{ fontSize: '1.4rem', color: s.accent ? 'var(--color-danger)' : undefined, fontFamily: s.mono ? 'var(--font-mono)' : undefined }}>
                  {s.value}
                </div>
                <div className="stat-card__label">{s.label}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{s.sub}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Active COA */}
        <div className="panel" style={{ flex: 'none' }}>
          <div className="panel-header">
            <h4>ACTIVE COA</h4>
            <span className="badge badge--green">COA-2</span>
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
            "Phased Block" — Balanced approach
          </div>
          <div className="progress-bar">
            <div className="progress-bar__fill" style={{ width: '62%' }} />
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '4px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            <span>Phase 2 / 4</span>
            <span>H+1:00 to Objective</span>
          </div>
          <div style={{ display: 'flex', gap: '6px', marginTop: '10px' }}>
            <button className="btn btn--secondary btn--sm" id="btn-override-coa">OVERRIDE</button>
            <button className="btn btn--danger btn--sm" id="btn-emergency-replan">EMERGENCY RPL</button>
          </div>
        </div>

        {/* Alerts */}
        <div className="panel" style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div className="panel-header">
            <h4>ALERTS</h4>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>3 active</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', overflowY: 'auto' }}>
            {alerts.map((a, i) => (
              <div key={i} className={`alert-item alert-item--${a.type}`}>
                <div>
                  <div style={{ fontWeight: 600, fontSize: '0.8rem' }}>{a.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{a.msg}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── BOTTOM STRIP ───────────────────────────────────── */}
      <div style={{ gridRow: '2', gridColumn: '1 / -1', display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '8px' }}>

        {/* Risk Radar placeholder */}
        <div className="panel" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <h4>RISK FACTORS</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {[['Terrain', 0.65], ['Threat', 0.83], ['Logistics', 0.41], ['Comms', 0.71]].map(([label, val]) => (
              <div key={label as string} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.75rem' }}>
                <span style={{ width: '70px', color: 'var(--text-secondary)', flexShrink: 0 }}>{label as string}</span>
                <div className="progress-bar" style={{ height: '4px', flex: 1 }}>
                  <div className="progress-bar__fill" style={{
                    width: `${(val as number) * 100}%`,
                    background: (val as number) > 0.7 ? 'var(--color-danger)' : (val as number) > 0.5 ? 'var(--color-warning)' : 'var(--color-success)'
                  }} />
                </div>
                <span style={{ fontFamily: 'var(--font-mono)', width: '30px', textAlign: 'right', color: 'var(--text-primary)', fontSize: '0.7rem' }}>
                  {Math.round((val as number) * 100)}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Unit Status */}
        <div className="panel">
          <h4 style={{ marginBottom: '8px' }}>UNIT STATUS</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {[
              { id: 'ALPHA', label: 'Alpha Coy', status: 'GREEN' as const },
              { id: 'BRAVO', label: 'Bravo Coy', status: 'AMBER' as const },
              { id: 'QRT-1', label: 'QRT North',  status: 'GREEN' as const },
              { id: 'MRT-1', label: 'Med Team',   status: 'GREEN' as const },
            ].map(u => (
              <div key={u.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem' }}>
                <span className={`readiness-dot readiness-dot--${u.status}`} />
                <span style={{ flex: 1, color: 'var(--text-secondary)' }}>{u.label}</span>
                <span className={`badge badge--${u.status === 'GREEN' ? 'green' : u.status === 'AMBER' ? 'amber' : 'red'}`}>
                  {u.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="panel">
          <h4 style={{ marginBottom: '8px' }}>QUICK ACTIONS</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
            <button className="btn btn--secondary btn--sm" id="btn-generate-coa">Generate COA</button>
            <button className="btn btn--secondary btn--sm" id="btn-run-wargame">Run Wargame</button>
            <button className="btn btn--secondary btn--sm" id="btn-threat-assess">Threat Assess</button>
            <button className="btn btn--secondary btn--sm" id="btn-what-if">What-If</button>
            <button className="btn btn--primary btn--sm" id="btn-approve-coa" style={{ gridColumn: '1/-1' }}>Approve COA-2 ✓</button>
          </div>
        </div>
      </div>
    </div>
  )
}
