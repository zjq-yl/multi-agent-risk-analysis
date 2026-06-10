from fastapi import APIRouter, Query

from app.agents.multi_agent_workflow import multi_agent_workflow
from app.memory.conversation_memory import memory


router = APIRouter(prefix="/agent", tags=["多智能体风控分析"])


@router.get("/risk/{user_id}")
def run_multi_agent_risk_analysis(
    user_id: str,
    session_id: str = Query(default="default-session", description="会话ID")
):
    result = multi_agent_workflow.invoke({
        "user_id": user_id,
        "transactions": [],
        "risk_analysis": {},
        "rag_query": "",
        "related_rules": [],
        "final_report": "",
        "agent_trace": []
    })

    risk_analysis = result["risk_analysis"]
    risk_transactions = risk_analysis.get("risk_transactions", [])

    high_risk_count = sum(
        1 for tx in risk_transactions if tx.get("risk_level") == "HIGH"
    )

    medium_risk_count = sum(
        1 for tx in risk_transactions if tx.get("risk_level") == "MEDIUM"
    )

    low_risk_count = sum(
        1 for tx in risk_transactions if tx.get("risk_level") == "LOW"
    )

    response_data = {
        "session_id": session_id,
        "user_id": user_id,

        "summary": {
            "risk_level": risk_analysis.get("overall_risk_level"),
            "risk_score": risk_analysis.get("overall_risk_score"),
            "transaction_count": len(result["transactions"]),
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "low_risk_count": low_risk_count
        },

        "agent_steps": result["agent_trace"],
        "risk_transactions": risk_transactions,
        "related_rules": result["related_rules"],
        "final_report": result["final_report"]
    }

    memory.save_analysis(
        session_id=session_id,
        user_id=user_id,
        result=response_data
    )

    return response_data


@router.get("/memory/{session_id}")
def get_memory_history(session_id: str):
    history = memory.get_history(session_id)

    return {
        "session_id": session_id,
        "count": len(history),
        "history": history
    }


@router.get("/memory/{session_id}/latest")
def get_latest_memory(session_id: str):
    latest = memory.get_latest(session_id)

    if latest is None:
        return {
            "session_id": session_id,
            "message": "暂无历史分析记录"
        }

    return latest


@router.delete("/memory/{session_id}")
def clear_memory(session_id: str):
    success = memory.clear(session_id)

    return {
        "session_id": session_id,
        "cleared": success
    }