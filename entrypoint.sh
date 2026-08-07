#!/bin/bash

# หยุดการทำงานทันทีหากมีคำสั่งใดทำงานผิดพลาด (Exit status != 0)
set -e

# อ่านค่า PORT จาก Environment Variable (GCP Cloud Run จะส่งเข้ามาให้อัตโนมัติ)
# หากรันใน Local/Docker ทั่วไป จะ Fallback ไปใช้ Port 8000
PORT="${PORT:-8000}"

echo "🚀 Starting FastAPI Application on port $PORT..."

# ใช้ exec เพื่อให้ Uvicorn รับ Process ID 1 (PID 1) โดยตรง
# ช่วยให้ระบบรองรับ Graceful Shutdown (SIGTERM) เวลา Scale Down บน Cloud Run
exec uvicorn main:app \
  --host 0.0.0.0 \
  --port "$PORT" \
  --proxy-headers \
  --forwarded-allow-ips '*'