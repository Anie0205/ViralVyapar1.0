from transformers import pipeline

intent_classifier = pipeline("text-classification", model="distilbert-base-uncased")

def classify_intent(text):
    result = intent_classifier(text)[0]
    return result['label']
