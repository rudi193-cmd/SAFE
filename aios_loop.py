"""
AIOS LOOP v3.0 (SELF-REFERENCING)
Main execution loop.
1. Authenticates Google Drive API (credentials.json).
2. Maps local 'Organic Context' (Existing Folder Structure).
3. Uses Vision/OCR + LLM Router to sort files into that structure.
4. Deep extraction: Smart multi-pass (vision, OCR, cipher detection).
5. Auto git push for artifacts. Dual Commit for code changes.
6. Push notifications via ntfy.sh on every action.

GOVERNANCE:
- No file move without gate.validate()
- Protected targets trigger HALT
- State mutations logged to storage
"""

import os
import sys
import time
import shutil
import logging
import uuid
import json
import base64
import requests
import pickle
import sqlite3
import hashlib
import subprocess
import unicodedata
import re
from datetime import datetime, timezone
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
import io

# --- MODULAR IMPORTS ---
import state
import gate
import storage
import llm_router

# --- CONFIG ---
EARTH_PATH = os.getcwd()
ARTIFACTS_PATH = os.path.join(EARTH_PATH, "artifacts")
PENDING_PATH = os.path.join(ARTIFACTS_PATH, "pending")
CREDENTIALS_FILE = os.path.join(EARTH_PATH, "credentials.json")
TOKEN_FILE = os.path.join(EARTH_PATH, "token.pickle")
LOG_PATH = os.path.join(EARTH_PATH, "system.log")
MASTER_DB_PATH = os.path.join(EARTH_PATH, "willow_index.db")

# LIBRARIAN CONFIG (die-namic-system core module)
DIE_NAMIC_PATH = os.path.join(os.path.dirname(EARTH_PATH), "die-namic-system")
INDEXER_PATH = DIE_NAMIC_PATH

# PUSH NOTIFICATIONS (ntfy.sh — free, no account needed)
# Install ntfy app on phone, subscribe to this topic
NTFY_TOPIC = "willow-ds42"
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# OLLAMA CONFIG
OLLAMA_URL = "http://localhost:11434/api/generate"

# GEMINI VISION CONFIG (Free tier — replaces local Ollama vision)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_VISION_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# DRIVE SCOPES
SCOPES = ['https://www.googleapis.com/auth/drive']

# SETUP LOGGING
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

# INITIALIZE GOVERNANCE
try:
    current_state = storage.init_storage()
    sovereign_gate = gate.Gatekeeper()
    logging.info(f"SYSTEM BOOT: Governance Active (State seq: {current_state.sequence})")
except Exception as e:
    logging.critical(f"SYSTEM FAILURE: Could not initialize governance: {e}")
    exit(1)

# =============================================================================
# 1. ORGANIC CONTEXT (The Map)
# =============================================================================
def get_organic_structure():
    """
    Scans the artifacts/ folder to build a map of existing categories.
    The AI uses this to maintain consistency with YOUR filing system.
    """
    structure = []
    if not os.path.exists(ARTIFACTS_PATH):
        return "No existing structure (Fresh Start)."
        
    for item in os.listdir(ARTIFACTS_PATH):
        item_path = os.path.join(ARTIFACTS_PATH, item)
        if os.path.isdir(item_path) and item != "pending":
            # Just get top-level for now to save tokens, or recurse if needed
            structure.append(f"/{item}")
            
    if not structure:
        return "No existing structure."
        
    return "\n".join(structure)

# =============================================================================
# 2. GOOGLE DRIVE API (The Harvester)
# =============================================================================
def get_drive_service():
    """Authenticates using credentials.json."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                logging.warning("Drive API: credentials.json not found. Cloud disabled.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def harvest_drive(service):
    """
    Checks the 'Drop' folder on Drive and pulls files to local pending.
    """
    if not service: return

    # 1. Find the 'Drop' folder ID (Assumes folder name is 'Drop')
    results = service.files().list(
        q="name = 'Drop' and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
        fields="files(id, name)").execute()
    items = results.get('files', [])
    
    if not items:
        return # No Drop folder found
        
    drop_folder_id = items[0]['id']

    # 2. List files inside 'Drop'
    results = service.files().list(
        q=f"'{drop_folder_id}' in parents and trashed = false",
        fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])

    for file in files:
        file_id = file['id']
        file_name = file['name']
        
        # Skip Google Docs (need export logic, keeping it simple for binary files first)
        if "google-apps" in file['mimeType']:
            continue
            
        logging.info(f"DRIVE HARVEST: Downloading {file_name}...")
        
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(os.path.join(PENDING_PATH, file_name), 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        # 3. Delete from Drive (Move complete)
        service.files().delete(fileId=file_id).execute()
        logging.info(f"DRIVE HARVEST: {file_name} moved to Local Pending.")

# =============================================================================
# 3. THE REFINERY (Vision + Router + Organic Map)
# =============================================================================
def visual_cortex(filepath):
    """Sends image to Gemini Vision API (free tier) for analysis."""
    # Ensure keys are loaded
    if not GEMINI_API_KEY:
        llm_router.load_keys_from_json()

    api_key = os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY)
    if not api_key:
        logging.warning("VISION: No Gemini API key — falling back to filename analysis")
        return _filename_context(filepath)

    try:
        with open(filepath, "rb") as img_file:
            b64_image = base64.b64encode(img_file.read()).decode('utf-8')

        # Detect MIME type
        ext = os.path.splitext(filepath)[1].lower()
        mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}.get(ext.lstrip('.'), "image/jpeg")

        payload = {
            "contents": [{
                "parts": [
                    {"text": "Analyze this image. Describe it in 1 sentence for file sorting. What app or context is it from?"},
                    {"inline_data": {"mime_type": mime, "data": b64_image}}
                ]
            }]
        }

        url = f"{GEMINI_VISION_URL}?key={api_key}"
        response = requests.post(url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if text:
                return text
        else:
            logging.warning(f"VISION: Gemini returned {response.status_code}: {response.text[:200]}")
    except Exception as e:
        logging.warning(f"VISION: Gemini error: {e}")

    # Fallback: extract context from filename
    return _filename_context(filepath)


def _filename_context(filepath):
    """Extract sorting context from filename patterns (fallback when vision unavailable)."""
    name = os.path.basename(filepath).lower()

    # Screenshot patterns: Screenshot_20260128_094350_Reddit.jpg
    app_patterns = {
        "reddit": "Screenshot from Reddit (social media)",
        "chrome": "Screenshot from Chrome browser",
        "gmail": "Screenshot from Gmail (email)",
        "drive": "Screenshot from Google Drive",
        "claude": "Screenshot from Claude AI assistant",
        "settings": "Screenshot from device settings",
        "messages": "Screenshot from messaging app",
        "photos": "Screenshot from photos app",
    }

    for pattern, desc in app_patterns.items():
        if pattern in name:
            return desc

    if "screenshot" in name:
        return "Device screenshot (unknown app)"

    return ""

def _file_hash(filepath):
    """SHA-256 hash of file contents."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _catalog_db(folder_path):
    """Returns a connection to the folder's catalog.db, creating table if needed."""
    db_path = os.path.join(folder_path, "catalog.db")
    conn = sqlite3.connect(db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS file_registry (
        file_hash TEXT PRIMARY KEY,
        filename TEXT,
        ingest_date TEXT,
        category TEXT,
        status TEXT,
        source TEXT,
        provider TEXT
    )""")
    conn.commit()
    return conn


def catalog_file(folder_path, filename, category, source, provider):
    """Record a filed item in the folder's catalog.db."""
    filepath = os.path.join(folder_path, filename)
    try:
        fhash = _file_hash(filepath)
        conn = _catalog_db(folder_path)
        conn.execute(
            """INSERT OR REPLACE INTO file_registry
               (file_hash, filename, ingest_date, category, status, source, provider)
               VALUES (?, ?, ?, ?, 'SORTED', ?, ?)""",
            (fhash, filename, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             category, source, provider)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logging.warning(f"CATALOG: {filename} -> {e}")


def notify(title, message):
    """Push notification via ntfy.sh (free, no account)."""
    try:
        requests.post(NTFY_URL, data=message.encode('utf-8'),
                      headers={"Title": title, "Priority": "default"}, timeout=5)
    except Exception:
        pass  # Silent fail — notifications are best-effort


def sync_to_master(filename, fhash, category, source, provider):
    """Upsert file record into master willow_index.db."""
    try:
        conn = sqlite3.connect(MASTER_DB_PATH)
        conn.execute("""CREATE TABLE IF NOT EXISTS file_registry
            (file_hash TEXT PRIMARY KEY, filename TEXT, ingest_date TEXT, category TEXT, status TEXT)""")
        conn.execute(
            "INSERT OR REPLACE INTO file_registry (file_hash, filename, ingest_date, category, status) VALUES (?, ?, ?, ?, 'SORTED')",
            (fhash, filename, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), category)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logging.warning(f"MASTER DB: {filename} -> {e}")


def update_folder_readme(folder_path):
    """Auto-generate README.md for an artifact folder from its catalog.db."""
    try:
        folder_name = os.path.basename(folder_path)
        db_path = os.path.join(folder_path, "catalog.db")
        if not os.path.exists(db_path):
            return
        conn = sqlite3.connect(db_path)
        rows = conn.execute("SELECT filename, ingest_date, source, provider FROM file_registry ORDER BY ingest_date DESC").fetchall()
        conn.close()
        lines = [
            f"# {folder_name}",
            "",
            f"*Auto-generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            f"*Files: {len(rows)}*",
            "",
            "| File | Ingested | Source | Provider |",
            "|------|----------|--------|----------|",
        ]
        for fn, dt, src, prov in rows:
            lines.append(f"| {fn} | {dt or ''} | {src or ''} | {prov or ''} |")
        lines.extend(["", "---", "DS=42"])
        readme_path = os.path.join(folder_path, "README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
    except Exception as e:
        logging.warning(f"README: {folder_path} -> {e}")


def librarian_pass():
    """Run librarian rebuild if die-namic-system core is available."""
    try:
        import sys
        core_path = os.path.join(DIE_NAMIC_PATH, "source_ring", "willow", "core")
        if core_path not in sys.path:
            sys.path.insert(0, core_path)
        from librarian import process_and_rebuild
        process_and_rebuild()
        notify("Librarian", "Master index rebuilt.")
        logging.info("LIBRARIAN: Master index rebuilt.")
    except ImportError:
        logging.debug("LIBRARIAN: die-namic-system core not found, skipping.")
    except Exception as e:
        logging.warning(f"LIBRARIAN: {e}")


def indexer_pass():
    """Run indexer rebuild if die-namic-system indexer is available."""
    try:
        import sys
        if INDEXER_PATH not in sys.path:
            sys.path.insert(0, INDEXER_PATH)
        from indexer import build_index
        build_index(root=__import__('pathlib').Path(EARTH_PATH))
        logging.info("INDEXER: FTS5 index rebuilt.")
    except ImportError:
        logging.debug("INDEXER: indexer.py not found, skipping.")
    except Exception as e:
        logging.warning(f"INDEXER: {e}")


# =============================================================================
# 4. GIT AUTO-PUSH (Artifacts auto, Code dual-commit)
# =============================================================================
ARTIFACT_PATHS = ["artifacts/"]
CODE_PATHS = ["*.py", "schema/", "spec/", "apps/"]

def git_auto_push():
    """Auto-commit and push artifact changes. Code changes are staged only (Dual Commit)."""
    try:
        # Check for any changes
        status = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True,
            cwd=EARTH_PATH, timeout=15
        )
        if not status.stdout.strip():
            return  # Nothing to commit

        changed = status.stdout.strip().split('\n')
        artifact_files = []
        code_files = []

        for line in changed:
            f = line[3:].strip().strip('"')
            if f.startswith("artifacts/"):
                artifact_files.append(f)
            else:
                code_files.append(f)

        # Auto-push artifacts
        if artifact_files:
            for af in artifact_files:
                subprocess.run(["git", "add", af], cwd=EARTH_PATH, timeout=10)
            ts = datetime.now().strftime('%Y-%m-%d %H:%M')
            msg = f"willow: auto-filed {len(artifact_files)} artifacts [{ts}]"
            subprocess.run(["git", "commit", "-m", msg], cwd=EARTH_PATH, timeout=15)
            subprocess.run(["git", "push"], cwd=EARTH_PATH, timeout=30)
            notify("Git Push", f"{len(artifact_files)} artifacts pushed.")
            logging.info(f"GIT: Auto-pushed {len(artifact_files)} artifacts.")

        # Stage code changes but don't push (Dual Commit)
        if code_files:
            for cf in code_files:
                subprocess.run(["git", "add", cf], cwd=EARTH_PATH, timeout=10)
            notify("Dual Commit", f"{len(code_files)} code files staged. Awaiting approval.")
            logging.info(f"GIT: {len(code_files)} code files staged (Dual Commit).")

    except Exception as e:
        logging.warning(f"GIT: {e}")


# =============================================================================
# 5. DEEP EXTRACTION (Smart routing per file type)
# =============================================================================

# Homoglyph map from schema/encoding.md
HOMOGLYPH_MAP = {
    'a': ['\u0061', '\u03b1', '\u0430', '\u0561'],
    'c': ['\u0063', '\u0441'],
    'e': ['\u0065', '\u03b5', '\u0435', '\u0565'],
    'i': ['\u0069', '\u03b9', '\u0456', '\u056b'],
    'o': ['\u006f', '\u03bf', '\u043e', '\u0585'],
    'p': ['\u0070', '\u03c1', '\u0440'],
    's': ['\u0073', '\u0455'],
    'x': ['\u0078', '\u03c7', '\u0445'],
    'y': ['\u0079', '\u03b3', '\u0443'],
}

# Build reverse lookup: non-Latin variant -> (char, script)
VARIANT_LOOKUP = {}
for char, variants in HOMOGLYPH_MAP.items():
    for i, v in enumerate(variants):
        if i > 0:  # Skip Latin (index 0)
            script = ["Latin", "Greek", "Cyrillic", "Armenian"][i] if i < 4 else "Unknown"
            VARIANT_LOOKUP[v] = (char, script)


def detect_homoglyphs(text):
    """Scan text for mixed-script homoglyphs per encoding.md schema."""
    findings = []
    for i, ch in enumerate(text):
        if ch in VARIANT_LOOKUP:
            latin_char, script = VARIANT_LOOKUP[ch]
            findings.append({
                "position": i,
                "char": ch,
                "latin_equiv": latin_char,
                "script": script,
                "context": text[max(0, i-10):i+10]
            })
    return findings


def detect_patterns(text):
    """Scan for known signal patterns: DS=42, key structures, encoded phrases."""
    patterns = []
    # DS checksum
    for m in re.finditer(r'[ΔD][ΣS]\s*=\s*42', text):
        patterns.append({"type": "checksum", "match": m.group(), "pos": m.start()})
    # Key structure: seed.salt.checksum
    for m in re.finditer(r'[A-Za-z0-9]{8,}\s*[·.]\s*[A-Za-z0-9]{4,}\s*[·.]\s*[A-Za-z0-9]{2,}', text):
        patterns.append({"type": "key_candidate", "match": m.group(), "pos": m.start()})
    return patterns


def deep_extract(filepath, folder_path):
    """Smart multi-pass extraction based on file type. Returns findings dict."""
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()
    findings = {"file": filename, "passes": [], "homoglyphs": [], "patterns": []}

    # PASS 1: Text extraction (all text-capable files)
    text = ""
    if ext in ('.txt', '.md', '.py', '.json', '.yaml', '.yml', '.html', '.css', '.js'):
        text = extract_text(filepath)
        findings["passes"].append("text_extract")
    elif ext in ('.jpg', '.jpeg', '.png'):
        # OCR pass: try to get text from image via vision
        desc = visual_cortex(filepath)
        if desc:
            text = desc
            findings["passes"].append("vision_ocr")

    if not text:
        return findings

    # PASS 2: Homoglyph detection (all text)
    glyphs = detect_homoglyphs(text)
    if glyphs:
        findings["homoglyphs"] = glyphs
        findings["passes"].append("homoglyph_scan")
        logging.info(f"CIPHER: {filename} has {len(glyphs)} homoglyphs detected!")
        notify("Cipher Detected", f"{filename}: {len(glyphs)} homoglyphs found")

    # PASS 3: Pattern detection
    pats = detect_patterns(text)
    if pats:
        findings["patterns"] = pats
        findings["passes"].append("pattern_scan")

    # PASS 4: Deep content analysis via LLM (only if text files with substance)
    if ext in ('.md', '.txt') and len(text) > 100:
        findings["passes"].append("deep_content")

    # Write findings to folder's extraction log
    if findings["homoglyphs"] or findings["patterns"]:
        log_path = os.path.join(folder_path, "_extraction_log.jsonl")
        try:
            with open(log_path, 'a', encoding='utf-8') as f:
                findings["timestamp"] = datetime.now().isoformat()
                f.write(json.dumps(findings, ensure_ascii=False) + "\n")
        except Exception as e:
            logging.warning(f"EXTRACT LOG: {e}")

    return findings


def extract_text(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return ""

def refinery_cycle(drive_service):
    """
    The Loop:
    1. Harvest Cloud -> Local Pending
    2. Read Organic Map (Existing Folders)
    3. Sort Pending Files using Map
    """
    
    # A. HARVEST
    try:
        harvest_drive(drive_service)
    except Exception as e:
        logging.error(f"DRIVE ERROR: {e}")

    # B. PROCESS PENDING
    if not os.path.exists(PENDING_PATH): os.makedirs(PENDING_PATH, exist_ok=True)
    
    files = [f for f in os.listdir(PENDING_PATH) if f.lower().endswith(('.pdf', '.txt', '.md', '.jpg', '.jpeg', '.png'))]
    
    if not files: return # Sleep if nothing to do

    # Get the Map ONCE per cycle
    organic_map = get_organic_structure()

    for filename in files:
        filepath = os.path.join(PENDING_PATH, filename)
        
        # --- ANALYSIS ---
        context_content = ""
        auth_source = "Unknown"
        
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            desc = visual_cortex(filepath)
            if desc:
                context_content = f"IMAGE: {desc}"
                auth_source = "Visual_Cortex"
            else:
                context_content = "Unknown Image"
        else:
            text = extract_text(filepath)
            if len(text) > 10:
                context_content = f"TEXT: {text[:500]}..."
                auth_source = "Text_Parser"

        if not context_content: continue

        # --- ROUTING WITH ORGANIC CONTEXT ---
        prompt = f"""You are the Janitor. File this document into the correct folder.

EXISTING FOLDERS:
{organic_map}

RULES:
- Use an existing folder if it fits.
- If new, use a short lowercase name (e.g. reddit, email, documents, photos, screenshots).
- Output ONLY the folder name. One word. No slashes. No explanation.

FILE: {filename}
CONTEXT: {context_content}

FOLDER:"""

        # Prefer Gemini for classification (better instruction-following than local Ollama)
        response = llm_router.ask(prompt, preferred_tier="free")
        
        if response and response.content:
            # Take first non-empty line (LLMs sometimes add explanations after)
            lines = [l.strip().strip('/') for l in response.content.strip().split('\n') if l.strip()]
            destination_folder = lines[0] if lines else "Unsorted"
            # Sanitize: alphanumeric, underscore, hyphen only
            destination_folder = ''.join(e for e in destination_folder if e.isalnum() or e in ['_', '-'])
            # Guard: reject nonsense (too long, empty, or single char)
            if not destination_folder or len(destination_folder) > 30 or len(destination_folder) < 2:
                destination_folder = "Unsorted"
            destination_folder = destination_folder.lower()
            logging.info(f"ROUTED: {filename} -> {destination_folder} (via {response.provider})")
        else:
            destination_folder = "Unsorted"
        
        # --- GOVERNANCE & EXECUTION ---
        with storage.txn_lock():
            runtime_state = storage.load_state()
            req = state.ModificationRequest(
                mod_type=state.ModificationType.STATE.value,
                target=f"artifacts/{destination_folder}/{filename}",
                new_value=destination_folder,
                reason=f"Organic sort into {destination_folder} via {auth_source}",
                authority=state.Authority.SYSTEM.value,
                sequence=runtime_state.sequence + 1,
                idempotency_key=str(uuid.uuid4())
            )
            
            decision, events = sovereign_gate.validate(req, runtime_state)
            
            if decision.approved:
                storage.apply_events(events, runtime_state)
                target_dir = os.path.join(ARTIFACTS_PATH, destination_folder)
                os.makedirs(target_dir, exist_ok=True)
                try:
                    shutil.move(filepath, os.path.join(target_dir, filename))
                    prov = response.provider if response else "unknown"
                    fhash = _file_hash(os.path.join(target_dir, filename))
                    catalog_file(target_dir, filename, destination_folder, auth_source, prov)
                    sync_to_master(filename, fhash, destination_folder, auth_source, prov)
                    deep_extract(os.path.join(target_dir, filename), target_dir)
                    update_folder_readme(target_dir)
                    notify("Willow Filed", f"{filename} -> {destination_folder}")
                    logging.info(f"FILED: {filename} -> {destination_folder}")
                except Exception as e:
                    logging.error(f"MOVE FAILED: {e}")
            elif decision.requires_human:
                logging.warning(f"HALT: {filename} needs approval.")

def main():
    print("--- AIOS OMNI-LOOP v2.0 ---")
    print("[*] Connecting to Google Drive API...")
    try:
        drive_service = get_drive_service()
        if drive_service: print("[OK] Drive Link Established.")
    except Exception as e:
        print(f"[!] Drive Auth Failed: {e}")
        drive_service = None
        
    print(f"[*] Vision: Gemini 2.5 Flash (Cloud API)")
    llm_router.print_status()
    
    cycle_count = 0
    while True:
        try:
            refinery_cycle(drive_service)
            cycle_count += 1
            # Librarian pass every 5th cycle
            if cycle_count % 5 == 0:
                librarian_pass()
            # Indexer pass every 10th cycle
            if cycle_count % 10 == 0:
                indexer_pass()
            # Git auto-push every 3rd cycle
            if cycle_count % 3 == 0:
                git_auto_push()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"LOOP ERROR: {e}")
            time.sleep(5)
        time.sleep(10)

if __name__ == "__main__":
    main()