/**
 * Banking Agent API Service
 * Handles communication with LangGraph Agent
 */

const AGENT_URL = import.meta.env.VITE_AGENT_URL || 'http://localhost:8003'

export const bankingAgentService = {
  /**
   * Send a query to the banking agent
   */
  async sendQuery(query, userId = 'user123') {
    try {
      const response = await fetch(`${AGENT_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          user_id: userId
        })
      })

      if (!response.ok) {
        throw new Error(`Agent error: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Banking agent error:', error)
      throw error
    }
  },

  /**
   * Check agent health
   */
  async checkHealth() {
    try {
      const response = await fetch(`${AGENT_URL}/health`)
      return await response.json()
    } catch (error) {
      console.error('Agent health check failed:', error)
      return { status: 'offline' }
    }
  }
}
