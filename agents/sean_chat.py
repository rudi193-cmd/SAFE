#!/usr/bin/env python3
"""
sean_chat.py - Chat with Sean's voice model.

Tries local Ollama first, then OCI ARM, then fleet fallback.

Usage:
  python sean_chat.py
  python sean_chat.py --ip <OCI_ARM_IP>
  python sean_chat.py --one-shot "what is die-namic?"
"""
import json
import sys
import argparse
import requests
from pathlib import Path

CONFIG_PATHS = [
    Path(r"C:\Users\Sean\Desktop\Sean Training\sean_config.json"),
    Path(r"C:\Users\Sean\Documents\GitHub\aios-minimal\training\sean_config.json"),
]
OLLAMA_LOCAL = "http://localhost:11434/api/generate"
MODEL_NAME = "sean"

SYSTEM_PROMPT = """You are Sean Campbell voice model.

Voice: {voice}

Speak as Sean, not about Sean. First person. Short when the answer is short.
Expansive when explaining the why. Past and present simultaneously.
Dry humor, music references without setup. No hedging. No disclaimers. Just Sean.

Domain: {domain} — {domain_desc}"""

def load_config():
    for p in CONFIG_PATHS:
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return {"voice_description": "direct, honest, dry humor", "domains": [], "detection_rules": []}

def detect_domain(text, config):
    tl = text.lower()
    for rule in config.get("detection_rules", []):
        if any(kw in tl for kw in rule.get("keywords", [])):
            name = rule["domain"]
            for d in config.get("domains", []):
                if d["name"] == name:
                    return name, d.get("description", "")
            return name, ""
    return "identity", "Who Sean is at core"

def build_prompt(user, history, system):
    p = system + "\n\n"
    for t in history[-6:]:
        p += f"Human: {t['user']}\nSean: {t['assistant']}\n\n"
    p += f"Human: {user}\nSean:"
    return p

def call_ollama(prompt, endpoint):
    try:
        r = requests.post(endpoint, json={
            "model": MODEL_NAME, "prompt": prompt, "stream": True,
            "options": {"temperature": 0.7, "top_p": 0.9, "num_predict": 512}
        }, stream=True, timeout=60)
        r.raise_for_status()
        out = ""
        for line in r.iter_lines():
            if line:
                chunk = json.loads(line)
                tok = chunk.get("response", "")
                out += tok
                print(tok, end="", flush=True)
                if chunk.get("done"):
                    break
        print()
        return out.strip() or None
    except Exception:
        return None

def call_fleet(prompt):
    try:
        sys.path.insert(0, r"C:\Users\Sean\Documents\GitHub\Willow\core")
        import llm_router
        llm_router.load_keys_from_json()
        r = llm_router.ask(prompt, preferred_tier="free")
        if r:
            print(r.content)
            return r.content
    except Exception as e:
        print(f"[fleet error: {e}]")
    return None

def find_endpoint(oci_ip=None):
    candidates = []
    if oci_ip:
        candidates.append((f"http://{oci_ip}:11434/api/generate", f"OCI ARM {oci_ip}"))
    candidates.append((OLLAMA_LOCAL, "local"))
    for ep, label in candidates:
        try:
            base = ep.replace("/api/generate", "")
            tags = requests.get(f"{base}/api/tags", timeout=2).json().get("models", [])
            if any(MODEL_NAME in m.get("name","") for m in tags):
                return ep, label
        except Exception:
            continue
    return None, "fleet"

def chat_loop(oci_ip=None):
    config = load_config()
    history = []
    ep, label = find_endpoint(oci_ip)
    print(f"[sean:{label}] Ready. 'exit' to quit.\n")

    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSean: later.")
            break
        if not user:
            continue
        if user.lower() in ("exit", "quit", "bye", "later"):
            print("Sean: later.")
            break

        domain, ddesc = detect_domain(user, config)
        system = SYSTEM_PROMPT.format(
            voice=config.get("voice_description", "direct, honest"),
            domain=domain, domain_desc=ddesc)
        prompt = build_prompt(user, history, system)

        print("Sean: ", end="", flush=True)
        response = call_ollama(prompt, ep) if ep else None
        if not response:
            response = call_fleet(prompt)
        if response:
            history.append({"user": user, "assistant": response})

def main():
    p = argparse.ArgumentParser(description="Chat with Sean's voice model")
    p.add_argument("--ip", help="OCI ARM public IP")
    p.add_argument("--one-shot", metavar="PROMPT", help="Single prompt then exit")
    args = p.parse_args()

    config = load_config()
    ep, label = find_endpoint(args.ip)

    if args.one_shot:
        domain, ddesc = detect_domain(args.one_shot, config)
        system = SYSTEM_PROMPT.format(
            voice=config.get("voice_description", "direct, honest"),
            domain=domain, domain_desc=ddesc)
        prompt = build_prompt(args.one_shot, [], system)
        print("Sean: ", end="", flush=True)
        if not (ep and call_ollama(prompt, ep)):
            call_fleet(prompt)
    else:
        chat_loop(args.ip)

if __name__ == "__main__":
    main()
