import type { Holding, PortfolioSummary, RebalanceSuggestion, DCASettings, AISummary } from '../types'

const BASE = '/api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || res.statusText)
  }
  return res.json()
}

export const api = {
  getPortfolio: () => request<PortfolioSummary>('/portfolio'),
  refreshPortfolio: () => request<PortfolioSummary>('/portfolio/refresh', { method: 'POST' }),

  addHolding: (data: Omit<Holding, 'id' | 'added_date'>) =>
    request<Holding>('/holdings', { method: 'POST', body: JSON.stringify(data) }),

  updateHolding: (id: number, data: Partial<Omit<Holding, 'id' | 'added_date'>>) =>
    request<Holding>(`/holdings/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  deleteHolding: (id: number) =>
    request<{ ok: boolean }>(`/holdings/${id}`, { method: 'DELETE' }),

  importCSV: async (file: File) => {
    const form = new FormData()
    form.append('file', file)
    const res = await fetch(`${BASE}/holdings/import`, { method: 'POST', body: form })
    if (!res.ok) throw new Error(await res.text())
    return res.json()
  },

  getSummary: () => request<AISummary>('/summary'),
  getSuggestions: () => request<RebalanceSuggestion[]>('/suggestions'),

  getDCA: () => request<DCASettings | null>('/dca'),
  saveDCA: (data: DCASettings) => request<DCASettings>('/dca', { method: 'POST', body: JSON.stringify(data) }),
}
