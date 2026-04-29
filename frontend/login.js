// login.js
import { CONFIG } from './config.js';

document.addEventListener("DOMContentLoaded", () => {
    // ─── 1. เลือกองค์ประกอบจาก DOM ─────────────────────────────
    const form = document.getElementById("login-form");
    const studentIdInput = document.getElementById("student-id");
    const passwordInput = document.getElementById("password-input");
    const togglePasswordBtn = document.getElementById("toggle-password");
    const submitBtn = form?.querySelector('button[type="submit"]');

    // ─── 2. ฟังก์ชันแสดง/ซ่อนรหัสผ่าน ──────────────────────────
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener("click", () => {
            const isPassword = passwordInput.type === "password";
            passwordInput.type = isPassword ? "text" : "password";

            const eyeOpen = togglePasswordBtn.querySelector(".eye-open");
            const eyeClosed = togglePasswordBtn.querySelector(".eye-closed");

            if (eyeOpen && eyeClosed) {
                eyeOpen.style.display = isPassword ? "none" : "block";
                eyeClosed.style.display = isPassword ? "block" : "none";
            }
        });
    }

    // ─── 3. จัดการฟอร์ม ────────────────────────────────────────
    if (form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const studentId = studentIdInput?.value.trim();
            const password = passwordInput?.value;

            if (!studentId || !password) {
                alert("กรุณากรอกรหัสนักศึกษาและรหัสผ่านให้ครบ");
                studentIdInput?.focus();
                return;
            }

            const originalBtnText = submitBtn?.innerHTML;

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = `
                    <svg class="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;animation:spin 1s linear infinite;margin-right:8px">
                        <circle cx="12" cy="12" r="10" stroke-opacity="0.3"/>
                        <path d="M12 2a10 10 0 0 1 10 10"/>
                    </svg>
                    Logging in...
                `;
            }

            try {
                console.log("📤 Sending login request to:", `${CONFIG.BACKEND_API_URL}/login`);

                const response = await fetch(`${CONFIG.BACKEND_API_URL}/login`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Accept": "application/json"
                    },
                    body: JSON.stringify({
                        username: studentId,
                        password: password
                    }),
                    credentials: "include"
                });

                let data; 
                
                const contentType = response.headers.get("content-type");

                if (contentType && contentType.includes("application/json")) {
                    data = await response.json();
                    data = data.data
                } else {
                    const text = await response.text();
                    throw new Error(`Server ตอบกลับไม่ใช่ JSON: ${text.substring(0, 100)}`);
                }

                console.log("📥 Response:", response.status, data);

                if (!response.ok) {
                    throw new Error(data.error || data.message || "Login ไม่สำเร็จ");
                }

                sessionStorage.setItem("user", JSON.stringify({
                    username: data.username,
                    display_name: data.display_name,
                    email: data.email
                }));
                
                sessionStorage.setItem('is_logged_in', 'true');


                if(data.is_new_user == false){
                    sessionStorage.setItem("moodle_synced", "false");

                }else{
                    sessionStorage.setItem("moodle_synced", "true");
                }

                console.log("🔄 Redirecting to student.html...");
                window.location.href = "dashboard.html";

            } catch (err) {
                console.error("💥 Login error:", err);

                let userMessage = "เกิดข้อผิดพลาดในการเชื่อมต่อ";

                if (err.message.includes("Failed to fetch") || err.message.includes("NetworkError")) {
                    userMessage = "❌ ไม่สามารถเชื่อมต่อกับเซิร์ฟเวอร์ได้";
                } else if (err.message.includes("Invalid")) {
                    userMessage = "❌ รหัสนักศึกษาหรือรหัสผ่านไม่ถูกต้อง";
                } else if (err.message.includes("404")) {
                    userMessage = "❌ ไม่พบ API endpoint";
                } else {
                    userMessage = err.message;
                }

                alert(userMessage);
                passwordInput?.focus();

            } finally {
                if (submitBtn && originalBtnText) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalBtnText;
                }
            }
        });
    }

    // ─── 4. CSS Spinner ────────────────────────────────────────
    const style = document.createElement("style");
    style.textContent = `
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .spinner {
            display: inline-block;
            vertical-align: middle;
        }
    `;
    document.head.appendChild(style);
});