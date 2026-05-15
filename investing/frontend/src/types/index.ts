export interface Holding {
  id: number
  ticker: string
  name: string
  quantity: number
  avg_cost: number
  currency: string
  asset_type: string
  target_allocation: number
  notes: string
  added_date: string
}

export interface HoldingWithMetrics extends Holding {
  current_price: number
  current_value: number
  cost_basis: number
  pnl: number
  pnl_pct: number
  actual_allocation: number
}

export interface PortfolioSummary {
  total_value: number
  total_cost: number
  total_pnl: number
  total_pnl_pct: number
  holdings: HoldingWithMetrics[]
  last_updated: string
}

export interface RebalanceSuggestion {
  ticker: string
  name: string
  current_pct: number
  target_pct: number
  diff_pct: number
  action: 'BUY' | 'HOLD'
  suggested_amount: number
  reason: string
}

export interface DCASettings {
  id?: number
  monthly_amount: number
  day_of_month: number
  enabled: boolean
}

export interface AISummary {
  summary: string
  generated_at: string
}
