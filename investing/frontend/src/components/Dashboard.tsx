import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import type { PortfolioSummary } from '../types'

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']

function fmt(n: number, decimals = 2) {
  return new Intl.NumberFormat('de-DE', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).format(n)
}

function StatCard({ label, value, sub, positive }: { label: string; value: string; sub?: string; positive?: boolean }) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <p className="text-xs text-gray-400 mb-1">{label}</p>
      <p className={`text-2xl font-bold ${positive === undefined ? 'text-white' : positive ? 'text-green-400' : 'text-red-400'}`}>{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}

export default function Dashboard({ portfolio }: { portfolio: PortfolioSummary }) {
  const allocationData = portfolio.holdings.map(h => ({
    name: h.ticker,
    value: Math.round(h.actual_allocation * 100) / 100,
  }))

  const pnlData = portfolio.holdings
    .map(h => ({ name: h.ticker, pnl: h.pnl, pct: h.pnl_pct }))
    .sort((a, b) => b.pnl - a.pnl)

  return (
    <div className="space-y-6">
      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Portfolio Value" value={`€${fmt(portfolio.total_value)}`} />
        <StatCard label="Cost Basis" value={`€${fmt(portfolio.total_cost)}`} />
        <StatCard
          label="Total P&L"
          value={`${portfolio.total_pnl >= 0 ? '+' : ''}€${fmt(Math.abs(portfolio.total_pnl))}`}
          sub={`${portfolio.total_pnl_pct >= 0 ? '+' : ''}${fmt(portfolio.total_pnl_pct)}%`}
          positive={portfolio.total_pnl >= 0}
        />
        <StatCard label="Positions" value={`${portfolio.holdings.length}`} sub={`Last updated ${new Date(portfolio.last_updated).toLocaleTimeString()}`} />
      </div>

      {portfolio.holdings.length === 0 ? (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-12 text-center text-gray-400">
          <p className="text-lg mb-2">No holdings yet</p>
          <p className="text-sm">Go to the Holdings tab to add your first position, or import a CSV.</p>
        </div>
      ) : (
        <div className="grid lg:grid-cols-2 gap-6">
          {/* Allocation pie */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <h2 className="text-sm font-medium text-gray-300 mb-4">Allocation</h2>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={allocationData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label={({ name, value }) => `${name} ${value}%`} labelLine={false}>
                  {allocationData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={(v: number) => [`${v}%`, 'Allocation']} contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* P&L bar */}
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
            <h2 className="text-sm font-medium text-gray-300 mb-4">P&L by Position</h2>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={pnlData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                <XAxis dataKey="name" tick={{ fill: '#9ca3af', fontSize: 12 }} />
                <YAxis tick={{ fill: '#9ca3af', fontSize: 12 }} tickFormatter={v => `€${v}`} />
                <Tooltip
                  formatter={(v: number, n: string) => [n === 'pnl' ? `€${fmt(v)}` : `${fmt(v)}%`, n === 'pnl' ? 'P&L' : 'P&L %']}
                  contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
                />
                <Bar dataKey="pnl" radius={[4, 4, 0, 0]}>
                  {pnlData.map((d, i) => <Cell key={i} fill={d.pnl >= 0 ? '#22c55e' : '#ef4444'} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Holdings table preview */}
      {portfolio.holdings.length > 0 && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-800">
            <h2 className="text-sm font-medium text-gray-300">Positions</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-xs text-gray-500 uppercase">
                  <th className="px-4 py-3 text-left">Ticker</th>
                  <th className="px-4 py-3 text-left">Name</th>
                  <th className="px-4 py-3 text-right">Qty</th>
                  <th className="px-4 py-3 text-right">Avg Cost</th>
                  <th className="px-4 py-3 text-right">Price</th>
                  <th className="px-4 py-3 text-right">Value</th>
                  <th className="px-4 py-3 text-right">P&L</th>
                  <th className="px-4 py-3 text-right">Alloc</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.holdings.map(h => (
                  <tr key={h.id} className="border-t border-gray-800 hover:bg-gray-800/50">
                    <td className="px-4 py-3 font-mono font-medium text-brand-400">{h.ticker}</td>
                    <td className="px-4 py-3 text-gray-300 max-w-xs truncate">{h.name}</td>
                    <td className="px-4 py-3 text-right text-gray-300">{fmt(h.quantity, 4)}</td>
                    <td className="px-4 py-3 text-right text-gray-400">€{fmt(h.avg_cost)}</td>
                    <td className="px-4 py-3 text-right text-gray-300">€{fmt(h.current_price)}</td>
                    <td className="px-4 py-3 text-right font-medium text-white">€{fmt(h.current_value)}</td>
                    <td className={`px-4 py-3 text-right font-medium ${h.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {h.pnl >= 0 ? '+' : ''}€{fmt(Math.abs(h.pnl))}
                      <span className="text-xs ml-1">({h.pnl_pct >= 0 ? '+' : ''}{fmt(h.pnl_pct)}%)</span>
                    </td>
                    <td className="px-4 py-3 text-right text-gray-400">{fmt(h.actual_allocation)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
