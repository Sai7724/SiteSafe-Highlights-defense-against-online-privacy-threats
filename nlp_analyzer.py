from transformers import pipeline

# Zero-shot classification pipeline (no training needed)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def ai_privacy_analysis(text):
    """
    Analyze privacy policy text using AI.
    Returns label (Safe/Moderate/High Risk) and confidence score.
    """
    candidate_labels = ["safe", "moderate risk", "high risk"]
    result = classifier(text, candidate_labels)

    label = result["labels"][0]
    score = round(result["scores"][0] * 100, 2)

    return label, score
