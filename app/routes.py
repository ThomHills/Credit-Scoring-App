from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.model import predict_credit_score

main = Blueprint('main', __name__)

# --- TEMP USER (login credentials) ---
USERNAME = "admin"
PASSWORD = "1234"

# --- TEMP STORAGE ---
applications = []

# --- HOME ---
@main.route('/')
def home():
    return render_template('index.html')


# --- LOGIN ---
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USERNAME and password == PASSWORD:
            session['user'] = username
            return redirect(url_for('main.dashboard'))
        else:
            return "Invalid credentials"

    return render_template('login.html')


# --- LOGOUT ---
@main.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main.login'))


# --- SCORE API ---
@main.route('/score', methods=['POST'])
def score():
    try:
        data = request.get_json()

        income = float(data.get('income', 0))
        expenses = float(data.get('expenses', 0))
        savings = float(data.get('savings', 0))
        missed = float(data.get('missed_payments', 0))

        result = predict_credit_score(income, expenses, savings, missed)

        applications.append({
            "income": income,
            "expenses": expenses,
            "savings": savings,
            "missed": missed,
            "score": result["score"],
            "risk": result["risk"]
        })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


# --- DASHBOARD (PROTECTED) ---
@main.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    return render_template('dashboard.html', apps=applications)