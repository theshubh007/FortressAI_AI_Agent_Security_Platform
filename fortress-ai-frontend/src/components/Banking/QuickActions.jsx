/**
 * Quick Actions Component
 * Pre-defined banking queries for quick access
 */

const QuickActions = ({ onActionClick, disabled }) => {
  const actions = [
    {
      id: 'balance',
      label: 'Check Balance',
      icon: '💰',
      query: 'What is my account balance?',
      color: 'bg-blue-50 hover:bg-blue-100 text-blue-700'
    },
    {
      id: 'transactions',
      label: 'Recent Transactions',
      icon: '📊',
      query: 'Show me my recent transactions',
      color: 'bg-purple-50 hover:bg-purple-100 text-purple-700'
    },
    {
      id: 'transfer',
      label: 'Transfer Money',
      icon: '💸',
      query: 'I want to transfer money',
      color: 'bg-green-50 hover:bg-green-100 text-green-700'
    },
    {
      id: 'summary',
      label: 'Account Summary',
      icon: '📈',
      query: 'Give me a summary of my accounts',
      color: 'bg-amber-50 hover:bg-amber-100 text-amber-700'
    }
  ]

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
      <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center">
        <span className="mr-2">⚡</span>
        Quick Actions
      </h3>

      <div className="grid grid-cols-2 gap-2">
        {actions.map((action) => (
          <button
            key={action.id}
            onClick={() => onActionClick(action.query)}
            disabled={disabled}
            className={`${action.color} px-3 py-2 rounded-lg text-xs font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-md`}
          >
            <div className="flex items-center space-x-2">
              <span className="text-base">{action.icon}</span>
              <span>{action.label}</span>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

export default QuickActions
