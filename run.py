from flask import Flask
from app.routes import main
from app.db import db
import os

app = Flask(__name__)

app.secret_key = "supersecretkey"

# DATABASE CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(main)

# CREATE TABLES
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()