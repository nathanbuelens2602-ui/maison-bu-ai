import os
import anthropic
from models import PortfolioSummary, RebalanceSuggestion
from datetime import datetime


def generate_weekly_summary(summary: PortfolioSummary, suggestions: list[RebalanceSuggestion]) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "⚠️ Set ANTHROPIC_API_KEY in your .env file to enable AI summaries."

    client = anthropic.Anthropic(api_key=api_key)

    holdings_text = "\n".join([
        f"- {h.ticker} ({h.name}): {h.quantity:.4f} units @ €{h.avg_cost:.2f} avg cost, "
        f"current price €{h.current_price:.2f}, value €{h.current_value:.2f}, "
        f"P&L {h.pnl_pct:+.1f}%, allocation {h.actual_allocation:.1f}% (target: {h.target_allocation:.1f}%)"
        for h in summary.holdings
    ]) or "No holdings yet."

    suggestions_text = "\n".join([
        f"- {s.ticker}: {s.action} — {s.reason} (suggested: €{s.suggested_amount:.0f})"
        for s in suggestions
    ]) or "Portfolio is well balanced."

    prompt = f"""You are a calm, long-term-focused investing assistant for a private investor using DEGIRO.
The investor manages their own portfolio manually (no automated trading).

Today's date: {datetime.utcnow().strftime('%Y-%m-%d')}

PORTFOLIO OVERVIEW:
- Total value: €{summary.total_value:,.2f}
- Total cost basis: €{summary.total_cost:,.2f}
- Total P&L: €{summary.total_pnl:+,.2f} ({summary.total_pnl_pct:+.2f}%)

HOLDINGS:
{holdings_text}

REBALANCING SUGGESTIONS:
{suggestions_text}

Write a concise weekly portfolio summary in 3 short paragraphs:
1. Overall portfolio health and performance
2. Notable positions (biggest winners/losers, allocation drift)
3. One or two actionable thoughts for the coming week (never suggest timing the market)

Tone: professional, grounded, long-term focused. No hype. No financial advice disclaimer needed (user knows this is AI analysis for personal use).
Keep it under 200 words."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text
