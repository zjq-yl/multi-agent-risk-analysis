from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.skills.sql_query_skill import query_transactions_by_user_id
from app.skills.risk_analysis_skill import analyze_transaction_risk
from app.skills.llm_report_skill import generate_llm_risk_report


router = APIRouter(prefix="/llm-report", tags=["LLM风控报告"])


@router.get("/{user_id}")
def get_llm_risk_report(user_id: str, db: Session = Depends(get_db)):
    transactions = query_transactions_by_user_id(db, user_id)

    risk_analysis = analyze_transaction_risk(transactions)

    report = generate_llm_risk_report(user_id, risk_analysis)

    return report