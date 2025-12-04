import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

init_db()


HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Expense Tracker</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            font-weight: 800;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }
        
        @media (max-width: 768px) {
            .content {
                grid-template-columns: 1fr;
            }
        }
        
        .card {
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            border: 2px solid #e9ecef;
            transition: all 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card h2 i {
            font-size: 1.2em;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #6c757d;
            font-weight: 600;
        }
        
        input, select {
            width: 100%;
            padding: 15px;
            border: 2px solid #dee2e6;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
            background: white;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        button {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .alert {
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            font-weight: 600;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 2px solid #c3e6cb;
        }
        
        .alert-warning {
            background: #fff3cd;
            color: #856404;
            border: 2px solid #ffeaa7;
            animation: pulse 2s infinite;
        }
        
        .alert-danger {
            background: #f8d7da;
            color: #721c24;
            border: 2px solid #f5c6cb;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.02); }
            100% { transform: scale(1); }
        }
        
        .reports-section {
            grid-column: span 2;
        }
        
        @media (max-width: 768px) {
            .reports-section {
                grid-column: span 1;
            }
        }
        
        .report-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .report-buttons button {
            background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        }
        
        .report-buttons button:hover {
            box-shadow: 0 10px 20px rgba(76, 175, 80, 0.3);
        }
        
        pre {
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            overflow: auto;
            font-size: 14px;
            max-height: 400px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #e9ecef;
        }
        
        .stat-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        
        .stat-card .label {
            color: #6c757d;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💰 Expense Tracker Pro</h1>
            <p>Track your expenses, set budgets, and get smart alerts</p>
        </div>
        
        <div class="content">
            <!-- Add Expense Card -->
            <div class="card">
                <h2>➕ Add New Expense</h2>
                <div class="form-group">
                    <label for="amount">Amount ($)</label>
                    <input type="number" id="amount" step="0.01" placeholder="0.00" min="0">
                </div>
                
                <div class="form-group">
                    <label for="category">Category</label>
                    <select id="category">
                        <option value="Food">🍔 Food & Dining</option>
                        <option value="Transport">🚗 Transport</option>
                        <option value="Entertainment">🎬 Entertainment</option>
                        <option value="Shopping">🛍️ Shopping</option>
                        <option value="Bills">💡 Bills & Utilities</option>
                        <option value="Other">📦 Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="desc">Description (Optional)</label>
                    <input type="text" id="desc" placeholder="What was this expense for?">
                </div>
                
                <button onclick="addExpense()" id="addBtn">➕ Add Expense</button>
                
                <div id="expenseMessage"></div>
            </div>
            
            <!-- Set Budget Card -->
            <div class="card">
                <h2>📊 Set Monthly Budget</h2>
                <div class="form-group">
                    <label for="bCategory">Category</label>
                    <select id="bCategory">
                        <option value="Food">🍔 Food & Dining</option>
                        <option value="Transport">🚗 Transport</option>
                        <option value="Entertainment">🎬 Entertainment</option>
                        <option value="Shopping">🛍️ Shopping</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="bAmount">Budget Amount ($)</label>
                    <input type="number" id="bAmount" step="0.01" placeholder="0.00" min="0">
                </div>
                
                <div class="stats">
                    <div class="form-group">
                        <label for="bMonth">Month</label>
                        <input type="number" id="bMonth" min="1" max="12" placeholder="MM" value="12">
                    </div>
                    
                    <div class="form-group">
                        <label for="bYear">Year</label>
                        <input type="number" id="bYear" placeholder="YYYY" value="2024">
                    </div>
                </div>
                
                <button onclick="setBudget()" id="budgetBtn">💾 Save Budget</button>
                
                <div id="budgetMessage"></div>
            </div>
            
            <!-- Reports Section -->
            <div class="card reports-section">
                <h2>📈 Reports & Analytics</h2>
                
                <div class="report-buttons">
                    <button onclick="getMonthlyReport()">📅 Monthly Spending</button>
                    <button onclick="getBudgetReport()">💰 Budget vs Actual</button>
                    <button onclick="getAllExpenses()">📋 All Expenses</button>
                    <button onclick="getStats()">📊 Quick Stats</button>
                </div>
                
                <div id="report"></div>
            </div>
        </div>
    </div>
    
    <script>
        function addExpense() {
            const amount = document.getElementById('amount').value;
            const category = document.getElementById('category').value;
            const description = document.getElementById('desc').value;
            
            if (!amount || amount <= 0) {
                showMessage('expenseMessage', 'Please enter a valid amount!', 'danger');
                return;
            }
            
            // Disable button and show loading
            const btn = document.getElementById('addBtn');
            btn.innerHTML = '⏳ Adding...';
            btn.disabled = true;
            
            fetch('/api/expense', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({amount, category, description})
            })
            .then(response => response.json())
            .then(data => {
                // Show message
                if (data.alert && data.alert.includes('exceeded')) {
                    showMessage('expenseMessage', data.message + ' ' + data.alert, 'danger');
                } else if (data.alert && data.alert.includes('Only')) {
                    showMessage('expenseMessage', data.message + ' ' + data.alert, 'warning');
                } else {
                    showMessage('expenseMessage', data.message, 'success');
                }
                
                // ✅ CLEAR FORM FIELDS
                document.getElementById('amount').value = '';
                document.getElementById('desc').value = '';
                document.getElementById('category').selectedIndex = 0;
                
                // Reset button
                btn.innerHTML = '➕ Add Expense';
                btn.disabled = false;
                
                // Play sound for alerts
                if (data.alert) {
                    playAlertSound();
                }
                
                // Auto-refresh stats
                setTimeout(getStats, 1000);
            })
            .catch(error => {
                showMessage('expenseMessage', 'Error: ' + error, 'danger');
                btn.innerHTML = '➕ Add Expense';
                btn.disabled = false;
            });
        }
        
        function setBudget() {
            const category = document.getElementById('bCategory').value;
            const amount = document.getElementById('bAmount').value;
            const month = document.getElementById('bMonth').value;
            const year = document.getElementById('bYear').value;
            
            if (!amount || amount <= 0) {
                showMessage('budgetMessage', 'Please enter a valid budget amount!', 'danger');
                return;
            }
            
            if (!month || month < 1 || month > 12) {
                showMessage('budgetMessage', 'Please enter a valid month (1-12)!', 'danger');
                return;
            }
            
            // Disable button and show loading
            const btn = document.getElementById('budgetBtn');
            btn.innerHTML = '⏳ Saving...';
            btn.disabled = true;
            
            fetch('/api/budget', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({category, amount, month, year})
            })
            .then(response => response.json())
            .then(data => {
                showMessage('budgetMessage', data.message, 'success');
                
                // CLEAR FORM FIELDS
                document.getElementById('bAmount').value = '';
                document.getElementById('bMonth').value = '';
                document.getElementById('bYear').value = '';
                document.getElementById('bCategory').selectedIndex = 0;
                
                // Reset button
                btn.innerHTML = ' Save Budget';
                btn.disabled = false;
                
                // Auto-refresh stats
                setTimeout(getStats, 1000);
            })
            .catch(error => {
                showMessage('budgetMessage', 'Error: ' + error, 'danger');
                btn.innerHTML = ' Save Budget';
                btn.disabled = false;
            });
        }
        
        function getMonthlyReport() {
            showLoading('report', 'Loading monthly report...');
            fetch('/api/report/monthly')
            .then(response => response.json())
            .then(data => {
                const html = `
                    <h3> Monthly Spending Report</h3>
                    <pre>${JSON.stringify(data, null, 2)}</pre>
                    ${generateChart(data)}
                `;
                document.getElementById('report').innerHTML = html;
            });
        }
        
        function getBudgetReport() {
            showLoading('report', 'Loading budget report...');
            fetch('/api/report/budget')
            .then(response => response.json())
            .then(data => {
                let html = '<h3> Budget vs Actual Report</h3>';
                
                if (data.length === 0) {
                    html += '<div class="alert alert-warning">No budgets set for current month</div>';
                } else {
                    data.forEach(item => {
                        const percentage = item.budget > 0 ? (item.spent / item.budget * 100) : 0;
                        const barWidth = Math.min(percentage, 100);
                        const barColor = percentage > 100 ? '#ff6b6b' : percentage > 80 ? '#ffa726' : '#4CAF50';
                        
                        html += `
                            <div class="card" style="margin: 10px 0; padding: 15px;">
                                <h4>${item.category}</h4>
                                <p>Budget: $${item.budget} | Spent: $${item.spent} | Remaining: $${item.remaining}</p>
                                <div style="background: #e9ecef; height: 20px; border-radius: 10px; margin: 10px 0;">
                                    <div style="width: ${barWidth}%; background: ${barColor}; height: 100%; border-radius: 10px;"></div>
                                </div>
                                <p style="text-align: center; font-weight: bold; color: ${barColor};">${percentage.toFixed(1)}% used</p>
                                ${item.alert ? `<div class="alert ${percentage > 100 ? 'alert-danger' : 'alert-warning'}">${item.alert}</div>` : ''}
                            </div>
                        `;
                    });
                }
                
                document.getElementById('report').innerHTML = html;
            });
        }
        
        function getAllExpenses() {
            showLoading('report', 'Loading all expenses...');
            fetch('/api/expenses')
            .then(response => response.json())
            .then(data => {
                let html = '<h3> All Expenses</h3>';
                
                if (data.length === 0) {
                    html += '<div class="alert alert-warning">No expenses recorded yet</div>';
                } else {
                    html += '<div style="max-height: 400px; overflow-y: auto;">';
                    data.forEach(expense => {
                        html += `
                            <div class="card" style="margin: 10px 0; padding: 15px;">
                                <div style="display: flex; justify-content: space-between;">
                                    <div>
                                        <strong>${expense.category}</strong><br>
                                        <small>${expense.description || 'No description'}</small>
                                    </div>
                                    <div style="text-align: right;">
                                        <strong style="color: #667eea; font-size: 1.2em;">$${expense.amount}</strong><br>
                                        <small>${expense.date}</small>
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                }
                
                document.getElementById('report').innerHTML = html;
            });
        }
        
        function getStats() {
            fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                let html = '<h3> Quick Statistics</h3>';
                html += '<div class="stats">';
                
                html += `
                    <div class="stat-card">
                        <div class="label">Total Spent This Month</div>
                        <div class="value">$${data.total_spent || '0'}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="label">Budget Categories</div>
                        <div class="value">${data.budget_count || '0'}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="label">Total Expenses</div>
                        <div class="value">${data.expense_count || '0'}</div>
                    </div>
                    
                    <div class="stat-card">
                        <div class="label">Top Category</div>
                        <div class="value">${data.top_category || 'None'}</div>
                    </div>
                `;
                
                html += '</div>';
                
                if (data.alerts && data.alerts.length > 0) {
                    html += '<div style="margin-top: 20px;">';
                    data.alerts.forEach(alert => {
                        html += `<div class="alert alert-warning">${alert}</div>`;
                    });
                    html += '</div>';
                }
                
                document.getElementById('report').innerHTML = html;
            });
        }
        
        function showMessage(elementId, message, type) {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
            
            // Auto-hide success messages after 5 seconds
            if (type === 'success') {
                setTimeout(() => {
                    element.innerHTML = '';
                }, 5000);
            }
        }
        
        function showLoading(elementId, message) {
            document.getElementById(elementId).innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div style="font-size: 2em; margin-bottom: 10px;">⏳</div>
                    <div>${message}</div>
                </div>
            `;
        }
        
        function generateChart(data) {
            if (!data.categories || Object.keys(data.categories).length === 0) {
                return '';
            }
            
            let html = '<div style="margin-top: 20px;"><h4>Category Breakdown</h4>';
            
            const categories = Object.keys(data.categories);
            const amounts = Object.values(data.categories);
            const total = amounts.reduce((a, b) => a + b, 0);
            
            categories.forEach((category, index) => {
                const percentage = total > 0 ? (amounts[index] / total * 100) : 0;
                html += `
                    <div style="margin: 10px 0;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                            <span>${category}</span>
                            <span>$${amounts[index]} (${percentage.toFixed(1)}%)</span>
                        </div>
                        <div style="background: #e9ecef; height: 10px; border-radius: 5px;">
                            <div style="width: ${percentage}%; background: #667eea; height: 100%; border-radius: 5px;"></div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            return html;
        }
        
        function playAlertSound() {
            // Simple alert sound using Web Audio API
            try {
                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const oscillator = audioContext.createOscillator();
                const gainNode = audioContext.createGain();
                
                oscillator.connect(gainNode);
                gainNode.connect(audioContext.destination);
                
                oscillator.frequency.value = 800;
                oscillator.type = 'sine';
                
                gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
                gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
                
                oscillator.start(audioContext.currentTime);
                oscillator.stop(audioContext.currentTime + 0.5);
            } catch (e) {
                console.log('Audio not supported');
            }
        }
        
        // Load stats on page load
        document.addEventListener('DOMContentLoaded', function() {
            getStats();
        });
        
        // Add Enter key support
        document.getElementById('amount').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') addExpense();
        });
        
        document.getElementById('desc').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') addExpense();
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/expense', methods=['POST'])
def add_expense():
    data = request.json
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    
    cursor.execute(
        'INSERT INTO expenses (amount, category, description) VALUES (?, ?, ?)',
        (float(data['amount']), data['category'], data.get('description', ''))
    )
    
   
    today = datetime.now()
    month = today.month
    year = today.year
    
    
    cursor.execute(
        'SELECT amount FROM budgets WHERE category=? AND month=? AND year=?',
        (data['category'], month, year)
    )
    
    budget_row = cursor.fetchone()
    alert_msg = ""
    
    if budget_row:
        budget = budget_row[0]
        
        
        cursor.execute('''
            SELECT SUM(amount) FROM expenses 
            WHERE category=? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
        ''', (data['category'], f'{month:02d}', str(year)))
        
        total_result = cursor.fetchone()
        total_spent = total_result[0] if total_result[0] else 0
        
        
        if total_spent > budget:
            alert_msg = f"BUDGET EXCEEDED! You've spent ${total_spent:.2f} out of ${budget} budget for {data['category']}"
        elif total_spent >= budget * 0.9:  
            remaining = budget - total_spent
            alert_msg = f" LOW BUDGET! Only ${remaining:.2f} left (${total_spent:.2f} spent of ${budget})"
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': f" Added ${data['amount']} to {data['category']}",
        'alert': alert_msg
    })

@app.route('/api/budget', methods=['POST'])
def set_budget():
    data = request.json
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO budgets (category, amount, month, year)
        VALUES (?, ?, ?, ?)
    ''', (data['category'], float(data['amount']), int(data['month']), int(data['year'])))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'message': f"Budget set: ${data['amount']} for {data['category']} in {data['month']}/{data['year']}"
    })

@app.route('/api/report/monthly')
def monthly_report():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    today = datetime.now()
    month = today.month
    year = today.year
    
    
    cursor.execute('''
        SELECT category, SUM(amount) as total 
        FROM expenses 
        WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
        GROUP BY category
    ''', (f'{month:02d}', str(year)))
    
    categories = {}
    total = 0
    for row in cursor.fetchall():
        categories[row[0]] = row[1]
        total += row[1]
    
    conn.close()
    
    return jsonify({
        'month': month,
        'year': year,
        'categories': categories,
        'total': round(total, 2)
    })

@app.route('/api/report/budget')
def budget_report():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    today = datetime.now()
    month = today.month
    year = today.year
    
   
    cursor.execute(
        'SELECT category, amount FROM budgets WHERE month=? AND year=?',
        (month, year)
    )
    
    budgets = cursor.fetchall()
    report = []
    
    for category, budget_amount in budgets:
        
        cursor.execute('''
            SELECT SUM(amount) FROM expenses 
            WHERE category=? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
        ''', (category, f'{month:02d}', str(year)))
        
        spent_result = cursor.fetchone()
        spent = spent_result[0] if spent_result[0] else 0
        remaining = budget_amount - spent
        
        alert = ""
        if spent > budget_amount:
            alert = " BUDGET EXCEEDED!"
        elif remaining <= budget_amount * 0.1:
            alert = f" Only ${remaining:.2f} left (less than 10%)"
        
        report.append({
            'category': category,
            'budget': budget_amount,
            'spent': round(spent, 2),
            'remaining': round(remaining, 2),
            'alert': alert
        })
    
    conn.close()
    return jsonify(report)

@app.route('/api/expenses')
def get_all_expenses():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, amount, category, description, 
               strftime('%Y-%m-%d %H:%M:%S', date) as date 
        FROM expenses 
        ORDER BY date DESC
    ''')
    
    expenses = []
    for row in cursor.fetchall():
        expenses.append({
            'id': row[0],
            'amount': row[1],
            'category': row[2],
            'description': row[3],
            'date': row[4]
        })
    
    conn.close()
    return jsonify(expenses)

@app.route('/api/stats')
def get_stats():
    conn = sqlite3.connect('expenses.db')
    cursor = conn.cursor()
    
    today = datetime.now()
    month = today.month
    year = today.year
    
    
    cursor.execute('''
        SELECT SUM(amount) FROM expenses 
        WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
    ''', (f'{month:02d}', str(year)))
    
    total_spent = cursor.fetchone()[0] or 0
    
    
    cursor.execute('SELECT COUNT(*) FROM budgets WHERE month=? AND year=?', (month, year))
    budget_count = cursor.fetchone()[0]
    
    
    cursor.execute('SELECT COUNT(*) FROM expenses')
    expense_count = cursor.fetchone()[0]
    
    
    cursor.execute('''
        SELECT category FROM expenses 
        WHERE strftime('%m', date) = ? AND strftime('%Y', date) = ?
        GROUP BY category 
        ORDER BY SUM(amount) DESC 
        LIMIT 1
    ''', (f'{month:02d}', str(year)))
    
    top_category_row = cursor.fetchone()
    top_category = top_category_row[0] if top_category_row else 'None'
    
    
    cursor.execute('SELECT category, amount FROM budgets WHERE month=? AND year=?', (month, year))
    budgets = cursor.fetchall()
    
    alerts = []
    for category, budget in budgets:
        cursor.execute('''
            SELECT SUM(amount) FROM expenses 
            WHERE category=? AND strftime('%m', date) = ? AND strftime('%Y', date) = ?
        ''', (category, f'{month:02d}', str(year)))
        
        spent = cursor.fetchone()[0] or 0
        if spent > budget:
            alerts.append(f"{category} budget exceeded!")
        elif spent >= budget * 0.9:
            alerts.append(f" {category} budget running low!")
    
    conn.close()
    
    return jsonify({
        'total_spent': round(total_spent, 2),
        'budget_count': budget_count,
        'expense_count': expense_count,
        'top_category': top_category,
        'alerts': alerts
    })

@app.route('/api/expense/share', methods=['POST'])
def share_expense():
    data = request.json
    users = data.get('users', [])
    amount = float(data['amount'])
    
    if users:
        per_person = amount / (len(users) + 1)
        return jsonify({
            'message': f'Expense shared with {len(users)} people',
            'amount_per_person': round(per_person, 2),
            'total_amount': amount,
            'shared_with': users
        })
    else:
        return jsonify({
            'message': ' No users specified for sharing',
            'amount_per_person': amount
        })

if __name__ == '__main__':
    print("=" * 60)
    print("EXPENSE TRACKER PRO - READY TO USE!")
    print("=" * 60)
    print("Features:")
    print("Forms auto-clear after submission")
    print("Beautiful modern UI")
    print("Smart budget alerts")
    print("Real-time statistics")
    print("Visual charts and reports")
    print("=" * 60)
    print(" Open: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, port=5000)