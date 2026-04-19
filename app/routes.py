from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from app.model import predict_credit_score
from app.models import Application, User
from app.db import db

import pickle
import os

main = Blueprint('main', __name__)


# -----------------------
# LOGIN
# -----------------------
@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.id
            return redirect('/dashboard')

        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


# -----------------------
# LOGOUT
# -----------------------
@main.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# -----------------------
# DASHBOARD
# -----------------------
@main.route('/dashboard')
def dashboard():

    apps = Application.query.all()

    total = len(apps)

    avg_score = round(sum([a.score for a in apps]) / total, 2) if total > 0 else 0

    approved = len([a for a in apps if a.decision == "Approved"])
    rejected = len([a for a in apps if a.decision == "Rejected"])

    approval_rate = round((approved / total) * 100, 2) if total > 0 else 0

    low = len([a for a in apps if a.risk == "Low"])
    medium = len([a for a in apps if a.risk == "Medium"])
    high = len([a for a in apps if a.risk == "High"])

    # ---- LOAD ROC DATA ----
    roc_path = os.path.join(os.path.dirname(__file__), "..", "roc_data.pkl")

    try:
        with open(roc_path, "rb") as f:
            roc_data = pickle.load(f)

        fpr = roc_data["fpr"]
        tpr = roc_data["tpr"]
        auc_score = round(roc_data["auc"], 3)

    except:
        fpr, tpr, auc_score = [], [], 0

    return render_template(
        'dashboard.html',
        apps=apps,
        total=total,
        avg_score=avg_score,
        approval_rate=approval_rate,
        approved=approved,
        rejected=rejected,
        low=low,
        medium=medium,
        high=high,
        fpr=fpr,
        tpr=tpr,
        auc=auc_score
    )


# -----------------------
# NEW APPLICATION PAGE
# -----------------------
@main.route('/new')
def new_application():
    return render_template('index.html')


# -----------------------
# SCORE + SAVE
# -----------------------
@main.route('/score', methods=['POST'])
def score():

    data = request.get_json()

    try:
        income = float(data.get('income', 0))
        expenses = float(data.get('expenses', 0))
        savings = float(data.get('savings', 0))
        missed = int(data.get('missed_payments', 0))

        # ---- ML MODEL ----
        result = predict_credit_score(income, expenses, savings, missed)

        if "error" in result:
            return jsonify(result)

        # ---- SAVE TO DB ----
        new_app = Application(
            income=income,
            expenses=expenses,
            savings=savings,
            missed=missed,
            score=float(result["score"]),
            risk=result["risk"],
            decision="Pending"
        )

        db.session.add(new_app)
        db.session.commit()

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})


# -----------------------
# APPROVE
# -----------------------
@main.route('/decide/<int:id>/approve')
def approve(id):
    app = Application.query.get(id)
    if app:
        app.decision = "Approved"
        db.session.commit()
    return redirect('/dashboard')


# -----------------------
# REJECT
# -----------------------
@main.route('/decide/<int:id>/reject')
def reject(id):
    app = Application.query.get(id)
    if app:
        app.decision = "Rejected"
        db.session.commit()
    return redirect('/dashboard')