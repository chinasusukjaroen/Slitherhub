// config.js
export const CONFIG = {
    // ✅ ต้องตรงกับ @auth_bp.route ใน backend
    BACKEND_API_URL: "http://127.0.0.1:5000/api",  // หรือ http://localhost:5000
    
    // ✅ ใช้ชื่อเดียวกันกับที่ backend เปิด
    ALLOWED_ORIGINS: ["http://127.0.0.1:5500", "http://localhost:5500"]
};