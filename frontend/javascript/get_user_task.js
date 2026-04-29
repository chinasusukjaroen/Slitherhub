import { CONFIG } from '../config.js';

const taskContainer = document.getElementById('userTaskList');

const params = new URLSearchParams(window.location.search);
const user_id = params.get('id');

async function loadUserTasks() {
    try {
        console.log("Starting fetch...");
        const response = await fetch(`${CONFIG.BACKEND_API_URL}/tasks`, {
            method: "GET",
            headers: { "Content-Type": "application/json" },
            credentials: "include"
        });

        console.log("Response received:", response.status);
        const jsonData = await response.json();
        console.log("Data parsed:", jsonData);

        if (!jsonData.success) {
            taskContainer.innerHTML = `<p>Error: ${jsonData.error}</p>`;
            return;
        }

        const tasks = jsonData.data;

        if (user_id) {
            const filtered = tasks.filter(task => String(task.user_id) === String(user_id));
            renderUserTasks(filtered);
        } else {
            renderUserTasks(tasks);
        }

    } catch (err) {
        console.error(err);
        taskContainer.innerHTML = "<p>Can't connect to server</p>";
    }
}

function renderUserTasks(tasks) {
    if (tasks.length === 0) {
        taskContainer.innerHTML = "<p>No tasks found</p>";
        return;
    }

    taskContainer.innerHTML = '';

    tasks.forEach(task => {
        const item = document.createElement('div');
        item.innerHTML = `
            <div>
                <p><strong>User ID:</strong> ${task.user_id}</p>
                <p><strong>Assignment ID:</strong> ${task.assignment_id}</p>
                <p><strong>Status:</strong> ${task.status}</p>
                <p><strong>Notified:</strong> ${task.is_notified}</p>
                <p><strong>Last Sync:</strong> ${task.last_sync_at}</p>
            </div>
        `;
        taskContainer.appendChild(item);
    });
}

loadUserTasks();