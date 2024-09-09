import spacy

# Load the trained model
nlp = spacy.load("trained_models/nlp_model")

# Function to test the model
def test_model(text):
    doc = nlp(text)
    return doc.cats

# Test examples
test_texts = [
    "We need to consider the ethical implications of this decision.",
    "What is the best way to handle this situation?",
    "This decision might have significant ethical consequences."
]

# Print the results for each test text
for text in test_texts:
    print(f"Text: {text}")
    print(f"Categories: {test_model(text)}")
    print()
