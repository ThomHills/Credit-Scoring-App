from flask import Blueprint, render_template, request, jsonify, redirect, session
from app.model import predict_credit_score, get_feature_importance
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
# REGISTER
# -----------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
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

    apps = Application.query.all() or []
    total = len(apps)

    avg_score = round(
        sum(float(a.score) for a in apps) / total, 2
    ) if total else 0

    approved = len([a for a in apps if a.decision == "Approved"])
    rejected = len([a for a in apps if a.decision == "Rejected"])

    approval_rate = round((approved / total) * 100, 2) if total else 0

    low = len([a for a in apps if a.risk == "Low"])
    medium = len([a for a in apps if a.risk == "Medium"])
    high = len([a for a in apps if a.risk == "High"])

    # Score distribution
    score_bins = {"0-20":0,"20-40":0,"40-60":0,"60-80":0,"80-100":0}

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

    # Risk vs decision
    risk_approval = {
        "Low": {"Approved": 0, "Rejected": 0},
        "Medium": {"Approved": 0, "Rejected": 0},
        "High": {"Approved": 0, "Rejected": 0}
    }

    for a in apps:
        if a.risk in risk_approval and a.decision in ["Approved", "Rejected"]:
            risk_approval[a.risk][a.decision] += 1

    recent_scores = [float(a.score) for a in apps[-10:]]

    # ROC data
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
        print("ROC ERROR:", e)

    feature_importance = get_feature_importance() or {}

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
        score_bins=score_bins,
        risk_approval=risk_approval,
        recent_scores=recent_scores,
        fpr=fpr,
        tpr=tpr,
        auc=auc_score,
        feature_importance=feature_importance
    )


# -----------------------
# NEW APPLICATION PAGE
# -----------------------
@main.route('/new')
def new_application():
    return render_template("index.html")


# -----------------------
# SCORE (CORE PIPELINE + DEBUG)
# -----------------------
@main.route('/score', methods=['POST'])
def score():
    try:
        print(">>> HIT /score ROUTE <<<")

        data = request.get_json()
        print("JSON RECEIVED:", data)

        if not data:
            return jsonify({"error": "No JSON received"})

        duration = float(data.get('duration', 0))
        amount = float(data.get('amount', 0))
        installment_rate = float(data.get('installment_rate', 0))
        age = float(data.get('age', 0))
        existing_credits = float(data.get('existing_credits', 0))

        print("PARSED:",
              duration, amount, installment_rate, age, existing_credits)

        print("DB COLUMNS:", Application.__table__.columns.keys())

        result = predict_credit_score(
            duration,
            amount,
            installment_rate,
            age,
            existing_credits
        )

        print("MODEL RESULT:", result)

        if "error" in result:
            return jsonify(result)

        new_app = Application(
            duration=duration,
            amount=amount,
            installment_rate=installment_rate,
            age=age,
            existing_credits=existing_credits,
            score=float(result["score"]),
            risk=result["risk"],
            decision="Pending"
        )

        print("OBJECT BEFORE SAVE:",
              new_app.duration, new_app.amount, new_app.age)

        db.session.add(new_app)
        db.session.commit()

        print(">>> SAVED SUCCESSFULLY <<<")

        return jsonify(result)

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)})


# -----------------------
# APPROVE / REJECT
# -----------------------
@main.route('/decide/<int:id>/<action>')
def decide(id, action):
    app = Application.query.get(id)

    if app:
        if action == "approve":
            app.decision = "Approved"
        elif action == "reject":
            app.decision = "Rejected"

        db.session.commit()

    return redirect('/dashboard')