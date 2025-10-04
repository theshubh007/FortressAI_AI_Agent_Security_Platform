/**
 * Banking API Service
 * Direct access to Banking API for UI data
 */

const API_URL = import.meta.env.VITE_BANKING_API_URL || 'http://localhost:8004'
const API_KEY = import.meta.env.VITE_BANKING_API_KEY || 'BANKING-API-KEY-123'

const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY
}

export const bankingAPIService = {
  /**
   * Get all accounts for a user
   */
  async getUserAccounts(userId) {
    try {
      const response = await fetch(`${API_URL}/accounts/${userId}`, { headers })
      if (!response.ok) throw new Error('Failed to fetch accounts')
      return await response.json()
    } catch (error) {
      console.error('Get accounts error:', error)
      throw error
    }
  },

  /**
   * Get account balance
   */
  async getAccountBalance(accountId) {
    try {
      const response = await fetch(`${API_URL}/accounts/${accountId}/balance`, { headers })
      if (!response.ok) throw new Error('Failed to fetch balance')
      return await response.json()
    } catch (error) {
      console.error('Get balance error:', error)
      throw error
    }
  },

  /**
   * Get transaction history
   */
  async getTransactions(accountId, limit = 10) {
    try {
      const response = await fetch(
        `${API_URL}/accounts/${accountId}/transactions?limit=${limit}`,
        { headers }
      )
      if (!response.ok) throw new Error('Failed to fetch transactions')
      return await response.json()
    } catch (error) {
      console.error('Get transactions error:', error)
      throw error
    }
  },

  /**
   * Transfer funds
   */
  async transferFunds(fromAccount, toAccount, amount, description = 'Transfer') {
    try {
      const response = await fetch(`${API_URL}/transfer`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          from_account: fromAccount,
          to_account: toAccount,
          amount,
          description
        })
      })
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'Transfer failed')
      }
      return await response.json()
    } catch (error) {
      console.error('Transfer error:', error)
      throw error
    }
  },

  /**
   * Get account summary
   */
  async getAccountSummary(accountId) {
    try {
      const response = await fetch(`${API_URL}/accounts/${accountId}/summary`, { headers })
      if (!response.ok) throw new Error('Failed to fetch summary')
      return await response.json()
    } catch (error) {
      console.error('Get summary error:', error)
      throw error
    }
  },

  /**
   * Check API health
   */
  async checkHealth() {
    try {
      const response = await fetch(`${API_URL}/health`)
      return await response.json()
    } catch (error) {
      console.error('API health check failed:', error)
      return { status: 'offline' }
    }
  }
}
