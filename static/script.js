document.addEventListener('DOMContentLoaded', () => {
    const API_BASE_URL = 'http://localhost:8000/api';
    const REFRESH_INTERVAL = 5000; // Refresh every 5 seconds

    // --- DOM Elements ---
    const transactionForm = document.getElementById('transaction-form');
    const retrainButton = document.getElementById('retrain-button');
    const statusBox = document.getElementById('status-box');
    const filterTxId = document.getElementById('filter-tx-id');
    const filterUserId = document.getElementById('filter-user-id');

    // KPI Elements
    const kpiTotalTransactions = document.getElementById('kpi-total-transactions');
    const kpiFraudAttempts = document.getElementById('kpi-fraud-attempts');
    const kpiFraudRate = document.getElementById('kpi-fraud-rate');

    // Chart contexts
    const pieChartCtx = document.getElementById('transaction-pie-chart').getContext('2d');
    const timelineChartCtx = document.getElementById('fraud-timeline-chart').getContext('2d');

    // Table Body Elements
    const legitTransactionsBody = document.getElementById('legit-transactions-body');
    const fraudLogsBody = document.getElementById('fraud-logs-body');

    // Chart instances
    let transactionPieChart;
    let fraudTimelineChart;

    // --- UTILITY FUNCTIONS ---

    const showStatus = (message, type) => {
        statusBox.innerHTML = message;
        statusBox.className = `alert alert-${type}`;
        statusBox.style.display = 'block';
        const timeout = message.length > 100 ? 8000 : 5000;
        setTimeout(() => { statusBox.style.display = 'none'; }, timeout);
    };

    const updateKPIs = (legitCount, fraudCount) => {
        const total = legitCount + fraudCount;
        const rate = total > 0 ? (fraudCount / total) * 100 : 0;
        kpiTotalTransactions.textContent = total;
        kpiFraudAttempts.textContent = fraudCount;
        kpiFraudRate.textContent = `${rate.toFixed(2)}%`;
    };

    const renderTransactionPieChart = (legitCount, fraudCount) => {
        if (transactionPieChart) transactionPieChart.destroy();
        transactionPieChart = new Chart(pieChartCtx, {
            type: 'doughnut',
            data: { labels: ['Legitimate', 'Fraudulent'], datasets: [{ data: [legitCount, fraudCount], backgroundColor: ['#2F855A', '#C53030'], borderColor: '#fff', borderWidth: 3 }] },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } } }
        });
    };

    const renderFraudTimelineChart = (fraudLogs) => {
        const countsByDate = fraudLogs.reduce((acc, log) => {
            const date = new Date(log.timestamp).toLocaleDateString();
            acc[date] = (acc[date] || 0) + 1;
            return acc;
        }, {});
        const labels = Object.keys(countsByDate).sort((a, b) => new Date(a) - new Date(b));
        const data = labels.map(label => countsByDate[label]);
        if (fraudTimelineChart) fraudTimelineChart.destroy();
        fraudTimelineChart = new Chart(timelineChartCtx, {
            type: 'line',
            data: { labels: labels, datasets: [{ label: 'Fraudulent Attempts', data: data, borderColor: '#C53030', backgroundColor: 'rgba(197, 48, 48, 0.1)', fill: true, tension: 0.2 }] },
            options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
        });
    };

    const renderTables = (legitData, fraudData) => {
        legitTransactionsBody.innerHTML = '';
        legitData.forEach(tx => {
            const row = legitTransactionsBody.insertRow();
            row.innerHTML = `<td>${tx.transaction_id}</td><td>${tx.user_id}</td><td>${parseFloat(tx.amount).toFixed(2)}</td><td>${tx.payment_method}</td><td>${tx.country}</td><td>${new Date(tx.transaction_timestamp).toLocaleString()}</td>`;
        });

        fraudLogsBody.innerHTML = '';
        fraudData.forEach(log => {
            const tx = log.transaction_data;
            const row = fraudLogsBody.insertRow();
            row.innerHTML = `<td>${tx.transaction_id}</td><td>${tx.user_id}</td><td>${parseFloat(tx.amount).toFixed(2)}</td><td>${tx.payment_method}</td><td>${tx.country}</td><td>${new Date(log.timestamp).toLocaleString()}</td>`;
        });
    };

    const filterTables = () => {
        const txIdFilter = filterTxId.value.toLowerCase();
        const userIdFilter = filterUserId.value.toLowerCase();
        document.querySelectorAll('#legit-transactions-body tr, #fraud-logs-body tr').forEach(row => {
            const txId = row.cells[0].textContent.toLowerCase();
            const userId = row.cells[1].textContent.toLowerCase();
            row.style.display = (txId.includes(txIdFilter) && userId.includes(userIdFilter)) ? '' : 'none';
        });
    };

    const fetchAndDisplayData = async () => {
        try {
            const [legitRes, fraudRes] = await Promise.all([ fetch(`${API_BASE_URL}/transactions`), fetch(`${API_BASE_URL}/honeypot_logs`) ]);
            const legitData = await legitRes.json();
            const fraudData = await fraudRes.json();

            updateKPIs(legitData.length, fraudData.length);
            renderTransactionPieChart(legitData.length, fraudData.length);
            renderFraudTimelineChart(fraudData);
            renderTables(legitData, fraudData);
            filterTables();

            feather.replace();
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    // --- EVENT LISTENERS ---
    filterTxId.addEventListener('input', filterTables);
    filterUserId.addEventListener('input', filterTables);

    transactionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const transaction = { transaction_id: document.getElementById('transaction_id').value, user_id: document.getElementById('user_id').value, Amount: parseFloat(document.getElementById('amount').value), currency: 'USD', timestamp: new Date().toISOString(), payment_method: document.getElementById('payment_method').value, country: document.getElementById('country').value };
        try {
            const response = await fetch(`${API_BASE_URL}/process_transaction`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(transaction) });
            const result = await response.json();
            let message = '', type = 'success';
            if (result.status === 'processed_legitimately') {
                // Must confirm the transaction to save it to DB
                await fetch(`${API_BASE_URL}/confirm_transaction`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        transaction: transaction,
                        risk_score: result.risk_score,
                        scaled_features: result.scaled_features
                    })
                });
                message = `Transaction ${result.transaction_id} processed successfully.`;
            } else if (result.status === 'diverted_to_honeypot') {
                type = 'info';
                message = `<strong>Suspicious transaction diverted.</strong>`;
                if (result.explanations && result.explanations.length > 0) message += ` Reasons: ${result.explanations.join(', ')}`;
            }
            showStatus(message, type);
            transactionForm.reset();
            fetchAndDisplayData();
        } catch (error) {
            showStatus('Error processing transaction.', 'danger');
            console.error('Transaction error:', error);
        }
    });

    retrainButton.addEventListener('click', async () => {
        showStatus('Model retraining initiated...', 'info');
        try {
            const response = await fetch(`${API_BASE_URL}/retrain_model`, { method: 'POST' });
            const result = await response.json();
            showStatus(result.message, 'success');
        } catch (error) {
            showStatus('Failed to initiate retraining.', 'danger');
            console.error('Retraining error:', error);
        }
    });

    // --- INITIALIZATION ---
    fetchAndDisplayData();
    // setInterval(fetchAndDisplayData, REFRESH_INTERVAL); // Disabled automatic database refreshing
});
