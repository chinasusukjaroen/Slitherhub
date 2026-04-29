import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from pathlib import Path

base_dir = Path(__file__).resolve().parent.parent 
env_path = base_dir / '.env'
 
load_dotenv(dotenv_path=env_path)

EMAIL_SENDER   = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  # Gmail App Password
 
 
def build_email(task):
    """สร้าง HTML email"""
    deadline_utc = datetime.strptime(task["deadline"], "%Y-%m-%d %H:%M:%S")
    deadline_th  = deadline_utc + timedelta(hours=7)  
    days_left    = (deadline_utc.replace(tzinfo=timezone.utc) -
                    datetime.now(timezone.utc)).days
 
    subject = f" แจ้งเตือน❗❗❗: {task['title']} ครบกำหนดในอีก {days_left} วัน"
 
    html = f"""
    <div style="font-family:sans-serif; max-width:560px; margin:auto;
                background:#1a1a1a; color:#f0f0f0; border-radius:12px; overflow:hidden;">
        <div style="background:#292929; padding:20px 24px; border-bottom:1px solid #353535;">
            <h2 style="margin:0; font-size:16px;">🐍 Slither hub Hub</h2>
        </div>
        <div style="padding:24px;">
            <p style="color:#b0b0b0; margin:0 0 16px;">Hi <strong>{task['name']}</strong></p>
            <div style="background:#363636; border-radius:10px; padding:16px; margin-bottom:16px;">
                <div style="font-size:12px; color:#787878; margin-bottom:4px;">{task['course_name']}</div>
                <div style="font-size:16px; font-weight:600; margin-bottom:12px;">{task['title']}</div>
                <div style="font-size:12px; color:#fcd34d;">
                    ⏳ ครบกำหนด: {deadline_th.strftime('%d/%m/%Y %H:%M')} น. (อีก {days_left} วัน)
                </div>
            </div>
            <p style="font-size:12px; color:#787878; margin:0;">
            </p>
        </div>
    </div>
    """
    return subject, html
 
 
def send_email(to_email, task):
    """ส่ง Email แจ้งเตือน"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        print(f"[EMAIL] ❌ ยังไม่ได้ตั้งค่า .env")
        return False
 
    subject, html = build_email(task)
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = to_email
    msg.attach(MIMEText(html, "html"))
 
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        print(f"[EMAIL] ✅ ส่งสำเร็จ → {to_email}")
        return True
    except Exception as e:
        print(f"[EMAIL] ❌ ส่งไม่ได้: {e}")
        return False