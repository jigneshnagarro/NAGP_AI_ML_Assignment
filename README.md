# Singapore AI Travel Planning Assistant

This project demonstrates a full-stack AI travel assistant for Singapore built with a FastAPI backend, a Vite + React frontend, a RAG pipeline and an MCP tool layer. The assistant answers travel questions using local knowledge about Singapore, while also using live tools for latest weather and exchange rate data.

## Architecture overview

The system is composed of four core layers:

1. Frontend UI
   - Built with React + Vite in `frontend/`
   - The app maintains a session ID per chat and sends user questions to the backend at `POST /api/chat`
   - It renders the assistant response, tool usage and source references

2. FastAPI backend
   - `app.py` exposes the API and orchestrates chat sessions
   - It stores per-session conversation history so follow-up questions can retain context
   - It calls `ask_agent` function from `agent.py` for each request

3. Agent + tool layer
   - `agent.py` defines the system prompt and tool-calling loop
   - The agent decides whether to use the RAG knowledge base or MCP tools for weather/currency requests
   - Tool outputs are appended back into the conversation history so the model can reason over fresh results

4. Retrieval and external data layer
   - `rag/ingest.py` loads Markdown source files, chunks them, creates embeddings and stores them in a FAISS vector index at `vector_store/`
   - `rag/rag_tool.py` exposes a LangChain search tool against the local Singapore knowledge base
   - `mcp/server.py` exposes MCP tools for weather and currency conversion
   - `rag/tools.py` wraps those MCP calls into LangChain tools used by the agent

## Repository layout

- `app.py` - FastAPI API entrypoint
- `agent.py` - agent orchestration and conversation manager
- `data/singapore/` - source documents used for the knowledge base
- `mcp/server.py` - MCP server with external tools
- `rag/ingest.py` - ingestion and FAISS index creation
- `rag/mcp_client.py` - async MCP client used to invoke MCP tools
- `rag/rag_tool.py` - RAG search tool over the local vector store
- `rag/tools.py` - LangChain wrappers for weather and currency tools
- `vector_store/` - FAISS index generated from the knowledge base
- `frontend/` - Vite + React UI
- `requirements.txt` - Python dependencies

## Knowledge-base sources

The assistant uses a small local knowledge base under `data/singapore/` to answer stable destination questions such as attractions, neighborhoods, transport, food, culture and itineraries.

Included source files:

- `data/singapore/essential_travel_information.md`
  - Source title: Visit Singapore — Essential Travel Information
  - Source URL: https://www.visitsingapore.com/travel-tips/essential-travel-information/

- `data/singapore/things_to_do.md`
  - Source title: Visit Singapore — Things To Do
  - Source URL: https://www.visitsingapore.com/things-to-do/top-things-to-do/

- `data/singapore/wikivoyage.md`
  - Source title: Wikivoyage — Singapore Travel Guide
  - Source URL: https://en.wikivoyage.org/wiki/Singapore

These markdown files are loaded, chunked, enriched with metadata, embedded and then stored in FAISS so the model can retrieve the most relevant passages during a user interaction.

## RAG workflow

The retrieval pipeline follows these steps:

1. Load all Markdown documents from `data/singapore/`
2. Split each document into overlapping text chunks using `RecursiveCharacterTextSplitter`
3. Attach source metadata such as title and URL for traceability
4. Convert each chunk to an embedding using `GoogleGenerativeAIEmbeddings` with the Gemini embedding model
5. Save the resulting vector index locally to `vector_store/`
6. At query time, retrieve the top relevant chunks using `vector_store.as_retriever(search_kwargs={"k": 4})`
7. Insert the retrieved passages into the model prompt as grounding context
8. Ask the LLM to answer using only supported facts from the retrieved context or say when the knowledge base is insufficient

This gives the assistant access to destination knowledge without needing to rely only on the base model's memory.

## MCP tools

The project includes a lightweight MCP server for dynamic, up-to-date information that should not be embedded in the static local knowledge base.

### Weather tool

Defined in `mcp/server.py`:

- `get_weather(city, start_date="", end_date="")`
- Uses Open-Meteo for weather and forecast data in Singapore
- Supports current conditions and date-based forecast requests

### Currency conversion tool

Defined in `mcp/server.py`:

- `convert_currency(amount, from_currency, to_currency)`
- Uses Frankfurter exchange-rate data
- The app specifically wraps it for INR-to-SGD conversion

These tools are exposed to the language model via LangChain tool definitions in `rag/tools.py` and called by the agent when relevant. The agent explicitly distinguishes between static travel knowledge and live MCP-provided data.

## Prompt and context strategy

The project uses a structured system prompt in `agent.py` to control how the model behaves:

- Prefer the knowledge base for relatively stable travel facts
- Use MCP tools for current weather and exchange data
- Never invent facts
- Clearly separate facts from recommendations
- Preserve conversation context across turns
- Cite the relevant source information when using the local knowledge base
- Identify MCP information as current data rather than static knowledge

The conversation history is maintained per session in `app.py` with `create_conversation_history()` and appended to as the user asks follow-up questions. This is important for references like “this trip,” “day 2,” or “that itinerary.”

The model runs in a tool-calling loop:

1. Send the conversation history to the LLM with tool bindings
2. If the model calls a tool, execute it
3. Append tool output back into the conversation
4. Continue until the model produces a final answer without further tool calls

This pattern lets the model combine retrieval, live data, and conversation memory into a single final response.

## Setup instructions

### 1. Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- A Google Generative AI API key

### 2. Python environment

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root with your Google API key:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Generate the FAISS knowledge base

```bash
python rag/ingest.py
```

This reads the Markdown files in `data/singapore/`, chunks them, creates embeddings, and saves the vector store in `vector_store/`.

### 4. Start the backend

```bash
uvicorn app:app --reload
```

The backend serves:

- Health endpoint: `http://localhost:8000/`
- Chat endpoint: `POST http://localhost:8000/api/chat`

### 5. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on Vite's default port:

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

## Example usage

A typical user flow looks like this:

- Ask: “What are the best neighborhoods to stay in Singapore?”
- The agent uses the local RAG retriever to find relevant knowledge passages
- The answer is grounded in the source content and includes relevant references
- If the user asks: “What is the weather like in Singapore next week?”
- The agent invokes the weather MCP tool and returns current forecast data
- If the user asks: “How much is 5000 INR in SGD?”
- The agent invokes the currency MCP tool and converts the amount using live exchange rate data


