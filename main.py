import asyncio
import logging
import os

from app.core.grpc_server import start_grpc_server
from app.core.mongodb import close_mongo_connection, connect_to_mongo
from app.core.pinecone import close_pinecone_connection, connect_to_pinecone

# ตั้งค่า Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("grpc_server")


async def serve() -> None:
    # อ่านค่า PORT จาก Cloud Run Environment Variable (Default: 8080)
    port = int(os.getenv("PORT", "8000"))

    # 1. เชื่อมต่อ Database และ Services
    logger.info("Connecting to databases...")
    await connect_to_mongo()
    await connect_to_pinecone()

    # 2. เริ่มต้นการทำงานของ gRPC Server
    logger.info(f"Starting gRPC server on port {port}...")
    server = await start_grpc_server(port=port)

    # 3. Graceful Shutdown เมื่อ Server ปิดตัวลง
    try:
        await server.wait_for_termination()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Stopping gRPC server...")
    finally:
        await server.stop(grace=5)
        await close_mongo_connection()
        await close_pinecone_connection()
        logger.info("Server stopped successfully.")


if __name__ == "__main__":
    asyncio.run(serve())
