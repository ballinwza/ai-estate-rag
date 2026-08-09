#!/bin/bash
set -e

PORT="${PORT:-8000}"

echo "🚀 Starting FastAPI Application on port $PORT..."

# ลบเว้นวรรคแปลกปลอมออกให้หมด พิมพ์เป็นบรรทัดเดียวกันเพื่อความชัวร์
exec uvicorn main:app --host 0.0.0.0 --port "$PORT" --proxy-headers --forwarded-allow-ips '*'