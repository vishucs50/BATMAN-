const units = [
  { id: 'ALPHA', name: 'Alpha Coy', fuel: 82, ammo: 91 },
  { id: 'BRAVO', name: 'Bravo Coy', fuel: 64, ammo: 78 },
  { id: 'CHARLIE', name: 'Charlie Coy', fuel: 91, ammo: 88 },
  { id: 'DELTA', name: 'Delta Sec', fuel: 41, ammo: 95, critical: true },
]
export default function LogisticsView() {
  return (
    <div style={{ padding: '16px', height: '100%', overflow: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <h2>Logistics Dashboard</h2>
      <div className="panel">
        <div className="panel-header"><h4>FUEL STATUS</h4><span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>72h forecast active</span></div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {units.map(u => (
            <div key={u.id} style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <span style={{ width: '90px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{u.name}</span>
              <div className="progress-bar" style={{ flex: 1 }}>
                <div className={`progress-bar__fill ${u.fuel < 50 ? 'progress-bar__fill--danger' : u.fuel < 70 ? 'progress-bar__fill--warning' : ''}`} style={{ width: `${u.fuel}%` }} />
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', width: '35px', textAlign: 'right' }}>{u.fuel}%</span>
              {u.critical && <span className="badge badge--red">CRITICAL</span>}
            </div>
          ))}
        </div>
        <div className="alert-item alert-item--warning" style={{ marginTop: '12px' }}>
          <div><strong>⚠ AI Advisory:</strong> DELTA reaches 20% at H+2:15. Pre-position fuel at Grid 4412 by H+1:45.</div>
        </div>
      </div>
      <div className="panel">
        <div className="panel-header"><h4>AMMUNITION STATE</h4></div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {[['INSAS 5.56mm', 91, '12,400 rds'], ['UBGL Rounds', 68, '34 rnds'], ['Smoke Grenades', 55, '22 rnds']].map(([k, v, sub]) => (
            <div key={k as string} style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
              <span style={{ width: '120px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{k as string}</span>
              <div className="progress-bar" style={{ flex: 1 }}>
                <div className={`progress-bar__fill ${(v as number) < 60 ? 'progress-bar__fill--warning' : ''}`} style={{ width: `${v as number}%` }} />
              </div>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>{sub as string}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
