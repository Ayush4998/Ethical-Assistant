from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import spacy
import joblib
import os
import numpy as np

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Ayushgos4998@localhost/ethical_assistant'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Initialize SQLAlchemy

# Session configuration
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SECRET_KEY'] = os.urandom(24)  # Generate a random secret key

# Load the trained models
nlp = spacy.load("trained_models/nlp_model")
model_path = os.path.join("trained_models/decision_tree_model", "decision_tree_model.pkl")
model = joblib.load(model_path)

# Initialize variables for conversation state
current_node = 1

# Example utility mapping
utility_mapping = {
    'happy': 1,
    'neutral': 0,
    'sad': -1,
    # Add other states and their utility values as needed
}

# Helper function to calculate utility for a single outcome
def calculate_outcome_utility(outcome):
    total_benefit = 0
    total_harm = 0
    
    for stakeholder_impact in outcome:
        state = stakeholder_impact.split(',')[1].strip()  # Extract state
        if state in utility_mapping:
            utility_value = utility_mapping[state]
            if utility_value > 0:
                total_benefit += utility_value
            else:
                total_harm += abs(utility_value)
    
    return total_benefit, total_harm

# Helper function to summarize outcomes
def summarize_outcomes(parsed_outcomes):
    outcomes_summary = []
    for i, outcome in enumerate(parsed_outcomes):
        total_benefit, total_harm = calculate_outcome_utility(outcome)
        outcome_status = "Harm outweighs benefit" if total_harm > total_benefit else "Benefit outweighs harm"
        outcomes_summary.append(f"Outcome {i + 1}: {outcome_status} (Benefit: {total_benefit}, Harm: {total_harm})")
    return outcomes_summary

# Process user input and manage nodes
@app.route('/api/decision', methods=['POST'])
def get_decision():
    global current_node
    data = request.get_json()
    user_message = data.get('message')

    # Node 1: Initial greeting and asking for scenario
    if current_node == 1:
        if user_message.lower() in ['hi', 'hello', 'hey']:
            return jsonify({
                'bot_response': "Welcome! I am your ethical assistant. Please provide a scenario or question you'd like help with."
            })
        elif len(user_message.split()) > 5:
            current_node = 3
            return jsonify({
                'bot_response': "Thank you for providing context. What area does your ethical dilemma concern? Please choose one of the following: Business, Healthcare, Education, Technology, or Environment."
            })
        else:
            return jsonify({
                'bot_response': "I need more information to assist you. Please provide more details about your ethical dilemma."
            })

    # Node 2: Ask for type of dilemma
    if current_node == 2:
        if len(user_message.split()) > 5:
            current_node = 3
            return jsonify({
                'bot_response': "Thank you for providing context. What area does your ethical dilemma concern? Please choose one of the following: Business, Healthcare, Education, Technology, or Environment."
            })
        else:
            return jsonify({
                'bot_response': "I still need more details to understand the situation. Could you provide more?"
            })

    # Node 3: Ask for all potential outcomes
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            return jsonify({
                'bot_response': "Could you provide a valid option from the given categories?"
            })

    # Node 4: Ask to list all the stakeholders affected by this decision
    if current_node == 4:
        outcomes = [outcome.strip() for outcome in user_message.split(',') if outcome]

        if len(outcomes) >= 2:
            formatted_outcomes = '\n'.join(outcomes)
            current_node = 5
            return jsonify({
                'bot_response': f"Here are the outcomes you've provided:\n{formatted_outcomes}.\nNow, please list all the stakeholders affected by this decision, separated by commas."
            })
        else:
            return jsonify({
                'bot_response': "I need at least two potential outcomes to proceed. Please list all the possible outcomes of this decision, separated by commas."
            })

    # Node 5: Affect on each stakeholder
    if current_node == 5:
        stakeholders = [stakeholder.strip() for stakeholder in user_message.split(',')]

        if len(stakeholders) >= 2:
            current_node = 6
            return jsonify({
                'bot_response': f"Thank you for providing the stakeholders: {', '.join(stakeholders)}. Let's proceed to analyze their impact."
            })
        else:
            return jsonify({
                'bot_response': "I need at least two stakeholders to continue. Please list all stakeholders affected by this decision, separated by commas."
            })

    # Node 6: Analyze the impact on each stakeholder
    if current_node == 6:
        # Split the message into different outcomes based on '.'
        outcomes_with_stakeholders = user_message.split('.')
        
        parsed_outcomes = []
        for outcome in outcomes_with_stakeholders:
            # Split each outcome by ';' to get stakeholder impacts
            stakeholder_impacts = [stakeholder.strip() for stakeholder in outcome.split(';')]
            parsed_outcomes.append(stakeholder_impacts)

        if all(len(stakeholder_impact.split(',')) == 2 for stakeholder_impact in parsed_outcomes[0]):
            outcomes_summary = summarize_outcomes(parsed_outcomes)
            return jsonify({
                'bot_response': f"Here is a summary of the outcomes:\n" +
                                '\n'.join(outcomes_summary)
            })
        else:
            return jsonify({
                'bot_response': "Each outcome should have at least two stakeholders with their impacts. Please provide the impact on stakeholders for each outcome, separated by '.' for different outcomes, and ';' for different stakeholders, with ',' separating stakeholder and impact."
            })


"""  
    # Node 7: If the benefit outweighs the harm, the chatbot supports the decision under 
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })

    # Node 8: Adherence to Moral Principles
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })


    # Node 9: Universalizability Test
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })


    # Node 10: If the action violates moral principles, the chatbot advises against it under Deontology
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })
        

    # Node 11: If the action upholds moral principles, the chatbot supports it
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })

    # Node 12: Protecting Individual Rights
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })

    # Node 13: Prioritizing Rights
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })

    # Node 14: If the decision violates individual rights, the chatbot advises reconsidering
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })

    # Node 15: If the decision respects individual rights, the chatbot supports the decision under Rights-Based Ethics
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })

    # Node 16: Synthesizing the Decision
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })

    # Node 17: Final Decision
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })

    # Node 18: Logging Decision
    if current_node == 3:
        if user_message.lower() in ['business', 'healthcare', 'education', 'technology', 'environment']:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 3
            return jsonify({
                'bot_response': "Could you give the correct option?"
            })
"""        
if __name__ == '__main__':
    app.run(debug=True)
