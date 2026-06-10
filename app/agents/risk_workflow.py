from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END

from app.db.database import SessionLocal
from app.skills.sql_query_skill import query_transactions_by_user_id
from app.skills.risk_analysis_skill import analyze_transaction_risk
from app.skills.rag_retrieval_skill import retrieve_risk_rules
from app.skills.llm_report_skill import generate_llm_risk_report


class RiskWorkflowState(TypedDict):
    user_id: str
    transactions: List[Dict[str, Any]]
    risk_analysis: Dict[str, Any]
    rag_query: str
    related_rules: List[Dict[str, str]]
    report: Dict[str, Any]


def sql_node(state: RiskWorkflowState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        transactions = query_transactions_by_user_id(
            db=db,
            user_id=state["user_id"]
        )
        return {
            "transactions": transactions
        }
    finally:
        db.close()


def risk_node(state: RiskWorkflowState) -> Dict[str, Any]:
    risk_analysis = analyze_transaction_risk(
        state["transactions"]
    )

    return {
        "risk_analysis": risk_analysis
    }


def rag_node(state: RiskWorkflowState) -> Dict[str, Any]:
    risk_analysis = state["risk_analysis"]

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

    rag_query = " ".join(list(set(keywords)))

    related_rules = retrieve_risk_rules(rag_query)

    return {
        "rag_query": rag_query,
        "related_rules": related_rules
    }


def report_node(state: RiskWorkflowState) -> Dict[str, Any]:
    # 这里复用之前的 LLM 报告 Skill
    # 注意：这个函数内部本身也会做一次 RAG
    # 为了先跑通工作流，我们暂时复用它
    report = generate_llm_risk_report(
        user_id=state["user_id"],
        risk_analysis=state["risk_analysis"]
    )

    return {
        "report": report
    }


def build_risk_workflow():
    workflow = StateGraph(RiskWorkflowState)

    workflow.add_node("sql_node", sql_node)
    workflow.add_node("risk_node", risk_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("report_node", report_node)

    workflow.add_edge(START, "sql_node")
    workflow.add_edge("sql_node", "risk_node")
    workflow.add_edge("risk_node", "rag_node")
    workflow.add_edge("rag_node", "report_node")
    workflow.add_edge("report_node", END)

    return workflow.compile()


risk_workflow = build_risk_workflow()