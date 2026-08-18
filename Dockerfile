# ==========================================
# --- Stage 1: Build dependencies ---
# ==========================================
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# ติดตั้ง C/C++ compiler สำหรับ tiktoken, grpcio และ C-extensions อื่นๆ
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# ติดตั้งลง /usr/local โดยตรงใน Builder stage
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ==========================================
# --- Stage 2: Final Runtime ---
# ==========================================
FROM python:3.11-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/usr/local/bin:$PATH"

WORKDIR /app

# 1. ก๊อปปี้ Installed Packages & Executables มาจาก Builder แบบ 1:1
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 2. ทำความสะอาด site-packages เพื่อลดขนาด Image (ลบ test files & cache)
RUN find /usr/local/lib/python3.11/site-packages/ -type d \( -name "tests" -o -name "test" \) -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.11/site-packages/ -name "*.pyc" -delete

# 3. สร้าง Non-root user
RUN useradd -m -u 1000 appuser

# 4. คัดลอก ซอร์สโค้ด
COPY --chown=appuser:appuser . /app

# ให้สิทธิ์ entrypoint (ถ้ามี)
RUN if [ -f /app/entrypoint.sh ]; then chmod +x /app/entrypoint.sh; fi

USER appuser

EXPOSE 8000

CMD ["python", "main.py"]