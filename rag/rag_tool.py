from pathlib import Path
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS


BASE_DIR = Path(__file__).resolve().parent.parent
VECTOR_STORE_DIR = BASE_DIR / "vector_store"

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)


vector_store = FAISS.load_local(
    str(VECTOR_STORE_DIR),
    embeddings,
    allow_dangerous_deserialization=True
)


retriever = vector_store.as_retriever(
    search_kwargs={"k": 4}
)


@tool
def search_singapore_knowledge(query: str) -> str:
    """
    Search the Singapore travel knowledge base.

    Use this tool for relatively stable destination information
    such as attractions, neighbourhoods, transportation,
    food, activities, cultural information, and sample itineraries.

    Do NOT use this tool for current weather or current exchange rates.
    """

    documents = retriever.invoke(query)

    if not documents:
        return (
            "No relevant information was found in the Singapore knowledge base."
        )

    results = []

    for document in documents:
        print("\n===== RAG DOCUMENT =====")
        print("Metadata:")
        print(document.metadata)
        title = document.metadata.get(
            "source_title",
            "Unknown source"
        )

        url = document.metadata.get(
            "source_url",
            ""
        )

        results.append(
            f"""
            SOURCE TITLE: {title}
            SOURCE URL: {url}

            CONTENT:
            {document.page_content}
            """
        )

    return "\n\n".join(results)