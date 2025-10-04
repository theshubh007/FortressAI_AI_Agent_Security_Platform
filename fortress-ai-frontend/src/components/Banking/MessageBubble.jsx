/**
 * Message Bubble Component
 * Displays chat messages with different styles for user/agent
 */

const MessageBubble = ({ message, type, timestamp }) => {
  const isUser = type === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}>
      <div className={`flex items-start space-x-2 max-w-[80%] ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${isUser ? 'bg-blue-600' : 'bg-gradient-to-br from-indigo-500 to-purple-600'
          }`}>
          <span className="text-white text-sm font-medium">
            {isUser ? '👤' : '🤖'}
          </span>
        </div>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-4 py-3 rounded-2xl ${isUser
              ? 'bg-blue-600 text-white rounded-tr-sm'
              : 'bg-white text-slate-900 shadow-sm border border-slate-200 rounded-tl-sm'
            }`}>
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message}</p>
          </div>

          {/* Timestamp */}
          {timestamp && (
            <span className="text-xs text-slate-400 mt-1 px-1">
              {new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </span>
          )}
        </div>
      </div>
    </div>
  )
}

export default MessageBubble
