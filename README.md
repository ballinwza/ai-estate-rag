ai-estate-rag/
├── app/
│   ├── api/                     # Controller / Routing Layer (FastAPI)
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── chat.py      # Main Chat & Text-to-NoSQL API
│   │   │   │   ├── documents.py # Document Upload (PDF/Image) API
│   │   │   │   └── audit.py     # Audit Trail & History Log API
│   │   │   └── api.py           # API Router compilation
│   │   └── deps.py              # Dependency Injection (DB session, auth, etc.)
│   │
│   ├── core/                    # Core Configurations & Utilities
│   │   ├── config.py            # Environment variables (.env settings)
│   │   ├── database.py          # MongoDB Connection (Motor / PyMongo)
│   │   └── security.py          # API Keys / Auth helpers
│   │
│   ├── domain/                  # Domain Layer (Enterprise Business Rules)
│   │   ├── entities/            # Business Models (Pure Python Data Classes / Pydantic)
│   │   │   ├── property.py      # Real Estate Property Entity
│   │   │   ├── chat.py          # Chat Message & Citation Entities
│   │   │   └── audit.py         # Audit Log & Metric Entities
│   │   └── repositories/        # Repository Interfaces (Abstract Classes)
│   │       ├── property_repo.py
│   │       └── audit_repo.py
│   │
│   ├── use_cases/               # Application Business Rules (Use Cases)
│   │   ├── query_property.py    # Text-to-NoSQL Orchestration + Summarization
│   │   ├── process_document.py  # Process Uploaded PDF/Image Context
│   │   └── get_audit_trail.py   # Retrieve Citation & Metrics
│   │
│   ├── infrastructure/          # Infrastructure Layer (External Frameworks & Libraries)
│   │   ├── llm/                 # LLM Integrations (LangChain / Gemini API)
│   │   │   ├── gemini_client.py # Gemini 1.5 Flash API Wrapper
│   │   │   ├── prompts.py       # Text-to-NoSQL & Executive Summary Prompts
│   │   │   └── chains.py        # LangChain Pipelines
│   │   ├── parsers/             # Document Processors
│   │   │   └── file_parser.py   # PDF & Image Parser (Multimodal / OCR)
│   │   └── persistence/         # Database Access Implementation
│   │       └── mongodb/
│   │           ├── property_repository_impl.py
│   │           └── audit_repository_impl.py
│   │
│   └── schemas/                 # Data Transfer Objects (DTOs / Request & Response Validation)
│       ├── chat_schema.py       # Chat Request/Response DTOs (includes Citation/Metrics)
│       ├── document_schema.py   # File Upload DTOs
│       └── property_schema.py   # MongoDB Property Data DTOs
│
├── .env.example                 # Environment variables template (API Keys, DB URI)
├── docker-compose.yml           # Docker setup for local MongoDB & FastAPI
├── Dockerfile                   # Production Dockerfile
├── main.py                      # FastAPI Application Entrypoint
└── requirements.txt             # Python Dependencies