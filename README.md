# PointerLM AI File Assistant

An intelligent AI assistant that answers questions about uploaded files using Retrieval Augmented Generation (RAG), web search, and conversational memory.

## Features

- **File-Based Q&A**: Upload documents (PDF, TXT, DOCX, etc.) and ask questions about their content
- **RAG Pipeline**: Semantic search using sentence transformers + FAISS vector similarity
- **Web Search Integration**: DuckDuckGo search for up-to-date information
- **Conversational Memory**: Chat history with sliding window (keeps last 10 responses)
- **User Authentication**: JWT-based auth with signup/login/delete flows
- **Command–Handler Architecture**: Commands and Events routed through a synchronous MessageBus

## Tech Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI + Uvicorn |
| AI/ML | LangChain, OpenAI client, Sentence Transformers |
| Vector Store | FAISS (CPU) |
| Database | PostgreSQL + SQLAlchemy |
| Auth | JWT (PyJWT) + Bcrypt |
| File Processing | UnstructuredLoader |

## Project Structure

```
PointerLM-AI-File-Assistant/
├── config.py                 # Environment configuration
├── requirements.txt           # Python dependencies
├── src/
│   ├── adapters/             # External integrations
│   │   ├── ai/               # AI services (abstract base + transformers_service.py)
│   │   ├── orm/              # SQLAlchemy ORM (conn.py, tables.py)
│   │   ├── oauth2.py         # JWT token handling
│   │   ├── repository.py     # Data access layer
│   │   ├── security.py       # Password hashing
│   │   └── ensure.py         # Custom HTTP exceptions + validation helpers
│   ├── domain/               # Core business logic
│   │   ├── model.py          # Entities (User, Response, Prompt)
│   │   ├── commands.py       # Command definitions
│   │   └── events.py         # Event definitions
│   ├── endpoints/            # FastAPI routes
│   │   ├── main.py           # App initialization
│   │   ├── users.py          # /user/* routes
│   │   ├── responses.py      # /response/* routes
│   │   └── schemas.py        # Pydantic models
│   ├── service_layer/        # Application services
│   │   ├── handlers.py       # Command/Event handlers
│   │   ├── messagebus.py     # CQRS message bus
│   │   └── unit_of_work.py   # Database transactions
│   └── bootstrap.py          # Dependency injection setup
├── content/                  # Reserved for file uploads / static assets
│   ├── static/
│   └── dynamic/
└── .env                      # Environment variables (gitignored)
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Endpoints  │────▶│  MessageBus │────▶│  Handlers   │
│  (FastAPI)  │     │  (CQRS-ish) │     │  (Service)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                    ┌─────────────────────────┼─────────────────────────┐
                    ▼                         ▼                         ▼
             ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
             │  UnitOfWork │          │  AIService  │          │    Events   │
             │  (SQLAlch)  │          │  (RAG+LLM)  │          │    (Sync)   │
             └─────────────┘          └─────────────┘          └─────────────┘
```

### Request Flow (Generate Response)

1. `POST /response/generate` → `Command.GenerateResponse` created
2. `MessageBus.handle()` → routes to `generate_response` handler
3. If a file was uploaded, handler calls `AIService.get_context_from_file()`:
   - File loaded via `UnstructuredLoader`
   - Text split into chunks (500 chars, 150 overlap)
   - Embeddings via `all-MiniLM-L6-v2` (SentenceTransformer)
   - Top-k chunks retrieved via FAISS (L2 distance)
4. Handler calls `AIService.question_answering()`:
   - Web search via DuckDuckGo (`langchain_community`)
   - Prompt constructed with file context + web results
   - OpenRouter API call to `arcee-ai/trinity-large-preview:free`
   - Response appended to in-memory chat history (sliding window)
5. If user is authenticated: `Response` entity created → event `ResponseGenerated` queued synchronously → handler persists to PostgreSQL
6. Old DB responses pruned (keeps newest 10 per user)

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/user/signup` | Create account → returns JWT |
| `POST` | `/user/login` | Login → returns JWT |
| `DELETE` | `/user/delete` | Delete account (auth required) |
| `GET` | `/user/info` | Get user info (auth required) |

### AI Responses

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/response/generate` | Generate AI response (auth optional) |
| `GET` | `/response/history` | Get chat history (auth required) |
| `GET` | `/response/clear_chat` | Clear conversation memory |

### Example Usage

```bash
# Generate response with file
curl -X POST "http://localhost:8000/response/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -F "text=What is this document about?" \
  -F "file=@document.pdf"

# Get chat history
curl -X GET "http://localhost:8000/response/history" \
  -H "Authorization: Bearer $TOKEN"
```

## Configuration

Create a `.env` file:

```env
# Database
db_user=your_db_user
db_password=your_db_password
db_host=localhost
db_port=5432
db_name=pointerlm_db

# JWT
secret_key=your-secret-key-here
algorithm=HS256
access_token_expire_minutes=30

# AI (OpenRouter)
model_api_key=your-openrouter-api-key
```

## Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.endpoints.main:app --reload
```

The API will be available at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

## For AI Engineers

### Extending the AI Service

The `TransformersAIService` implements `AbstractAIService`:

```python
# src/adapters/ai/ai_service.py
from abc import ABC, abstractmethod

class AbstractAIService(ABC):
    @abstractmethod
    def get_context_from_file(self, query: str, file_path: str): ...

    @abstractmethod
    def question_answering(self, query: str, docsearch): ...

    @abstractmethod
    def clear_chat_memory(self): ...
```

To swap the LLM, modify `transformers_service.py`:

```python
# Line 40: Change MODEL_ID
self.MODEL_ID = "your-model-id"

# Lines 41-44: Change API configuration
self.client = OpenAI(
    api_key=os.environ.get('MODEL_API_KEY'),
    base_url="https://your-api-endpoint",
)
```

### Adding New Commands

1. Define command in `src/domain/commands.py`:

```python
@dataclass
class MyNewCommand:
    param: str
```

2. Create handler in `src/service_layer/handlers.py`:

```python
def my_handler(cmd: Command.MyNewCommand, uow: AbstractUnitOfWork):
    # Business logic
    return result
```

3. Register in `HANDLER_COMMANDS` dict:

```python
HANDLER_COMMANDS = {
    # ...existing
    Command.MyNewCommand: my_handler,
}
```

### RAG Pipeline Tuning

Adjust chunking in `transformers_service.py` (lines 26-27):

```python
self.text_splitter = CharacterTextSplitter(
    chunk_size=500,      # Larger = more context
    chunk_overlap=150,   # Larger = better continuity
    separator="\n"
)
```

Adjust retrieval in line 27:

```python
self.MIN_CHUNKS = 5  # More chunks = more context, higher latency
```
