from sqlalchemy import text
from sqlalchemy.orm import Session


def query_transactions_by_user_id(
    db: Session,
    user_id: str,
    limit: int = 20
):
    sql = text("""
        SELECT
            transaction_id,
            account_id,
            user_id,
            amount,
            transaction_type,
            direction,
            location,
            device_id,
            ip_address,
            transaction_time,
            status
        FROM transactions
        WHERE user_id = :user_id
        ORDER BY transaction_time DESC
        LIMIT :limit
    """)

    result = db.execute(
        sql,
        {
            "user_id": user_id,
            "limit": limit
        }
    )

    rows = result.mappings().all()
    return [dict(row) for row in rows]