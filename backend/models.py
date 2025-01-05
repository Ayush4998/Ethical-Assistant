# models.py
from app import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class EthicalDecision(db.Model):
    __tablename__ = 'ethical_decisions'
    decision_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    decision = db.Column(db.Text, nullable=False)
    ethical_framework = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
