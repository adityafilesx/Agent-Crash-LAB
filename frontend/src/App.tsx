/**
 * AgentCrashLab — App Router
 */

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import DashboardHome from './pages/DashboardHome';
import TestRunsList from './pages/TestRunsList';
import TestRunCreate from './pages/TestRunCreate';
import TestRunDetails from './pages/TestRunDetails';
import AgentsList from './pages/AgentsList';
import ScenariosList from './pages/ScenariosList';
import FailuresList from './pages/FailuresList';
import ReplayList from './pages/ReplayList';
import RegressionDashboard from './pages/RegressionDashboard';
import ReportsPage from './pages/ReportsPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route index element={<DashboardHome />} />
          <Route path="/agents" element={<AgentsList />} />
          <Route path="/scenarios" element={<ScenariosList />} />
          <Route path="/test-runs" element={<TestRunsList />} />
          <Route path="/test-runs/new" element={<TestRunCreate />} />
          <Route path="/test-runs/:id" element={<TestRunDetails />} />
          <Route path="/failures" element={<FailuresList />} />
          <Route path="/replay" element={<ReplayList />} />
          <Route path="/regression" element={<RegressionDashboard />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
