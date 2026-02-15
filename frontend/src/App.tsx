import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Organizations from './pages/Organizations'
import PeriodForm from './pages/PeriodForm'
import Plans from './pages/Plans'
import CalculationTable from './pages/CalculationTable'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token')
  if (!token) return <Navigate to="/login" replace />
  return <>{children}</>
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="orgs" element={<Organizations />} />
        <Route path="orgs/:orgId/periods" element={<PeriodForm />} />
        <Route path="orgs/:orgId/periods/:periodId" element={<PeriodForm />} />
        <Route path="orgs/:orgId/table" element={<CalculationTable />} />
        <Route path="orgs/:orgId/plans" element={<Plans />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
