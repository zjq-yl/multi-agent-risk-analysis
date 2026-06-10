from typing import Dict, Any


def generate_risk_report(user_id: str, risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
    overall_level = risk_analysis["overall_risk_level"]
    overall_score = risk_analysis["overall_risk_score"]
    risk_transactions = risk_analysis["risk_transactions"]

    high_risk_count = sum(1 for tx in risk_transactions if tx["risk_level"] == "HIGH")
    medium_risk_count = sum(1 for tx in risk_transactions if tx["risk_level"] == "MEDIUM")
    low_risk_count = sum(1 for tx in risk_transactions if tx["risk_level"] == "LOW")

    report_text = f"""
用户 {user_id} 风控分析报告

一、总体风险结论
该用户当前综合风险评分为 {overall_score}，综合风险等级为 {overall_level}。

二、交易风险统计
本次共分析 {len(risk_transactions)} 笔交易，其中：
- 高风险交易：{high_risk_count} 笔
- 中风险交易：{medium_risk_count} 笔
- 低风险交易：{low_risk_count} 笔

三、重点风险交易
"""

    for tx in risk_transactions:
        if tx["risk_level"] in ["HIGH", "MEDIUM"]:
            report_text += f"""
交易ID：{tx["transaction_id"]}
交易金额：{tx["amount"]} 元
交易时间：{tx["transaction_time"]}
交易地点：{tx["location"]}
风险等级：{tx["risk_level"]}
风险分数：{tx["risk_score"]}
风险原因：{"；".join(tx["risk_reasons"])}
"""

    report_text += """

四、风控建议
建议对中高风险交易进行人工复核，重点关注夜间大额转账、异地交易、异常设备登录及短时间内连续转账等行为。
"""

    return {
        "user_id": user_id,
        "overall_risk_level": overall_level,
        "overall_risk_score": overall_score,
        "report": report_text.strip()
    }