from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.model import predict_credit_score
from app.models import Application
from app.db import db

main = Blueprint('main', __name__)

# --- TEMP USER ---
USERNAME = "admin"
PASSWORD = "1234"

# --- TEMP STORAGE ---
applications = []

# --- HOME (SCORING PAGE, PROTECTED) ---
@main.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('main.login'))
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

       new_app = Application(
           income=income,
           expenses=expenses,
           savings=savings,
           missed=missed,
           score=result["score"],
           risk=result["risk"]
           )
        db.session.add(new_app)
        db.session.commit()

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


# --- DASHBOARD ---
@main.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    apps = Application.query.all()
    return render_template('dashboard.html', apps=apps)


# --- APPROVE / REJECT ---
@main.route('/decide/<int:index>/<action>')
def decide(index, action):
    if 'user' not in session:
        return redirect(url_for('main.login'))

    if action == "approve":
        app_item = Application.query.get(index)
        if action == "approve":
            app_item.decision = "Approved"
        elif action == "reject":
            app_item.decision = "Rejected"
    db.session.commit()

    return redirect(url_for('main.dashboard'))