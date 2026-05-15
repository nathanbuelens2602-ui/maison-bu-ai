import { useState, useEffect } from 'react'
import { ArrowUpCircle, MinusCircle, RefreshCw, AlertCircle } from 'lucide-react'
import { api } from '../api/client'
import type { RebalanceSuggestion } from '../types'

function fmt(n: number, decimals = 2) {
  return new Intl.NumberFormat('de-DE', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(n)
}

export default function SuggestionsTab() {
  const [suggestions, setSuggestions] = useState<RebalanceSuggestion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      setSuggestions(await api.getSuggestions())
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">Rebalancing Suggestions</h2>
          <p className="text-sm text-gray-400">Positions that deviate more than 2% from their target allocation.</p>
        </div>
        <button onClick={load} disabled={loading} className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors">
          <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      <div className="bg-amber-950/50 border border-amber-800/50 rounded-xl p-4 flex gap-3">
        <AlertCircle size={18} className="text-amber-400 shrink-0 mt-0.5" />
        <p className="text-sm text-amber-300">These are suggestions only. This app never places orders. All trades must be executed manually on DEGIRO.</p>
      </div>

      {error && <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg p-3 text-sm">{error}</div>}

      {!loading && suggestions.length === 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center text-gray-400">
          <p className="text-lg mb-1">Portfolio is well balanced</p>
          <p className="text-sm">Set target allocations on your holdings to see rebalancing suggestions.</p>
        </div>
      )}

      {suggestions.map((s, i) => (
        <div key={i} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              {s.action === 'BUY'
                ? <ArrowUpCircle size={22} className="text-green-400 shrink-0" />
                : <MinusCircle size={22} className="text-gray-500 shrink-0" />}
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-brand-400">{s.ticker}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${s.action === 'BUY' ? 'bg-green-900/60 text-green-300' : 'bg-gray-800 text-gray-400'}`}>
                    {s.action}
                  </span>
                </div>
                <p className="text-sm text-gray-400 mt-0.5">{s.name}</p>
                <p className="text-sm text-gray-300 mt-1">{s.reason}</p>
              </div>
            </div>
            <div className="text-right shrink-0">
              <div className="text-xs text-gray-500 mb-1">Current → Target</div>
              <div className="text-sm font-medium text-gray-300">{fmt(s.current_pct)}% → {fmt(s.target_pct)}%</div>
              <div className={`text-xs mt-0.5 ${s.diff_pct > 0 ? 'text-green-400' : 'text-red-400'}`}>
                {s.diff_pct > 0 ? '+' : ''}{fmt(s.diff_pct)}%
              </div>
              {s.suggested_amount > 0 && (
                <div className="mt-2 px-2 py-1 bg-green-900/40 border border-green-800/40 rounded-lg text-green-300 text-sm font-medium">
                  Suggested: €{fmt(s.suggested_amount, 0)}
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
