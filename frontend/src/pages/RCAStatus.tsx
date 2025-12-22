import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

interface AgentStatus {
  agent_name: string
  status: string
  progress: number
  current_task: string
}

interface StatusData {
  session_id: string
  status: string
  overall_progress: number
  agents: AgentStatus[]
  message?: string
}

export default function RCAStatus() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [status, setStatus] = useState<StatusData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sessionId) return
    
    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/v1/rca/status/${sessionId}`)
        if (!response.ok) throw new Error(`Failed to fetch status: ${response.statusText}`)
        const data = await response.json()
        setStatus(data)
        setError(null)
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    pollStatus()
    const interval = setInterval(pollStatus, 3000) // Poll every 3 seconds

    return () => clearInterval(interval)
  }, [sessionId])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600'
      case 'running': return 'text-blue-600'
      case 'failed': return 'text-red-600'
      case 'queued': return 'text-yellow-600'
      default: return 'text-gray-600'
    }
  }

  if (loading) {
    return (
      <div className="animate-fade-in">
        <div className="text-center py-20">
          <div className="relative inline-flex">
            <div className="w-20 h-20 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
          </div>
          <p className="mt-6 text-gray-600 font-medium text-lg">Loading analysis status...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="animate-fade-in">
        <div className="rounded-2xl bg-red-50 border border-red-200 p-8 shadow-lg">
          <div className="flex items-start">
            <svg className="w-8 h-8 text-red-600 mt-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="ml-4 flex-1">
              <h3 className="text-lg font-semibold text-red-800">Error Loading Status</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
              <div className="mt-6">
                <Link to="/" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-red-600 hover:bg-red-700 transition-all">
                  ← Back to Dashboard
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="animate-fade-in">
      <div className="mb-6">
        <Link to="/" className="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-700">
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Dashboard
        </Link>
      </div>

      <div className="bg-white shadow-xl overflow-hidden rounded-2xl border border-gray-100">
        <div className="px-6 py-6 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                RCA Analysis Status
              </h3>
              <p className="mt-1 text-sm text-gray-600">
                Session ID: <span className="font-mono font-semibold">{sessionId?.slice(0, 8)}...</span>
              </p>
            </div>
            <div className={`px-4 py-2 rounded-full font-semibold text-sm ${getStatusColor(status?.status || 'unknown')}`}>
              {status?.status?.toUpperCase() || 'UNKNOWN'}
            </div>
          </div>
        </div>
        
        <div className="px-6 py-6">
          <dl className="grid grid-cols-1 gap-6 sm:grid-cols-2">
            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 p-5 rounded-xl">
              <dt className="text-sm font-medium text-indigo-700">Status</dt>
              <dd className={`mt-2 text-xl font-bold ${getStatusColor(status?.status || 'unknown')}`}>
                {status?.status?.toUpperCase() || 'UNKNOWN'}
              </dd>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-5 rounded-xl">
              <dt className="text-sm font-medium text-purple-700">Overall Progress</dt>
              <dd className="mt-2">
                <div className="flex items-center">
                  <div className="flex-1">
                    <div className="bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
                      <div
                        className="bg-gradient-to-r from-indigo-600 to-purple-600 h-3 rounded-full transition-all duration-500 shadow-sm"
                        style={{ width: `${status?.overall_progress || 0}%` }}
                      ></div>
                    </div>
                  </div>
                  <span className="ml-4 text-xl font-bold text-gray-900">{status?.overall_progress || 0}%</span>
                </div>
              </dd>
            </div>
          </dl>

          {status?.message && (
            <div className="mt-6 rounded-xl bg-blue-50 border border-blue-200 p-5 shadow-sm">
              <div className="flex items-start">
                <svg className="w-5 h-5 text-blue-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="ml-3 text-sm text-blue-800 font-medium">{status.message}</p>
              </div>
            </div>
          )}

          {status?.status === 'completed' && (
            <div className="mt-6">
              <Link
                to={`/results/${sessionId}`}
                className="w-full inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-xl shadow-lg text-white bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 transition-all duration-200 hover:shadow-xl"
              >
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                View Results
              </Link>
            </div>
          )}
        </div>

        {status?.agents && status.agents.length > 0 && (
          <div className="border-t border-gray-200 px-6 py-6 bg-gray-50">
            <h4 className="text-lg font-semibold text-gray-900 mb-5">Agent Status</h4>
            <div className="space-y-4">
              {status.agents.map((agent, idx) => (
                <div key={idx} className="border border-gray-200 rounded-xl p-5 bg-white shadow-sm hover:shadow-md transition-shadow">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <div className={`w-3 h-3 rounded-full mr-3 ${
                        agent.status === 'completed' ? 'bg-green-500 animate-pulse-slow' :
                        agent.status === 'running' ? 'bg-blue-500 animate-pulse' :
                        agent.status === 'failed' ? 'bg-red-500' :
                        'bg-gray-400'
                      }`}></div>
                      <h5 className="text-base font-semibold text-gray-900">{agent.agent_name}</h5>
                    </div>
                    <span className={`text-xs font-bold uppercase px-3 py-1 rounded-full ${
                      agent.status === 'completed' ? 'bg-green-100 text-green-800' :
                      agent.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      agent.status === 'failed' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {agent.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mb-3 italic">{agent.current_task}</p>
                  <div className="flex items-center">
                    <div className="flex-1">
                      <div className="bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          className={`h-2 rounded-full transition-all duration-500 ${
                            agent.status === 'completed' ? 'bg-green-500' :
                            agent.status === 'running' ? 'bg-blue-500' :
                            'bg-gray-400'
                          }`}
                          style={{ width: `${agent.progress}%` }}
                        ></div>
                      </div>
                    </div>
                    <span className="ml-3 text-sm font-semibold text-gray-700">{agent.progress}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
