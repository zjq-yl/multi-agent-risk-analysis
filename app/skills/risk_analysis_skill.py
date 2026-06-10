from datetime import datetime
from typing import List, Dict, Any


def analyze_transaction_risk(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    risk_results = []
    total_score = 0

    for tx in transactions:
        score = 0
        reasons = []

        amount = float(tx["amount"])
        location = tx.get("location")
        device_id = tx.get("device_id")
        transaction_time = tx.get("transaction_time")

        if isinstance(transaction_time, str):
            transaction_time = datetime.fromisoformat(transaction_time)

        # 规则1：大额交易
        if amount >= 50000:
            score += 40
            reasons.append("单笔交易金额超过50000元，存在大额交易风险")

        # 规则2：夜间交易
        if transaction_time.hour < 6 or transaction_time.hour >= 23: # type: ignore
            score += 20
            reasons.append("交易发生在夜间敏感时段，存在异常交易风险")

        # 规则3：异常设备
        if device_id and device_id.startswith("D8"):
            score += 20
            reasons.append("交易使用异常设备，可能存在盗刷或账户接管风险")

        # 规则4：异地交易
        if location in ["广州", "深圳", "上海"]:
            score += 20
            reasons.append("交易地点与常用地区不一致，存在异地交易风险")

        risk_level = get_risk_level(score)

        risk_results.append({
            "transaction_id": tx["transaction_id"],
            "amount": amount,
            "transaction_time": str(transaction_time),
            "location": location,
            "device_id": device_id,
            "risk_score": score,
            "risk_level": risk_level,
            "risk_reasons": reasons
        })

        total_score += score

    overall_risk_level = get_risk_level(total_score / max(len(transactions), 1))

    return {
        "overall_risk_score": round(total_score / max(len(transactions), 1), 2),
        "overall_risk_level": overall_risk_level,
        "risk_transactions": risk_results
    }


def get_risk_level(score: float) -> str:
    if score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"