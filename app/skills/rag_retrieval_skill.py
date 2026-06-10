from typing import List, Dict

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import settings


def retrieve_risk_rules(query: str, top_k: int = 3) -> List[Dict[str, str]]:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    vector_store = FAISS.load_local(
        settings.faiss_index_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    docs = vector_store.similarity_search(query, k=top_k)

    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown")
        }
        for doc in docs
    ]