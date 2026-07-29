const API_BASE = 'http://127.0.0.1:5000';
let token = null;
let barChart = null;
let pieChart = null;
let trendChart = null;

async function register() {
    const username = document.getElementById('reg-username').value;
    const password = document.getElementById('reg-password').value;

    const res = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    const data = await res.json();
    document.getElementById('reg-message').innerText = data.message || data.error;
}

async function login() {
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;

    const res = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username, password})
    });
    const data = await res.json();

    if (res.ok) {
        token = data.access_token;
        document.getElementById('current-user').innerText = username;
        document.getElementById('auth-section').style.display = 'none';
        document.getElementById('app-section').style.display = 'block';
        loadDashboard();
        loadTransactions();
    } else {
        document.getElementById('login-message').innerText = data.error;
    }
}

function logout() {
    token = null;
    document.getElementById('auth-section').style.display = 'block';
    document.getElementById('app-section').style.display = 'none';
}

function showAuthForm(which) {
    document.getElementById('register-form').style.display = which === 'register' ? 'block' : 'none';
    document.getElementById('login-form').style.display = which === 'login' ? 'block' : 'none';
    document.getElementById('tab-register').classList.toggle('active', which === 'register');
    document.getElementById('tab-login').classList.toggle('active', which === 'login');
}

async function addTransaction() {
    const amount = parseFloat(document.getElementById('tx-amount').value);
    const type = document.getElementById('tx-type').value;
    const category = document.getElementById('tx-category').value;
    const description = document.getElementById('tx-description').value;

    if (!amount || !category) {
        document.getElementById('tx-message').innerText = 'Amount and category are required';
        return;
    }

    const res = await fetch(`${API_BASE}/transactions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({amount, type, category, description})
    });
    const data = await res.json();

    if (res.ok) {
        document.getElementById('tx-message').innerText = 'Transaction added!';
        document.getElementById('tx-amount').value = '';
        document.getElementById('tx-category').value = '';
        document.getElementById('tx-description').value = '';
        loadDashboard();
        loadTransactions();
    } else {
        document.getElementById('tx-message').innerText = data.error;
    }
}

async function loadTransactions() {
    const res = await fetch(`${API_BASE}/transactions`, {
        headers: {'Authorization': `Bearer ${token}`}
    });
    const transactions = await res.json();

    const tbody = document.getElementById('tx-list');
    tbody.innerHTML = '';

    transactions.forEach(t => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${t.type}</td>
            <td>${t.category}</td>
            <td>${t.amount}</td>
            <td>${t.description || ''}</td>
            <td>${new Date(t.date).toLocaleDateString()}</td>
            <td><button class="btn-delete" onclick="deleteTransaction(${t.id})">Delete</button></td>
        `;
        tbody.appendChild(row);
    });
}

async function deleteTransaction(id) {
    await fetch(`${API_BASE}/transactions/${id}`, {
        method: 'DELETE',
        headers: {'Authorization': `Bearer ${token}`}
    });
    loadDashboard();
    loadTransactions();
}

async function loadDashboard() {
    const res = await fetch(`${API_BASE}/dashboard`, {
        headers: {'Authorization': `Bearer ${token}`}
    });
    const data = await res.json();

    document.getElementById('total-income').innerText = data.total_income;
    document.getElementById('total-expenses').innerText = data.total_expenses;
    document.getElementById('total-savings').innerText = data.savings;

    // Bar Chart
    const ctx = document.getElementById('chart').getContext('2d');
    if (barChart) barChart.destroy();

    barChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Income', 'Expenses'],
            datasets: [{
                label: 'Amount',
                data: [data.total_income, data.total_expenses],
                backgroundColor: ['#4CAF50', '#e53935']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });

    // Pie Chart
    const categories = Object.keys(data.category_breakdown);
    const amounts = Object.values(data.category_breakdown);
    const colors = ['#4CAF50', '#e53935', '#2196F3', '#FF9800', '#9C27B0', '#00BCD4', '#FFEB3B', '#795548'];

    const pieCtx = document.getElementById('pie-chart').getContext('2d');
    if (pieChart) pieChart.destroy();

    pieChart = new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: categories,
            datasets: [{
                data: amounts,
                backgroundColor: colors.slice(0, categories.length)
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } }
        }
    });

    // Line Chart
    const months = Object.keys(data.monthly_trends).sort();
    const monthlyAmounts = months.map(m => data.monthly_trends[m]);

    const trendCtx = document.getElementById('trend-chart').getContext('2d');
    if (trendChart) trendChart.destroy();

    trendChart = new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Monthly Expenses',
                data: monthlyAmounts,
                borderColor: '#e53935',
                backgroundColor: 'rgba(229, 57, 53, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true } }
        }
    });
}