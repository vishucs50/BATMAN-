import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { RootState, AppDispatch } from '../store'
import { fetchSimulationStats } from '../store/slices/wargameSlice'

export default function WargameView() {
  const dispatch = useDispatch<AppDispatch>()
  const alerts = useSelector((state: RootState) => state.alerts.alerts)
  const simEvents = alerts.filter(a => a.type === 'SIMULATION_UPDATE')
  const { stats: simStats, loading } = useSelector((state: RootState) => state.wargame)

  // Auto-fetch stats if we see a "Simulation complete" event
  useEffect(() => {
    const completeEvt = simEvents.find(e => e.msg.includes('Simulation complete'))
    if (completeEvt) {
      const match = completeEvt.msg.match(/Job ([^:]+):/)
      if (match && match[1]) {
        dispatch(fetchSimulationStats(match[1]))
      }
    }
  }, [simEvents, dispatch])

  return (
    <div style={{ padding: '16px', height: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2>War Gaming Engine</h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Live Simulation Execution via Redis PubSub
          </p>
        </div>
      </div>
      <div className="panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        <h4 style={{ marginBottom: '8px' }}>LIVE EVENTS</h4>
        <div style={{ flex: 1, overflowY: 'auto', backgroundColor: 'var(--bg-default)', padding: '12px', borderRadius: '4px', fontFamily: 'monospace', fontSize: '0.85rem' }}>
          {simEvents.length === 0 ? (
            <div style={{ color: 'var(--text-muted)' }}>Waiting for simulation events...</div>
          ) : (
            simEvents.map((evt, idx) => (
              <div key={idx} style={{ marginBottom: '8px', borderBottom: '1px solid var(--border-color)', paddingBottom: '4px' }}>
                <span style={{ color: 'var(--color-primary)' }}>[{new Date(evt.timestamp).toLocaleTimeString()}]</span>{' '}
                <strong style={{ color: 'var(--text-primary)' }}>{evt.title}:</strong>{' '}
                <span style={{ color: 'var(--text-secondary)' }}>{evt.msg}</span>
              </div>
            ))
          )}
        </div>
      </div>
      <div className="panel">
        <h4 style={{ marginBottom: '8px' }}>SIMULATION STATISTICS {loading && <span style={{fontSize: '0.8rem', color: 'var(--text-muted)'}}>(Loading...)</span>}</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px', fontSize: '0.8rem' }}>
          {simStats ? (
            <>
              {[
                ['Success Rate', `${(simStats.success_rate * 100).toFixed(1)}%`, simStats.success_rate > 0.8 ? 'green' : ''],
                ['Mean Casualties', simStats.mean_casualties.toFixed(1), ''],
                ['P95 Timeline', `${(simStats.timeline_p95_min / 60).toFixed(1)}h`, ''],
                ['ROE Violations', `${(simStats.roe_violation_rate * 100).toFixed(1)}%`, simStats.roe_violation_rate < 0.05 ? 'green' : ''],
                ['Fuel Efficiency', `${((1 - simStats.fuel_consumed_mean) * 100).toFixed(1)}%`, '']
              ].map(([k, v, c]) => (
                <div key={k as string} className="stat-card">
                  <div className="stat-card__value" style={{ fontSize: '1.5rem', color: c === 'green' ? 'var(--color-success)' : undefined }}>{v as string}</div>
                  <div className="stat-card__label">{k as string}</div>
                </div>
              ))}
            </>
          ) : (
            <div style={{ color: 'var(--text-muted)', gridColumn: '1 / -1' }}>No simulation data yet. Run a wargame to view stats.</div>
          )}
        </div>
      </div>
    </div>
  )
}
