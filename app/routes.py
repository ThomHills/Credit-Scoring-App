from flask import Blueprint, render_template, request, jsonify, redirect
from app.models import Application
from app.db import db
from app.model import predict_credit_score


main = Blueprint('main', __name__)


@main.route('/')
def home():
    return render_template("login.html")

# -----------------------
# DASHBOARD
# -----------------------
@main.route('/dashboard')
def dashboard():
    apps = Application.query.order_by(Application.id.desc()).all()

    return render_template("dashboard.html", apps=apps)

@main.route('/register', methods=['GET', 'POST'])
def register():
    from app.models import User

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # check if user exists
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="User already exists")

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/')

    return render_template('register.html')

# -----------------------
# NEW APPLICATION PAGE
# -----------------------
@main.route('/new')
def new_application():
    return render_template("index.html")


# -----------------------
# SCORE (CORE PIPELINE)
# -----------------------
@main.route('/score', methods=['POST'])
def score():
    try:
        data = request.get_json()

        print("JSON:", data)

        duration = float(data.get('duration', 0))
        amount = float(data.get('amount', 0))
        installment_rate = float(data.get('installment_rate', 0))
        age = float(data.get('age', 0))
        existing_credits = float(data.get('existing_credits', 0))

        print("PARSED:", duration, amount, installment_rate, age, existing_credits)

        result = predict_credit_score(
            duration,
            amount,
            installment_rate,
            age,
            existing_credits
        )

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

        db.session.add(new_app)
        db.session.commit()

        # 🔥 VERIFY SAVE (CRITICAL)
        saved = Application.query.order_by(Application.id.desc()).first()
        print("SAVED FROM DB:",
              saved.duration,
              saved.amount,
              saved.installment_rate,
              saved.age,
              saved.existing_credits)

        return jsonify(result)

    except Exception as e:
        print("ERROR:", e)
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