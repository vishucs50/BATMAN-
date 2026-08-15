import { ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '../../store/hooks'

// Icons as inline SVG components (no external icon lib needed)
const IconMap      = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"/></svg>
const IconShield   = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
const IconSim      = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
const IconPackage  = () => <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
const IconBat      = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 14H9V8h2v8zm4 0h-2V8h2v8z"/></svg>

interface AppShellProps {
  children: ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  return (
    <div className="app-shell">
      {/* CLASSIFICATION BANNER */}
      <div className="classification-banner" style={{ gridColumn: '1/-1', height: '18px' }}>
        ⚠ UNCLASSIFIED — RESEARCH / ACADEMIC DEMONSTRATION ONLY ⚠
      </div>

      {/* TOP BAR */}
      <header className="topbar" style={{ gridColumn: '1/-1' }}>
        <div className="flex items-center gap-2" style={{ gap: '10px' }}>
          <span style={{ color: 'var(--color-accent-primary)', fontSize: '1.25rem' }}>🦇</span>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.9rem', letterSpacing: '0.05em', color: 'var(--text-primary)' }}>
              BATMAN
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              Battlefield Analytics & Tactical Mission Assistance Network
            </div>
          </div>
        </div>

        <div style={{ flex: 1 }} />

        {/* Mission Status Indicator */}
        <div className="flex items-center gap-2" style={{ gap: '8px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          <span className="live-dot" />
          <span>LIVE</span>
        </div>

        <div style={{ width: '1px', height: '24px', background: 'var(--border-primary)', margin: '0 8px' }} />

        {/* Time */}
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          {new Date().toLocaleTimeString('en-IN', { hour12: false })} IST
        </div>

        <div style={{ width: '1px', height: '24px', background: 'var(--border-primary)', margin: '0 8px' }} />

        {/* User indicator */}
        <div className="flex items-center gap-2" style={{ gap: '6px' }}>
          <div style={{
            width: '28px', height: '28px',
            borderRadius: '50%',
            background: 'var(--color-accent-glow)',
            border: '1px solid var(--border-accent)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.7rem', fontWeight: 700, color: 'var(--color-accent-primary)'
          }}>CO</div>
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 600 }}>Col. Demo</div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Commanding Officer</div>
          </div>
        </div>
      </header>

      {/* SIDEBAR */}
      <aside className="sidebar">
        <div style={{ padding: '0 var(--space-4)', marginBottom: 'var(--space-4)' }}>
          <div style={{ fontSize: '0.65rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: 'var(--space-2)' }}>
            Navigation
          </div>
        </div>

        <nav>
          <NavLink to="/command" className={({ isActive }) => `nav-item ${isActive ? 'nav-item--active' : ''}`} id="nav-command">
            <IconMap /> Command View
          </NavLink>
          <NavLink to="/coa" className={({ isActive }) => `nav-item ${isActive ? 'nav-item--active' : ''}`} id="nav-coa">
            <IconShield /> COA Planning
          </NavLink>
          <NavLink to="/wargame" className={({ isActive }) => `nav-item ${isActive ? 'nav-item--active' : ''}`} id="nav-wargame">
            <IconSim /> War Gaming
          </NavLink>
          <NavLink to="/logistics" className={({ isActive }) => `nav-item ${isActive ? 'nav-item--active' : ''}`} id="nav-logistics">
            <IconPackage /> Logistics
          </NavLink>
        </nav>

        <div className="divider" style={{ margin: 'var(--space-4) var(--space-4)' }} />

        {/* Threat Level */}
        <div style={{ padding: '0 var(--space-4)' }}>
          <div style={{ fontSize: '0.65rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: 'var(--space-2)' }}>
            Threat Level
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ flex: 1, height: '6px', background: 'var(--color-bg-elevated)', borderRadius: '3px', overflow: 'hidden' }}>
              <div style={{ width: '75%', height: '100%', background: 'var(--color-danger)', borderRadius: '3px' }} />
            </div>
            <span className="badge badge--red">HIGH</span>
          </div>
        </div>

        <div style={{ flex: 1 }} />

        {/* System Status */}
        <div style={{ padding: 'var(--space-4)', borderTop: '1px solid var(--border-primary)' }}>
          <div style={{ fontSize: '0.65rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.1em', color: 'var(--text-muted)', marginBottom: 'var(--space-2)' }}>
            System Status
          </div>
          {[
            { label: 'Database', status: 'online' },
            { label: 'Kafka Bus', status: 'online' },
            { label: 'AI Engine', status: 'phase1' },
          ].map(({ label, status }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px', fontSize: '0.75rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
              <span className={`badge ${status === 'online' ? 'badge--green' : 'badge--amber'}`}>
                {status === 'online' ? 'OK' : 'Phase 1'}
              </span>
            </div>
          ))}
        </div>

        {/* Version */}
        <div style={{ padding: '0 var(--space-4) var(--space-4)', fontSize: '0.65rem', color: 'var(--text-muted)' }}>
          BATMAN v2.0 — Phase 0
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}
