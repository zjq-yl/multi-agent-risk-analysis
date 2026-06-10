from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.skills.sql_query_skill import query_transactions_by_user_id
from app.skills.risk_analysis_skill import analyze_transaction_risk
from app.skills.report_generation_skill import generate_risk_report


router = APIRouter(prefix="/report", tags=["风控报告"])


@router.get("/{user_id}")
def get_risk_report(user_id: str, db: Session = Depends(get_db)):
    transactions = query_transactions_by_user_id(db, user_id)

    risk_analysis = analyze_transaction_risk(transactions)

    report = generate_risk_report(user_id, risk_analysis)

    return report