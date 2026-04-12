from flask import Blueprint, request, jsonify, render_template
from app.model import predict_credit_score

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