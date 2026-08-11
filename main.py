# import uvicorn
# from fastapi import FastAPI
# from fastapi.concurrency import asynccontextmanager
# from fastapi.middleware.cors import CORSMiddleware

# from app.api.v1.api import api_router
# from app.core.grpc_server import start_grpc_server
# from app.core.mongodb import close_mongo_connection, connect_to_mongo
# from app.core.pinecone import close_pinecone_connection, connect_to_pinecone


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # 1. ทำการเชื่อมต่อ Database เมื่อ Server เริ่มทำงาน
#     try:
#         await connect_to_mongo()
#         await connect_to_pinecone()
#         grpc_server = await start_grpc_server(port=50052)

#     except Exception as e:
#         print(f"❌ Database connection failed during startup: {e}")
#         # สามารถเลือก raise e หรือปล่อยให้แอปขึ้นมาก่อนเพื่อดู Log ได้
#     yield
#     # 2. ปิดการเชื่อมต่อเมื่อ Server ปิดตัวลง
#     await close_mongo_connection()
#     await close_pinecone_connection()
#     await grpc_server.stop(grace=5)


# app = FastAPI(
#     title="Enterprise RAG Backend API",
#     description="Backend Service (Clean Architecture) - FastAPI + LangChain + MongoDB",
#     version="1.0.0",
#     lifespan=lifespan,
# )

# # ตั้งค่า CORS Middleware สำหรับรองรับ Frontend/External Client
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(api_router, prefix="/api/v1")

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


import asyncio
import logging

from app.core.grpc_server import start_grpc_server
from app.core.mongodb import close_mongo_connection, connect_to_mongo
from app.core.pinecone import close_pinecone_connection, connect_to_pinecone

logging.basicConfig(level=logging.INFO)


async def main():
    await connect_to_mongo()
    await connect_to_pinecone()

    # รันบน port 8080 (พอร์ตมาตรฐานของ Cloud Run)
    server = await start_grpc_server(port=8000)

    try:
        await server.wait_for_termination()
    finally:
        await close_mongo_connection()
        await close_pinecone_connection()


if __name__ == "__main__":
    asyncio.run(main())
