import { CONFIG } from '../config.js';

// แก้: ชี้ไป contentArea ให้ตรงกับ HTML
const taskContainer = document.getElementById('contentArea');

const params = new URLSearchParams(window.location.search);
const user_id = params.get('id');

async function loadUserTasks() {
    try {
        const response = await fetch(`${CONFIG.BACKEND_API_URL}/tasks`, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
            credentials: "include"
        });

        // แก้: เช็ค response.ok แทน result.success
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            taskContainer.innerHTML = `<p>Error: ${err.error || response.status}</p>`;
            return;
        }

        const result = await response.json();
        console.log("API response:", result);

        // แก้: รับ data ตรงๆ ไม่เช็ค success
        const tasks = result.data ?? [];

        const filtered = user_id
            ? tasks.filter(task => String(task.user_id) === String(user_id))
            : tasks;

        updateStats(filtered);
        renderUserTasks(filtered);

    } catch (err) {
        console.error(err);
        taskContainer.innerHTML = "<p>Can't connect to server</p>";
    }
}

function updateStats(tasks) {
    const total     = tasks.length;
    const submitted = tasks.filter(t => t.status === 'submitted').length;
    const pending   = tasks.filter(t => t.status === 'pending').length;
    const late      = tasks.filter(t => t.status === 'late').length;

    document.getElementById('statTotal').textContent     = total;
    document.getElementById('statSubmitted').textContent = submitted;
    document.getElementById('statPending').textContent   = pending;
    document.getElementById('statLate').textContent      = late;

    if (total > 0) {
        document.getElementById('barSubmitted').style.width = `${(submitted / total) * 100}%`;
        document.getElementById('barPending').style.width   = `${(pending   / total) * 100}%`;
        document.getElementById('barLate').style.width      = `${(late      / total) * 100}%`;
    }
}

function renderUserTasks(tasks) {
    if (tasks.length === 0) {
        taskContainer.innerHTML = `
            <div class="empty-state">
                <p>ไม่พบงาน</p>
            </div>`;
        return;
    }

    taskContainer.innerHTML = '<div class="assignment-list"></div>';
    const list = taskContainer.querySelector('.assignment-list');

    tasks.forEach(task => {
        const status = task.status || 'pending';
        const item = document.createElement('div');
        item.className = 'assignment-card';
        item.innerHTML = `
            <div class="card-status-stripe stripe-${status}"></div>
            <div class="card-body">
                <div class="status-icon-box icon-${status}">
                    <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path d="M9 11l3 3L22 4"/>
                    </svg>
                </div>
                <div class="assignment-info">
                    <div class="assignment-title">Assignment #${task.assignment_id}</div>
                    <div class="assignment-meta">
                        <span>User ID: ${task.user_id}</span>
                        <span>Last Sync: ${task.last_sync_at ?? '-'}</span>
                    </div>
                    <div class="card-status-row">
                        <span class="badge badge-${status}">${status}</span>
                        <span class="badge-subject">Notified: ${task.is_notified}</span>
                    </div>
                </div>
            </div>
        `;
        list.appendChild(item);
    });
}

loadUserTasks();