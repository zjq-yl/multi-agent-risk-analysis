import json
from typing import TypedDict, List, Dict, Any

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import SystemMessage, HumanMessage

from app.db.database import SessionLocal
from app.skills.sql_query_skill import query_transactions_by_user_id
from app.skills.risk_analysis_skill import analyze_transaction_risk
from app.skills.rag_retrieval_skill import retrieve_risk_rules
from app.core.llm import get_llm


class MultiAgentState(TypedDict):
    user_id: str
    transactions: List[Dict[str, Any]]
    risk_analysis: Dict[str, Any]
    rag_query: str
    related_rules: List[Dict[str, str]]
    final_report: str
    agent_trace: List[Dict[str, Any]]


def add_trace(
    state: MultiAgentState,
    agent: str,
    status: str,
    description: str,
    output: str
) -> List[Dict[str, Any]]:
    trace = state.get("agent_trace", []).copy()

    trace.append({
        "agent": agent,
        "status": status,
        "description": description,
        "output": output
    })

    return trace


def sql_agent(state: MultiAgentState) -> Dict[str, Any]:
    db = SessionLocal()
    try:
        transactions = query_transactions_by_user_id(
            db=db,
            user_id=state["user_id"]
        )

        return {
            "transactions": transactions,
            "agent_trace": add_trace(
                state,
                agent="SQL Agent",
                status="success",
                description="查询用户交易流水数据",
                output=f"共查询到 {len(transactions)} 笔交易"
            )
        }
    finally:
        db.close()


def risk_agent(state: MultiAgentState) -> Dict[str, Any]:
    risk_analysis = analyze_transaction_risk(
        state["transactions"]
    )

    return {
        "risk_analysis": risk_analysis,
        "agent_trace": add_trace(
            state,
            agent="Risk Agent",
            status="success",
            description="基于金额、时间、地点和设备信息进行风险识别",
            output=f"综合风险等级：{risk_analysis.get('overall_risk_level')}"
        )
    }


def rag_agent(state: MultiAgentState) -> Dict[str, Any]:
    keywords = []

    for tx in state["risk_analysis"].get("risk_transactions", []):
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
        "related_rules": related_rules,
        "agent_trace": add_trace(
            state,
            agent="RAG Agent",
            status="success",
            description="检索风控知识库中的相关规则",
            output=f"检索关键词：{rag_query}，命中 {len(related_rules)} 条规则"
        )
    }


def report_agent(state: MultiAgentState) -> Dict[str, Any]:
    llm = get_llm()

    rules_text = "\n\n".join(
        [
            f"规则来源：{rule['source']}\n规则内容：{rule['content']}"
            for rule in state["related_rules"]
        ]
    )

    system_prompt = """
你是一名金融风控分析师，负责根据交易数据、风险识别结果和风控规则生成专业报告。

要求：
1. 报告必须基于输入数据，不要编造。
2. 说明总体风险等级和风险原因。
3. 重点解释中高风险交易。
4. 引用风控规则作为判断依据。
5. 给出明确处置建议。
6. 使用中文，结构清晰。
"""

    user_prompt = f"""
请生成金融交易风控分析报告。

【用户ID】
{state["user_id"]}

【交易数据】
{json.dumps(state["transactions"], ensure_ascii=False, indent=2, default=str)}

【风险识别结果】
{json.dumps(state["risk_analysis"], ensure_ascii=False, indent=2, default=str)}

【风控规则依据】
{rules_text}
"""

    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ])

    return {
        "final_report": response.content,
        "agent_trace": add_trace(
            state,
            agent="Report Agent",
            status="success",
            description="调用大模型生成风控分析报告",
            output="风控报告生成完成"
        )
    }


def build_multi_agent_workflow():
    workflow = StateGraph(MultiAgentState)

    workflow.add_node("sql_agent", sql_agent)
    workflow.add_node("risk_agent", risk_agent)
    workflow.add_node("rag_agent", rag_agent)
    workflow.add_node("report_agent", report_agent)

    workflow.add_edge(START, "sql_agent")
    workflow.add_edge("sql_agent", "risk_agent")
    workflow.add_edge("risk_agent", "rag_agent")
    workflow.add_edge("rag_agent", "report_agent")
    workflow.add_edge("report_agent", END)

    return workflow.compile()


multi_agent_workflow = build_multi_agent_workflow()