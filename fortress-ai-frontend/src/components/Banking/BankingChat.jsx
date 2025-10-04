/**
 * Banking Chat Component
 * Main chat interface for banking agent
 */

import { useState, useEffect, useRef } from 'react'
import { bankingAgentService } from '../../services/bankingAgent'
import MessageBubble from './MessageBubble'
import QuickActions from './QuickActions'
import AccountSidebar from './AccountSidebar'

const BankingChat = ({ userId = 'user123' }) => {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [agentStatus, setAgentStatus] = useState('checking')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    checkAgentHealth()
    addWelcomeMessage()
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const checkAgentHealth = async () => {
    try {
      const health = await bankingAgentService.checkHealth()
      setAgentStatus(health.status === 'healthy' ? 'online' : 'offline')
    } catch {
      setAgentStatus('offline')
    }
  }

  const addWelcomeMessage = () => {
    setMessages([
      {
        id: Date.now(),
        type: 'agent',
        message: "👋 Hello! I'm your AI banking assistant powered by Claude. I can help you with:\n\n• Checking account balances\n• Viewing transactions\n• Transferring money\n• Account summaries\n\nHow can I help you today?",
        timestamp: new Date().toISOString()
      }
    ])
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async (messageText = inputValue) => {
    if (!messageText.trim() || isLoading) return

    const userMessage = {
      id: Date.now(),
      type: 'user',
      message: messageText,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await bankingAgentService.sendQuery(messageText, userId)

      const agentMessage = {
        id: Date.now() + 1,
        type: 'agent',
        message: response.response,
        timestamp: new Date().toISOString(),
        metadata: {
          messageCount: response.message_count,
          toolCalls: response.tool_calls_made
        }
      }

      setMessages(prev => [...prev, agentMessage])
    } catch (error) {
      const errorMessage = {
        id: Date.now() + 1,
        type: 'agent',
        message: `❌ Sorry, I encountered an error: ${error.message}\n\nPlease make sure the banking agent is running on port 8003.`,
        timestamp: new Date().toISOString()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickAction = (query) => {
    handleSendMessage(query)
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
      {/* Sidebar - Accounts */}
      <div className="lg:col-span-1 space-y-4">
        <AccountSidebar userId={userId} />
        <QuickActions onActionClick={handleQuickAction} disabled={isLoading} />
      </div>

      {/* Main Chat Area */}
      <div className="lg:col-span-3">
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col h-[700px]">
          {/* Chat Header */}
          <div className="px-6 py-4 border-b border-slate-200 bg-gradient-to-r from-blue-50 to-indigo-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-lg">🤖</span>
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-slate-900">Banking Assistant</h2>
                  <p className="text-xs text-slate-500">Powered by AWS Bedrock Claude</p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <div className={`flex items-center space-x-2 ${agentStatus === 'online' ? 'text-green-600' : 'text-red-600'
                  }`}>
                  <div className={`w-2 h-2 rounded-full ${agentStatus === 'online' ? 'bg-green-600 animate-pulse' : 'bg-red-600'
                    }`}></div>
                  <span className="text-xs font-medium">
                    {agentStatus === 'online' ? 'Online' : 'Offline'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-6 bg-slate-50">
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg.message}
                type={msg.type}
                timestamp={msg.timestamp}
              />
            ))}

            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-white rounded-2xl px-4 py-3 shadow-sm border border-slate-200">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="px-6 py-4 border-t border-slate-200 bg-white">
            <div className="flex items-end space-x-3">
              <div className="flex-1">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything about your accounts..."
                  disabled={isLoading || agentStatus === 'offline'}
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:bg-slate-100 disabled:cursor-not-allowed"
                  rows="2"
                />
              </div>
              <button
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || isLoading || agentStatus === 'offline'}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-all hover:shadow-md"
              >
                {isLoading ? (
                  <span className="flex items-center space-x-2">
                    <span className="animate-spin">⏳</span>
                    <span>Sending...</span>
                  </span>
                ) : (
                  <span className="flex items-center space-x-2">
                    <span>Send</span>
                    <span>📤</span>
                  </span>
                )}
              </button>
            </div>

            <p className="text-xs text-slate-400 mt-2">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BankingChat
