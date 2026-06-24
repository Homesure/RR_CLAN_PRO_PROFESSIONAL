from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "login"


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    app.config["SECRET_KEY"] = "change-this-secret-key-before-production"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///rrclanpro.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["RAZORPAY_KEY_ID"] = os.getenv("RAZORPAY_KEY_ID")
    app.config["RAZORPAY_KEY_SECRET"] = os.getenv("RAZORPAY_KEY_SECRET")

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User
    from app.routes import register_routes

    register_routes(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()
        seed_database()

    return app


def seed_database():
    from app.models import User

    default_users = [
        {
            "name": "RR CLAN PRO Admin",
            "email": "admin@rrclanpro.com",
            "password": "admin123",
            "role": "admin",
            "skill": None,
        },
        {
            "name": "Rahul Cleaning Expert",
            "email": "cleaning@rrclanpro.com",
            "password": "tech123",
            "role": "technician",
            "skill": "Cleaning",
        },
        {
            "name": "Imran Plumbing Expert",
            "email": "plumbing@rrclanpro.com",
            "password": "tech123",
            "role": "technician",
            "skill": "Plumbing",
        },
        {
            "name": "Arjun Electrical Expert",
            "email": "electrical@rrclanpro.com",
            "password": "tech123",
            "role": "technician",
            "skill": "Electrical",
        },
        {
            "name": "Sameer AC Expert",
            "email": "ac@rrclanpro.com",
            "password": "tech123",
            "role": "technician",
            "skill": "AC Service",
        },
    ]

    for item in default_users:
        existing_user = User.query.filter_by(email=item["email"]).first()

        if not existing_user:
            user = User(
                name=item["name"],
                email=item["email"],
                password_hash=generate_password_hash(item["password"]),
                role=item["role"],
                skill=item["skill"],
            )

            db.session.add(user)

    db.session.commit()