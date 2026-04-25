from flask import Flask
from app.routes import main
from app.db import db

app = Flask(__name__)
app.secret_key = "secret"

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Register routes
app.register_blueprint(main)

# Create tables
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)