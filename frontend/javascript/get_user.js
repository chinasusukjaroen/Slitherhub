import { CONFIG } from './config.js';


const userListContainer = document.getElementById('userList');

const params = new URLSearchParams(window.location.search);
const student_id = params.get('id');

async function loadUsers() {
    try {
        // let url = '/api/users';


        // const response = await fetch(url);
        // const result = await response.json();

        // if (!result.success) {
        //     userListContainer.innerHTML = `<p>Error: ${result.error}</p>`;
        //     return;
        // }

        const user = JSON.parse(sessionStorage.getItem("user"));

        if (user) {
            renderSingleUser(user);
        } else {
            renderUsers(user);
        }

    } catch (err) {
        console.error(err);
        userListContainer.innerHTML = "<p>Can't connect to server</p>";
    }
}

function renderUsers(users) {
    if (users.length === 0) {
        userListContainer.innerHTML = "<p>No users found</p>";
        return;
    }

    userListContainer.innerHTML = '';

    users.forEach(user => {
        const item = document.createElement('div');
        item.className = 'user-card';

        item.innerHTML = `
            <div class="user-box">
                <h3>${user.display_name || user.username}</h3>
                <p><strong>Student ID:</strong> ${user.student_id}</p>
                <p><strong>Email:</strong> ${user.email || '-'}</p>
                <p><strong>Last login:</strong> ${user.last_login || '-'}</p>
                <a href="?id=${user.student_id}">View</a>
            </div>
        `;

        userListContainer.appendChild(item);
    });
}

function renderSingleUser(user) {
    userListContainer.innerHTML = `
        <div class="user-box">
            <h2>${user.display_name || user.username}</h2>
            <p><strong>Student ID:</strong> ${user.student_id}</p>
            <p><strong>Email:</strong> ${user.email || '-'}</p>
            <p><strong>Last login:</strong> ${user.last_login || '-'}</p>
            <a href="users.html">Back to list</a>
        </div>
    `;
}

loadUsers();