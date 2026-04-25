from flask import Blueprint, render_template, request, jsonify, redirect, session
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
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            user = User.query.filter_by(username=username, password=password).first()

            if user:
                session['user_id'] = user.id
                return redirect('/dashboard')

            return render_template('login.html', error="Invalid credentials")

        return render_template('login.html')

    except Exception as e:
        return f"Login error: {e}"


# -----------------------
# REGISTER
# -----------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            if User.query.filter_by(username=username).first():
                return render_template('register.html', error="User already exists")

            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            return redirect('/')

        return render_template('register.html')

    except Exception as e:
        return f"Register error: {e}"


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
    try:
        apps = Application.query.all() or []

        total = len(apps)

        avg_score = round(
            sum([float(a.score) for a in apps]) / total, 2
        ) if total > 0 else 0

        approved = len([a for a in apps if a.decision == "Approved"])
        rejected = len([a for a in apps if a.decision == "Rejected"])

        approval_rate = round((approved / total) * 100, 2) if total > 0 else 0

        low = len([a for a in apps if a.risk == "Low"])
        medium = len([a for a in apps if a.risk == "Medium"])
        high = len([a for a in apps if a.risk == "High"])

        # -----------------------
        # EXTRA ANALYTICS
        # -----------------------
        avg_pd = round(
            sum([(100 - float(a.score)) / 100 for a in apps]) / total, 3
        ) if total > 0 else 0

        score_bins = {
            "0-20": 0,
            "20-40": 0,
            "40-60": 0,
            "60-80": 0,
            "80-100": 0
        }

        for a in apps:
            s = float(a.score)
            if s <= 20:
                score_bins["0-20"] += 1
            elif s <= 40:
                score_bins["20-40"] += 1
            elif s <= 60:
                score_bins["40-60"] += 1
            elif s <= 80:
                score_bins["60-80"] += 1
            else:
                score_bins["80-100"] += 1

        risk_approval = {
            "Low": {"Approved": 0, "Rejected": 0},
            "Medium": {"Approved": 0, "Rejected": 0},
            "High": {"Approved": 0, "Rejected": 0}
        }

        for a in apps:
            if a.risk in risk_approval and a.decision in ["Approved", "Rejected"]:
                risk_approval[a.risk][a.decision] += 1

        recent_scores = [float(a.score) for a in apps[-10:]]

        # -----------------------
        # LOAD ROC DATA
        # -----------------------
        fpr, tpr, auc_score = [], [], 0

        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            roc_path = os.path.join(base_dir, "roc_data.pkl")

            if os.path.exists(roc_path):
                with open(roc_path, "rb") as f:
                    roc = pickle.load(f)

                fpr = roc.get("fpr", [])
                tpr = roc.get("tpr", [])
                auc_score = round(float(roc.get("auc", 0)), 3)

        except Exception as e:
            print("ROC error:", e)

        return render_template(
            "dashboard.html",
            apps=apps,
            total=total,
            avg_score=avg_score,
            approval_rate=approval_rate,
            approved=approved,
            rejected=rejected,
            low=low,
            medium=medium,
            high=high,
            avg_pd=avg_pd,
            score_bins=score_bins,
            risk_approval=risk_approval,
            recent_scores=recent_scores,
            fpr=fpr,
            tpr=tpr,
            auc=auc_score
        )

    except Exception as e:
        return f"Dashboard error: {e}"


# -----------------------
# NEW APPLICATION PAGE
# -----------------------
@main.route('/new')
def new_application():
    return render_template('index.html')


# -----------------------
# SCORE
# -----------------------
@main.route('/score', methods=['POST'])
def score():
    try:
        data = request.get_json() or {}

        # BASIC
        income = float(data.get('income', 0))
        expenses = float(data.get('expenses', 0))
        savings = float(data.get('savings', 0))
        missed = int(data.get('missed_payments', 0))

        # ADVANCED
        total_debt = float(data.get('total_debt', 0))
        credit_limit = float(data.get('credit_limit', 1))
        used_credit = float(data.get('used_credit', 0))
        late_payments = int(data.get('late_payments', 0))
        credit_history = int(data.get('credit_history', 1))
        new_accounts = int(data.get('new_accounts', 0))
        job_years = int(data.get('job_years', 0))
        residence_years = int(data.get('residence_years', 0))

        result = predict_credit_score(
            income, expenses, savings, missed,
            total_debt, credit_limit, used_credit,
            late_payments, credit_history,
            new_accounts, job_years, residence_years
        )

        if not result or "error" in result:
            return jsonify({"error": "Model error"})

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
    try:
        app = Application.query.get(id)
        if app:
            app.decision = "Approved"
            db.session.commit()
    except Exception as e:
        print("Approve error:", e)

    return redirect('/dashboard')


# -----------------------
# REJECT
# -----------------------
@main.route('/decide/<int:id>/reject')
def reject(id):
    try:
        app = Application.query.get(id)
        if app:
            app.decision = "Rejected"
            db.session.commit()
    except Exception as e:
        print("Reject error:", e)

    return redirect('/dashboard')