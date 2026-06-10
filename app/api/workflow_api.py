from fastapi import APIRouter
from app.agents.risk_workflow import risk_workflow


router = APIRouter(prefix="/workflow", tags=["LangGraph工作流"])


@router.get("/risk/{user_id}")
def run_risk_workflow(user_id: str):
    result = risk_workflow.invoke({
        "user_id": user_id,
        "transactions": [],
        "risk_analysis": {},
        "rag_query": "",
        "related_rules": [],
        "report": {}
    })

    return {
        "user_id": user_id,
        "transactions_count": len(result["transactions"]),
        "risk_analysis": result["risk_analysis"],
        "rag_query": result["rag_query"],
        "related_rules": result["related_rules"],
        "report": result["report"]
    }