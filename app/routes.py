from flask import Blueprint, request, jsonify, render_template
from app.model import predict_credit_score
from flask import session, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/score', methods=['POST'])
def score():
    try:
        data = request.get_json()

        income = float(data.get('income', 0))
        expenses = float(data.get('expenses', 0))
        savings = float(data.get('savings', 0))
        missed = float(data.get('missed_payments', 0))

        result = predict_credit_score(income, expenses, savings, missed)

        return jsonify(result)

    except Exception as e:
        print("ERROR:", str(e))  # shows in Render logs
        return jsonify({"error": str(e)})

USERNAME = "admin"
PASSWORD = "1234"

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


@main.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('main.login'))

@main.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('main.login'))

    return render_template('dashboard.html', apps=applications)