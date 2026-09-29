import json
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.core.config import settings

FINANCIAL_RISK_SYSTEM_PROMPT = """
你是一名专业的金融风控分析师，擅长基于交易数据、风险识别结果和风控规则生成专业、准确、可执行的风控分析结论。

请遵循以下要求：
1. 只基于用户提供的交易数据、风险识别结果和风控规则进行判断，不要编造任何不存在的交易或风险事件。
2. 必须明确说明总体风险等级、风险原因、关键风险事件以及判定依据。
3. 对高风险和中风险交易，重点解释其异常特征、触发的风控规则、潜在风险影响和必要处理方式。
4. 需引用规则依据，说明为什么这类交易属于高风险、中风险或低风险。
5. 结论必须清晰、结构化，适合业务人员和风控审核人员查看。
6. 最后给出明确、可执行的风控处置建议，如人工复核、限额控制、二次验证、交易拦截、延迟放行或账户关注。
7. 输出必须为中文，表达专业、审慎、简洁。
8. 如果信息不足或存在不确定性，必须说明不确定性并给出保守的建议，而不是无根据地下结论。

输出建议结构：
- 总体风险等级
- 风险评分/结论
- 关键风险事件
- 判定依据
- 风控处理建议
- 结论摘要
"""


def get_llm():
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url="https://api.deepseek.com/v1",
        temperature=0.3,
    )


def build_risk_messages(
    user_prompt: str,
    system_prompt: str = FINANCIAL_RISK_SYSTEM_PROMPT,
) -> List[Any]:
    """构造标准的 LLM prompt 消息，统一使用金融风控系统提示词。"""
    return [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]


def build_risk_analysis_prompt(
    user_id: str,
    transactions: Optional[List[Dict[str, Any]]] = None,
    risk_analysis: Optional[Dict[str, Any]] = None,
    related_rules: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """按统一模板生成用户 prompt，便于调用风险分析或报告生成。"""
    tx_data = transactions if transactions is not None else []
    risk_data = risk_analysis if risk_analysis is not None else {}
    rules_data = related_rules if related_rules is not None else []

    rules_text = "\n\n".join(
        [
            f"规则来源：{rule.get('source', '未知')}\n规则内容：{rule.get('content', '')}"
            for rule in rules_data
        ]
    ) if rules_data else "未检索到相关风控规则。"

    return f"""
请根据以下信息生成一份中文金融风控分析报告，要求严格依据给定数据，不要编造。

【用户ID】
{user_id}

【交易数据】
{json.dumps(tx_data, ensure_ascii=False, indent=2, default=str)}

【风险识别结果】
{json.dumps(risk_data, ensure_ascii=False, indent=2, default=str)}

【风控规则依据】
{rules_text}

请输出：
1. 总体风险等级
2. 风险评分与判断依据
3. 关键风险事件说明
4. 中高风险交易的详细原因分析
5. 风控处置建议
6. 最终结论摘要
"""