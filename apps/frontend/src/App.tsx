import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import AgentDetails from './pages/AgentDetails'
import RegisterAgent from './pages/RegisterAgent'
import GroupManagement from './pages/GroupManagement'
import Reputation from './pages/Reputation'
import Analytics from './pages/Analytics'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agents/:id" element={<AgentDetails />} />
            <Route path="/register" element={<RegisterAgent />} />
            <Route path="/groups" element={<GroupManagement />} />
            <Route path="/reputation" element={<Reputation />} />
            <Route path="/analytics" element={<Analytics />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  )
}

export default App

