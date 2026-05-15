import { useState } from 'react'
import { Plus, Pencil, Trash2, Upload } from 'lucide-react'
import { api } from '../api/client'
import type { Holding, PortfolioSummary } from '../types'

interface Props {
  portfolio: PortfolioSummary
  onRefresh: () => void
}

const EMPTY_FORM = {
  ticker: '', name: '', quantity: '', avg_cost: '',
  currency: 'EUR', asset_type: 'ETF', target_allocation: '', notes: ''
}

export default function HoldingsTab({ portfolio, onRefresh }: Props) {
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Holding | null>(null)
  const [form, setForm] = useState(EMPTY_FORM)
  const [saving, setSaving] = useState(false)
  const [importing, setImporting] = useState(false)
  const [importResult, setImportResult] = useState<{ imported: number; errors: string[] } | null>(null)

  const openAdd = () => { setEditing(null); setForm(EMPTY_FORM); setShowForm(true) }
  const openEdit = (h: Holding) => {
    setEditing(h)
    setForm({
      ticker: h.ticker, name: h.name, quantity: String(h.quantity),
      avg_cost: String(h.avg_cost), currency: h.currency,
      asset_type: h.asset_type, target_allocation: String(h.target_allocation),
      notes: h.notes
    })
    setShowForm(true)
  }

  const save = async () => {
    setSaving(true)
    try {
      const data = {
        ticker: form.ticker.toUpperCase(),
        name: form.name,
        quantity: parseFloat(form.quantity),
        avg_cost: parseFloat(form.avg_cost),
        currency: form.currency,
        asset_type: form.asset_type,
        target_allocation: parseFloat(form.target_allocation || '0'),
        notes: form.notes
      }
      if (editing) {
        await api.updateHolding(editing.id, data)
      } else {
        await api.addHolding(data)
      }
      setShowForm(false)
      onRefresh()
    } finally {
      setSaving(false)
    }
  }

  const remove = async (id: number) => {
    if (!confirm('Remove this holding?')) return
    await api.deleteHolding(id)
    onRefresh()
  }

  const handleCSV = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImporting(true)
    try {
      const result = await api.importCSV(file)
      setImportResult(result)
      onRefresh()
    } finally {
      setImporting(false)
      e.target.value = ''
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Holdings</h2>
        <div className="flex gap-2">
          <label className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium cursor-pointer transition-colors bg-gray-800 text-gray-300 hover:bg-gray-700 ${importing ? 'opacity-50 pointer-events-none' : ''}`}>
            <Upload size={16} />
            {importing ? 'Importing…' : 'Import CSV'}
            <input type="file" accept=".csv" className="hidden" onChange={handleCSV} />
          </label>
          <button onClick={openAdd} className="flex items-center gap-2 px-3 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-medium transition-colors">
            <Plus size={16} /> Add Holding
          </button>
        </div>
      </div>

      {importResult && (
        <div className={`rounded-lg p-3 text-sm ${importResult.errors.length > 0 ? 'bg-yellow-950 border border-yellow-800 text-yellow-300' : 'bg-green-950 border border-green-800 text-green-300'}`}>
          Imported {importResult.imported} holding{importResult.imported !== 1 ? 's' : ''}.
          {importResult.errors.length > 0 && <> Errors: {importResult.errors.join('; ')}</>}
          <button onClick={() => setImportResult(null)} className="ml-2 underline">dismiss</button>
        </div>
      )}

      {/* CSV hint */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-3 text-xs text-gray-500">
        CSV columns: <span className="font-mono text-gray-400">ticker, name, quantity, avg_cost, currency, asset_type, target_allocation, notes</span>
      </div>

      {/* Table */}
      {portfolio.holdings.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center text-gray-400">
          No holdings yet — add one above or import a CSV.
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-xs text-gray-500 uppercase border-b border-gray-800">
                <th className="px-4 py-3 text-left">Ticker</th>
                <th className="px-4 py-3 text-left">Name</th>
                <th className="px-4 py-3 text-left">Type</th>
                <th className="px-4 py-3 text-right">Qty</th>
                <th className="px-4 py-3 text-right">Avg Cost</th>
                <th className="px-4 py-3 text-right">Target %</th>
                <th className="px-4 py-3 text-right">Added</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.holdings.map(h => (
                <tr key={h.id} className="border-t border-gray-800 hover:bg-gray-800/40">
                  <td className="px-4 py-3 font-mono font-medium text-brand-400">{h.ticker}</td>
                  <td className="px-4 py-3 text-gray-300 max-w-[180px] truncate">{h.name}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded-full text-xs bg-gray-800 text-gray-300">{h.asset_type}</span>
                  </td>
                  <td className="px-4 py-3 text-right text-gray-300 font-mono">{h.quantity}</td>
                  <td className="px-4 py-3 text-right text-gray-400">€{h.avg_cost}</td>
                  <td className="px-4 py-3 text-right text-gray-400">{h.target_allocation}%</td>
                  <td className="px-4 py-3 text-right text-gray-500 text-xs">{h.added_date}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex justify-end gap-1">
                      <button onClick={() => openEdit(h)} className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"><Pencil size={14} /></button>
                      <button onClick={() => remove(h.id)} className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded-lg transition-colors"><Trash2 size={14} /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add/Edit modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md space-y-4">
            <h3 className="text-lg font-semibold text-white">{editing ? 'Edit Holding' : 'Add Holding'}</h3>
            <div className="grid grid-cols-2 gap-3">
              {[
                { key: 'ticker', label: 'Ticker (e.g. IWDA.AS)', full: true },
                { key: 'name', label: 'Name', full: true },
                { key: 'quantity', label: 'Quantity', type: 'number' },
                { key: 'avg_cost', label: 'Avg Cost (€)', type: 'number' },
                { key: 'target_allocation', label: 'Target % (0–100)' },
                { key: 'notes', label: 'Notes', full: true },
              ].map(f => (
                <div key={f.key} className={f.full ? 'col-span-2' : ''}>
                  <label className="block text-xs text-gray-400 mb-1">{f.label}</label>
                  <input
                    type={f.type || 'text'}
                    value={(form as Record<string, string>)[f.key]}
                    onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))}
                    className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500"
                  />
                </div>
              ))}
              <div>
                <label className="block text-xs text-gray-400 mb-1">Asset Type</label>
                <select value={form.asset_type} onChange={e => setForm(p => ({ ...p, asset_type: e.target.value }))}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500">
                  {['ETF', 'Stock', 'Bond', 'Crypto', 'Other'].map(t => <option key={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs text-gray-400 mb-1">Currency</label>
                <select value={form.currency} onChange={e => setForm(p => ({ ...p, currency: e.target.value }))}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-brand-500">
                  {['EUR', 'USD', 'GBP', 'CHF'].map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
            </div>
            <div className="flex gap-3 pt-2">
              <button onClick={() => setShowForm(false)} className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg text-sm transition-colors">Cancel</button>
              <button onClick={save} disabled={saving || !form.ticker || !form.quantity || !form.avg_cost}
                className="flex-1 py-2 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors">
                {saving ? 'Saving…' : editing ? 'Save Changes' : 'Add Holding'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
