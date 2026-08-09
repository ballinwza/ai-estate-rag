```
ai-estate-rag/
├── app/
│   ├── api/                     # Controller / Routing Layer (FastAPI)
│   │   ├── v1/
│   │   │   ├── endpoints/
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
│   │   └── repositories/        # Repository Interfaces (Abstract Classes)
│   │
│   ├── use_cases/               # Application Business Rules (Use Cases)
│   │
│   ├── infrastructure/          # Infrastructure Layer (External Frameworks & Libraries)
│   │   ├── llm/                 # LLM Integrations (LangChain / Gemini API)
│   │   ├── core/             # Mixed service
│   │   └── persistence/         # Database Access Implementation
│   │       └── mongodb/
│   │
│   └── schemas/                 # Data Transfer Objects (DTOs / Request & Response Validation)
│
├── .env.example                 # Environment variables template (API Keys, DB URI)
├── docker-compose.yml           # Docker setup for local MongoDB & FastAPI
├── Dockerfile                   # Production Dockerfile
├── main.py                      # FastAPI Application Entrypoint
└── requirements.txt             # Python Dependencies
```

## Preview

[https://ai-estate-rag-758337397665.asia-southeast1.run.app/docs](https://ai-estate-rag-758337397665.asia-southeast1.run.app/docs)
