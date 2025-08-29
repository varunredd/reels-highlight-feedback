"""
Text utilities (NLP scoring, embeddings)
"""

from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_text_embedding(text: str):
    return model.encode(text, convert_to_tensor=True)
