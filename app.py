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

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import spacy
import joblib

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ayushgos4998@localhost/ethical-assistant'
db = SQLAlchemy(app)

# Load the trained SpaCy NLP model
nlp = spacy.load("trained_models/nlp_model")

# Load the trained decision tree model for ethical decision-making
decision_tree_model = joblib.load("trained_models/decision_tree_model.pkl")

# Function to process and categorize user input
def process_text(text):
    doc = nlp(text)
    return doc.cats

# Function to extract features (impact, net utility) from user message (placeholder logic)
def extract_features(message):
    # Example logic for extracting features, you can replace this with actual NLP logic
    # based on the context of the message
    if "harm" in message or "negative" in message:
        impact = 9  # High impact
        net_utility = -3  # Negative net utility
    elif "benefit" in message or "positive" in message:
        impact = 7  # Medium-high impact
        net_utility = 6  # Positive net utility
    else:
        impact = 5  # Neutral impact
        net_utility = 3  # Neutral/slightly positive utility
    return impact, net_utility

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
    if categories.get("ETHICS", 0.0) > 0.5:
        bot_response = "You've mentioned ethics. Let's analyze the dilemma further."

        # Extract features from the message
        impact, net_utility = extract_features(user_message)

        # Use the decision tree model to classify the dilemma
        prediction = decision_tree_model.predict([[impact, net_utility]])
        ethical_label = "Ethical" if prediction == 1 else "Unethical"
        bot_response += f" This scenario seems {ethical_label}."

    else:
        bot_response = f"You said: {user_message}. Here's a thoughtful response!"

    return jsonify({
        'bot_response': bot_response
    })

if __name__ == '__main__':
    app.run(debug=True)
"""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import spacy
import pandas as pd
import joblib
import os

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ayushgos4998@localhost/ethical-assistant'
db = SQLAlchemy(app)

# Load the trained models
nlp = spacy.load("trained_models/nlp_model")

# Load the trained DecisionTreeClassifier model
model_path = os.path.join("trained_models", "decision_tree_model.pkl")
model = joblib.load(model_path)

# Define feature names used during training
feature_names = ['Impact', 'Net Utility']  # Use actual feature names from your training data

# Function to process and categorize user input
def process_text(text):
    doc = nlp(text)
    # This should return a dictionary of features for the model, adjust as needed
    # Dummy implementation, replace with your actual logic
    return {'Impact': doc.cats.get('ETHICAL', 0), 'Net Utility': doc.cats.get('GENERAL', 0)}

# Function to make a decision based on input data
# Dummy function to simulate decision-making (Replace with actual logic)
def make_decision(input_data):
    # Create a DataFrame from input data
    df_input = pd.DataFrame([input_data], columns=['Impact', 'Net Utility'])
    prediction = model.predict(df_input)
    
    # Determine the decision result
    decision_result = 'Ethical' if prediction[0] == 1 else 'Unethical'
    
    # Route to specific node based on decision result
    return {
        'decision_result': decision_result,
        'next_node': 2  # Move to Node 2 for decision
    }

@app.route('/api/decision', methods=['POST'])
def get_decision():
    data = request.get_json()
    user_message = data.get('message')
    current_node = data.get('current_node', 0)  # Default to Node 0

    # Node 0: Initial Welcome
    if current_node == 0:
        if user_message.lower() in ['hi', 'hello', 'hey']:
            return jsonify({
                'bot_response': "Welcome! I am your ethical assistant. Please provide an ethical scenario or question.",
                'next_node': 1  # Move to Node 1 for more details
            })
        else:
            # Assuming user provided enough details, move to Node 2
            return jsonify({
                'bot_response': "Thank you for providing an ethical scenario. Processing your request...",
                'next_node': 2
            })

    # Node 1: Request more information
    if current_node == 1:
        if len(user_message.split()) > 5:  # A basic check for sufficient details
            # Process scenario and move to Node 2
            input_data = process_text(user_message)
            decision_result = make_decision(input_data)
            return jsonify({
                'bot_response': f"Decision result: {decision_result['decision_result']}.",
                'next_node': decision_result['next_node']
            })
        else:
            return jsonify({
                'bot_response': "I need more information to evaluate this ethical scenario. Could you provide more details?",
                'next_node': 1  # Stay in Node 1 until we get sufficient details
            })

    # Node 2: Process decision and give result
    if current_node == 2:
        input_data = process_text(user_message)
        decision_result = make_decision(input_data)
        return jsonify({
            'bot_response': f"It seems that this decision is considered {decision_result['decision_result']}.",
            'next_node': decision_result['next_node']
        })


if __name__ == '__main__':
    app.run(debug=True)
