document.addEventListener('DOMContentLoaded', () => {
    const authContainer = document.getElementById('auth-container');
    const todoContainer = document.getElementById('todo-container');
    const authMessage = document.getElementById('auth-message');

    const registerBtn = document.getElementById('register-btn');
    const loginBtn = document.getElementById('login-btn');
    const logoutBtn = document.getElementById('logout-btn');

    const taskInput = document.getElementById('task-input');
    const addTaskBtn = document.getElementById('add-task-btn');
    const taskList = document.getElementById('task-list');

    const regUsernameInput = document.getElementById('reg-username');
    const regPasswordInput = document.getElementById('reg-password');
    const loginUsernameInput = document.getElementById('login-username');
    const loginPasswordInput = document.getElementById('login-password');
    const welcomeUserSpan = document.getElementById('welcome-user');

    const api = {
        register: '/auth/register',
        login: '/auth/login',
        tasks: '/api/tasks'
    };

    function updateUI() {
        const token = localStorage.getItem('token');
        const username = localStorage.getItem('username');
        if (token) {
            authContainer.style.display = 'none';
            todoContainer.style.display = 'block';
            welcomeUserSpan.textContent = username;
            fetchTasks();
        } else {
            authContainer.style.display = 'block';
            todoContainer.style.display = 'none';
        }
    }

    async function handleRegister() {
        const username = regUsernameInput.value.trim();
        const password = regPasswordInput.value.trim();
        if (!username || !password) return;

        const response = await fetch(api.register, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const data = await response.json();
        authMessage.textContent = data.message || data.error;
    }

    async function handleLogin() {
        const username = loginUsernameInput.value.trim();
        const password = loginPasswordInput.value.trim();
        if (!username || !password) return;

        const response = await fetch(api.login, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        
        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('token', data.token);
            localStorage.setItem('username', username);
            updateUI();
        } else {
            const data = await response.json();
            authMessage.textContent = data.error;
        }
    }

    function handleLogout() {
        localStorage.removeItem('token');
        localStorage.removeItem('username');
        updateUI();
    }

    async function fetchTasks() {
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const response = await fetch(api.tasks, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const tasks = await response.json();
            if (tasks.message) { // Handle token errors
                handleLogout();
                return;
            }
            taskList.innerHTML = '';
            tasks.forEach(task => {
                const li = document.createElement('li');
                li.textContent = task.description;
                taskList.appendChild(li);
            });
        } catch (error) {
            taskList.innerHTML = '<li>Error loading tasks.</li>';
        }
    }

    async function addTask() {
        const token = localStorage.getItem('token');
        const description = taskInput.value.trim();
        if (!description || !token) return;
        
        await fetch(api.tasks, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ description }),
        });
        taskInput.value = '';
        fetchTasks();
    }

    registerBtn.addEventListener('click', handleRegister);
    loginBtn.addEventListener('click', handleLogin);
    logoutBtn.addEventListener('click', handleLogout);
    addTaskBtn.addEventListener('click', addTask);
    
    updateUI();
});