import os
from flask import Flask
from app.routes import main
from app.db import db

app = Flask(__name__)

# -----------------------
# BASIC CONFIG
# -----------------------
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

# -----------------------
# DATABASE CONFIG
# -----------------------
DATABASE_URL = os.environ.get("DATABASE_URL")

if DATABASE_URL:
    # Fix for Render/Postgres (required)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
else:
    # Fallback for local development
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# -----------------------
# INIT DB
# -----------------------
db.init_app(app)

# -----------------------
# REGISTER ROUTES
# -----------------------
app.register_blueprint(main)

# -----------------------
# CREATE TABLES (SAFE INIT)
# -----------------------
with app.app_context():
    db.create_all()

# -----------------------
# RUN LOCAL SERVER
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)