import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { submitRCA, RCASessionCreate } from '../api/client'

export default function SubmitRCA() {
  const navigate = useNavigate()
  const [formData, setFormData] = useState<RCASessionCreate>({
    lot_id: '',
    wafer_id: '',
    bin: 5,
    priority: 'normal',
    user_id: 'user@company.com',
  })

  const mutation = useMutation({
    mutationFn: submitRCA,
    onSuccess: (data) => {
      navigate(`/status/${data.session_id}`)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate(formData)
  }

  return (
    <div className="max-w-3xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Submit New RCA Request</h2>
        <p className="mt-2 text-sm text-gray-600">Initiate a root cause analysis for defect investigation</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white shadow-xl rounded-2xl px-8 pt-8 pb-8 border border-gray-100">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-gray-700 text-sm font-semibold mb-2" htmlFor="lot_id">
              Lot ID
            </label>
            <input
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              id="lot_id"
              type="text"
              placeholder="LOT-2024-001"
              value={formData.lot_id}
              onChange={(e) => setFormData({ ...formData, lot_id: e.target.value })}
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-semibold mb-2" htmlFor="wafer_id">
              Wafer ID
            </label>
            <input
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              id="wafer_id"
              type="text"
              placeholder="W123"
              value={formData.wafer_id}
              onChange={(e) => setFormData({ ...formData, wafer_id: e.target.value })}
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block text-gray-700 text-sm font-semibold mb-2" htmlFor="bin">
              Bin Number
            </label>
            <input
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              id="bin"
              type="number"
              placeholder="5"
              value={formData.bin}
              onChange={(e) => setFormData({ ...formData, bin: parseInt(e.target.value) })}
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-semibold mb-2" htmlFor="priority">
              Priority Level
            </label>
            <select
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all bg-white"
              id="priority"
              value={formData.priority}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  priority: e.target.value as RCASessionCreate['priority'],
                })
              }
            >
              <option value="low">🟢 Low Priority</option>
              <option value="normal">🟡 Normal Priority</option>
              <option value="high">🟠 High Priority</option>
              <option value="critical">🔴 Critical Priority</option>
            </select>
          </div>
        </div>

        <div className="mb-8">
          <label className="block text-gray-700 text-sm font-semibold mb-2" htmlFor="user_id">
            User ID
          </label>
          <input
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
            id="user_id"
            type="email"
            placeholder="engineer@company.com"
            value={formData.user_id}
            onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
            required
          />
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-all duration-200"
          >
            Cancel
          </button>
          <button
            className="px-8 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transition-all duration-200 flex items-center"
            type="submit"
            disabled={mutation.isPending}
          >
            {mutation.isPending ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Submitting...
              </>
            ) : (
              <>
                <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Submit RCA Request
              </>
            )}
          </button>
        </div>

        {mutation.isError && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-xl flex items-start">
            <svg className="w-5 h-5 text-red-600 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="font-semibold">Error submitting request</h3>
              <p className="text-sm mt-1">{(mutation.error as Error).message}</p>
            </div>
          </div>
        )}
      </form>
    </div>
  )
}
