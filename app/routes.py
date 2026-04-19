from flask import Blueprint, render_template, request, jsonify, redirect, session
from app.model import predict_credit_score
from app.models import Application, User
from app.db import db

import pickle
import os

main = Blueprint('main', __name__)

# --------------------------------
# REGISTER
# -------------------------------

@main.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')

            # check if user exists
            existing = User.query.filter_by(username=username).first()
            if existing:
                return render_template('register.html', error="User already exists")

            # create user
            user = User(username=username, password=password)
            db.session.add(user)
            db.session.commit()

            return redirect('/')

        return render_template('register.html')

    except Exception as e:
        return f"Register error: {e}"
# -----------------------
# LOGIN
# -----------------------
@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')

        user = User.query.filter_by(username=username).first()

        if user:
            session['user_id'] = user.id
            return redirect('/dashboard')

        return render_template('login.html', error="User not found")

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
    try:
        apps = Application.query.all() or []

        total = len(apps)

        avg_score = round(sum([float(a.score) for a in apps]) / total, 2) if total > 0 else 0

        approved = len([a for a in apps if a.decision == "Approved"])
        rejected = len([a for a in apps if a.decision == "Rejected"])

        approval_rate = round((approved / total) * 100, 2) if total > 0 else 0

        low = len([a for a in apps if a.risk == "Low"])
        medium = len([a for a in apps if a.risk == "Medium"])
        high = len([a for a in apps if a.risk == "High"])

        # -----------------------
        # LOAD ROC SAFELY
        # -----------------------
        fpr, tpr, auc_score = [], [], 0

        try:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
            roc_path = os.path.join(base_dir, "roc_data.pkl")

            if os.path.exists(roc_path):
                with open(roc_path, "rb") as f:
                    roc_data = pickle.load(f)

                fpr = roc_data.get("fpr", [])
                tpr = roc_data.get("tpr", [])
                auc_score = round(float(roc_data.get("auc", 0)), 3)

        except Exception as e:
            print("ROC load error:", e)

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
# SCORE + SAVE
# -----------------------
@main.route('/score', methods=['POST'])
def score():
    try:
        data = request.get_json() or {}

        income = float(data.get('income', 0))
        expenses = float(data.get('expenses', 0))
        savings = float(data.get('savings', 0))
        missed = int(data.get('missed_payments', 0))

        # ---- MODEL ----
        result = predict_credit_score(income, expenses, savings, missed)

        if not result or "error" in result:
            return jsonify({"error": "Model failed"})

        # ---- SAVE ----
        new_app = Application(
            income=income,
            expenses=expenses,
            savings=savings,
            missed=missed,
            score=float(result.get("score", 0)),
            risk=result.get("risk", "Unknown"),
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