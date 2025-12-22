import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'

interface Evidence {
  type: string
  description: string
  confidence: number
}

interface Hypothesis {
  hypothesis: string
  rank: number
  confidence_score: number
  evidence: Evidence[]
  recommended_actions?: string[]
}

interface ResultsData {
  session_id: string
  status: string
  hypotheses: Hypothesis[]
  metadata?: {
    lot_id?: string
    wafer_id?: string
    defect_type?: string
  }
}

export default function RCAResults() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const [results, setResults] = useState<ResultsData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!sessionId) return
    
    const loadResults = async () => {
      try {
        const response = await fetch(`/api/v1/rca/results/${sessionId}`)
        if (!response.ok) throw new Error(`Failed to fetch results: ${response.statusText}`)
        const data = await response.json()
        setResults(data)
        setError(null)
      } catch (err: any) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadResults()
  }, [sessionId])

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-500'
    if (confidence >= 0.6) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'High'
    if (confidence >= 0.6) return 'Medium'
    return 'Low'
  }

  if (loading) {
    return (
      <div className="animate-fade-in">
        <div className="text-center py-20">
          <div className="relative inline-flex">
            <div className="w-20 h-20 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin"></div>
          </div>
          <p className="mt-6 text-gray-600 font-medium text-lg">Loading results...</p>
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
              <h3 className="text-lg font-semibold text-red-800">Error Loading Results</h3>
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

      <div className="bg-white shadow-xl overflow-hidden rounded-2xl mb-8 border border-gray-100">
        <div className="px-6 py-6 bg-gradient-to-r from-indigo-50 to-purple-50 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-2xl font-bold text-gray-900">
                RCA Analysis Results
              </h3>
              <p className="mt-1 text-sm text-gray-600">
                Session ID: <span className="font-mono font-semibold">{sessionId?.slice(0, 8)}...</span>
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-green-600 font-semibold">Completed</span>
            </div>
          </div>
        </div>
        
        {results?.metadata && (
          <div className="px-6 py-5 bg-gray-50">
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              {results.metadata.lot_id && (
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                  <dt className="text-xs font-medium text-gray-500 uppercase tracking-wide">Lot ID</dt>
                  <dd className="mt-1 text-base font-semibold text-gray-900">{results.metadata.lot_id}</dd>
                </div>
              )}
              {results.metadata.wafer_id && (
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                  <dt className="text-xs font-medium text-gray-500 uppercase tracking-wide">Wafer ID</dt>
                  <dd className="mt-1 text-base font-semibold text-gray-900">{results.metadata.wafer_id}</dd>
                </div>
              )}
              {results.metadata.defect_type && (
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
                  <dt className="text-xs font-medium text-gray-500 uppercase tracking-wide">Defect Type</dt>
                  <dd className="mt-1 text-base font-semibold text-gray-900">{results.metadata.defect_type}</dd>
                </div>
              )}
            </dl>
          </div>
        )}
      </div>

      {results?.hypotheses && results.hypotheses.length > 0 ? (
        <div className="space-y-6">
          {results.hypotheses.map((hypothesis, idx) => (
            <div key={idx} className="bg-white shadow-lg rounded-2xl overflow-hidden border border-gray-200 hover:shadow-xl transition-shadow">
              <div className="px-6 py-5 bg-gradient-to-r from-gray-50 to-gray-100">
                <div className="flex items-start justify-between">
                  <div className="flex-1 flex items-start">
                    <span className="inline-flex items-center justify-center h-12 w-12 rounded-xl bg-gradient-to-br from-indigo-600 to-purple-600 text-white text-lg font-bold mr-4 shadow-lg flex-shrink-0">
                      #{hypothesis.rank}
                    </span>
                    <div className="flex-1">
                      <h4 className="text-xl font-bold text-gray-900">
                        {hypothesis.hypothesis}
                      </h4>
                    </div>
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <span className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-bold text-white shadow-md ${getConfidenceColor(hypothesis.confidence_score)}`}>
                      {getConfidenceLabel(hypothesis.confidence_score)} ({(hypothesis.confidence_score * 100).toFixed(0)}%)
                    </span>
                  </div>
                </div>
                <div className="mt-4">
                  <div className="bg-gray-200 rounded-full h-3 overflow-hidden shadow-inner">
                    <div
                      className={`h-3 rounded-full transition-all duration-500 ${getConfidenceColor(hypothesis.confidence_score)}`}
                      style={{ width: `${hypothesis.confidence_score * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="px-6 py-6">
                <h5 className="text-base font-bold text-gray-900 mb-4 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                  Supporting Evidence
                </h5>
                <ul className="space-y-4">
                  {hypothesis.evidence.map((evidence, evidenceIdx) => (
                    <li key={evidenceIdx} className="border-l-4 border-indigo-500 pl-5 py-2 bg-indigo-50 rounded-r-lg">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <p className="text-xs font-bold text-indigo-700 uppercase tracking-wider">{evidence.type}</p>
                          <p className="mt-1 text-sm text-gray-800">{evidence.description}</p>
                        </div>
                        <div className="ml-4 flex-shrink-0">
                          <div className="text-xs text-gray-600 font-semibold bg-white px-3 py-1 rounded-full border border-gray-200">
                            {(evidence.confidence * 100).toFixed(0)}%
                          </div>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>

                {hypothesis.recommended_actions && hypothesis.recommended_actions.length > 0 && (
                  <div className="mt-8 pt-6 border-t border-gray-200">
                    <h5 className="text-base font-bold text-gray-900 mb-4 flex items-center">
                      <svg className="w-5 h-5 mr-2 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                      Recommended Actions
                    </h5>
                    <ul className="space-y-3">
                      {hypothesis.recommended_actions.map((action, actionIdx) => (
                        <li key={actionIdx} className="flex items-start bg-purple-50 p-4 rounded-lg border border-purple-200">
                          <svg className="w-5 h-5 text-purple-600 mr-3 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span className="text-sm text-gray-800">{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white shadow-lg rounded-2xl p-12 text-center border border-gray-200">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-gray-600 text-lg">No hypotheses found for this analysis.</p>
        </div>
      )}
    </div>
  )
}
