import spacy

# Load a lightweight English model; fallback to a minimal one if unavailable.
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # If the model is not installed, warn and load a dummy pipeline that does nothing.
    nlp = spacy.blank("en")

def extract(text: str) -> list[tuple[str, str]]:
    """Extract (entity, label) pairs from the given text.
    Returns a list of tuples, e.g. [("Transformer", "ORG"), ("GPT", "PRODUCT")]"""
    doc = nlp(text)
    return [(ent.text, ent.label_) for ent in doc.ents]
