const PolicyView = ({ connectionStatus }) => {
  return (
    <div className="text-center py-20">
      <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <span className="text-3xl">🛡️</span>
      </div>
      <h2 className="text-2xl font-semibold text-slate-900 mb-2">Policy Management</h2>
      <p className="text-slate-600">
        DLP and security policies coming soon
      </p>
    </div>
  )
}

export default PolicyView
