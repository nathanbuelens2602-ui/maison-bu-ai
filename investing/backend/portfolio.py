from models import Holding, HoldingWithMetrics, PortfolioSummary, RebalanceSuggestion
from market_data import get_prices_bulk
from datetime import datetime


def calculate_portfolio(holdings: list[Holding]) -> PortfolioSummary:
    if not holdings:
        return PortfolioSummary(
            total_value=0, total_cost=0, total_pnl=0, total_pnl_pct=0,
            holdings=[], last_updated=datetime.utcnow().isoformat()
        )

    tickers = [h.ticker for h in holdings]
    prices = get_prices_bulk(tickers)

    enriched = []
    total_value = 0.0
    total_cost = 0.0

    for h in holdings:
        price = prices.get(h.ticker)
        cost_basis = h.quantity * h.avg_cost
        if price is not None:
            current_value = h.quantity * price
            pnl = current_value - cost_basis
            pnl_pct = (pnl / cost_basis * 100) if cost_basis > 0 else 0.0
        else:
            current_value = cost_basis
            price = h.avg_cost
            pnl = 0.0
            pnl_pct = 0.0

        total_value += current_value
        total_cost += cost_basis
        enriched.append((h, price, current_value, cost_basis, pnl, pnl_pct))

    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0.0

    result_holdings = []
    for h, price, cv, cb, pnl, pnl_pct in enriched:
        actual_alloc = (cv / total_value * 100) if total_value > 0 else 0.0
        result_holdings.append(HoldingWithMetrics(
            id=h.id, ticker=h.ticker, name=h.name, quantity=h.quantity,
            avg_cost=h.avg_cost, currency=h.currency, asset_type=h.asset_type,
            target_allocation=h.target_allocation, notes=h.notes, added_date=h.added_date,
            current_price=round(price, 4), current_value=round(cv, 2),
            cost_basis=round(cb, 2), pnl=round(pnl, 2),
            pnl_pct=round(pnl_pct, 2), actual_allocation=round(actual_alloc, 2)
        ))

    return PortfolioSummary(
        total_value=round(total_value, 2), total_cost=round(total_cost, 2),
        total_pnl=round(total_pnl, 2), total_pnl_pct=round(total_pnl_pct, 2),
        holdings=result_holdings, last_updated=datetime.utcnow().isoformat()
    )


def generate_suggestions(summary: PortfolioSummary, monthly_dca: float = 0) -> list[RebalanceSuggestion]:
    suggestions = []
    total_target = sum(h.target_allocation for h in summary.holdings)
    if total_target == 0:
        return []

    for h in summary.holdings:
        if h.target_allocation <= 0:
            continue
        diff = h.target_allocation - h.actual_allocation
        if abs(diff) >= 2.0:  # Only flag if >2% off target
            if diff > 0:
                suggested_amount = (diff / 100) * summary.total_value
                action = "BUY"
                reason = f"{h.ticker} is {abs(diff):.1f}% below its target allocation"
            else:
                suggested_amount = 0
                action = "HOLD"
                reason = f"{h.ticker} is {abs(diff):.1f}% above its target — add to other positions instead"

            suggestions.append(RebalanceSuggestion(
                ticker=h.ticker, name=h.name,
                current_pct=h.actual_allocation, target_pct=h.target_allocation,
                diff_pct=round(diff, 2), action=action,
                suggested_amount=round(max(suggested_amount, 0), 2),
                reason=reason
            ))

    # Prioritise biggest gaps
    suggestions.sort(key=lambda s: abs(s.diff_pct), reverse=True)
    return suggestions
