# controllers/auth_controller.py
from flask import Blueprint, request, jsonify, make_response
from services.auth_service import verify_login, create_token, JWT_SECRET
from model.user_model import save_user
import jwt

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """รับ username+password → เช็ค TU API → บันทึกลง DB → สร้าง token → ตอบกลับ"""

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"error": "กรุณากรอกชื่อผู้ใช้งานและรหัสผ่าน"}), 400

    # 1) Verify login
    result = verify_login(username, password)

    if not result["status"]:
        return jsonify({"error": result["message"]}), 401

    # 2) Save user to DB
    try:
        save_result = save_user(
            student_id=result["username"],
            username=result["username"],
            display_name=result.get("DisplayName"),
            email=result.get("Email")
        )

        if not save_result.get("success"):
            print(f"[WARN] save_user failed: {save_result.get('error')}")

    except Exception as e:
        print(f"[ERROR] save_user exception: {e}")
        save_result = {"success": False, "data": None}

    # 3) Create token
    token = create_token(result["username"])

    # 4) Build response
    response = make_response(jsonify({
        "message": "Login สำเร็จ",
        "user": save_result.get("data"),
        "token": token
    }), 200)

    # 5) Set cookie
    response.set_cookie(
        "token",
        token,
        httponly=True,
        secure=False,   # เปลี่ยนเป็น True ตอน deploy HTTPS
        samesite="Lax",
        max_age=60 * 60 * 24 * 7,
        path="/"
    )

    print(f"✅ Login success: {result['username']}")
    return response


@auth_bp.route("/login", methods=["GET"])
def check_login():
    """เช็คสถานะการล็อกอินจาก token ใน cookie"""

    token = request.cookies.get("token")

    if not token:
        return jsonify({"error": "ไม่มี token"}), 401

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])

        return jsonify({
            "message": "Login อยู่",
            "username": payload.get("username")
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token หมดอายุ"}), 401

    except jwt.InvalidTokenError:
        return jsonify({"error": "Token ไม่ถูกต้อง"}), 401

    except Exception as e:
        return jsonify({"error": f"Token validation failed: {str(e)}"}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """ลบ cookie token"""

    response = make_response(jsonify({
        "message": "Logout สำเร็จ"
    }))

    response.delete_cookie("token")

    return response, 200