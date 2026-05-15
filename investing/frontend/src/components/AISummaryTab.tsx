import { useState } from 'react'
import { Brain, RefreshCw, AlertCircle } from 'lucide-react'
import { api } from '../api/client'
import type { AISummary } from '../types'

export default function AISummaryTab() {
  const [summary, setSummary] = useState<AISummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const generate = async () => {
    setLoading(true)
    setError(null)
    try {
      setSummary(await api.getSummary())
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4 max-w-2xl">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-white">AI Portfolio Summary</h2>
          <p className="text-sm text-gray-400">Generate a weekly analysis using Claude AI.</p>
        </div>
        <button
          onClick={generate}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Brain size={16} />
          {loading ? 'Generating…' : 'Generate Summary'}
        </button>
      </div>

      <div className="bg-amber-950/50 border border-amber-800/50 rounded-xl p-4 flex gap-3">
        <AlertCircle size={18} className="text-amber-400 shrink-0 mt-0.5" />
        <p className="text-sm text-amber-300">
          AI summaries are for informational purposes only. Not financial advice. Always do your own research before making investment decisions.
        </p>
      </div>

      {error && (
        <div className="bg-red-950 border border-red-800 text-red-300 rounded-lg p-3 text-sm">{error}</div>
      )}

      {!summary && !loading && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center text-gray-400">
          <Brain size={40} className="mx-auto mb-3 text-gray-600" />
          <p className="text-lg mb-1">No summary yet</p>
          <p className="text-sm">Click "Generate Summary" to get a weekly AI analysis of your portfolio.</p>
          <p className="text-xs mt-2 text-gray-600">Requires ANTHROPIC_API_KEY in your .env file.</p>
        </div>
      )}

      {loading && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center">
          <RefreshCw size={32} className="animate-spin text-green-500 mx-auto mb-3" />
          <p className="text-gray-400">Analysing your portfolio…</p>
        </div>
      )}

      {summary && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-green-400">
              <Brain size={18} />
              <span className="text-sm font-medium">Weekly Analysis</span>
            </div>
            <span className="text-xs text-gray-500">
              {new Date(summary.generated_at).toLocaleString()}
            </span>
          </div>
          <div className="space-y-3">
            {summary.summary.split('\n').filter(Boolean).map((line, i) => (
              <p key={i} className="text-gray-300 text-sm leading-relaxed">{line}</p>
            ))}
          </div>
          <button
            onClick={generate}
            className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors mt-2"
          >
            <RefreshCw size={12} /> Regenerate
          </button>
        </div>
      )}
    </div>
  )
}
