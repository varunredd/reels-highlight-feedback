import re
from math import exp

# Tweak these lists/weights as you like
STRONG_KWS = {
    "secret", "important", "tip", "trick", "hack",
    "listen", "never", "always", "must", "mistake",
    "warning", "lesson", "key", "rule", "best",
    "proof", "fact", "data", "example", "story"
}

def _tokenize(text: str):
    return re.findall(r"[A-Za-z0-9']+", text.lower())

def score_text(text: str) -> float:
    """
    Returns a 0..1 'highlightness' pseudo-label for a text window.
    Uses cheap signals: keywords, punctuation, length sweet-spot, lexical variety.
    """
    t = text.strip()
    if not t:
        return 0.0

    toks = _tokenize(t)
    n = len(toks)
    uniq = len(set(toks)) or 1

    # keyword hit rate
    kw_hits = sum(1 for w in toks if w in STRONG_KWS)
    kw_score = min(1.0, kw_hits / 3.0)

    # punctuation hooks
    punct = 0.0
    if "?" in t: punct += 0.35
    if "!" in t: punct += 0.35
    punct = min(1.0, punct)

    # length sweet spot (roughly 20–110 tokens)
    # gaussian-ish bell around ~60 tokens
    center, width = 60.0, 35.0
    len_score = exp(-((n - center) ** 2) / (2 * width ** 2))

    # lexical variety
    variety = min(1.0, uniq / (n + 1e-6))

    # combine
    score = 0.45 * len_score + 0.30 * kw_score + 0.15 * punct + 0.10 * variety
    # clamp
    return max(0.0, min(1.0, score))
