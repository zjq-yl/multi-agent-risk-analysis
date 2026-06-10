from fastapi import APIRouter
from app.skills.rag_retrieval_skill import retrieve_risk_rules


router = APIRouter(prefix="/rag", tags=["知识库检索"])


@router.get("/search")
def search_rules(query: str):
    results = retrieve_risk_rules(query)

    return {
        "query": query,
        "count": len(results),
        "results": results
    }