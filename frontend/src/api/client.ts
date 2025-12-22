/// <reference types="vite/client" />
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface RCASessionCreate {
  lot_id: string
  wafer_id: string
  bin: number
  priority: 'low' | 'normal' | 'high' | 'critical'
  user_id: string
}

export interface RCASessionResponse {
  session_id: string
  status: string
  message: string
}

export interface RCAStatusResponse {
  session_id: string
  status: string
  progress: number
  active_agents: string[]
  completed_agents: string[]
  started_at: string | null
  completed_at: string | null
}

export interface Hypothesis {
  rank: number
  hypothesis: string
  confidence: number
  evidence: Array<{ type: string; detail: string }>
}

export interface RCAResultsResponse {
  session_id: string
  status: string
  hypotheses: Hypothesis[]
  wafer_map_path: string | null
  report_path: string | null
  metadata: Record<string, any>
}

// API functions
export const submitRCA = async (data: RCASessionCreate): Promise<RCASessionResponse> => {
  const response = await api.post('/rca/submit', data)
  return response.data
}

export const getRCAStatus = async (sessionId: string): Promise<RCAStatusResponse> => {
  const response = await api.get(`/rca/status/${sessionId}`)
  return response.data
}

export const getRCAResults = async (sessionId: string): Promise<RCAResultsResponse> => {
  const response = await api.get(`/rca/results/${sessionId}`)
  return response.data
}

export const submitFeedback = async (
  sessionId: string,
  hypothesisId: string,
  rating: number,
  comment?: string,
) => {
  const response = await api.post(`/rca/feedback/${sessionId}`, {
    hypothesis_id: hypothesisId,
    rating,
    comment,
  })
  return response.data
}

export const downloadReport = async (sessionId: string) => {
  const response = await api.get(`/rca/download/${sessionId}/report`)
  return response.data
}

// WebSocket connection
export const connectWebSocket = (sessionId: string) => {
  const wsUrl = `ws://localhost:8000/api/v1/ws/rca/${sessionId}`
  return new WebSocket(wsUrl)
}
