import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

interface AARSummary {
  mission_id: string
  mission_code: string
  mission_type: string
  outcome: string
  final_score: number
  mission_duration: number
  friendly_casualties: number
  selected_coa: string
  timestamp: string
}

export default function MissionHistoryView() {
  const navigate = useNavigate()
  const [aars, setAars] = useState<AARSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('ALL')
  const [outcomeFilter, setOutcomeFilter] = useState('ALL')

  useEffect(() => {
    fetchAARs()
  }, [typeFilter, outcomeFilter])

  const fetchAARs = async () => {
    setLoading(true)
    try {
      let url = 'http://127.0.0.1:8003/wargame/aar?'
      if (typeFilter !== 'ALL') url += `mission_type=${typeFilter}&`
      if (outcomeFilter !== 'ALL') url += `outcome=${outcomeFilter}&`
      if (search) url += `search=${encodeURIComponent(search)}&`

      const resp = await fetch(url)
      if (resp.ok) {
        const data = await resp.json()
        setAars(data.aars || [])
      }
    } catch (e) {
      console.error("Failed fetching AARs", e)
    } finally {
      setLoading(false)
    }
  }

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    fetchAARs()
  }

  const filteredAars = aars.filter(a => {
    if (!search) return true
    const s = search.toLowerCase()
    return a.mission_code.toLowerCase().includes(s) || a.mission_type.toLowerCase().includes(s) || a.mission_id.toLowerCase().includes(s)
  })

  return (
    <div style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
      {/* HEADER */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-accent-primary)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
            HISTORICAL INTELLIGENCE RECORDS
          </div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', margin: '4px 0' }}>
            Mission History & After Action Reviews
          </h1>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
            Review completed tactical operations, analyze simulation metrics, and replay simulated engagements.
          </div>
        </div>

        <button 
          onClick={fetchAARs}
          className="btn btn--secondary" 
          style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem' }}
        >
          🔄 Refresh Log
        </button>
      </div>

      {/* FILTER BAR */}
      <div className="panel" style={{ padding: 'var(--space-4)', display: 'flex', flexWrap: 'wrap', gap: 'var(--space-4)', alignItems: 'center', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
        <form onSubmit={handleSearchSubmit} style={{ flex: '1 1 250px', display: 'flex', gap: '8px' }}>
          <input 
            type="text"
            placeholder="Search Mission Code / ID / Type..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{
              flex: 1,
              background: 'var(--color-bg-card)',
              border: '1px solid var(--border-secondary)',
              color: 'var(--text-primary)',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.85rem'
            }}
          />
          <button type="submit" className="btn btn--primary" style={{ fontSize: '0.85rem', padding: '0 16px' }}>Search</button>
        </form>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>TYPE:</label>
          <select 
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            style={{
              background: 'var(--color-bg-card)',
              border: '1px solid var(--border-secondary)',
              color: 'var(--text-primary)',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.85rem'
            }}
          >
            <option value="ALL">All Mission Types</option>
            <option value="COUNTER_INFILTRATION">Counter Infiltration</option>
            <option value="COUNTER_TERRORISM">Counter Terrorism</option>
            <option value="HIGH_ALTITUDE_LOGISTICS">High Altitude Logistics</option>
            <option value="CONVOY_PROTECTION">Convoy Protection</option>
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>OUTCOME:</label>
          <select 
            value={outcomeFilter}
            onChange={(e) => setOutcomeFilter(e.target.value)}
            style={{
              background: 'var(--color-bg-card)',
              border: '1px solid var(--border-secondary)',
              color: 'var(--text-primary)',
              padding: '8px 12px',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.85rem'
            }}
          >
            <option value="ALL">All Outcomes</option>
            <option value="SUCCESS">Success</option>
            <option value="PARTIAL">Partial</option>
            <option value="FAILURE">Failure</option>
          </select>
        </div>
      </div>

      {/* TABLE / LIST */}
      <div className="panel" style={{ padding: '0', overflow: 'hidden', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)' }}>
        {loading ? (
          <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading mission history records...
          </div>
        ) : filteredAars.length === 0 ? (
          <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
            No mission history records found matching criteria.
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ background: 'var(--color-bg-card)', borderBottom: '1px solid var(--border-primary)', color: 'var(--text-muted)', fontSize: '0.7rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                <th style={{ padding: '12px 16px' }}>Mission Code</th>
                <th style={{ padding: '12px 16px' }}>Type</th>
                <th style={{ padding: '12px 16px' }}>COA Selected</th>
                <th style={{ padding: '12px 16px' }}>Duration</th>
                <th style={{ padding: '12px 16px' }}>Casualties</th>
                <th style={{ padding: '12px 16px' }}>Score</th>
                <th style={{ padding: '12px 16px' }}>Outcome</th>
                <th style={{ padding: '12px 16px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredAars.map((item) => {
                const outcomeBadgeClass = 
                  item.outcome === 'SUCCESS' ? 'badge--green' :
                  item.outcome === 'PARTIAL' ? 'badge--amber' : 'badge--red'

                return (
                  <tr key={item.mission_id} style={{ borderBottom: '1px solid var(--border-primary)', transition: 'background var(--transition-fast)' }} className="table-row-hover">
                    <td style={{ padding: '14px 16px', fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
                      {item.mission_code}
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontWeight: 400 }}>{item.mission_id}</div>
                    </td>
                    <td style={{ padding: '14px 16px', color: 'var(--text-secondary)' }}>
                      {item.mission_type}
                    </td>
                    <td style={{ padding: '14px 16px', color: 'var(--color-accent-primary)', fontWeight: 500 }}>
                      {item.selected_coa}
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                      {Math.round(item.mission_duration)} min
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', color: item.friendly_casualties > 0 ? 'var(--color-danger)' : 'var(--text-secondary)' }}>
                      {item.friendly_casualties} WIA/KIA
                    </td>
                    <td style={{ padding: '14px 16px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {item.final_score.toFixed(1)} / 100
                    </td>
                    <td style={{ padding: '14px 16px' }}>
                      <span className={`badge ${outcomeBadgeClass}`}>
                        {item.outcome}
                      </span>
                    </td>
                    <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        <button 
                          onClick={() => navigate(`/aar/${item.mission_id}`)}
                          style={{
                            background: 'var(--color-bg-card)',
                            border: '1px solid var(--border-secondary)',
                            color: 'var(--text-primary)',
                            padding: '6px 12px',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.75rem',
                            cursor: 'pointer'
                          }}
                        >
                          📋 AAR Report
                        </button>
                        <button 
                          onClick={() => navigate(`/replay/${item.mission_id}`)}
                          style={{
                            background: 'var(--color-accent-glow)',
                            border: '1px solid var(--border-accent)',
                            color: 'var(--color-accent-primary)',
                            padding: '6px 12px',
                            borderRadius: 'var(--radius-sm)',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                        >
                          ▶ Replay
                        </button>
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
