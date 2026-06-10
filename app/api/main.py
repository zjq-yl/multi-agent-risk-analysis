from fastapi import FastAPI

from app.core.config import settings
from app.api.transaction_api import router as transaction_router
from app.api.risk_api import router as risk_router
from app.api.report_api import router as report_router
from app.api.llm_report_api import router as llm_report_router
from app.api.rag_api import router as rag_router
from app.api.workflow_api import router as workflow_router
from app.api.multi_agent_api import router as multi_agent_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.app_name,
    description="多智能体金融风控分析 Agent",
    version=settings.app_version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transaction_router)
app.include_router(risk_router)
app.include_router(report_router)
app.include_router(llm_report_router)
app.include_router(rag_router)
app.include_router(workflow_router)  # 新增工作流路由
app.include_router(multi_agent_router)


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} is running.",
        "version": settings.app_version,
        "status": "success"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }