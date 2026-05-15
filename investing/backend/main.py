import io
import csv
from contextlib import asynccontextmanager
from datetime import datetime, date
from typing import Optional
import os

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

from database import create_db, get_session
from models import (
    Holding, HoldingCreate, HoldingUpdate,
    DCASettings, PortfolioSummary, RebalanceSuggestion
)
from portfolio import calculate_portfolio, generate_suggestions
from ai_summary import generate_weekly_summary
from market_data import clear_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db()
    yield


app = FastAPI(title="Investing Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Portfolio ──────────────────────────────────────────────────────────────────

@app.get("/api/portfolio", response_model=PortfolioSummary)
def get_portfolio(session: Session = Depends(get_session)):
    holdings = session.exec(select(Holding)).all()
    return calculate_portfolio(list(holdings))


@app.post("/api/portfolio/refresh", response_model=PortfolioSummary)
def refresh_portfolio(session: Session = Depends(get_session)):
    clear_cache()
    holdings = session.exec(select(Holding)).all()
    return calculate_portfolio(list(holdings))


# ── Holdings ──────────────────────────────────────────────────────────────────

@app.get("/api/holdings", response_model=list[Holding])
def list_holdings(session: Session = Depends(get_session)):
    return session.exec(select(Holding)).all()


@app.post("/api/holdings", response_model=Holding)
def add_holding(data: HoldingCreate, session: Session = Depends(get_session)):
    holding = Holding(
        **data.model_dump(),
        added_date=date.today().isoformat()
    )
    session.add(holding)
    session.commit()
    session.refresh(holding)
    return holding


@app.put("/api/holdings/{holding_id}", response_model=Holding)
def update_holding(holding_id: int, data: HoldingUpdate, session: Session = Depends(get_session)):
    holding = session.get(Holding, holding_id)
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(holding, field, value)
    session.add(holding)
    session.commit()
    session.refresh(holding)
    return holding


@app.delete("/api/holdings/{holding_id}")
def delete_holding(holding_id: int, session: Session = Depends(get_session)):
    holding = session.get(Holding, holding_id)
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    session.delete(holding)
    session.commit()
    return {"ok": True}


# ── CSV Import ─────────────────────────────────────────────────────────────────

@app.post("/api/holdings/import")
async def import_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """
    Expected CSV columns (case-insensitive):
    ticker, name, quantity, avg_cost, currency, asset_type, target_allocation, notes
    """
    content = await file.read()
    text = content.decode("utf-8-sig")  # handle BOM
    reader = csv.DictReader(io.StringIO(text))

    imported = 0
    errors = []
    for i, row in enumerate(reader, start=2):
        row = {k.strip().lower(): v.strip() for k, v in row.items()}
        try:
            holding = Holding(
                ticker=row["ticker"].upper(),
                name=row.get("name", row["ticker"]),
                quantity=float(row["quantity"]),
                avg_cost=float(row["avg_cost"]),
                currency=row.get("currency", "EUR").upper(),
                asset_type=row.get("asset_type", "ETF"),
                target_allocation=float(row.get("target_allocation", 0)),
                notes=row.get("notes", ""),
                added_date=date.today().isoformat()
            )
            session.add(holding)
            imported += 1
        except (KeyError, ValueError) as e:
            errors.append(f"Row {i}: {e}")

    session.commit()
    return {"imported": imported, "errors": errors}


# ── AI Summary ─────────────────────────────────────────────────────────────────

@app.get("/api/summary")
def get_summary(session: Session = Depends(get_session)):
    holdings = session.exec(select(Holding)).all()
    summary = calculate_portfolio(list(holdings))
    suggestions = generate_suggestions(summary)
    text = generate_weekly_summary(summary, suggestions)
    return {"summary": text, "generated_at": datetime.utcnow().isoformat()}


# ── Suggestions ────────────────────────────────────────────────────────────────

@app.get("/api/suggestions", response_model=list[RebalanceSuggestion])
def get_suggestions(session: Session = Depends(get_session)):
    holdings = session.exec(select(Holding)).all()
    summary = calculate_portfolio(list(holdings))
    return generate_suggestions(summary)


# ── DCA Settings ───────────────────────────────────────────────────────────────

@app.get("/api/dca", response_model=Optional[DCASettings])
def get_dca(session: Session = Depends(get_session)):
    return session.exec(select(DCASettings)).first()


@app.post("/api/dca", response_model=DCASettings)
def save_dca(data: DCASettings, session: Session = Depends(get_session)):
    existing = session.exec(select(DCASettings)).first()
    if existing:
        existing.monthly_amount = data.monthly_amount
        existing.day_of_month = data.day_of_month
        existing.enabled = data.enabled
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    session.add(data)
    session.commit()
    session.refresh(data)
    return data
