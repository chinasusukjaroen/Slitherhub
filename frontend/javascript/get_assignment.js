// getElementById('assignment-list') ในพารามิเตอร์อย่าลืมเปลี่ยนชื่่อในhtmlที่ต้องใช้jsให้ตรงกับบรรทัดที่ 2 ด้วยนะ
import { CONFIG } from '../config.js';


const listContainer = document.getElementById('assignmentList');

async function loadAssignments() {
    try {
        // เปลี่ยน api path ด้วยนะถ้าสร้าง api ชื่อไม่เหมือนกัน ตรงบรรทัด7 แล้วก็อันนี้js สำหรับดึงข้อมูล assignment นะ
        const response = await fetch(`${CONFIG.BACKEND_API_URL}/tasks`); 
        const result = await response.json();

        if (result.success) {
            renderAssignments(result.data);
        } else {
            listContainer.innerHTML = `<p>Error: ${result.error}</p>`;
        }
    } catch (err) {
        console.error("Fetch error:", err);
        listContainer.innerHTML = "<p>Can't connect to server</p>";
    }
}

function renderAssignments(assignments) {
    if (assignments.length === 0) {
        listContainer.innerHTML = "<p>No pending assignments at the moment</p>";
        return;
    }

    // ล้างข้อความ Loading
    listContainer.innerHTML = '';

    assignments.forEach(task => {
        const item = document.createElement('div');
        item.className = 'assignment-card';
        item.innerHTML = `
            <div>
                <small>${task.course_name} (${task.course_id})</small>
                <h3>${task.title}</h3>
                <p>${task.description || 'No description'}</p>
                <p><strong>Deadline:</strong> ${new Date(task.deadline).toLocaleString('en-US')}</p>
                ${task.source_url ? `<a href="${task.source_url}" target="_blank">Go to assignment</a>` : ''}
    </div>
`;
        listContainer.appendChild(item);
    });
}

// เรียกใช้งานฟังก์ชันเมื่อโหลดหน้าเว็บ
loadAssignments();