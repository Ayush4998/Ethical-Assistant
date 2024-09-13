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
