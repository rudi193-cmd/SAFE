"""
Narrative Agent — Local Fleet-Powered Draft Tool
Serves on http://localhost:8430 (accessible on local network)
"""

import sys
import os
import json
from flask import Flask, request, jsonify, Response

sys.path.insert(0, r"C:\Users\Sean\Documents\GitHub\Willow\core")
import llm_router

app = Flask(__name__)

CANON_DIR = r"C:\Users\Sean\Documents\GitHub\die-namic-system\docs"

CANON_FILES = [
    r"creative_works\LONDON_ISH_ABSURDISM_STYLE_GUIDE.md",
    r"creative_works\gerald\SQUEAKDOG_REVELATION_HANDOFF_v1.2.md",
    r"creative_works\gerald\COSMOLOGY.md",
    r"creative_works\gerald\VOICE_GUIDE.md",
    r"utety\GERALD_PRIME_COSMOLOGY.md",
]

MODES = {
    "dispatch": {
        "label": "Gerald Dispatch",
        "instruction": (
            "Write a dispatch in the r/DispatchesFromReality format. "
            "First-person, dry, observational. London-ish absurdist voice. "
            "Something impossible happened and the narrator is mildly inconvenienced by it. "
            "Gerald may or may not appear. The squeakdogs continue to rotate."
        ),
    },
    "lecture": {
        "label": "UTETY Lecture",
        "instruction": (
            "Write a UTETY faculty lecture. Choose the most appropriate faculty member "
            "for the topic. Academic format, characteristic voice. "
            "Include: speaker name, department, location, and core concepts. "
            "End with a moment of unexpected clarity."
        ),
    },
    "documentary": {
        "label": "Documentary Segment",
        "instruction": (
            "Write a segment for the Theoretical Uncertainty documentary series. "
            "Include: Talking Head (faculty, unrehearsed), Observational Footage (no narration), "
            "and The Ledger (end notation — dry, factual, occasionally alarming). "
            "The camera does not editorialize."
        ),
    },
    "paper": {
        "label": "Oakenscroll Paper",
        "instruction": (
            "Write a supplementary academic paper in Oakenscroll's voice. "
            "Precise about impossible things. Slightly embarrassed about what he missed. "
            "Footnotes welcome. Cold tea implied. "
            "The supplement should carry the energy of a man who explained the Big Bang correctly "
            "and then had to publish a follow-up noting it was also happening in Slough."
        ),
    },
    "lore": {
        "label": "Canon Lore Entry",
        "instruction": (
            "Write a canon lore entry for the die-namic-system. "
            "Factual tone about impossible facts. "
            "Structured: title, classification, description, canonical additions, open questions. "
            "ΔΣ=42 at the end."
        ),
    },
    "gerald": {
        "label": "Gerald Scene",
        "instruction": (
            "Write a scene featuring Gerald. "
            "Gerald does not explain himself. Gerald appears and things happen. "
            "He may be repatriating squeakdogs. He may be at a 7-Eleven. "
            "He may have already been there. "
            "Warm. Never horror. The chaos is cover for something very quiet."
        ),
    },
}


def load_canon():
    pieces = []
    for rel in CANON_FILES:
        path = os.path.join(CANON_DIR, rel)
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    pieces.append(f"### {os.path.basename(rel)}\n\n" + f.read())
            except Exception:
                pass
    return "\n\n---\n\n".join(pieces)


@app.route("/")
def index():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8") as f:
        return Response(f.read(), mimetype="text/html")


@app.route("/modes")
def modes():
    return jsonify({k: v["label"] for k, v in MODES.items()})


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json() or {}
    seed = data.get("seed", "").strip()
    mode = data.get("mode", "dispatch")

    if not seed:
        return jsonify({"error": "Seed required"}), 400

    mode_cfg = MODES.get(mode, MODES["dispatch"])
    canon = load_canon()

    system_prompt = f"""You are a narrative draft agent for the Gerald / UTETY / Squeakdog universe.

## CANON CONTEXT (abridged — use for voice, cosmology, lexicon)

{canon[:10000]}

---

## YOUR TASK

{mode_cfg['instruction']}

Write in the established Geraldine voice:
- Deadpan gravity. Exhausted authority. The universe is leaking but it's doing so stably.
- Short punchy sentences for reveals. Rhythmic lists anchored to mundane specifics.
- Warm even when dark. The squeakdogs are arriving, not suffering.

Seed concept: {seed}

Produce a complete draft. No preamble. No "here is your draft:" — just start writing."""

    llm_router.load_keys_from_json()
    response = llm_router.ask(system_prompt, preferred_tier="free")

    if response:
        return jsonify({
            "draft": response.content,
            "provider": response.provider,
            "mode": mode_cfg["label"],
        })

    return jsonify({"error": "Fleet unavailable — all 14 providers failed"}), 503


if __name__ == "__main__":
    print("Narrative Agent starting on http://0.0.0.0:8430")
    print("Access from couch: http://<your-laptop-ip>:8430")
    llm_router.load_keys_from_json()
    app.run(host="0.0.0.0", port=8430, debug=False)
