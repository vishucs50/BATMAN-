import { Routes, Route, Navigate, Outlet } from 'react-router-dom'
import AppShell from './components/shared/AppShell'
import LandingPage from './pages/LandingPage'
import CommandView from './pages/CommandView'
import COAView from './pages/COAView'
import WargameView from './pages/WargameView'
import LogisticsView from './pages/LogisticsView'
import MissionHistoryView from './pages/MissionHistoryView'
import AARDetailsView from './pages/AARDetailsView'
import ReplayView from './pages/ReplayView'

const DashboardLayout = () => (
  <AppShell>
    <Outlet />
  </AppShell>
)

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route element={<DashboardLayout />}>
        <Route path="/command"   element={<CommandView />} />
        <Route path="/coa"       element={<COAView />} />
        <Route path="/wargame"   element={<WargameView />} />
        <Route path="/logistics" element={<LogisticsView />} />
        <Route path="/history"   element={<MissionHistoryView />} />
        <Route path="/aar/:missionId" element={<AARDetailsView />} />
        <Route path="/replay/:missionId" element={<ReplayView />} />
        <Route path="*"          element={<Navigate to="/command" replace />} />
      </Route>
    </Routes>
  )
}
