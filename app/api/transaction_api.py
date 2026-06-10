from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.skills.sql_query_skill import query_transactions_by_user_id


router = APIRouter(prefix="/transactions", tags=["交易查询"])


@router.get("/{user_id}")
def get_transactions(user_id: str, db: Session = Depends(get_db)):
    transactions = query_transactions_by_user_id(db, user_id)

    return {
        "user_id": user_id,
        "count": len(transactions),
        "transactions": transactions
    }