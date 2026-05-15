import { useState, useEffect } from 'react'
import { Save, Bell, Calendar } from 'lucide-react'
import { api } from '../api/client'
import type { DCASettings } from '../types'

export default function SettingsTab() {
  const [dca, setDca] = useState<DCASettings>({ monthly_amount: 500, day_of_month: 1, enabled: true })
  const [saved, setSaved] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getDCA().then(d => {
      if (d) setDca(d)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const save = async () => {
    await api.saveDCA(dca)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const today = new Date()
  const nextDate = new Date(today.getFullYear(), today.getMonth() + (today.getDate() > dca.day_of_month ? 1 : 0), dca.day_of_month)
  const daysUntil = Math.ceil((nextDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))

  return (
    <div className="space-y-6 max-w-xl">
      <h2 className="text-lg font-semibold text-white">Settings</h2>

      {/* DCA reminder */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Calendar size={18} className="text-brand-400" />
          <h3 className="font-medium text-white">Monthly DCA Reminder</h3>
        </div>
        <p className="text-sm text-gray-400">Set a monthly investment target. The app will show you when it's time to invest.</p>

        {!loading && dca.enabled && daysUntil <= 5 && (
          <div className="bg-brand-950/60 border border-brand-800/50 rounded-lg p-3 flex gap-2">
            <Bell size={16} className="text-brand-400 shrink-0 mt-0.5" />
            <p className="text-sm text-brand-300">
              {daysUntil === 0
                ? `Today is your DCA day! Consider investing €${dca.monthly_amount}.`
                : `DCA reminder in ${daysUntil} day${daysUntil !== 1 ? 's' : ''} — €${dca.monthly_amount} on the ${dca.day_of_month}${['st','nd','rd'][dca.day_of_month - 1] || 'th'}.`}
            </p>
          </div>
        )}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs text-gray-400 mb-1">Monthly Amount (€)</label>
            <input
              type="number"
              value={dca.monthly_amount}
              onChange={e => setDca(d => ({ ...d, monthly_amount: parseFloat(e.target.value) || 0 }))}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-400 mb-1">Day of Month (1–28)</label>
            <input
              type="number"
              min={1}
              max={28}
              value={dca.day_of_month}
              onChange={e => setDca(d => ({ ...d, day_of_month: Math.min(28, Math.max(1, parseInt(e.target.value) || 1)) }))}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
            />
          </div>
        </div>

        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 cursor-pointer">
            <div className={`w-10 h-6 rounded-full transition-colors ${dca.enabled ? 'bg-brand-600' : 'bg-gray-700'}`}
              onClick={() => setDca(d => ({ ...d, enabled: !d.enabled }))}>
              <div className={`w-5 h-5 bg-white rounded-full mt-0.5 transition-transform ${dca.enabled ? 'translate-x-4.5 ml-[18px]' : 'ml-0.5'}`} />
            </div>
            <span className="text-sm text-gray-300">Enable reminders</span>
          </label>
        </div>

        <button
          onClick={save}
          className="flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Save size={16} />
          {saved ? 'Saved!' : 'Save Settings'}
        </button>
      </div>

      {/* Info */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-2">
        <h3 className="font-medium text-white text-sm">About</h3>
        <p className="text-xs text-gray-500">Prices provided by Yahoo Finance via yfinance. For personal use only.</p>
        <p className="text-xs text-gray-500">This app never places orders. All trades must be executed manually on DEGIRO or any other broker.</p>
        <p className="text-xs text-gray-500">Data is stored locally in a SQLite database (portfolio.db).</p>
      </div>
    </div>
  )
}
