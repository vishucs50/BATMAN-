import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { RootState, AppDispatch } from '../store'
import { fetchMissionCOAs, generateCOAs, approveCOA, simulateCOA } from '../store/slices/missionsSlice'

export default function COAView() {
  const dispatch = useDispatch<AppDispatch>()
  const missions = useSelector((state: RootState) => state.missions.list)
  const coas = useSelector((state: RootState) => state.missions.coas)
  const activeMission = missions.length > 0 ? missions[0] : null
  const [selectedCoaId, setSelectedCoaId] = useState<string | null>(null)

  useEffect(() => {
    if (activeMission) {
      dispatch(fetchMissionCOAs(activeMission.id))
    }
  }, [dispatch, activeMission])

  const handleGenerate = () => {
    if (activeMission) {
      dispatch(generateCOAs(activeMission.id))
    }
  }

  const handleSimulate = (coaId: string) => {
    if (activeMission) {
      dispatch(simulateCOA({ missionId: activeMission.id, coaId }))
    }
  }

  const handleApprove = () => {
    if (activeMission && selectedCoaId) {
      dispatch(approveCOA({ missionId: activeMission.id, coaId: selectedCoaId }))
    }
  }

  const selectedCoa = coas.find(c => c.id === selectedCoaId)

  return (
    <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px', height: '100%', overflow: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h2>Course of Action Comparison</h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Mission: {activeMission?.mission_code || 'None'} • {coas.length} COAs generated
          </p>
        </div>
        <button className="btn btn--primary" id="btn-generate-new-coas" onClick={handleGenerate}>
          Generate New COAs
        </button>
      </div>
      
      <div className="grid-3">
        {coas.length === 0 ? (
          <div style={{ padding: '20px', color: 'var(--text-muted)' }}>No COAs generated yet. Click generate.</div>
        ) : coas.map(c => {
          const isSelected = c.id === selectedCoaId
          const isApproved = c.status === 'APPROVED'
          return (
            <div key={c.id} className={`coa-card coa-card--${c.style?.toLowerCase() || 'balanced'} ${isSelected ? 'coa-card--selected' : ''}`} id={`coa-card-${c.coa_number}`}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3>COA-{c.coa_number}: "{c.name}"</h3>
                {isApproved && <span className="badge badge--green">APPROVED</span>}
              </div>
              <div className="divider" />
              <div className="coa-metric">
                <span>Utility Score</span>
                <span className="coa-metric-value">{c.utility_score?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="coa-metric">
                <span>Status</span>
                <span className="coa-metric-value">{c.status}</span>
              </div>
              <div className="divider" />
              <div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '4px' }}>EXPLANATION</div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                  {c.explanation?.decision || 'Detailed explanation not available.'}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '6px', marginTop: '12px' }}>
                <button className="btn btn--secondary btn--sm" style={{ flex: 1 }} onClick={() => handleSimulate(c.id)}>
                  SIMULATE
                </button>
                <button className={`btn btn--sm ${isSelected ? 'btn--primary' : 'btn--secondary'}`} style={{ flex: 1 }} onClick={() => setSelectedCoaId(c.id)}>
                  {isSelected ? 'SELECTED ★' : 'SELECT'}
                </button>
              </div>
            </div>
          )
        })}
      </div>

      <div className="panel">
        <h4 style={{ marginBottom: '8px' }}>AI REASONING — {selectedCoa ? `Why COA-${selectedCoa.coa_number} is selected` : 'Select a COA to view reasoning'}</h4>
        {selectedCoa ? (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
            <div><strong style={{ color: 'var(--text-primary)' }}>Utility:</strong> {selectedCoa.utility_score?.toFixed(4)}<br/><strong style={{ color: 'var(--text-primary)' }}>Style:</strong> {selectedCoa.style}</div>
            <div>
              <strong style={{ color: 'var(--text-primary)' }}>Primary Reasons:</strong>
              <ul style={{ margin: '4px 0 0 16px', padding: 0 }}>
                {selectedCoa.explanation?.primary_reasons?.map((r: string, i: number) => <li key={i}>{r}</li>)}
              </ul>
            </div>
            <div>
              <strong style={{ color: 'var(--text-primary)' }}>Rule Firings & CBR:</strong>
              <ul style={{ margin: '4px 0 0 16px', padding: 0 }}>
                {selectedCoa.explanation?.rule_firings?.map((r: string, i: number) => <li key={`rule-${i}`}>{r}</li>)}
                {selectedCoa.explanation?.cbr_matches?.map((r: string, i: number) => <li key={`cbr-${i}`}>{r}</li>)}
              </ul>
            </div>
          </div>
        ) : (
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No selection made.</div>
        )}
        <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
          <button className="btn btn--secondary btn--sm" id="btn-expand-reasoning" disabled={!selectedCoa}>Expand Reasoning</button>
          <button className="btn btn--secondary btn--sm" id="btn-show-simulation" disabled={!selectedCoa}>Show Simulation</button>
          <button className="btn btn--secondary btn--sm" id="btn-adjust-weights" disabled={!selectedCoa}>Adjust Weights</button>
          <div style={{ flex: 1 }} />
          <button className="btn btn--primary" id="btn-approve-coa" disabled={!selectedCoa} onClick={handleApprove}>
            APPROVE COA-{selectedCoa?.coa_number || ''}
          </button>
        </div>
      </div>
    </div>
  )
}
