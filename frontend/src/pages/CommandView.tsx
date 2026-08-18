import { useEffect, useRef, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import ReactECharts from 'echarts-for-react'
import BatmanMap from '../components/map/BatmanMap'
import { RootState, AppDispatch } from '../store'
import { fetchMissions, generateCOAs, approveCOA, simulateCOA, createMission, selectMission, createWhatIfBranch } from '../store/slices/missionsSlice'
import { addAlert, setConnectionStatus } from '../store/slices/alertSlice'
import { fetchThreatAssessment } from '../store/slices/threatSlice'
import { fetchGNNReasoning, fetchUnits } from '../store/slices/kgSlice'

export default function CommandView() {
  const dispatch = useDispatch<AppDispatch>()
  const missions = useSelector((state: RootState) => state.missions.list)
  const selectedMission = useSelector((state: RootState) => state.missions.selected)
  const activeMission = selectedMission || (missions.length > 0 ? missions[0] : null)
  const alerts = useSelector((state: RootState) => state.alerts.alerts)
  const threatLevel = useSelector((state: RootState) => state.threats.overallThreatLevel)
  const threatAssessments = useSelector((state: RootState) => state.threats.assessments)
  const kgReasoning = useSelector((state: RootState) => state.kg.reasoning)
  const kgUnits = useSelector((state: RootState) => state.kg.units)
  const wsRef = useRef<WebSocket | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [newMission, setNewMission] = useState({ mission_code: '', mission_type: 'COUNTER_INFILTRATION', classification: 'UNCLASSIFIED' })
  const [showWhatIfModal, setShowWhatIfModal] = useState(false)
  const [isWhatIfLoading, setIsWhatIfLoading] = useState(false)
  const [whatIfParams, setWhatIfParams] = useState({ threat_level: 'HIGH', weather: 'CLEAR' })

  useEffect(() => {
    dispatch(fetchMissions())
    dispatch(fetchUnits())
  }, [dispatch])

  useEffect(() => {
    if (activeMission?.id) {
      dispatch(fetchThreatAssessment(activeMission.id))
      dispatch(fetchGNNReasoning(activeMission.id))
    }
  }, [dispatch, activeMission?.id])

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/api/v1/ws/alerts')
    wsRef.current = ws

    ws.onopen = () => dispatch(setConnectionStatus(true))
    ws.onclose = () => dispatch(setConnectionStatus(false))
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        dispatch(addAlert(data))
      } catch (e) {
        console.error("Failed to parse alert", e)
      }
    }

    return () => {
      ws.close()
    }
  }, [dispatch])

  const radarOptions = {
    radar: {
      indicator: [
        { name: 'Terrain', max: 100 },
        { name: 'Threat', max: 100 },
        { name: 'Logistics', max: 100 },
        { name: 'Comms', max: 100 },
        { name: 'Weather', max: 100 }
      ],
      shape: 'circle',
      splitArea: {
        areaStyle: {
          color: ['rgba(255, 255, 255, 0.05)', 'rgba(255, 255, 255, 0.1)']
        }
      },
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } }
    },
    series: [{
      name: 'Risk Profile',
      type: 'radar',
      data: [
        {
          value: kgReasoning?.radar_metrics ? [
            kgReasoning.radar_metrics.Terrain,
            kgReasoning.radar_metrics.Threat,
            kgReasoning.radar_metrics.Logistics,
            kgReasoning.radar_metrics.Comms,
            kgReasoning.radar_metrics.Weather
          ] : [0, 0, 0, 0, 0],
          name: 'Current Risk',
          areaStyle: { color: 'rgba(239, 68, 68, 0.4)' },
          lineStyle: { color: '#ef4444' },
          itemStyle: { color: '#ef4444' }
        }
      ]
    }],
    textStyle: { fontFamily: 'var(--font-sans)', color: '#a1a1aa' }
  }

  const maxThreatProb = threatAssessments.length > 0 ? Math.max(...threatAssessments.map(t => t.probability)) : 0
  const stats = [
    { label: 'Active Units', value: kgUnits.length.toString() || '0', sub: 'in theater' },
    { label: 'Threat Prob.', value: `${(maxThreatProb * 100).toFixed(1)}%`, sub: `${threatLevel} confidence`, accent: threatLevel === 'CRITICAL' || threatLevel === 'HIGH' },
    { label: 'Mission Phase', value: activeMission?.status || 'PLANNING', sub: activeMission?.mission_code || 'None' },
    { label: 'H+ Time', value: '00:00', sub: 'elapsed', mono: true }, // We can compute real elapsed if start_time exists
  ]

  const handleGenerateCOA = async () => {
    if (!activeMission) {
      alert("No active mission selected. Select or create a mission first.")
      return
    }
    setIsGenerating(true)
    try {
      await dispatch(generateCOAs(activeMission.id)).unwrap()
      alert("COAs generated. They are now available in the COA Planning/Comparison screen.")
    } catch (err: any) {
      alert("Generation failed: " + (err.message || "Unknown error"))
    } finally {
      setIsGenerating(false)
    }
  }

  const handleCreateMission = async () => {
    if (!newMission.mission_code) {
      alert("Mission code is required.")
      return
    }
    setIsCreating(true)
    try {
      await dispatch(createMission(newMission)).unwrap()
      setShowCreateModal(false)
      setNewMission({ mission_code: '', mission_type: 'COUNTER_INFILTRATION', classification: 'UNCLASSIFIED' })
    } catch (err: any) {
      alert("Creation failed: " + (err.message || "Unknown error"))
    } finally {
      setIsCreating(false)
    }
  }

  const handleCreateWhatIf = async () => {
    if (!activeMission) {
      alert("No active mission selected.")
      return
    }
    setIsWhatIfLoading(true)
    try {
      await dispatch(createWhatIfBranch({
        missionId: activeMission.id,
        overrides: {
          mission_params: {
            ...whatIfParams
          }
        }
      })).unwrap()
      setShowWhatIfModal(false)
      alert("What-If scenario generated. The new branch is now selected.")
    } catch (err: any) {
      alert("What-If failed: " + (err.message || "Unknown error"))
    } finally {
      setIsWhatIfLoading(false)
    }
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 280px', gridTemplateRows: '1fr 180px', height: '100%', gap: '8px', padding: '8px', overflow: 'hidden' }}>

      {/* ── CREATE MISSION MODAL ──────────────────────────── */}
      {showCreateModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="panel" style={{ width: '400px', background: '#1c2128' }}>
            <h3 style={{ marginBottom: '16px' }}>Create New Mission</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Mission Code</label>
                <input style={{ width: '100%', marginTop: '4px', padding: '6px', background: '#0d1117', color: 'white', border: '1px solid #30363d', borderRadius: '4px' }} value={newMission.mission_code} onChange={e => setNewMission({...newMission, mission_code: e.target.value})} placeholder="e.g. OP-THUNDER" />
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Mission Type</label>
                <select style={{ width: '100%', marginTop: '4px', padding: '6px', background: '#0d1117', color: 'white', border: '1px solid #30363d', borderRadius: '4px' }} value={newMission.mission_type} onChange={e => setNewMission({...newMission, mission_type: e.target.value})}>
                  <option value="COUNTER_INFILTRATION">COUNTER_INFILTRATION</option>
                  <option value="COUNTER_TERRORISM">COUNTER_TERRORISM</option>
                  <option value="HIGH_ALTITUDE_LOGISTICS">HIGH_ALTITUDE_LOGISTICS</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Classification</label>
                <select style={{ width: '100%', marginTop: '4px', padding: '6px', background: '#0d1117', color: 'white', border: '1px solid #30363d', borderRadius: '4px' }} value={newMission.classification} onChange={e => setNewMission({...newMission, classification: e.target.value})}>
                  <option value="UNCLASSIFIED">UNCLASSIFIED</option>
                  <option value="SECRET">SECRET</option>
                  <option value="TOP SECRET">TOP SECRET</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', marginTop: '16px' }}>
                <button className="btn btn--secondary" onClick={() => setShowCreateModal(false)} disabled={isCreating}>Cancel</button>
                <button className="btn btn--primary" onClick={handleCreateMission} disabled={isCreating}>{isCreating ? "Creating..." : "Create"}</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── WHAT-IF MODAL ──────────────────────────── */}
      {showWhatIfModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 }}>
          <div className="panel" style={{ width: '400px', background: '#1c2128' }}>
            <h3 style={{ marginBottom: '16px' }}>What-If Analysis</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Threat Level</label>
                <select style={{ width: '100%', marginTop: '4px', padding: '6px', background: '#0d1117', color: 'white', border: '1px solid #30363d', borderRadius: '4px' }} value={whatIfParams.threat_level} onChange={e => setWhatIfParams({...whatIfParams, threat_level: e.target.value})}>
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="CRITICAL">CRITICAL</option>
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Weather Conditions</label>
                <select style={{ width: '100%', marginTop: '4px', padding: '6px', background: '#0d1117', color: 'white', border: '1px solid #30363d', borderRadius: '4px' }} value={whatIfParams.weather} onChange={e => setWhatIfParams({...whatIfParams, weather: e.target.value})}>
                  <option value="CLEAR">CLEAR</option>
                  <option value="RAIN">RAIN</option>
                  <option value="SNOW">SNOW</option>
                  <option value="FOG">FOG</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', marginTop: '16px' }}>
                <button className="btn btn--secondary" onClick={() => setShowWhatIfModal(false)} disabled={isWhatIfLoading}>Cancel</button>
                <button className="btn btn--primary" onClick={handleCreateWhatIf} disabled={isWhatIfLoading}>{isWhatIfLoading ? "Generating..." : "Generate Scenario"}</button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ── MAP (main) ─────────────────────────────────────── */}
      <div style={{ gridRow: '1', gridColumn: '1', borderRadius: '8px', overflow: 'hidden', background: '#0d1117' }}>
        <BatmanMap center={[76.9, 34.2]} zoom={10} />
      </div>

      {/* ── RIGHT PANEL ────────────────────────────────────── */}
      <div style={{ gridRow: '1', gridColumn: '2', display: 'flex', flexDirection: 'column', gap: '8px', overflow: 'hidden' }}>

        {/* Mission Control */}
        <div className="panel" style={{ flex: 'none', background: 'var(--bg-panel-highlight, #161b22)' }}>
          <div className="panel-header" style={{ marginBottom: '8px' }}>
            <h4>MISSION CONTROL</h4>
            <button className="btn btn--primary btn--sm" onClick={() => setShowCreateModal(true)}>Create New</button>
          </div>
          <select 
            style={{ width: '100%', padding: '6px', background: '#0d1117', color: 'white', border: '1px solid #30363d', borderRadius: '4px' }}
            value={activeMission?.id || ''}
            onChange={(e) => {
              const mission = missions.find(m => m.id === e.target.value)
              dispatch(selectMission(mission || null))
            }}
          >
            <option value="" disabled>Select a mission...</option>
            {missions.map(m => (
              <option key={m.id} value={m.id}>{m.mission_code} ({m.mission_type})</option>
            ))}
          </select>
        </div>

        {/* Situation Summary */}
        <div className="panel" style={{ flex: 'none' }}>
          <div className="panel-header">
            <h4>SITUATION</h4>
            <span className={`badge badge--${threatLevel === 'CRITICAL' || threatLevel === 'HIGH' ? 'red' : 'amber'}`}>{threatLevel} THREAT</span>
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
        </div>

        {/* Alerts */}
        <div className="panel" style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div className="panel-header">
            <h4>LIVE ALERTS</h4>
            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{alerts.length} active</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', overflowY: 'auto' }}>
            {alerts.length === 0 ? (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontStyle: 'italic', padding: '8px' }}>No active alerts</div>
            ) : alerts.map((a, i) => (
              <div key={i} className={`alert-item alert-item--${a.severity.toLowerCase() === 'critical' ? 'danger' : a.severity.toLowerCase()}`}>
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

        {/* Risk Radar */}
        <div className="panel" style={{ display: 'flex', flexDirection: 'column', padding: '4px' }}>
          <h4 style={{ marginLeft: '8px', marginTop: '4px' }}>RISK FACTORS</h4>
          <div style={{ flex: 1, minHeight: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {kgReasoning?.radar_metrics ? (
              <ReactECharts option={radarOptions} style={{ height: '100%', width: '100%' }} opts={{ renderer: 'svg' }} />
            ) : (
              <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Loading Risk Profile...</span>
            )}
          </div>
        </div>

        {/* Unit Status */}
        <div className="panel">
          <h4 style={{ marginBottom: '8px' }}>UNIT STATUS</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {kgUnits.slice(0, 5).map((u, i) => {
              const status = u.properties.status || 'GREEN'
              return (
                <div key={u.id || i} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem' }}>
                  <span className={`readiness-dot readiness-dot--${status}`} />
                  <span style={{ flex: 1, color: 'var(--text-secondary)' }}>{u.label || u.properties.name}</span>
                  <span className={`badge badge--${status === 'GREEN' ? 'green' : status === 'AMBER' ? 'amber' : 'red'}`}>
                    {status}
                  </span>
                </div>
              )
            })}
            {kgUnits.length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Loading units...</div>}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="panel">
          <h4 style={{ marginBottom: '8px' }}>QUICK ACTIONS</h4>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
            <button 
              className="btn btn--secondary btn--sm" 
              id="btn-generate-coa"
              onClick={handleGenerateCOA}
              disabled={isGenerating}
            >
              {isGenerating ? "Generating..." : "Generate COA"}
            </button>
            <button 
              className="btn btn--secondary btn--sm" 
              id="btn-run-wargame"
              onClick={async () => {
                if (activeMission && activeMission.coas) {
                  await dispatch(simulateCOA({ missionId: activeMission.id, coaId: activeMission.coas[0]?.id || '' }))
                  dispatch(fetchGNNReasoning(activeMission.id))
                }
              }}
            >
              Run Wargame
            </button>
            <button 
              className="btn btn--secondary btn--sm" 
              id="btn-threat-assess"
              onClick={async () => {
                if (activeMission) {
                  await dispatch(fetchThreatAssessment(activeMission.id))
                  dispatch(fetchGNNReasoning(activeMission.id))
                }
              }}
            >
              Threat Assess
            </button>
            <button className="btn btn--secondary btn--sm" id="btn-what-if" onClick={() => setShowWhatIfModal(true)}>What-If</button>
            <button 
              className="btn btn--primary btn--sm" 
              id="btn-approve-coa" 
              style={{ gridColumn: '1/-1' }}
              onClick={async () => {
                if (activeMission && activeMission.coas) {
                  await dispatch(approveCOA({ missionId: activeMission.id, coaId: activeMission.coas[0]?.id || '' }))
                  dispatch(fetchGNNReasoning(activeMission.id))
                }
              }}
            >
              Approve Active COA ✓
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
