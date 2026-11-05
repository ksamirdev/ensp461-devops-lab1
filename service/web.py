"""Text statistics web service deployed by the ENSP461 Lab 1 pipeline."""
import os

from flask import Flask, jsonify, request

RELEASE = os.environ.get("RELEASE", "1.1.0")
app = Flask(__name__)


def text_stats(text):
    words = text.split()
    return {
        "characters": len(text),
        "words": len(words),
        "unique_words": len({w.lower() for w in words}),
    }


@app.get("/")
def home():
    return jsonify(service="text-stats", release=RELEASE)


@app.get("/healthz")
def healthz():
    return jsonify(healthy=True, release=RELEASE)


@app.post("/stats")
def stats():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text")
    if not isinstance(text, str):
        return jsonify(error="JSON field 'text' must be a string"), 400
    return jsonify(text_stats(text))
