"""Experimental AI-text detector using a public Hugging Face classifier.

The selected detector was trained for GPT-2-era generated text. Its output is
not a calibrated probability and should not be treated as proof of authorship.
"""
import re
from functools import lru_cache

MODEL_NAME = "openai-community/roberta-base-openai-detector"


@lru_cache(maxsize=1)
def _load_classifier():
    try:
        from transformers import pipeline
    except ImportError as exc:
        raise RuntimeError(
            "AI detection dependencies are not installed. Run: pip install -r requirements-ai.txt"
        ) from exc
    try:
        return pipeline("text-classification", model=MODEL_NAME, tokenizer=MODEL_NAME)
    except Exception as exc:
        raise RuntimeError(
            "Could not load the AI detection model. Check your internet connection, then retry. "
            "The model is downloaded on first use and may require several hundred MB of storage."
        ) from exc


def _split_sentences(text):
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]


def _classify(text):
    classifier = _load_classifier()
    # Truncate conservatively to avoid model tokenizer limits.
    result = classifier(text[:5000], truncation=True, max_length=512)[0]
    label = str(result.get("label", "")).lower()
    score = float(result.get("score", 0.0))
    # This model labels generated samples as FAKE and human samples as REAL.
    if "fake" in label or label in {"label_0"}:
        predicted = "AI-like"
    elif "real" in label or label in {"label_1"}:
        predicted = "Human-like"
    else:
        predicted = "Unclear"
    return {"label": predicted, "model_label": result.get("label", "Unknown"),
            "model_score": round(score * 100, 1)}


def analyze_ai_text(text):
    if not text or not text.strip():
        raise ValueError("Enter some text to analyze.")
    if len(text) > 200_000:
        raise ValueError("Text limit is 200,000 characters.")
    overall = _classify(text)
    sentences = _split_sentences(text)
    sentence_results = []
    # Sentence scores are exploratory and only calculated for sufficiently substantial passages.
    if len(sentences) > 1:
        for sentence in sentences[:30]:
            if len(sentence.split()) >= 8:
                sentence_results.append({"text": sentence, **_classify(sentence)})
    return {"overall": overall, "sentences": sentence_results,
            "word_count": len(text.split()), "model_name": MODEL_NAME}
