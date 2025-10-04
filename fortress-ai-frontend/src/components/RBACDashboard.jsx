import { useState, useEffect } from 'react'

const RBACDashboard = ({ connectionStatus }) => {
  const [selectedRole, setSelectedRole] = useState(null)
  const [testScenario, setTestScenario] = useState(null)
  const [testResult, setTestResult] = useState(null)
  const [isTestingAPI, setIsTestingAPI] = useState(false)

  // Banking roles configuration
  const roles = [
    {
      id: 'csr',
      name: 'Customer Service Rep',
      icon: '👤',
      color: 'blue',
      users: ['Alice Johnson', 'Bob Smith'],
      apiKey: 'CSR-KEY-001',
      transferLimit: 0,
      description: 'Read-only access to customer accounts',
      apis: [
        'internal://agent/account_inquiry',
        'internal://agent/transaction_history',
        'internal://agent/balance_check'
      ]
    },
    {
      id: 'branch_manager',
      name: 'Branch Manager',
      icon: '👔',
      color: 'indigo',
      users: ['Charlie Brown'],
      apiKey: 'MANAGER-KEY-001',
      transferLimit: 50000,
      description: 'Branch operations and loan approvals',
      apis: [
        'internal://agent/account_inquiry',
        'internal://agent/initiate_transfer',
        'internal://agent/approve_loan',
        'internal://agent/override_limit'
      ]
    },
    {
      id: 'treasury_manager',
      name: 'Treasury Manager',
      icon: '💼',
      color: 'purple',
      users: ['Diana Prince'],
      apiKey: 'TREASURY-KEY-001',
      transferLimit: 10000000,
      description: 'Corporate treasury and FX trading',
      apis: [
        'internal://agent/initiate_transfer',
        'internal://agent/fx_execution',
        'internal://agent/cash_forecast',
        'internal://agent/liquidity_report'
      ]
    },
    {
      id: 'fraud_investigator',
      name: 'Fraud Investigator',
      icon: '🔍',
      color: 'red',
      users: ['Eve Martinez', 'Frank Castle'],
      apiKey: 'FRAUD-KEY-001',
      transferLimit: 0,
      description: 'Fraud detection and account security',
      apis: [
        'internal://agent/freeze_account',
        'internal://agent/fraud_alert',
        'internal://agent/transaction_analysis',
        'internal://agent/kyc_verify'
      ]
    },
    {
      id: 'compliance_officer',
      name: 'Compliance Officer',
      icon: '📋',
      color: 'green',
      users: ['Grace Hopper'],
      apiKey: 'COMPLIANCE-KEY-001',
      transferLimit: 0,
      description: 'Compliance, audit, and reporting',
      apis: [
        'internal://agent/kyc_verify',
        'internal://agent/aml_check',
        'internal://agent/regulatory_report',
        'internal://agent/audit_trail'
      ]
    },
    {
      id: 'loan_officer',
      name: 'Loan Officer',
      icon: '🏦',
      color: 'teal',
      users: ['Henry Ford'],
      apiKey: 'LOAN-KEY-001',
      transferLimit: 0,
      description: 'Loan processing and credit analysis',
      apis: [
        'internal://agent/credit_check',
        'internal://agent/loan_application',
        'internal://agent/approve_loan'
      ]
    },
    {
      id: 'cfo',
      name: 'CFO',
      icon: '👑',
      color: 'amber',
      users: ['Iris West'],
      apiKey: 'CFO-KEY-001',
      transferLimit: 100000000,
      description: 'Executive oversight - full access',
      apis: [
        'internal://agent/*',
        'https://api.bank.com/*'
      ]
    },
    {
      id: 'payment_processor',
      name: 'Payment Processor',
      icon: '💳',
      color: 'cyan',
      users: ['Jack Ryan'],
      apiKey: 'PAYMENT-KEY-001',
      transferLimit: 100000,
      description: 'Payment processing and batch transfers',
      apis: [
        'internal://agent/initiate_transfer',
        'internal://agent/batch_payment',
        'internal://agent/payment_status'
      ]
    },
    {
      id: 'risk_analyst',
      name: 'Risk Analyst',
      icon: '📈',
      color: 'orange',
      users: ['Kate Bishop'],
      apiKey: 'RISK-KEY-001',
      transferLimit: 0,
      description: 'Risk management and analytics',
      apis: [
        'internal://agent/risk_assessment',
        'internal://agent/portfolio_analysis',
        'internal://agent/stress_test'
      ]
    },
    {
      id: 'customer',
      name: 'Customer',
      icon: '🙋',
      color: 'slate',
      users: ['John Doe', 'Jane Smith', 'Mike Wilson'],
      apiKey: 'CUSTOMER-KEY-001',
      transferLimit: 5000,
      description: 'Self-service banking',
      apis: [
        'internal://agent/account_inquiry',
        'internal://agent/transaction_history',
        'internal://agent/initiate_transfer',
        'internal://agent/bill_payment'
      ]
    }
  ]

  // Test scenarios
  const scenarios = [
    {
      id: 1,
      name: 'Account Balance Check',
      input: 'Show me account balance for customer #12345',
      api: 'internal://agent/account_inquiry',
      amount: null,
      shouldPass: ['csr', 'branch_manager', 'customer', 'cfo']
    },
    {
      id: 2,
      name: 'Small Transfer ($1,000)',
      input: 'Transfer $1,000 to vendor account',
      api: 'internal://agent/initiate_transfer',
      amount: 1000,
      shouldPass: ['branch_manager', 'treasury_manager', 'payment_processor', 'customer', 'cfo']
    },
    {
      id: 3,
      name: 'Large Transfer ($100,000)',
      input: 'Wire $100,000 to supplier',
      api: 'internal://agent/initiate_transfer',
      amount: 100000,
      shouldPass: ['treasury_manager', 'cfo']
    },
    {
      id: 4,
      name: 'Freeze Account',
      input: 'Freeze account #67890 due to suspicious activity',
      api: 'internal://agent/freeze_account',
      amount: null,
      shouldPass: ['fraud_investigator', 'cfo']
    },
    {
      id: 5,
      name: 'Compliance Report',
      input: 'Generate compliance report for Q4',
      api: 'internal://agent/regulatory_report',
      amount: null,
      shouldPass: ['compliance_officer', 'cfo']
    }
  ]

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 border-blue-200 text-blue-700',
      indigo: 'bg-indigo-50 border-indigo-200 text-indigo-700',
      purple: 'bg-purple-50 border-purple-200 text-purple-700',
      red: 'bg-red-50 border-red-200 text-red-700',
      green: 'bg-green-50 border-green-200 text-green-700',
      teal: 'bg-teal-50 border-teal-200 text-teal-700',
      amber: 'bg-amber-50 border-amber-200 text-amber-700',
      cyan: 'bg-cyan-50 border-cyan-200 text-cyan-700',
      orange: 'bg-orange-50 border-orange-200 text-orange-700',
      slate: 'bg-slate-50 border-slate-200 text-slate-700'
    }
    return colors[color] || colors.blue
  }

  const testAPIAccess = async (role, scenario) => {
    setIsTestingAPI(true)
    setTestScenario(scenario)
    
    // Simulate API test (in real implementation, call your RBAC engine)
    await new Promise(resolve => setTimeout(resolve, 500))
    
    const shouldPass = scenario.shouldPass.includes(role.id)
    const exceedsLimit = scenario.amount && scenario.amount > role.transferLimit
    
    const result = {
      role: role.name,
      scenario: scenario.name,
      allowed: shouldPass && !exceedsLimit,
      reason: !shouldPass ? 'API not permitted' : 
              exceedsLimit ? `Amount exceeds limit ($${role.transferLimit.toLocaleString()})` : 
              'Permission granted'
    }
    
    setTestResult(result)
    setIsTestingAPI(false)
  }

  if (connectionStatus === 'offline') {
    return (
      <div className="text-center py-20">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <span className="text-3xl">⚠️</span>
        </div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">System Offline</h2>
        <p className="text-slate-600 mb-6">
          Start the FortressAI backend to access RBAC features
        </p>
        <div className="bg-slate-900 text-green-400 rounded-lg p-4 max-w-md mx-auto font-mono text-sm">
          docker-compose up --build
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900 mb-2">
          Role-Based Access Control Dashboard
        </h1>
        <p className="text-slate-600">
          10 banking roles with unified API permissions and financial guardrails
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-600 text-sm font-medium">Total Roles</span>
            <span className="text-2xl">🔐</span>
          </div>
          <div className="text-3xl font-bold text-slate-900">{roles.length}</div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-600 text-sm font-medium">Active Users</span>
            <span className="text-2xl">👥</span>
          </div>
          <div className="text-3xl font-bold text-slate-900">
            {roles.reduce((sum, role) => sum + role.users.length, 0)}
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-600 text-sm font-medium">Internal APIs</span>
            <span className="text-2xl">🔌</span>
          </div>
          <div className="text-3xl font-bold text-slate-900">25+</div>
        </div>
        
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-600 text-sm font-medium">Architecture</span>
            <span className="text-2xl">🛡️</span>
          </div>
          <div className="text-lg font-bold text-slate-900">Zero-Trust</div>
        </div>
      </div>

      {/* Roles Grid */}
      <div>
        <h2 className="text-xl font-semibold text-slate-900 mb-4">Banking Roles</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {roles.map((role) => (
            <div
              key={role.id}
              onClick={() => setSelectedRole(role)}
              className={`bg-white rounded-xl shadow-sm border-2 p-6 cursor-pointer transition-all hover:shadow-md ${
                selectedRole?.id === role.id ? 'border-blue-500 ring-2 ring-blue-200' : 'border-slate-200'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-2xl ${getColorClasses(role.color)}`}>
                    {role.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-900">{role.name}</h3>
                    <p className="text-xs text-slate-500">{role.users.length} user(s)</p>
                  </div>
                </div>
              </div>
              
              <p className="text-sm text-slate-600 mb-3">{role.description}</p>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500">Transfer Limit:</span>
                  <span className="font-semibold text-slate-900">
                    {role.transferLimit === 0 ? 'None' : `$${role.transferLimit.toLocaleString()}`}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-500">APIs:</span>
                  <span className="font-semibold text-slate-900">{role.apis.length}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Role Details */}
      {selectedRole && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className={`w-14 h-14 rounded-lg flex items-center justify-center text-3xl ${getColorClasses(selectedRole.color)}`}>
                {selectedRole.icon}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-900">{selectedRole.name}</h2>
                <p className="text-slate-600">{selectedRole.description}</p>
              </div>
            </div>
            <button
              onClick={() => setSelectedRole(null)}
              className="text-slate-400 hover:text-slate-600"
            >
              <span className="text-2xl">×</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Users */}
            <div>
              <h3 className="text-sm font-semibold text-slate-700 mb-3">Assigned Users</h3>
              <div className="space-y-2">
                {selectedRole.users.map((user, index) => (
                  <div key={index} className="flex items-center space-x-2 text-sm">
                    <div className="w-8 h-8 bg-slate-100 rounded-full flex items-center justify-center">
                      <span className="text-slate-600">👤</span>
                    </div>
                    <span className="text-slate-900">{user}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Limits */}
            <div>
              <h3 className="text-sm font-semibold text-slate-700 mb-3">Financial Limits</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">Max Transfer:</span>
                  <span className="font-semibold text-slate-900">
                    {selectedRole.transferLimit === 0 ? 'Not Allowed' : `$${selectedRole.transferLimit.toLocaleString()}`}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-600">API Key:</span>
                  <span className="font-mono text-xs text-slate-500">{selectedRole.apiKey}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Allowed APIs */}
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Allowed APIs ({selectedRole.apis.length})</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {selectedRole.apis.map((api, index) => (
                <div key={index} className="bg-slate-50 rounded-lg px-3 py-2 text-sm font-mono text-slate-700 border border-slate-200">
                  {api}
                </div>
              ))}
            </div>
          </div>

          {/* Test Scenarios */}
          <div>
            <h3 className="text-sm font-semibold text-slate-700 mb-3">Test Scenarios</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {scenarios.map((scenario) => (
                <button
                  key={scenario.id}
                  onClick={() => testAPIAccess(selectedRole, scenario)}
                  disabled={isTestingAPI}
                  className="text-left p-4 bg-slate-50 hover:bg-slate-100 rounded-lg border border-slate-200 transition-colors disabled:opacity-50"
                >
                  <div className="font-medium text-slate-900 mb-1">{scenario.name}</div>
                  <div className="text-xs text-slate-600 mb-2">{scenario.input}</div>
                  <div className="text-xs font-mono text-slate-500">{scenario.api}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Test Result */}
          {testResult && testScenario && (
            <div className={`mt-6 p-4 rounded-lg border-2 ${
              testResult.allowed 
                ? 'bg-green-50 border-green-200' 
                : 'bg-red-50 border-red-200'
            }`}>
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-slate-900">Test Result</span>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                  testResult.allowed 
                    ? 'bg-green-100 text-green-700' 
                    : 'bg-red-100 text-red-700'
                }`}>
                  {testResult.allowed ? '✅ ALLOWED' : '❌ DENIED'}
                </span>
              </div>
              <div className="text-sm text-slate-700">
                <strong>{testResult.role}</strong> attempting: <strong>{testResult.scenario}</strong>
              </div>
              <div className="text-sm text-slate-600 mt-1">
                Reason: {testResult.reason}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default RBACDashboard
