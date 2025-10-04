import { useState, useEffect } from 'react'
import RBACDashboard from './components/RBACDashboard'
import CustomerChat from './components/CustomerChat'
import AnalystConsole from './components/AnalystConsole'
import PolicyView from './components/PolicyView'

function App() {
  const [currentView, setCurrentView] = useState('rbac')
  const [systemHealth, setSystemHealth] = useState(null)
  const [connectionStatus, setConnectionStatus] = useState('checking')
  const [incidents, setIncidents] = useState([])

  useEffect(() => {
    checkSystemConnection()
    const interval = setInterval(checkSystemConnection, 8000)
    return () => clearInterval(interval)
  }, [])

  const checkSystemConnection = async () => {
    try {
      const response = await fetch('http://localhost:9000/health')
      if (response.ok) {
        const data = await response.json()
        setSystemHealth(data)
        setConnectionStatus('connected')
        fetchIncidents()
      } else {
        setConnectionStatus('error')
      }
    } catch (error) {
      setConnectionStatus('offline')
    }
  }

  const fetchIncidents = async () => {
    try {
      const response = await fetch('http://localhost:9000/incidents')
      if (response.ok) {
        const data = await response.json()
        setIncidents(data.incidents || [])
      }
    } catch (error) {
      console.log('Could not fetch incidents')
    }
  }

  const getStatusColor = () => {
    if (connectionStatus === 'connected') return 'text-emerald-600'
    if (connectionStatus === 'offline') return 'text-red-600'
    return 'text-amber-600'
  }

  const getStatusText = () => {
    if (connectionStatus === 'connected') return 'System Online'
    if (connectionStatus === 'offline') return 'System Offline'
    return 'Connecting...'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-xl font-bold">F</span>
              </div>
              <div>
                <div className="text-xl font-semibold text-slate-900">FortressAI</div>
                <div className="text-xs text-slate-500">Banking Security Platform</div>
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex space-x-1">
              {[
                { id: 'chat', label: 'Banking Assistant', icon: '🤖' },
                { id: 'rbac', label: 'RBAC Dashboard', icon: '🔐' },
                { id: 'analyst', label: 'Security Console', icon: '📊' },
                { id: 'policy', label: 'Policies', icon: '🛡️' }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setCurrentView(item.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${currentView === item.id
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'text-slate-600 hover:bg-slate-100'
                    }`}
                >
                  <span>{item.icon}</span>
                  <span>{item.label}</span>
                </button>
              ))}
            </nav>

            {/* Status */}
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 ${getStatusColor()}`}>
                <div className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-emerald-600 animate-pulse' :
                    connectionStatus === 'offline' ? 'bg-red-600' : 'bg-amber-600'
                  }`}></div>
                <span className="text-sm font-medium">{getStatusText()}</span>
              </div>
              {systemHealth && (
                <div className="px-3 py-1 bg-slate-100 rounded-full">
                  <span className="text-sm font-medium text-slate-700">
                    Health: {systemHealth.health_score}%
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {currentView === 'rbac' && (
          <RBACDashboard
            connectionStatus={connectionStatus}
          />
        )}

        {currentView === 'chat' && (
          <CustomerChat
            systemHealth={systemHealth}
            connectionStatus={connectionStatus}
            onIncidentUpdate={fetchIncidents}
          />
        )}

        {currentView === 'analyst' && (
          <AnalystConsole
            systemHealth={systemHealth}
            incidents={incidents}
            connectionStatus={connectionStatus}
            refreshData={checkSystemConnection}
          />
        )}

        {currentView === 'policy' && (
          <PolicyView
            connectionStatus={connectionStatus}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 border-t border-slate-200 bg-white">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-slate-500">
          <p>FortressAI Banking Security Platform • Unified RBAC • 10 Banking Roles • Zero-Trust Architecture</p>
        </div>
      </footer>
    </div>
  )
}

export default App
