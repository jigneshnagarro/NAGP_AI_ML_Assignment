import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "singapore"
VECTOR_STORE_DIR = BASE_DIR / "vector_store"

load_dotenv()


loader = DirectoryLoader(
    DATA_DIR,
    glob="*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"},
)

documents = loader.load()

print(f"Loaded {len(documents)} documents")


text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
)

chunks = text_splitter.split_documents(documents)

for chunk in chunks:
    source_path = chunk.metadata.get("source", "")

    if "wikivoyage" in source_path.lower():
        chunk.metadata["source_title"] = "Wikivoyage — Singapore Travel Guide"
        chunk.metadata["source_url"] = "https://en.wikivoyage.org/wiki/Singapore"

    elif "essential_travel_information" in source_path.lower():
        chunk.metadata["source_title"] = (
            "Visit Singapore — Essential Travel Information"
        )
        chunk.metadata["source_url"] = (
            "https://www.visitsingapore.com/travel-tips/"
            "essential-travel-information/"
        )

    elif "things_to_do" in source_path.lower():
        chunk.metadata["source_title"] = (
            "Visit Singapore — Things To Do"
        )
        chunk.metadata["source_url"] = (
            "https://www.visitsingapore.com/things-to-do/"
            "top-things-to-do/"
        )
        
print(f"Created {len(chunks)} chunks")


embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)


vector_store = FAISS.from_documents(
    chunks,
    embeddings
)

vector_store.save_local(str(VECTOR_STORE_DIR))
