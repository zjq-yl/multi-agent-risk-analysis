import json
from typing import Dict, Any

from langchain_core.messages import HumanMessage, SystemMessage

from app.core.llm import get_llm
from app.skills.rag_retrieval_skill import retrieve_risk_rules


def generate_llm_risk_report(user_id: str, risk_analysis: Dict[str, Any]) -> Dict[str, Any]:
    llm = get_llm()

    query = build_rag_query(risk_analysis)
    related_rules = retrieve_risk_rules(query)

    rules_text = "\n\n".join(
        [
            f"规则来源：{rule['source']}\n规则内容：{rule['content']}"
            for rule in related_rules
        ]
    )

    system_prompt = """
你是一名金融风控分析师，擅长根据交易风险结果和风控规则生成专业报告。

要求：
1. 报告必须基于输入的交易风险结果和风控规则。
2. 不要编造不存在的交易数据。
3. 需要说明风险判断依据。
4. 对中高风险交易给出原因解释。
5. 最后给出风控处置建议。
6. 输出中文报告，结构清晰。
"""

    user_prompt = f"""
请根据以下内容生成一份中文金融风控分析报告。

【用户ID】
{user_id}

【交易风险分析结果】
{json.dumps(risk_analysis, ensure_ascii=False, indent=2)}

【检索到的风控规则】
{rules_text}
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    return {
        "user_id": user_id,
        "overall_risk_level": risk_analysis["overall_risk_level"],
        "overall_risk_score": risk_analysis["overall_risk_score"],
        "rag_query": query,
        "related_rules": related_rules,
        "report": response.content
    }


def build_rag_query(risk_analysis: Dict[str, Any]) -> str:
    keywords = []

    for tx in risk_analysis.get("risk_transactions", []):
        for reason in tx.get("risk_reasons", []):
            if "大额" in reason:
                keywords.append("大额交易风险")
            if "夜间" in reason:
                keywords.append("夜间交易风险")
            if "异地" in reason:
                keywords.append("异地交易风险")
            if "异常设备" in reason:
                keywords.append("异常设备风险")
            if "频繁" in reason:
                keywords.append("短时间频繁交易风险")

    if not keywords:
        keywords.append("金融交易风险处置建议")

    return " ".join(list(set(keywords)))