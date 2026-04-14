from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.model import predict_credit_score
from app.models import Application
from app.db import db

main = Blueprint('main', __name__)

USERNAME = "admin"
PASSWORD = "1234"

# --- LOGIN ---
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == USERNAME and request.form.get('password') == PASSWORD:
            session['user'] = USERNAME
            return redirect(url_for('main.dashboard'))
        return "Invalid credentials"
    return render_template('login.html')


# --- LOGOUT ---
@main.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main.login'))


# --- DASHBOARD (NOW WORKS FOR BOTH / AND /dashboard) ---
@main.route('/')
@main.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    apps = Application.query.all()

    total = len(apps)

    avg_score = round(sum([a.score for a in apps]) / total, 2) if total > 0 else 0

    approved = len([a for a in apps if a.decision == "Approved"])
    approval_rate = round((approved / total) * 100, 2) if total > 0 else 0

    low = len([a for a in apps if a.risk == "Low"])
    medium = len([a for a in apps if a.risk == "Medium"])
    high = len([a for a in apps if a.risk == "High"])

    return render_template(
        'dashboard.html',
        apps=apps,
        total=total,
        avg_score=avg_score,
        approval_rate=approval_rate,
        low=low,
        medium=medium,
        high=high
    )


# --- NEW APPLICATION PAGE ---
@main.route('/new')
def new_app():
    if 'user' not in session:
        return redirect(url_for('main.login'))
    return render_template('index.html')


# --- SCORE (API) ---
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


# --- APPROVE / REJECT ---
@main.route('/decide/<int:id>/<action>')
def decide(id, action):
    if 'user' not in session:
        return redirect(url_for('main.login'))

    app_item = Application.query.get(id)

    if app_item:
        if action == "approve":
            app_item.decision = "Approved"
        elif action == "reject":
            app_item.decision = "Rejected"

        db.session.commit()

    return redirect(url_for('main.dashboard'))