import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

export default function AARDetailsView() {
  const { missionId } = useParams<{ missionId: string }>()
  const navigate = useNavigate()
  const [aar, setAar] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'summary' | 'timeline' | 'threat' | 'scores' | 'explanation'>('summary')

  useEffect(() => {
    if (missionId) {
      fetchAAR(missionId)
    }
  }, [missionId])

  const fetchAAR = async (id: string) => {
    setLoading(true)
    try {
      const resp = await fetch(`http://127.0.0.1:8003/wargame/aar/${id}`)
      if (resp.ok) {
        const data = await resp.json()
        setAar(data)
      }
    } catch (e) {
      console.error("Error fetching AAR detail", e)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading After Action Review data for Mission {missionId}...
      </div>
    )
  }

  if (!aar) {
    return (
      <div style={{ padding: 'var(--space-8)', textAlign: 'center' }}>
        <h2 style={{ color: 'var(--color-danger)' }}>AAR Report Not Found</h2>
        <div style={{ margin: '16px 0', color: 'var(--text-muted)' }}>No record exists for mission ID {missionId}.</div>
        <button onClick={() => navigate('/history')} className="btn btn--secondary">Back to History</button>
      </div>
    )
  }

  const outcomeBadge = 
    aar.outcome === 'SUCCESS' ? 'badge--green' :
    aar.outcome === 'PARTIAL' ? 'badge--amber' : 'badge--red'

  return (
    <div style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* HEADER */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '4px' }}>
            <button onClick={() => navigate('/history')} className="btn btn--secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
              ← History
            </button>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-accent-primary)', letterSpacing: '0.1em' }}>
              CLASSIFIED AFTER ACTION REVIEW
            </span>
            <span className={`badge ${outcomeBadge}`}>{aar.outcome}</span>
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
            {aar.mission_code} — Operational Evaluation
          </h1>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
            ID: {aar.mission_id} | Timestamp: {new Date(aar.timestamp).toLocaleString()} | Classification: {aar.classification}
          </div>
        </div>

        <button 
          onClick={() => navigate(`/replay/${aar.mission_id}`)}
          style={{
            background: 'var(--color-accent-primary)',
            color: '#000',
            border: 'none',
            padding: '10px 20px',
            borderRadius: 'var(--radius-md)',
            fontWeight: 700,
            fontSize: '0.9rem',
            cursor: 'pointer',
            boxShadow: 'var(--shadow-accent)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          ▶ LAUNCH SIMULATION REPLAY
        </button>
      </div>

      {/* METRIC CARDS HEADER */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 'var(--space-4)' }}>
        <div className="panel" style={{ padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>UTILITY SCORE</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--color-accent-primary)', fontFamily: 'var(--font-mono)' }}>
            {aar.final_score.toFixed(1)} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>/ 100</span>
          </div>
        </div>

        <div className="panel" style={{ padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>DURATION</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', fontFamily: 'var(--font-mono)' }}>
            {Math.round(aar.mission_duration)} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>min</span>
          </div>
        </div>

        <div className="panel" style={{ padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>CASUALTIES</div>
          <div style={{ fontSize: '1.75rem', fontWeight: 700, color: aar.casualties?.friendly > 0 ? 'var(--color-danger)' : 'var(--color-success)', fontFamily: 'var(--font-mono)' }}>
            {aar.casualties?.friendly || 0} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Friendly</span>
          </div>
        </div>

        <div className="panel" style={{ padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
          <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>COA STYLE</div>
          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
            {aar.selected_coa?.style || 'BOLD'}
          </div>
        </div>
      </div>

      {/* NAVIGATION TABS */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-primary)', paddingBottom: '8px' }}>
        {[
          { id: 'summary', label: '📊 Summary & Decision' },
          { id: 'timeline', label: '⏱ Operational Timeline' },
          { id: 'threat', label: '🎯 Threat & Resources' },
          { id: 'scores', label: '📈 Monte Carlo Stats' },
          { id: 'explanation', label: '🧠 AI Rationale' },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            style={{
              padding: '8px 16px',
              background: activeTab === tab.id ? 'var(--color-accent-glow)' : 'transparent',
              border: activeTab === tab.id ? '1px solid var(--border-accent)' : '1px solid transparent',
              color: activeTab === tab.id ? 'var(--color-accent-primary)' : 'var(--text-secondary)',
              borderRadius: 'var(--radius-sm)',
              fontWeight: activeTab === tab.id ? 600 : 400,
              fontSize: '0.85rem',
              cursor: 'pointer'
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* TAB CONTENT */}
      {activeTab === 'summary' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }}>
          {/* MISSION PARAMETERS */}
          <div className="panel" style={{ padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
            <h3 style={{ fontSize: '1rem', color: 'var(--color-accent-primary)', marginBottom: '12px' }}>Operational Parameters</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Mission Type:</span>
                <span style={{ fontWeight: 600 }}>{aar.mission_type}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Target Location:</span>
                <span>{aar.mission_params?.target || 'Hanupatta'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Terrain / Elevation:</span>
                <span>{aar.mission_params?.terrain || 'PLAINS'} ({aar.mission_params?.elevation_m || 1870}m)</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Weather:</span>
                <span>{aar.mission_params?.weather || 'CLEAR'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Threat Level:</span>
                <span style={{ color: 'var(--color-danger)', fontWeight: 600 }}>{aar.mission_params?.threat_level || 'HIGH'}</span>
              </div>
            </div>
          </div>

          {/* COMMANDER DECISION RECORD */}
          <div className="panel" style={{ padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
            <h3 style={{ fontSize: '1rem', color: 'var(--color-accent-primary)', marginBottom: '12px' }}>Commander Decision Record</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Authorization Status:</span>
                <span className="badge badge--green">{aar.commander_decision?.status || 'APPROVED'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Commanding Officer:</span>
                <span style={{ fontWeight: 600 }}>{aar.commander_decision?.actor || 'Col. Demo'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Authorized At:</span>
                <span style={{ fontFamily: 'var(--font-mono)' }}>{new Date(aar.commander_decision?.timestamp || aar.timestamp).toLocaleTimeString()}</span>
              </div>
              <div style={{ marginTop: '8px', background: 'var(--color-bg-card)', padding: '10px', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--color-accent-primary)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>COMMAND RATIONALE</div>
                <div style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                  "{aar.commander_decision?.rationale || 'Execution approved based on simulation analytics.'}"
                </div>
              </div>
            </div>
          </div>

          {/* LESSONS LEARNED */}
          <div className="panel" style={{ gridColumn: '1/-1', padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
            <h3 style={{ fontSize: '1rem', color: 'var(--color-accent-primary)', marginBottom: '12px' }}>Lessons Learned & Vulnerabilities</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
              {(aar.monte_carlo_stats?.failure_modes || []).length > 0 ? (
                aar.monte_carlo_stats.failure_modes.map((fm: any, idx: number) => (
                  <div key={idx} style={{ background: 'var(--color-bg-card)', padding: '12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-secondary)' }}>
                    <div style={{ fontWeight: 600, color: 'var(--color-warning)', fontSize: '0.85rem' }}>
                      ⚠ {typeof fm === 'string' ? fm : fm.mode}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                      Simulated probability: {typeof fm === 'object' && fm.probability ? `${(fm.probability * 100).toFixed(0)}%` : 'Detected in simulation runs'}
                    </div>
                  </div>
                ))
              ) : (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No critical vulnerabilities or failure modes recorded for this simulation.</div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'timeline' && (
        <div className="panel" style={{ padding: 'var(--space-6)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
          <h3 style={{ fontSize: '1rem', color: 'var(--color-accent-primary)', marginBottom: '16px' }}>HTN Task Hierarchy & Execution Milestones</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {(aar.timeline || []).map((step: any, idx: number) => (
              <div key={idx} style={{ display: 'flex', gap: '16px', alignItems: 'center', padding: '12px', background: 'var(--color-bg-card)', borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--color-accent-primary)' }}>
                <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-accent-primary)', minWidth: '70px' }}>
                  T+{step.time_min}m
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{step.event}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Phase: {step.phase || 'Execution'}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'threat' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-6)' }}>
          <div className="panel" style={{ padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
            <h3 style={{ fontSize: '1rem', color: 'var(--color-accent-primary)', marginBottom: '12px' }}>Bayesian Threat Profile</h3>
            <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Baseline Threat Probability:</span>
                <span style={{ fontWeight: 600, color: 'var(--color-danger)' }}>{((aar.threat_assessment?.threat_probability || 0.25) * 100).toFixed(0)}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Bayesian Assessment Score:</span>
                <span>{aar.threat_assessment?.bayesian_score || 0.78}</span>
              </div>
              <div style={{ marginTop: '8px' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '4px' }}>IDENTIFIED RISK FACTORS:</div>
                <ul style={{ paddingLeft: '16px', color: 'var(--text-secondary)' }}>
                  {(aar.threat_assessment?.risk_factors || []).map((rf: string, i: number) => (
                    <li key={i}>{rf}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="panel" style={{ padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
            <h3 style={{ fontSize: '1rem', color: 'var(--color-accent-primary)', marginBottom: '12px' }}>Resource & Logistics Consumption</h3>
            <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Fuel Consumed:</span>
                <span style={{ fontWeight: 600 }}>{aar.logistics_usage?.fuel_consumed_pct?.toFixed(1) || 20.0}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Ammunition Consumed:</span>
                <span style={{ fontWeight: 600 }}>{aar.logistics_usage?.ammo_consumed_pct?.toFixed(1) || 0.0}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Personnel Allocated:</span>
                <span>{aar.resource_consumption?.personnel || 377} Troops</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--text-muted)' }}>Sensors & Drones:</span>
                <span>{aar.resource_consumption?.sensors || 13} Sensors, {aar.resource_consumption?.drones || 2} Drones</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'scores' && (
        <div className="panel" style={{ padding: 'var(--space-6)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
          <h3 style={{ fontSize: '1rem', color: 'var(--color-accent-primary)', marginBottom: '16px' }}>Monte Carlo Simulation Outcome Statistics</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div style={{ background: 'var(--color-bg-card)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>SIMULATION RUNS</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{aar.monte_carlo_stats?.run_count || 50}</div>
            </div>
            <div style={{ background: 'var(--color-bg-card)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>WIN/SUCCESS RATE</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-success)', fontFamily: 'var(--font-mono)' }}>
                {((aar.monte_carlo_stats?.success_rate || 0.85) * 100).toFixed(1)}%
              </div>
            </div>
            <div style={{ background: 'var(--color-bg-card)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>P50 COMPLETION TIME</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                {Math.round(aar.monte_carlo_stats?.timeline_p50_min || 120)} min
              </div>
            </div>
            <div style={{ background: 'var(--color-bg-card)', padding: '16px', borderRadius: 'var(--radius-sm)' }}>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>ROE VIOLATION RATE</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-success)', fontFamily: 'var(--font-mono)' }}>
                {(aar.monte_carlo_stats?.roe_violation_rate || 0.0).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'explanation' && (
        <div className="panel" style={{ padding: 'var(--space-6)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
          <h3 style={{ fontSize: '1rem', color: 'var(--color-accent-primary)', marginBottom: '16px' }}>AI Decision Rationale & Rule Engine Firings</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ background: 'var(--color-bg-card)', padding: '16px', borderRadius: 'var(--radius-sm)', borderLeft: '4px solid var(--color-accent-primary)' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '6px' }}>
                PRIMARY DECISION RATIONALE
              </div>
              <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                {aar.ai_explanation?.decision}
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>SUPPORTING REASONS:</h4>
              <ul style={{ paddingLeft: '20px', color: 'var(--text-primary)', fontSize: '0.85rem' }}>
                {(aar.ai_explanation?.primary_reasons || []).map((r: string, idx: number) => (
                  <li key={idx} style={{ marginBottom: '4px' }}>{r}</li>
                ))}
              </ul>
            </div>

            <div>
              <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>RULE ENGINE FIRINGS:</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {(aar.rule_engine_decisions || []).map((rule: string, idx: number) => (
                  <div key={idx} style={{ background: 'var(--color-bg-card)', padding: '8px 12px', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', fontFamily: 'var(--font-mono)' }}>
                    ✓ {rule}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
