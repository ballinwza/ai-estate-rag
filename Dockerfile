# --- Stage 1: Build dependencies ---
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# --- Stage 2: Final Runtime ---
FROM python:3.11-slim

WORKDIR /app

# ติดตั้ง runtime dependencies ที่จำเป็น (เช่น git)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# คัดลอก wheels และ requirements มาจาก Builder Stage
COPY --from=builder /app/wheels /app/wheels
COPY --from=builder /app/requirements.txt .

# ติดตั้ง packages จาก Wheels และลบไฟล์ wheels ทิ้งเพื่อลดขนาด Image
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir /app/wheels/* \
    && rm -rf /app/wheels

# สร้าง Non-root user เพื่อความปลอดภัย (Best Practice สำหรับ Security)
RUN useradd -m -u 1000 appuser

# คัดลอก ซอร์สโค้ด และกำหนดสิทธิ์ (Ownership) ให้ appuser
COPY --chown=appuser:appuser . /app

# ปรับ สิทธิ์ให้ entrypoint.sh ให้สามารถรันได้
RUN chmod +x /app/entrypoint.sh

# สลับไปใช้ Non-root user
USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]