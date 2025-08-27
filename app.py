# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'monthly_data.json'

def get_data():
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, sort_keys=True)

def calculate_bonus_logic(monthly_profit, num_employees=3):
    if monthly_profit <= 0 or num_employees == 0:
        return { "bonus_pool": 0, "monthly_payout_total": 0, "semester_reserve": 0, "payout_per_employee": 0 }
    bonus_pool = monthly_profit * 0.50
    monthly_payout_total = bonus_pool * 0.60
    semester_reserve = bonus_pool * 0.40
    payout_per_employee = monthly_payout_total / num_employees
    return { "bonus_pool": bonus_pool, "monthly_payout_total": monthly_payout_total, "semester_reserve": semester_reserve, "payout_per_employee": payout_per_employee }

@app.route('/')
def dashboard():
    all_data = get_data()
    dashboard_data = {}
    sorted_months = sorted(all_data.keys(), reverse=True)
    for month_key in sorted_months:
        data = all_data[month_key]
        profit = data.get('profit', 0)
        bonus_info = calculate_bonus_logic(profit)
        dashboard_data[month_key] = { "profit": profit, **bonus_info }
    return render_template('index.html', data=dashboard_data)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == 'JTD2026':
            month_year = request.form.get('month')
            try:
                profit = float(request.form.get('profit'))
                all_data = get_data()
                all_data[month_year] = {"profit": profit}
                save_data(all_data)
                return redirect(url_for('dashboard'))
            except (ValueError, TypeError):
                return "Erro: O valor do lucro tem de ser um número.", 400
        else:
            return "Password incorreta.", 403
    current_month = datetime.now().strftime('%Y-%m')
    return render_template('login.html', current_month=current_month)

if __name__ == '__main__':
    print("*"*50)
    print("Servidor da App de Transparência JTD a arrancar...")
    print("Para ver o dashboard, abra o seu browser e vá para: http://127.0.0.1:5000")
    print("\nPara adicionar dados, vá para: http://127.0.0.1:5000/admin")
    print("*"*50)
    app.run(host='0.0.0.0', port=5000, debug=False)
