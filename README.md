# PointerLM AI File Assistant

An intelligent AI assistant that answers questions about uploaded files using Retrieval Augmented Generation (RAG), web search, and conversational memory.

## Features

- **File-Based Q&A**: Upload documents (PDF, TXT, DOCX, etc.) and ask questions about their content
- **RAG Pipeline**: Semantic search using sentence transformers + FAISS vector similarity
- **Web Search Integration**: DuckDuckGo search for up-to-date information
- **Conversational Memory**: Chat history with sliding window (keeps last 10 responses)
- **User Authentication**: JWT-based auth with signup/login/delete flows
- **CQRS Architecture**: Clean separation of Commands and Events via MessageBus

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
│   │   ├── ai/               # AI services (transformers_service.py)
│   │   ├── orm/              # SQLAlchemy ORM (conn.py, tables.py)
│   │   ├── oauth2.py         # JWT token handling
│   │   ├── repository.py     # Data access layer
│   │   ├── security.py       # Password hashing
│   │   └── ensure.py         # Custom exceptions
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
├── content/                  # Static/dynamic content
│   ├── static/
│   └── dynamic/
└── .env                      # Environment variables (gitignored)
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Endpoints  │────▶│  MessageBus │────▶│  Handlers   │
│  (FastAPI)  │     │   (CQRS)    │     │ (Service)  │
└─────────────┘     └─────────────┘     └─────────────┘
                                              │
                   ┌──────────────────────────┼──────────────────────────┐
                   ▼                          ▼                          ▼
            ┌─────────────┐          ┌─────────────┐           ┌─────────────┐
            │  UnitOfWork │          │ AIService   │           │    Events   │
            │  (SQLAlch)  │          │ (RAG+LLM)  │           │  (Async)   │
            └─────────────┘          └─────────────┘           └─────────────┘
```

### Request Flow (Generate Response)

1. `POST /response/generate` → Command created
2. `MessageBus.handle()` → Routes to `GenerateResponse` handler
3. Handler calls `AIService.get_context_from_file()`:
   - File loaded via `UnstructuredLoader`
   - Text split into chunks (500 chars, 150 overlap)
   - Embeddings via `all-MiniLM-L6-v2`
   - Top-k chunks retrieved via FAISS similarity
4. Handler calls `AIService.question_answering()`:
   - Web search via DuckDuckGo
   - Prompt constructed with context
   - OpenRouter API call to Trinity Large
   - Response cached in chat memory
5. Response persisted to PostgreSQL (if authenticated)
6. Old responses pruned (keeps last 10)

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
class AbstractAIService:
    def get_context_from_file(self, query: str, file_path: str) -> List[str]: ...
    def question_answering(self, query: str, doc_text: List[str]) -> str: ...
    def clear_chat_memory(self) -> None: ...
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

## License

[MIT](LICENSE)
