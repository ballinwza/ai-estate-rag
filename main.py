import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# นำเข้า Hello Router จากชั้น api
from app.api.v1.endpoints.hello import router as hello_router

app = FastAPI(
    title="Enterprise RAG Backend API",
    description="Backend Service (Clean Architecture) - FastAPI + LangChain + MongoDB",
    version="1.0.0",
)

# ตั้งค่า CORS Middleware สำหรับรองรับ Frontend/External Client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Endpoints
app.include_router(hello_router, prefix="/api/v1", tags=["Health & Demo"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "API Service is running properly",
        "docs": "/docs",  # Swagger UI Path
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)