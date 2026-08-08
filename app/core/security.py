import hmac

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic_settings import BaseSettings

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


class SecuritySettings(BaseSettings):
    api_key: str = "default_secret_key"
    allowed_hosts: list[str] = ["*"]

    class Config:
        env_file = ".env"
        extra = "ignore"


security_settings = SecuritySettings()


async def verify_api_key(
    api_key: str | None = Security(api_key_header),
) -> str:
    """ตรวจสอบความถูกต้องของ API Key ใน Request Header"""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API Key Header",
        )

    # ใช้ hmac.compare_digest เพื่อป้องกัน Timing Attacks
    is_valid = hmac.compare_digest(api_key, security_settings.api_key)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or unauthorized API Key",
        )

    return api_key


def sanitize_input(text_input: str) -> str:
    """ทําความสะอาด Input string เบื้องต้นก่อนส่งไปยัง LLM หรือ Database"""
    if not text_input:
        return ""
    # ตัด Whitespace ที่ไม่จำเป็น
    clean_text = text_input.strip()
    return clean_text


def mask_sensitive_data(
    payload: dict[str, str | int | float | None],
) -> dict[str, str | int | float | None]:
    """ซ่อนข้อมูลสําคัญสำหรับใช้บันทึก Audit Log"""
    masked_payload = payload.copy()
    sensitive_keys = ["password", "secret", "api_key", "token"]

    for key in masked_payload:
        if any(s_key in key.lower() for s_key in sensitive_keys):
            masked_payload[key] = "******"

    return masked_payload
