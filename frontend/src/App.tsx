import { Routes, Route, Navigate } from 'react-router-dom'
import AppShell from './components/shared/AppShell'
import CommandView from './pages/CommandView'
import COAView from './pages/COAView'
import WargameView from './pages/WargameView'
import LogisticsView from './pages/LogisticsView'

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/"          element={<Navigate to="/command" replace />} />
        <Route path="/command"   element={<CommandView />} />
        <Route path="/coa"       element={<COAView />} />
        <Route path="/wargame"   element={<WargameView />} />
        <Route path="/logistics" element={<LogisticsView />} />
        <Route path="*"          element={<Navigate to="/command" replace />} />
      </Routes>
    </AppShell>
  )
}
