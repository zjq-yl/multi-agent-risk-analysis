from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import settings


def build_vector_store():
    loader = TextLoader(
        "docs/risk_rules.txt",
        encoding="utf-8"
    )

    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    vector_store.save_local(settings.faiss_index_path)

    print(f"知识库构建完成，共切分 {len(chunks)} 个文本块")
    print(f"向量库保存路径：{settings.faiss_index_path}")


if __name__ == "__main__":
    build_vector_store()