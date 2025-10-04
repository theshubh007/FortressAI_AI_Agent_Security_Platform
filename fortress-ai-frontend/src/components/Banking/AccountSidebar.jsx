/**
 * Account Sidebar Component
 * Displays user accounts with balances
 */

import { useState, useEffect } from 'react'
import { bankingAPIService } from '../../services/bankingAPI'

const AccountSidebar = ({ userId, onAccountSelect }) => {
  const [accounts, setAccounts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selectedAccount, setSelectedAccount] = useState(null)

  useEffect(() => {
    loadAccounts()
  }, [userId])

  const loadAccounts = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await bankingAPIService.getUserAccounts(userId)
      setAccounts(data)
      if (data.length > 0) {
        setSelectedAccount(data[0].account_id)
      }
    } catch (err) {
      setError('Failed to load accounts')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const formatBalance = (balance) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(balance)
  }

  const getAccountIcon = (type) => {
    const icons = {
      checking: '💳',
      savings: '🏦',
      credit: '💰',
      business: '🏢'
    }
    return icons[type] || '💼'
  }

  const getAccountColor = (type) => {
    const colors = {
      checking: 'from-blue-500 to-blue-600',
      savings: 'from-green-500 to-green-600',
      credit: 'from-purple-500 to-purple-600',
      business: 'from-amber-500 to-amber-600'
    }
    return colors[type] || 'from-slate-500 to-slate-600'
  }

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-slate-200 rounded w-3/4"></div>
          <div className="h-20 bg-slate-200 rounded"></div>
          <div className="h-20 bg-slate-200 rounded"></div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="text-center text-red-600">
          <span className="text-2xl mb-2 block">⚠️</span>
          <p className="text-sm">{error}</p>
          <button
            onClick={loadAccounts}
            className="mt-3 text-xs text-blue-600 hover:text-blue-700 font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-700 flex items-center">
          <span className="mr-2">👤</span>
          My Accounts
        </h3>
        <button
          onClick={loadAccounts}
          className="text-slate-400 hover:text-slate-600 transition-colors"
          title="Refresh"
        >
          <span className="text-sm">🔄</span>
        </button>
      </div>

      <div className="space-y-3">
        {accounts.map((account) => (
          <div
            key={account.account_id}
            onClick={() => {
              setSelectedAccount(account.account_id)
              onAccountSelect?.(account)
            }}
            className={`p-4 rounded-lg cursor-pointer transition-all ${selectedAccount === account.account_id
                ? 'ring-2 ring-blue-500 bg-blue-50'
                : 'bg-slate-50 hover:bg-slate-100'
              }`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center space-x-2">
                <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${getAccountColor(account.account_type)} flex items-center justify-center`}>
                  <span className="text-white text-sm">{getAccountIcon(account.account_type)}</span>
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-900">{account.nickname}</p>
                  <p className="text-xs text-slate-500">{account.account_id}</p>
                </div>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${account.status === 'active'
                  ? 'bg-green-100 text-green-700'
                  : 'bg-slate-100 text-slate-700'
                }`}>
                {account.status}
              </span>
            </div>

            <div className="mt-2 pt-2 border-t border-slate-200">
              <p className="text-xs text-slate-500 mb-1">Balance</p>
              <p className="text-lg font-bold text-slate-900">{formatBalance(account.balance)}</p>
            </div>
          </div>
        ))}
      </div>

      {accounts.length === 0 && (
        <div className="text-center py-8 text-slate-400">
          <span className="text-3xl mb-2 block">📭</span>
          <p className="text-sm">No accounts found</p>
        </div>
      )}
    </div>
  )
}

export default AccountSidebar
