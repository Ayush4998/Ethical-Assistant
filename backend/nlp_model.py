import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding
import random
import os

# Initialize the NLP model
nlp = spacy.blank("en")

# Add the text categorizer to the pipeline if it doesn't exist
if "textcat" not in nlp.pipe_names:
    textcat = nlp.add_pipe("textcat", last=True)
else:
    textcat = nlp.get_pipe("textcat")

# Add labels to the text classifier
textcat.add_label("ETHICS")
textcat.add_label("NOT_ETHICS")

# Training data: each tuple contains the text and the corresponding label
train_data = [
    ("It's unethical to harm others for personal gain.", {"cats": {"ETHICS": 1.0, "NOT_ETHICS": 0.0}}),
    ("The company's decision benefits the majority of employees.", {"cats": {"ETHICS": 1.0, "NOT_ETHICS": 0.0}}),
    ("I am going to the store to buy groceries.", {"cats": {"ETHICS": 0.0, "NOT_ETHICS": 1.0}}),
    ("We should focus on long-term consequences of this policy.", {"cats": {"ETHICS": 1.0, "NOT_ETHICS": 0.0}}),
    ("Let's schedule a meeting next week.", {"cats": {"ETHICS": 0.0, "NOT_ETHICS": 1.0}})
    # Add more examples as necessary
]

# Function to train the model
def train_nlp_model():
    # Initialize the model's optimizer
    optimizer = nlp.begin_training()

    # Training loop
    for epoch in range(10):  # Adjust number of epochs as necessary
        losses = {}
        random.shuffle(train_data)
        batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))

        for batch in batches:
            for text, annotations in batch:
                doc = nlp.make_doc(text)
                example = Example.from_dict(doc, annotations)
                nlp.update([example], sgd=optimizer, losses=losses)

        print(f"Epoch {epoch + 1} completed. Losses: {losses}")

    # Save the trained model to disk
    model_dir = "trained_models"
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    nlp.to_disk(os.path.join(model_dir, "nlp_model"))
    print(f"Model saved to {os.path.join(model_dir, 'nlp_model')}")

if __name__ == "__main__":
    train_nlp_model()

import random
import os

# Create a new SpaCy model
nlp = spacy.blank("en")

# Add text categorizer to the pipeline
text_cat = nlp.add_pipe("textcat", last=True)

# Define labels
text_cat.add_label("ETHICAL")
text_cat.add_label("GENERAL")

# Training data (list of (text, label) tuples)
train_data = [
    ("We need to consider the ethical implications of this decision.", {"cats": {"ETHICAL": 1, "GENERAL": 0}}),
    ("What is the best way to handle this situation?", {"cats": {"ETHICAL": 0, "GENERAL": 1}}),
    ("This decision might have significant ethical consequences.", {"cats": {"ETHICAL": 1, "GENERAL": 0}}),
    # Add more training examples here
]

# Convert training data to SpaCy's format
def create_examples(data):
    examples = []
    for text, annotations in data:
        doc = nlp.make_doc(text)
        example = Example.from_dict(doc, annotations)
        examples.append(example)
    return examples

# Train the model
def train_model(nlp, train_data):
    # Initialize optimizer
    optimizer = nlp.begin_training()
    # Training loop
    for epoch in range(10):  # Number of epochs
        random.shuffle(train_data)
        losses = {}
        # Create a minibatch
        examples = create_examples(train_data)
        minibatch = spacy.util.minibatch(examples, size=2)
        for batch in minibatch:
            # Update model with batch of Example objects
            nlp.update(batch, drop=0.5, losses=losses)
        print(f"Epoch {epoch}: {losses}")

import os


def save_model(nlp, model_path):
    # Ensure the directory exists
    try:
        if not os.path.exists(model_path):
            os.makedirs(model_path)
        nlp.to_disk(model_path)
        print(f"Model saved to {model_path}")
    except Exception as e:
        print(f"An error occurred while saving the model: {e}")

# Main function to run the training and saving
if __name__ == "__main__":
    train_model(nlp, train_data)
    save_model(nlp, "trained_models/nlp_model")
