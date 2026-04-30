# services/auth_service.py
import jwt
import os
import requests
import logging
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# โหลด .env แบบระบุ path ชัดเจน
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

logger = logging.getLogger(__name__)

#  Config 
JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError(" JWT_SECRET is missing in .env")

if not isinstance(JWT_SECRET, str):
    raise TypeError(" JWT_SECRET must be a string")

if len(JWT_SECRET) < 32:
    logger.warning("JWT_SECRET ไม่ปลอดภัย! ควรยาว ≥ 32 ตัวอักษร")

TU_API_URL = os.getenv(
    "TU_API_URL",
    "https://restapi.tu.ac.th/api/v1/auth/Ad/verify"
)

TU_API_KEY = os.getenv("TU_API_KEY", "")
USE_MOCK_AUTH = os.getenv("USE_MOCK_AUTH", "false").lower() == "true"


# ─── Mock Data ──────────────────────────────────────────
MOCK_USERS = {
    "6512345678": {
        "password": "password123",
        "DisplayName": "สมชาย ใจดี",
        "Email": "somchai@tu.ac.th",
        "Faculty": "วิศวกรรมศาสตร์",
        "Department": "คอมพิวเตอร์"
    },
    "6709420019": {
        "password": "mypassword",
        "DisplayName": "คุณตอร์น เย็น",
        "Email": "kuntorn@tu.ac.th",
        "Faculty": "วิทยาศาสตร์",
        "Department": "วิทยาการคอมพิวเตอร์"
    }
}


# ─── 1. สร้าง JWT Token ─────────────────────────────────
def create_token(username, extra_claims=None):
    """สร้าง JWT Token อายุ 7 วัน"""
    now = datetime.utcnow()

    payload = {
        "username": username,
        "iat": now,
        "exp": now + timedelta(days=7),
        "type": "access",
        **(extra_claims or {})
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    # PyJWT บางเวอร์ชันอาจคืน bytes
    if isinstance(token, bytes):
        token = token.decode("utf-8")

    return token


# ตรวจสอบการล็อกอิน 
def verify_login(username, password):
    if not username or not password:
        return {"status": False, "message": "กรุณากรอกข้อมูลให้ครบ"}

    if USE_MOCK_AUTH:
        return _verify_mock(username, password)

    return _verify_tu_api(username, password)


def _verify_mock(username, password):
    user = MOCK_USERS.get(username)

    if not user:
        return {"status": False, "message": "ไม่พบรหัสนักศึกษานี้ในระบบ"}

    if user["password"] != password:
        return {"status": False, "message": "รหัสผ่านไม่ถูกต้อง"}

    return {
        "status": True,
        "username": username,
        "DisplayName": user["DisplayName"],
        "Email": user["Email"],
        "Faculty": user.get("Faculty", ""),
        "Department": user.get("Department", "")
    }


def _verify_tu_api(username, password):
    try:
        logger.info(f"📡 Calling TU API for user: {username}")

        response = requests.post(
            TU_API_URL,
            json={
                "UserName": username,
                "PassWord": password
            },
            headers={
                "Application-Key": TU_API_KEY,
                "Content-Type": "application/json"
            },
            timeout=10
        )

        logger.info(f"📥 TU API Response: {response.status_code}")

        data = response.json()

        if data.get("status") is True:
            return {
                "status": True,
                "username": data.get("username", username),
                "DisplayName": data.get("displayname_th") or data.get("DisplayNameTH") or "",
                "Email": data.get("email") or data.get("Email") or "",
                "Faculty": data.get("faculty") or data.get("Faculty") or "",
                "Department": data.get("department") or data.get("Department") or "",
                "TUStatus": data.get("tu_status") or data.get("Status") or ""
            }

        return {
            "status": False,
            "message": data.get("message", "Login ไม่สำเร็จ")
        }

    except requests.Timeout:
        logger.error(" TU API timeout")
        return {
            "status": False,
            "message": "ระบบยืนยันตัวตนไม่ตอบสนอง (หมดเวลา)"
        }

    except requests.ConnectionError:
        logger.error(" Cannot connect to TU API")
        return {
            "status": False,
            "message": "ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ยืนยันตัวตน"
        }

    except Exception as e:
        logger.error(f"TU API error: {type(e).__name__}: {e}")
        return {
            "status": False,
            "message": f"เกิดข้อผิดพลาด: {str(e)}"
        }