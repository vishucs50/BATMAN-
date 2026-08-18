import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'

interface ReplayEvent {
  sequence: number
  time_min: number
  event_type: string
  unit: string
  location: { lat: number; lng: number; name: string }
  payload: any
}

export default function ReplayView() {
  const { missionId } = useParams<{ missionId: string }>()
  const navigate = useNavigate()
  const [aar, setAar] = useState<any>(null)
  const [events, setEvents] = useState<ReplayEvent[]>([])
  const [loading, setLoading] = useState(true)

  // Playback Controls State
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0.0)
  const [speed, setSpeed] = useState<1 | 2 | 4>(1)

  const maxTime = aar?.mission_duration || 120.0
  const animationRef = useRef<number | null>(null)
  const lastTickRef = useRef<number | null>(null)

  useEffect(() => {
    if (missionId) {
      loadReplayData(missionId)
    }
  }, [missionId])

  const loadReplayData = async (id: string) => {
    setLoading(true)
    try {
      const [aarResp, replayResp] = await Promise.all([
        fetch(`http://127.0.0.1:8003/wargame/aar/${id}`),
        fetch(`http://127.0.0.1:8003/wargame/aar/${id}/replay`)
      ])

      if (aarResp.ok) {
        const aarData = await aarResp.json()
        setAar(aarData)
      }
      if (replayResp.ok) {
        const replayData = await replayResp.json()
        setEvents(replayData.events || [])
      }
    } catch (e) {
      console.error("Error loading replay data", e)
    } finally {
      setLoading(false)
    }
  }

  // Animation Loop for Smooth Timeline Scrubbing
  useEffect(() => {
    if (isPlaying) {
      lastTickRef.current = performance.now()
      const tick = (now: number) => {
        if (lastTickRef.current !== null) {
          const deltaSec = (now - lastTickRef.current) / 1000.0
          setCurrentTime((prev) => {
            const nextTime = prev + deltaSec * 2.0 * speed // 2 mins per real second * speed
            if (nextTime >= maxTime) {
              setIsPlaying(false)
              return maxTime
            }
            return nextTime
          })
        }
        lastTickRef.current = now
        animationRef.current = requestAnimationFrame(tick)
      }
      animationRef.current = requestAnimationFrame(tick)
    } else {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current)
      }
    }

    return () => {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [isPlaying, speed, maxTime])

  // Filter events up to currentTime
  const visibleEvents = events.filter((e) => e.time_min <= currentTime)
  const activeEvents = visibleEvents.slice(-6)

  // Compute live gauges based on currentTime
  const currentCasualties = visibleEvents.filter(e => e.event_type === 'CASUALTY').length
  const latestFuelEvent = [...visibleEvents].reverse().find(e => e.payload?.fuel_remaining_pct !== undefined)
  const fuelRemaining = latestFuelEvent ? latestFuelEvent.payload.fuel_remaining_pct : Math.max(20, Math.round(100 - (currentTime / maxTime) * 80))

  const handleStepForward = () => {
    setCurrentTime(prev => Math.min(maxTime, prev + 5.0))
  }

  const handleStepBackward = () => {
    setCurrentTime(prev => Math.max(0, prev - 5.0))
  }

  if (loading) {
    return (
      <div style={{ padding: 'var(--space-8)', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading interactive simulation replay engine...
      </div>
    )
  }

  return (
    <div style={{ padding: 'var(--space-6)', display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', height: 'calc(100vh - 80px)' }}>
      {/* TOP HEADER */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button onClick={() => navigate(`/aar/${missionId}`)} className="btn btn--secondary" style={{ padding: '4px 10px', fontSize: '0.75rem' }}>
            ← Back to AAR Report
          </button>
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--color-accent-primary)', letterSpacing: '0.1em' }}>
              INTERACTIVE SIMULATION REPLAY
            </div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0 }}>
              {aar?.mission_code || 'OP-SIMULATION'} — Time Scrubbing
            </h2>
          </div>
        </div>

        {/* LIVE GAUGES */}
        <div style={{ display: 'flex', gap: '16px', fontSize: '0.8rem' }}>
          <div style={{ background: 'var(--color-bg-card)', padding: '6px 12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-primary)' }}>
            <span style={{ color: 'var(--text-muted)' }}>Time: </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-accent-primary)' }}>
              T+{Math.floor(currentTime)}m
            </span>
          </div>

          <div style={{ background: 'var(--color-bg-card)', padding: '6px 12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-primary)' }}>
            <span style={{ color: 'var(--text-muted)' }}>Fuel: </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--text-primary)' }}>
              {fuelRemaining}%
            </span>
          </div>

          <div style={{ background: 'var(--color-bg-card)', padding: '6px 12px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-primary)' }}>
            <span style={{ color: 'var(--text-muted)' }}>Casualties: </span>
            <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: currentCasualties > 0 ? 'var(--color-danger)' : 'var(--color-success)' }}>
              {currentCasualties} WIA
            </span>
          </div>
        </div>
      </div>

      {/* MAIN PLAYBACK GRID */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-4)', flex: 1, minHeight: 0 }}>
        {/* TACTICAL MAP CANVAS REPLAY */}
        <div className="panel" style={{ padding: '0', background: '#07090c', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)', position: 'relative', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* MAP CANVAS GRID */}
          <div style={{ flex: 1, position: 'relative', background: 'radial-gradient(circle, #121824 0%, #07090c 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            {/* Grid overlay lines */}
            <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(to right, rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(to bottom, rgba(255,255,255,0.03) 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

            {/* Tactical Checkpoint Markers */}
            <div style={{ position: 'absolute', top: '25%', left: '20%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--color-info)', boxShadow: '0 0 10px var(--color-info)' }} />
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>Base HQ</span>
            </div>

            <div style={{ position: 'absolute', top: '40%', left: '50%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', background: 'var(--color-warning)', boxShadow: '0 0 10px var(--color-warning)' }} />
              <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>CP Alpha</span>
            </div>

            <div style={{ position: 'absolute', top: '70%', left: '75%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <div style={{ width: '14px', height: '14px', borderRadius: '50%', background: 'var(--color-danger)', boxShadow: '0 0 12px var(--color-danger)', animation: 'pulse 1.5s infinite' }} />
              <span style={{ fontSize: '0.65rem', color: 'var(--color-danger)', fontFamily: 'var(--font-mono)', marginTop: '4px', fontWeight: 700 }}>Obj Zulu</span>
            </div>

            {/* Active Moving Units */}
            {visibleEvents.slice(-4).map((evt, idx) => {
              const leftPct = 20 + ((evt.time_min / maxTime) * 60)
              const topPct = 25 + ((idx * 18) % 55)

              return (
                <div 
                  key={evt.sequence} 
                  style={{
                    position: 'absolute',
                    top: `${topPct}%`,
                    left: `${leftPct}%`,
                    transition: 'all 0.4s ease',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center'
                  }}
                >
                  <div style={{
                    padding: '4px 8px',
                    background: 'rgba(245, 158, 11, 0.2)',
                    border: '1px solid var(--color-accent-primary)',
                    color: 'var(--color-accent-primary)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    fontFamily: 'var(--font-mono)'
                  }}>
                    ♟ {evt.unit}
                  </div>
                  <div style={{ fontSize: '0.6rem', color: '#fff', background: 'rgba(0,0,0,0.7)', padding: '2px 4px', borderRadius: '2px', marginTop: '2px' }}>
                    {evt.event_type}
                  </div>
                </div>
              )
            })}
          </div>

          {/* PLAYBACK CONTROLS BAR */}
          <div style={{ padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderTop: '1px solid var(--border-primary)', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {/* TIMELINE SLIDER */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>0m</span>
              <input 
                type="range"
                min={0}
                max={maxTime}
                step={1}
                value={currentTime}
                onChange={(e) => setCurrentTime(parseFloat(e.target.value))}
                style={{ flex: 1, accentColor: 'var(--color-accent-primary)', cursor: 'pointer' }}
              />
              <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-muted)' }}>{Math.round(maxTime)}m</span>
            </div>

            {/* BUTTON CONTROLS */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button 
                  onClick={handleStepBackward} 
                  className="btn btn--secondary" 
                  style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                >
                  ⏮ Step -5m
                </button>

                <button 
                  onClick={() => setIsPlaying(!isPlaying)} 
                  style={{
                    background: isPlaying ? 'var(--color-warning)' : 'var(--color-accent-primary)',
                    color: '#000',
                    border: 'none',
                    padding: '8px 20px',
                    borderRadius: 'var(--radius-sm)',
                    fontWeight: 700,
                    cursor: 'pointer'
                  }}
                >
                  {isPlaying ? '⏸ Pause' : '▶ Play'}
                </button>

                <button 
                  onClick={handleStepForward} 
                  className="btn btn--secondary" 
                  style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                >
                  Step +5m ⏭
                </button>
              </div>

              {/* SPEED TOGGLE */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600 }}>SPEED:</span>
                {([1, 2, 4] as const).map(s => (
                  <button
                    key={s}
                    onClick={() => setSpeed(s)}
                    style={{
                      padding: '4px 8px',
                      background: speed === s ? 'var(--color-accent-glow)' : 'var(--color-bg-card)',
                      border: speed === s ? '1px solid var(--border-accent)' : '1px solid var(--border-secondary)',
                      color: speed === s ? 'var(--color-accent-primary)' : 'var(--text-secondary)',
                      borderRadius: 'var(--radius-sm)',
                      fontSize: '0.75rem',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    {s}x
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* REAL-TIME EVENT LOG FEED */}
        <div className="panel" style={{ padding: 'var(--space-4)', background: 'var(--color-bg-panel)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-primary)', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--color-accent-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            SIMULATION EVENT LOG ({visibleEvents.length} / {events.length})
          </div>

          <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', paddingRight: '4px' }}>
            {activeEvents.length === 0 ? (
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center', margin: 'auto' }}>
                Press Play or Scrub timeline to begin event replay...
              </div>
            ) : (
              activeEvents.map((evt) => (
                <div key={evt.sequence} style={{ background: 'var(--color-bg-card)', padding: '10px', borderRadius: 'var(--radius-sm)', borderLeft: '3px solid var(--color-accent-primary)', fontSize: '0.8rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2px' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-accent-primary)' }}>
                      T+{evt.time_min}m
                    </span>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Seq #{evt.sequence}</span>
                  </div>
                  <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{evt.event_type} — {evt.unit}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    Location: {evt.location?.name || 'Grid Sector'}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
