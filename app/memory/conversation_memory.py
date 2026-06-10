from datetime import datetime
from typing import Dict, Any, List, Optional


class ConversationMemory:
    def __init__(self):
        self.store: Dict[str, List[Dict[str, Any]]] = {}

    def save_analysis(
        self,
        session_id: str,
        user_id: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        record = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "summary": result.get("summary", {}),
            "agent_steps": result.get("agent_steps", []),
            "risk_transactions": result.get("risk_transactions", []),
            "related_rules": result.get("related_rules", []),
            "final_report": result.get("final_report", "")
        }

        if session_id not in self.store:
            self.store[session_id] = []

        self.store[session_id].append(record)

        return record

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        return self.store.get(session_id, [])

    def get_latest(self, session_id: str) -> Optional[Dict[str, Any]]:
        history = self.get_history(session_id)

        if not history:
            return None

        return history[-1]

    def clear(self, session_id: str) -> bool:
        if session_id in self.store:
            del self.store[session_id]
            return True

        return False


memory = ConversationMemory()