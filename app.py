# app.py (VERSÃO ATUALIZADA)
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from datetime import datetime
from collections import defaultdict

app = Flask(__name__)

# --- NÚMERO DE COLABORADORES ---
# Altere este número para o total de pessoas que participam na partilha.
NUM_EMPLOYEES = 3 

# --- BASE DE DADOS E LÓGICA DE CÁLCULO (sem alterações) ---
DATA_FILE = 'monthly_data.json'

def get_data():
    if not os.path.exists(DATA_FILE): return {}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError): return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4, sort_keys=True)

def calculate_bonus_logic(monthly_profit, num_employees=NUM_EMPLOYEES):
    if monthly_profit <= 0 or num_employees == 0:
        return { "bonus_pool": 0, "monthly_payout_total": 0, "semester_reserve": 0, "payout_per_employee": 0 }
    bonus_pool = monthly_profit * 0.50
    monthly_payout_total = bonus_pool * 0.60
    semester_reserve = bonus_pool * 0.40
    payout_per_employee = monthly_payout_total / num_employees
    return { "bonus_pool": bonus_pool, "monthly_payout_total": monthly_payout_total, "semester_reserve": semester_reserve, "payout_per_employee": payout_per_employee }

# --- NOVA LÓGICA PARA CALCULAR OS TOTAIS SEMESTRAIS ---
def calculate_semester_totals(all_monthly_data):
    semester_reserves = defaultdict(float)
    for month_key, data in all_monthly_data.items():
        year, month = map(int, month_key.split('-'))
        profit = data.get('profit', 0)
        
        # Apenas lucros positivos contribuem para a reserva
        if profit > 0:
            reserve_value = calculate_bonus_logic(profit)['semester_reserve']
            
            # Determinar o semestre (S1 ou S2)
            semester_key = f"{year}-S1" if month <= 6 else f"{year}-S2"
            semester_reserves[semester_key] += reserve_value
            
    return dict(sorted(semester_reserves.items(), reverse=True))

# --- ROTAS DA APLICAÇÃO ---
@app.route('/')
def dashboard():
    """A página principal que agora mostra também o bónus semestral."""
    all_data = get_data()
    
    # Processamento para a tabela mensal
    dashboard_data = {}
    sorted_months = sorted(all_data.keys(), reverse=True)
    for month_key in sorted_months:
        data = all_data[month_key]
        profit = data.get('profit', 0)
        bonus_info = calculate_bonus_logic(profit)
        dashboard_data[month_key] = { "profit": profit, **bonus_info }
        
    # NOVO: Calcular os totais semestrais
    semester_totals = calculate_semester_totals(all_data)
    
    return render_template('index.html', data=dashboard_data, semester_data=semester_totals, num_employees=NUM_EMPLOYEES)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    """Página de admin (sem alterações na lógica principal)."""
    if request.method == 'POST':
        # Altere a sua password aqui se desejar
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
    print("Para ver o dashboard, abra o seu browser e vá para: http://12.0.0.1:5000")
    print("\nPara adicionar dados, vá para: http://127.0.0.1:5000/admin")
    print("*"*50)
    app.run(host='0.0.0.0', port=5000, debug=False)