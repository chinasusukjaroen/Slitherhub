const taskContainer = document.getElementById('userTaskList');

const params = new URLSearchParams(window.location.search);
const user_id = params.get('id');

async function loadUserTasks() {
    try {
        let url = '/api/user-tasks';

        if (user_id) {
            url = `/api/user-tasks/${user_id}`;
        }

        const response = await fetch(url);
        const result = await response.json();

        if (!result.success) {
            taskContainer.innerHTML = `<p>Error: ${result.error}</p>`;
            return;
        }

        renderUserTasks(result.data);

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

    // 🔥 1. sort ก่อน (สำคัญมาก ไม่งั้น grouping จะมั่ว)
    tasks.sort((a, b) => a.subject.localeCompare(b.subject));

    let currentSubject = "";

    tasks.forEach(task => {
        const wrapper = document.createElement('div');

        let subjectHeader = "";

        // 🔥 2. ถ้าเป็นวิชาใหม่ → สร้างหัวข้อ
        if (task.subject !== currentSubject) {
            subjectHeader = `
                <div class="subject-header">
                    <h2>${task.subject}</h2>
                </div>
            `;
            currentSubject = task.subject;
        }

        wrapper.innerHTML = `
            ${subjectHeader}
            <div class="task-card">
                <p><strong>User ID:</strong> ${task.user_id}</p>
                <p><strong>Assignment ID:</strong> ${task.assignment_id}</p>
                <p><strong>Status:</strong> ${task.status}</p>
                <p><strong>Notified:</strong> ${task.is_notified}</p>
                <p><strong>Last Sync:</strong> ${task.last_sync_at}</p>
            </div>
        `;

        taskContainer.appendChild(wrapper);
    });
}

loadUserTasks();