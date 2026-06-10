from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.skills.sql_query_skill import query_transactions_by_user_id
from app.skills.risk_analysis_skill import analyze_transaction_risk


router = APIRouter(prefix="/risk", tags=["风险分析"])


@router.get("/analyze/{user_id}")
def analyze_user_risk(user_id: str, db: Session = Depends(get_db)):
    transactions = query_transactions_by_user_id(db, user_id)

    risk_result = analyze_transaction_risk(transactions)

    return {
        "user_id": user_id,
        "transaction_count": len(transactions),
        "risk_analysis": risk_result
    }