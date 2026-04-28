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

        if (user_id) {
            renderUserTasks(result.data);
        } else {
            renderUserTasks(result.data);
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