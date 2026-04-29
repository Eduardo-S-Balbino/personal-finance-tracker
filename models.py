from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    goal_percentage = db.Column(db.Float, nullable=False, default=20)

    transactions = db.relationship("Transaction", backref="user", lazy=True)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text, nullable=True)

    is_recurring = db.Column(db.Boolean, default=False)
    recurrence_type = db.Column(db.String(20), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)