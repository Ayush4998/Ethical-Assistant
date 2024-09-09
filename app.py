"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure the database connection
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Example route
@app.route('/')
def home():
    return "Welcome to the Ethical Assistant Backend!"

# Define your models

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    ethical_decisions = db.relationship('EthicalDecision', backref='user', lazy=True, cascade="all, delete-orphan")
    interactions = db.relationship('Interaction', backref='user', lazy=True, cascade="all, delete-orphan")
    feedback = db.relationship('Feedback', backref='user', lazy=True, cascade="all, delete-orphan")
    logs = db.relationship('Log', backref='user', lazy=True, cascade="all, delete-orphan")

class EthicalDecision(db.Model):
    __tablename__ = 'ethical_decisions'
    decision_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    decision = db.Column(db.Text, nullable=False)
    ethical_framework = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    interactions = db.relationship('Interaction', backref='ethical_decision', lazy=True, cascade="all, delete-orphan")

class Interaction(db.Model):
    __tablename__ = 'interactions'
    interaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    decision_id = db.Column(db.Integer, db.ForeignKey('ethical_decisions.decision_id', ondelete='CASCADE'), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Feedback(db.Model):
    __tablename__ = 'feedback'
    feedback_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    decision_id = db.Column(db.Integer, db.ForeignKey('ethical_decisions.decision_id', ondelete='CASCADE'), nullable=False)
    feedback_text = db.Column(db.Text)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Log(db.Model):
    __tablename__ = 'logs'
    log_id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False)
    event_message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)

# Optional: Use SQLAlchemy Index constructs if needed
from sqlalchemy.schema import Index

Index('idx_decision_user_id', EthicalDecision.user_id)
Index('idx_interaction_user_id', Interaction.user_id)
Index('idx_feedback_user_id', Feedback.user_id)
Index('idx_feedback_decision_id', Feedback.decision_id)
Index('idx_logs_created_at', Log.created_at)

if __name__ == '__main__':
    app.run(debug=True)
"""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import spacy

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ayushgos4998@localhost/ethical-assistant'
db = SQLAlchemy(app)

# Load the trained model
nlp = spacy.load("trained_models/nlp_model")

# Function to process and categorize user input
def process_text(text):
    doc = nlp(text)
    return doc.cats

@app.route('/api/get_user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    from models import User  # Import inside function
    user = User.query.get(user_id)
    if user:
        return jsonify({
            'user_id': user.user_id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at
        })
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/decision', methods=['POST'])
def get_decision():
    data = request.get_json()
    user_message = data.get('message')

    # Process the user message using the NLP model
    categories = process_text(user_message)
    
    # Determine response based on the categories
    if categories.get("ETHICAL", 0) > 0.5:
        bot_response = "You've mentioned ethics. Let's discuss ethical implications."
    elif categories.get("GENERAL", 0) > 0.5:
        bot_response = f"You said: {user_message}. Here's a thoughtful response!"
    else:
        bot_response = "I'm not sure how to categorize this message. Could you provide more details?"

    return jsonify({
        'bot_response': bot_response
    })

if __name__ == '__main__':
    app.run(debug=True)
