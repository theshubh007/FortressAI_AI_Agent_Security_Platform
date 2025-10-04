import BankingChat from './Banking/BankingChat'

const CustomerChat = ({ systemHealth, connectionStatus, onIncidentUpdate }) => {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Banking Assistant</h1>
        <p className="text-slate-600">
          Chat with our AI-powered banking assistant to manage your accounts, view transactions, and transfer money.
        </p>
      </div>

      <BankingChat userId="user123" />
    </div>
  )
}

export default CustomerChat
