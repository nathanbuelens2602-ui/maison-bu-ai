import { useState, useEffect, useCallback } from 'react'
import { TrendingUp, TrendingDown, RefreshCw, LayoutDashboard, List, Lightbulb, Brain, Settings } from 'lucide-react'
import { api } from './api/client'
import type { PortfolioSummary } from './types'
import Dashboard from './components/Dashboard'
import HoldingsTab from './components/HoldingsTab'
import SuggestionsTab from './components/SuggestionsTab'
import AISummaryTab from './components/AISummaryTab'
import SettingsTab from './components/SettingsTab'

type Tab = 'dashboard' | 'holdings' | 'suggestions' | 'ai' | 'settings'

function fmt(n: number, decimals = 2) {
  return new Intl.NumberFormat('de-DE', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(n)
}

export default function App() {
  const [tab, setTab] = useState<Tab>('dashboard')
  const [portfolio, setPortfolio] = useState<PortfolioSummary | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      setError(null)
      const data = await api.getPortfolio()
      setPortfolio(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  const refresh = async () => {
    setRefreshing(true)
    try {
      const data = await api.refreshPortfolio()
      setPortfolio(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setRefreshing(false)
    }
  }

  useEffect(() => { load() }, [load])

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard size={16} /> },
    { id: 'holdings', label: 'Holdings', icon: <List size={16} /> },
    { id: 'suggestions', label: 'Suggestions', icon: <Lightbulb size={16} /> },
    { id: 'ai', label: 'AI Summary', icon: <Brain size={16} /> },
    { id: 'settings', label: 'Settings', icon: <Settings size={16} /> },
  ]

  return (
    <div className="min-h-screen bg-gray-950">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center">
              <TrendingUp size={18} className="text-white" />
            </div>
            <span className="font-semibold text-white text-lg">Investing Assistant</span>
          </div>
          {portfolio && (
            <div className="flex items-center gap-6">
              <div className="text-right">
                <p className="text-xs text-gray-400">Portfolio Value</p>
                <p className="font-bold text-white text-lg">€{fmt(portfolio.total_value)}</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-400">Total P&L</p>
                <p className={`font-bold text-lg flex items-center gap-1 ${portfolio.total_pnl >= 0 ? 'text-brand-500' : 'text-red-400'}`}>
                  {portfolio.total_pnl >= 0 ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                  €{fmt(Math.abs(portfolio.total_pnl))} ({portfolio.total_pnl >= 0 ? '+' : '-'}{fmt(Math.abs(portfolio.total_pnl_pct))}%)
                </p>
              </div>
              <button
                onClick={refresh}
                disabled={refreshing}
                className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors disabled:opacity-50"
                title="Refresh prices"
              >
                <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
              </button>
            </div>
          )}
        </div>

        {/* Tabs */}
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex gap-1">
            {tabs.map(t => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                  tab === t.id
                    ? 'border-brand-500 text-brand-400'
                    : 'border-transparent text-gray-400 hover:text-gray-200'
                }`}
              >
                {t.icon}
                {t.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {loading && (
          <div className="flex items-center justify-center h-64">
            <RefreshCw size={32} className="animate-spin text-brand-500" />
          </div>
        )}

        {error && (
          <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg p-4 mb-4">
            <strong>Error:</strong> {error}. Make sure the backend is running on port 8000.
          </div>
        )}

        {!loading && portfolio && (
          <>
            {tab === 'dashboard' && <Dashboard portfolio={portfolio} />}
            {tab === 'holdings' && <HoldingsTab portfolio={portfolio} onRefresh={load} />}
            {tab === 'suggestions' && <SuggestionsTab />}
            {tab === 'ai' && <AISummaryTab />}
            {tab === 'settings' && <SettingsTab />}
          </>
        )}
      </main>
    </div>
  )
}
