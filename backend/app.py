from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import requests

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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

# Cohere API configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")  # Ensure to set your Cohere API key in the environment

headers = {
    'Authorization': f'Bearer {COHERE_API_KEY}',
    'Content-Type': 'application/json'
}

@app.route('/api/decision', methods=['POST'])
def get_decision():
    data = request.get_json()
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({'bot_response': "Please provide a scenario or question you'd like help with."})

    try:
        # Make a POST request to Cohere API for text generation
        url = "https://api.cohere.ai/generate"
        body = {
            'model': 'command-r-plus',  # Specify the model you want to use
            'prompt': f"Give the best options to solve this scenario under 150 characters: {user_message}",
            'max_tokens': 150
        }

        response = requests.post(url, headers=headers, json=body)
        
        # Check if the response is successful
        if response.status_code == 200:
            bot_response = response.json()['text']
            return jsonify({'bot_response': bot_response})
        else:
            return jsonify({'bot_response': f"Error from Cohere API: {response.text}"})
    
    except Exception as e:
        return jsonify({'bot_response': f"An error occurred while processing your request: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)


"""  from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import spacy
import joblib
import os

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
model_path = os.path.join("trained_models", "decision_tree_model.pkl")
model = joblib.load(model_path)

# Initialize variables for conversation state
current_node = 1
# Mapping of qualitative terms to numerical impact values
IMPACT_MAP = {
    "happy": 1,
    "neutral": 0,
    "unhappy": -1
}

def calculate_utility(outcome):

    Calculate the utility of an outcome by summing the impact scores.
    Positive values indicate benefits, while negative values indicate harm.

    return sum(IMPACT_MAP.get(impact.lower().strip(), 0) for _, impact in outcome)

def compare_outcomes(outcomes):
    Compare two outcomes based on their utility.
    Returns a suggestion on which outcome is better or if they are equal.

    if len(outcomes) != 2:
        return "Comparison requires exactly two outcomes."

    utility1 = calculate_utility(outcomes[0])
    utility2 = calculate_utility(outcomes[1])

    if utility1 > utility2:
        return "\nOutcome 1 is preferable because it maximizes overall positive impact, with less harm to involved stakeholders."
    elif utility2 > utility1:
        return "\nOutcome 2 is preferable because it maximizes overall positive impact, with less harm to involved stakeholders."
    else:
        return "\nBoth outcomes have equal overall impact. You may consider other factors."

# Usage in the Flask route
@app.route('/api/decision', methods=['POST'])
def get_decision():
    global current_node
    data = request.get_json()
    user_message = data.get('message')

    # Node 1: Ask for scenario or type of dilemma
    if current_node == 1:
        if user_message.lower() in ['hi', 'hello', 'hey']:
            current_node = 1
            return jsonify({
                'bot_response': "Welcome! I am your ethical assistant. Please provide a scenario or question you'd like help with."
            })
        elif len(user_message.split()) > 5:  # A basic check for sufficient details
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            current_node = 2
            return jsonify({
                'bot_response': "I need more information to assist you. Please provide more details about your ethical dilemma."
            })

    # Node 2: Ask for type of dilemma
    if current_node == 2:
        if len(user_message.split()) > 5:
            current_node = 4
            return jsonify({
                'bot_response': "Let’s evaluate this using the Utilitarianism framework. What are the potential outcomes of this decision?"
            })
        else:
            return jsonify({
                'bot_response': "I still need more details to understand the situation. Could you provide more?"
            })

    # Node 4: Ask to list all the stakeholders affected by this decision
    if current_node == 4:
        outcomes = [outcome.strip() for outcome in user_message.split(',') if outcome]
            
        if len(outcomes) >= 2:  # Check if at least two outcomes are provided
            # Store outcomes in session for further use in the conversation
            formatted_outcomes = ' and '.join(outcomes)
            current_node = 5  # Move to next node to ask for stakeholders
            return jsonify({
                'bot_response': f"Here are the outcomes you've provided:{formatted_outcomes}.\nNow, please list all the stakeholders affected by this decision, separated by commas.",
            })
        else:
            return jsonify({
                'bot_response': "I need at least two potential outcomes to proceed. Please list all the possible outcomes of this decision, separated by commas."
            })
 
    # Node 5: Affect on each stakeholder
    if current_node == 5:
        # Collect stakeholders after outcomes have been listed
        stakeholders = [stakeholder.strip() for stakeholder in user_message.split(',')]

        if len(stakeholders) >= 2:  # Check if at least two stakeholders are provided
            current_node = 6  # Move to Node 6 to analyze the stakeholders
            return jsonify({
                'bot_response': f"Thank you for providing the stakeholders: {' and '.join(stakeholders)}. Let's proceed to analyze their impact."
            })
        else:
            return jsonify({
                'bot_response': "I need at least two stakeholders to continue. Please list all stakeholders affected by this decision, separated by commas."
            })
        
    # Node 6: Utility of outcomes
    if current_node == 6:
        outcomes_with_stakeholders = user_message.split(';')

        parsed_outcomes = []
        for outcome in outcomes_with_stakeholders:
            stakeholder_impact_pairs = outcome.split(',')
            
            stakeholders_with_impact = []
            for pair in stakeholder_impact_pairs:
                # Expecting format: "Stakeholder: impact" (e.g., "Friend: happy")
                if ':' in pair:
                    stakeholder, impact = pair.split(':')
                    stakeholders_with_impact.append((stakeholder.strip(), impact.strip()))
            
            if stakeholders_with_impact:
                parsed_outcomes.append(stakeholders_with_impact)

        # Check if outcomes are formatted correctly
        if all(len(stakeholders) >= 2 for stakeholders in parsed_outcomes):
            comparison_result = compare_outcomes(parsed_outcomes)
            current_node = 7
            return jsonify({

                'bot_response': (
                    "Thank you for providing the impacts. Here is the breakdown:\n" +
                    '\n'.join([
                        f"Outcome {i+1}: " + ', '.join([f"{stakeholder} (Impact: {impact})" for stakeholder, impact in stakeholders])
                        for i, stakeholders in enumerate(parsed_outcomes)
                    ]) +
                    f"\n\n{comparison_result}"+"\n\nWould you like to evaluate a different scenario"
                ),
                'parsed_outcomes': parsed_outcomes  # For utility calculation
            })
        else:
            return jsonify({
                'bot_response': "Each outcome should have at least two stakeholders with an impact score. Format each as 'Stakeholder: impact' (e.g., 'Friend: happy'). Separate outcomes with ';' and stakeholders within an outcome by ','."
            })

    # Node 7: If the harm outweighs the benefit, the chatbot suggests reconsidering the decision
    if current_node == 7:
        if user_message.lower() in ["yes", "sure", "yup"]:
            return jsonify({
                'bot_response': "Please provide a scenario or question you'd like help with."
            })

    # Node 8: If the benefit outweighs the harm, the chatbot supports the decision under Utilitarian principles
    if current_node == 8:
        return jsonify({
            'bot_response': "Based on the Utilitarian analysis, the benefit of this decision outweighs the harm. It seems ethical under Utilitarian principles."
        })

    # Node 9: Adherence to Moral Principles (Deontological Ethics)
    if current_node == 9:
        return jsonify({
            'bot_response': "Let’s evaluate this using the Deontology framework. Are there any moral duties or rules you must follow regardless of the outcome? (e.g., honesty, fairness, respect)"
        })

    # Node 10: Universalizability Test (Deontological Ethics)
    if current_node == 10:
        return jsonify({
            'bot_response': "Would it be acceptable if everyone facing this situation made the same decision? (i.e., firing employees to cut costs)."
        })

    # Node 11: If the action violates moral principles, the chatbot advises against it under Deontology
    if current_node == 11:
        return jsonify({
            'bot_response': "This action seems to violate moral principles such as fairness or honesty. Under Deontology, it would be unethical to proceed."
        })

    # Node 12: If the action upholds moral principles, the chatbot supports it
    if current_node == 12:
        return jsonify({
            'bot_response': "This action seems to uphold moral duties such as honesty and fairness. It appears ethical under Deontological principles."
        })

    # Node 13: Protecting Individual Rights (Rights-Based Ethics)
    if current_node == 13:
        return jsonify({
            'bot_response': "Now let’s consider Rights-Based Ethics. Does this decision respect the rights of all individuals involved? (e.g., employee rights to job security)."
        })

    # Node 14: Prioritizing Rights (Rights-Based Ethics)
    if current_node == 14:
        return jsonify({
            'bot_response': "Are some rights more important to protect in this scenario than others? (e.g., company rights vs. employee rights)."
        })

    # Node 15: If the decision violates individual rights, the chatbot advises reconsidering
    if current_node == 15:
        return jsonify({
            'bot_response': "This decision seems to violate individual rights. Under Rights-Based Ethics, you may need to reconsider this action."
        })

    # Node 16: If the decision respects individual rights, the chatbot supports the decision under Rights-Based Ethics
    if current_node == 16:
        return jsonify({
            'bot_response': "This decision respects individual rights, which aligns with Rights-Based Ethics. It seems ethical."
        })

    # Node 17: Synthesizing the Decision (Final Recommendation)
    if current_node == 17:
        return jsonify({
            'bot_response': "Based on Utilitarian principles, this decision maximizes benefits for the company but harms the employee. Under Deontological ethics, it may violate your duty to fairness. Additionally, under Rights-Based Ethics, this action compromises the employee’s rights. You might want to reconsider this action or find an alternative."
        })

    # Node 18: Final Decision (Recommend reconsideration or proceed)
    if current_node == 18:
        return jsonify({
            'bot_response': "I recommend that you reconsider the action, explore alternatives (such as offering severance or retraining), or proceed if you believe the benefits outweigh the moral concerns."
        })

    # Node 19: Logging the Decision
    if current_node == 19:
        # You can log the decision to a database or file for transparency
        # For simplicity, just return a confirmation message
        return jsonify({
            'bot_response': "Your decision has been logged for transparency. Thank you for using the ethical assistant."
        })


        

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
      
if __name__ == '__main__':
    app.run(debug=True)
"""  