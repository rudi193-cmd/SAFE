#!/usr/bin/env python3
"""
Willow UI Server — FastAPI wrapper around local_api.py

GOVERNANCE: Localhost-only. No external network binding.
"""

import sys
import hashlib
import httpx
import psutil
import queue
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Wire imports
sys.path.insert(0, str(Path(__file__).parent))

import local_api
from core import knowledge
from core.coherence import get_coherence_report, check_intervention
from core import topology
from core.awareness import on_scan_complete, on_organize_complete, on_coherence_update, on_topology_update, say as willow_say
from apps.pa import drive_scan, drive_organize

app = FastAPI(title="Willow", docs_url=None, redoc_url=None)

# Track server start time for uptime
SERVER_START_TIME = datetime.now()

# CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # LAN + Neocities + tunnel all need access
    allow_methods=["*"],
    allow_headers=["*"],
)

USERNAME = local_api.DEFAULT_USER


# --- API Endpoints ---

@app.get("/api/health")
def health():
    """Fast health check — no Ollama ping, no DB queries."""
    return {"status": "ok"}


@app.get("/api/system/status")
async def system_status():
    """
    Comprehensive system status for Willow health monitoring.
    Checks: Ollama, server uptime, governance queue, intake pipeline, engine, tunnel.
    """
    status = {
        "ollama": {"running": False, "models": []},
        "server": {"uptime_seconds": 0, "port": 8420},
        "governance": {"pending_commits": 0, "last_ratification": None},
        "intake": {"dump": 0, "hold": 0, "process": 0, "route": 0, "clear": 0},
        "engine": {"running": False},
        "tunnel": {"url": None, "reachable": False}
    }

    # --- Ollama Check ---
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r = await client.get("http://127.0.0.1:11434/api/tags")
            r.raise_for_status()
            data = r.json()
            status["ollama"]["running"] = True
            status["ollama"]["models"] = [m["name"] for m in data.get("models", [])]
    except:
        pass

    # --- Server Uptime ---
    status["server"]["uptime_seconds"] = int((datetime.now() - SERVER_START_TIME).total_seconds())

    # --- Governance Check ---
    try:
        gov_dir = Path("governance/commits")
        if gov_dir.is_dir():
            pending = list(gov_dir.glob("*.pending"))
            status["governance"]["pending_commits"] = len(pending)

            # Last ratification = most recent non-pending file
            all_files = [f for f in gov_dir.iterdir() if f.is_file() and not f.name.endswith(".pending")]
            if all_files:
                latest = max(all_files, key=lambda f: f.stat().st_mtime)
                status["governance"]["last_ratification"] = datetime.fromtimestamp(latest.stat().st_mtime).isoformat()
    except:
        pass

    # --- Intake Check ---
    try:
        intake_dir = Path("intake")
        for stage in ["dump", "hold", "process", "route", "clear"]:
            stage_path = intake_dir / stage
            if stage_path.is_dir():
                status["intake"][stage] = len(list(stage_path.iterdir()))
    except:
        pass

    # --- Engine Check (kart process) ---
    try:
        for proc in psutil.process_iter(['name']):
            if 'kart' in proc.info['name'].lower() or 'python' in proc.info['name'].lower():
                # Check if it's running kart.py (basic heuristic)
                try:
                    if any('kart' in arg.lower() for arg in proc.cmdline()):
                        status["engine"]["running"] = True
                        break
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass
    except:
        pass

    # --- Tunnel Check ---
    try:
        tunnel_file = Path(".tunnel_url")
        if tunnel_file.is_file():
            tunnel_url = tunnel_file.read_text().strip()
            if tunnel_url:
                status["tunnel"]["url"] = tunnel_url
                try:
                    async with httpx.AsyncClient(timeout=5) as client:
                        r = await client.head(tunnel_url + "/api/health")
                        status["tunnel"]["reachable"] = r.is_success
                except:
                    pass
    except:
        pass

    return status


@app.get("/api/status")
def status():
    ollama_up = local_api.check_ollama()
    models = local_api.list_models() if ollama_up else []
    gemini = local_api.check_gemini_available()
    claude = local_api.check_claude_available()

    # Knowledge stats
    stats = {"atoms": 0, "conversations": 0, "entities": 0, "gaps": 0}
    try:
        import sqlite3
        db_path = knowledge._db_path(USERNAME)
        if Path(db_path).exists():
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            for table, key in [("knowledge", "atoms"), ("conversation_memory", "conversations"),
                               ("entities", "entities"), ("knowledge_gaps", "gaps")]:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[key] = cur.fetchone()[0]
                except:
                    pass
            conn.close()
    except:
        pass

    return {
        "ollama": ollama_up,
        "models": models,
        "gemini": gemini,
        "claude": claude,
        "knowledge": stats,
    }


@app.get("/api/personas")
def personas():
    result = {}
    for name, prompt in local_api.PERSONAS.items():
        result[name] = {
            "name": name,
            "folder": local_api.PERSONA_FOLDERS.get(name, name.lower()),
            "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
        }
    return result


@app.post("/api/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt", "")
    persona = body.get("persona", "Willow")

    if not prompt:
        return {"error": "No prompt provided"}

    def generate():
        full_response = []
        for chunk in local_api.process_smart_stream(prompt, persona=persona, user=USERNAME):
            full_response.append(chunk)
            yield f"data: {chunk}\n\n"

        # Send coherence metrics as final SSE event
        try:
            coherence = local_api.log_conversation(
                persona=persona,
                user_input=prompt,
                assistant_response="".join(full_response),
                model="streamed",
                tier=0,
            )
            import json
            yield f"event: coherence\ndata: {json.dumps(coherence)}\n\n"
            on_coherence_update(coherence)
        except Exception:
            pass

        yield "event: done\ndata: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.post("/api/chat/multi")
async def chat_multi(request: Request):
    """
    Parallel multi-persona chat.

    Body: {"tasks": [{"persona": "Kart", "prompt": "..."}, ...]}

    Spawns threads for each persona, streams all responses tagged by persona.
    """
    body = await request.json()
    tasks = body.get("tasks", [])

    if not tasks:
        return {"error": "No tasks provided"}

    # Validate tasks
    for task in tasks:
        if "persona" not in task or "prompt" not in task:
            return {"error": "Each task must have 'persona' and 'prompt'"}

    def generate():
        # Queue for collecting chunks from all threads
        chunk_queue = queue.Queue()
        active_personas = set(task["persona"] for task in tasks)

        def worker(persona: str, prompt: str):
            """Worker thread that streams from one persona."""
            try:
                full_response = []
                for chunk in local_api.process_smart_stream(prompt, persona=persona, user=USERNAME):
                    full_response.append(chunk)
                    # Tag chunk with persona and put in queue
                    chunk_queue.put((persona, "chunk", chunk))

                # Log conversation for this persona
                try:
                    coherence = local_api.log_conversation(
                        persona=persona,
                        user_input=prompt,
                        assistant_response="".join(full_response),
                        model="streamed",
                        tier=0,
                    )
                    chunk_queue.put((persona, "coherence", coherence))
                except:
                    pass

                # Signal this persona is done
                chunk_queue.put((persona, "done", None))
            except Exception as e:
                chunk_queue.put((persona, "error", str(e)))

        # Start all threads
        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            futures = []
            for task in tasks:
                future = executor.submit(worker, task["persona"], task["prompt"])
                futures.append(future)

            # Stream events as they arrive
            while active_personas:
                try:
                    persona, event_type, data = chunk_queue.get(timeout=0.1)

                    if event_type == "chunk":
                        yield f"event: {persona}\ndata: {data}\n\n"

                    elif event_type == "coherence":
                        import json
                        yield f"event: coherence_{persona}\ndata: {json.dumps(data)}\n\n"

                    elif event_type == "done":
                        yield f"event: done_{persona}\ndata: [DONE]\n\n"
                        active_personas.discard(persona)

                    elif event_type == "error":
                        yield f"event: error_{persona}\ndata: {data}\n\n"
                        active_personas.discard(persona)

                except queue.Empty:
                    continue

            # All personas finished
            yield "event: complete\ndata: [COMPLETE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/knowledge/search")
def knowledge_search(q: str = "", limit: int = 5):
    if not q:
        return {"results": [], "query": q}
    results = knowledge.search(USERNAME, q, max_results=limit)
    return {"results": results, "query": q}


@app.get("/api/knowledge/gaps")
def knowledge_gaps(limit: int = 10):
    gaps = knowledge.get_top_gaps(USERNAME, limit=limit)
    return {"gaps": gaps}


@app.get("/api/knowledge/stats")
def knowledge_stats():
    import sqlite3
    stats = {}
    try:
        db_path = knowledge._db_path(USERNAME)
        if Path(db_path).exists():
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            for table in ["knowledge", "conversation_memory", "entities", "knowledge_gaps"]:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    stats[table] = cur.fetchone()[0]
                except:
                    stats[table] = 0
            conn.close()
    except:
        pass
    return stats


@app.get("/api/coherence")
def coherence():
    report = get_coherence_report()
    needs_intervention, reason = check_intervention()
    return {**report, "needs_intervention": needs_intervention, "intervention_reason": reason}


@app.post("/api/ingest")
async def ingest(file: UploadFile = File(...)):
    """Ingest a dropped file into the knowledge DB."""
    allowed_ext = {".txt", ".md", ".pdf", ".docx", ".json", ".csv", ".html", ".htm"}
    suffix = Path(file.filename).suffix.lower()

    if suffix not in allowed_ext:
        return {"error": f"Unsupported file type: {suffix}", "accepted": list(allowed_ext)}

    content_bytes = await file.read()
    file_hash = hashlib.md5(content_bytes).hexdigest()

    # Extract text content
    try:
        text = content_bytes.decode("utf-8", errors="ignore")
    except:
        return {"error": "Could not decode file as text"}

    if len(text) < 10:
        return {"error": "File too small or empty"}

    # Truncate for ingestion (same as unified_watcher)
    text_for_ingest = text[:4000]

    knowledge.ingest_file_knowledge(
        username=USERNAME,
        filename=file.filename,
        file_hash=file_hash,
        category="ui_drop",
        content_text=text_for_ingest,
        provider="willow_ui",
    )

    return {"status": "ingested", "filename": file.filename, "hash": file_hash, "chars": len(text_for_ingest)}


# --- Topology Endpoints ---

@app.get("/api/topology/rings")
def topology_rings():
    """Atom counts by ring."""
    return topology.get_ring_distribution(USERNAME)


@app.get("/api/topology/zoom/{node_id}")
def topology_zoom(node_id: int, depth: int = 1):
    """Traverse from an atom. ?depth=2 for recursive."""
    depth = min(depth, 3)  # Cap recursion
    return topology.zoom(USERNAME, node_id, depth)


@app.get("/api/topology/continuity")
def topology_continuity():
    """Strip continuity check — find gaps in the Möbius strip."""
    return topology.check_strip_continuity(USERNAME)


@app.get("/api/topology/flow")
def topology_flow():
    """Sankey-style ring flow graph."""
    return topology.get_ring_flow_graph(USERNAME)


@app.post("/api/topology/build_edges")
def topology_build_edges(batch_size: int = 50):
    """Compute edges between atoms. Incremental."""
    created = topology.build_edges(USERNAME, batch_size=batch_size)
    if created:
        on_topology_update(edges_created=created)
    return {"edges_created": created}


@app.post("/api/topology/cluster")
def topology_cluster(n_clusters: int = 10):
    """Cluster atoms via KMeans over embeddings."""
    cluster_ids = topology.cluster_atoms(USERNAME, n_clusters=n_clusters)
    if cluster_ids:
        on_topology_update(clusters_created=len(cluster_ids))
    return {"clusters_created": len(cluster_ids), "cluster_ids": cluster_ids}


# --- PA (Personal Assistant) Endpoints ---

DRIVE_ROOT = str(Path.home() / "My Drive")
_pa_catalog = []  # Module-level state for scan results
_pa_plan = {}     # Module-level state for current plan
_pa_near_dupes = []  # Near-duplicate pairs


@app.post("/api/pa/scan")
async def pa_scan():
    """Scan the entire Drive, classify everything, detect duplicates."""
    global _pa_catalog, _pa_plan, _pa_near_dupes
    if not Path(DRIVE_ROOT).exists():
        return {"error": f"Drive not mounted at {DRIVE_ROOT}"}

    _pa_catalog = drive_scan.scan(DRIVE_ROOT)
    drive_scan.find_duplicates(_pa_catalog, DRIVE_ROOT)
    _pa_near_dupes = drive_scan.find_near_duplicates(_pa_catalog, DRIVE_ROOT)
    _pa_plan = drive_organize.generate_plan(_pa_catalog)
    summary = drive_scan.catalog_summary(_pa_catalog)
    summary["near_duplicate_pairs"] = len(_pa_near_dupes)
    on_scan_complete(summary)
    return {"status": "scanned", "summary": summary}


@app.get("/api/pa/plan")
def pa_plan():
    """Get the current move plan."""
    if not _pa_plan:
        return {"error": "No scan performed yet. POST /api/pa/scan first."}
    return {
        "summary": _pa_plan.get("summary", {}),
        "folders_to_create": _pa_plan.get("folders_to_create", []),
        "review": drive_organize.review(_pa_plan),
        "move_count": len(_pa_plan.get("moves", [])),
        "delete_count": len(_pa_plan.get("deletes", [])),
    }


@app.post("/api/pa/execute")
async def pa_execute(request: Request):
    """Execute approved moves. Body: {scope: "organize"|"dedupe"|"cleanup"}"""
    if not _pa_plan:
        return {"error": "No plan generated. POST /api/pa/scan first."}

    body = await request.json()
    scope = body.get("scope", "organize")

    if scope == "organize":
        result = drive_organize.execute_moves(_pa_plan, DRIVE_ROOT, USERNAME)
    elif scope == "dedupe":
        result = drive_organize.execute_deletes(_pa_plan, DRIVE_ROOT, scope="dedupe")
    elif scope == "cleanup":
        result = drive_organize.execute_deletes(_pa_plan, DRIVE_ROOT, scope="cleanup")
        # Also remove empty dirs
        removed = drive_organize.cleanup_empty_dirs(DRIVE_ROOT)
        result["empty_dirs_removed"] = removed
    else:
        return {"error": f"Unknown scope: {scope}. Use organize|dedupe|cleanup"}

    on_organize_complete(result)
    return {"status": "executed", "scope": scope, "result": result}


@app.get("/api/pa/status")
def pa_status():
    """Get current PA progress."""
    return drive_organize.get_progress()


@app.post("/api/pa/correct")
async def pa_correct(request: Request):
    """
    Correct a misrouted file or mis-transcribed content.
    Body: {
        path: "current/relative/path.md",        (required)
        destination: "Creative/",                 (optional — move here)
        text: "corrected transcription content",  (optional — re-ingest)
        category: "creative"                      (optional — new category)
    }
    """
    body = await request.json()
    path = body.get("path")
    if not path:
        return {"error": "path is required"}
    result = drive_organize.correct_file(
        drive_root=DRIVE_ROOT,
        current_path=path,
        new_destination=body.get("destination"),
        corrected_text=body.get("text"),
        new_category=body.get("category"),
        username=USERNAME,
    )
    return {"status": "corrected", "result": result}


# --- Neocities Deploy ---

@app.post("/api/neocities/deploy")
def neocities_deploy():
    """Push pocket Willow to seancampbell.neocities.org."""
    try:
        from apps.neocities import deploy_pocket_willow
        result = deploy_pocket_willow()
        return {"status": "deployed", "result": result}
    except Exception as e:
        return {"error": str(e)}


@app.get("/api/neocities/info")
def neocities_info():
    """Get Neocities site info."""
    try:
        from apps.neocities import info
        return info()
    except Exception as e:
        return {"error": str(e)}


# --- Governance (Dual Commit) ---

GOV_COMMITS_DIR = Path("governance/commits")
GOV_COMMITS_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/api/governance/pending")
def governance_pending():
    """List all pending governance commits awaiting ratification."""
    try:
        pending = []
        for f in GOV_COMMITS_DIR.glob("*.pending"):
            stat = f.stat()
            pending.append({
                "id": f.stem,
                "filename": f.name,
                "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "size": stat.st_size,
            })
        # Sort by timestamp descending (newest first)
        pending.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"pending": pending}
    except Exception as e:
        return {"error": str(e), "pending": []}


@app.get("/api/governance/history")
def governance_history(limit: int = 50):
    """List ratified and rejected commits (history)."""
    try:
        history = []
        for f in list(GOV_COMMITS_DIR.glob("*.commit")) + list(GOV_COMMITS_DIR.glob("*.reject")):
            stat = f.stat()
            action = "approved" if f.suffix == ".commit" else "rejected"
            history.append({
                "id": f.stem,
                "filename": f.name,
                "action": action,
                "timestamp": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
        # Sort by timestamp descending
        history.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"history": history[:limit]}
    except Exception as e:
        return {"error": str(e), "history": []}


@app.get("/api/governance/diff/{commit_id}")
def governance_diff(commit_id: str):
    """Get the contents of a pending commit for review."""
    try:
        filepath = GOV_COMMITS_DIR / f"{commit_id}.pending"
        if not filepath.exists():
            return {"error": "Commit not found"}
        content = filepath.read_text(encoding="utf-8")
        return {"id": commit_id, "content": content}
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/governance/approve")
async def governance_approve(request: Request):
    """Approve (ratify) a pending commit. Moves .pending → .commit."""
    try:
        body = await request.json()
        commit_id = body.get("commit_id")
        if not commit_id:
            return {"error": "Missing commit_id"}

        pending_file = GOV_COMMITS_DIR / f"{commit_id}.pending"
        if not pending_file.exists():
            return {"error": "Commit not found"}

        # Move to .commit
        approved_file = GOV_COMMITS_DIR / f"{commit_id}.commit"
        pending_file.rename(approved_file)

        return {"success": True, "action": "approved", "commit_id": commit_id}
    except Exception as e:
        return {"error": str(e), "success": False}


@app.post("/api/governance/reject")
async def governance_reject(request: Request):
    """Reject a pending commit. Moves .pending → .reject and appends reason."""
    try:
        body = await request.json()
        commit_id = body.get("commit_id")
        reason = body.get("reason", "No reason provided")

        if not commit_id:
            return {"error": "Missing commit_id"}

        pending_file = GOV_COMMITS_DIR / f"{commit_id}.pending"
        if not pending_file.exists():
            return {"error": "Commit not found"}

        # Move to .reject
        rejected_file = GOV_COMMITS_DIR / f"{commit_id}.reject"
        content = pending_file.read_text(encoding="utf-8")

        # Append rejection reason
        new_content = f"{content}\n\n---\nREJECTED: {datetime.now().isoformat()}\nReason: {reason}\n"
        rejected_file.write_text(new_content, encoding="utf-8")
        pending_file.unlink()

        return {"success": True, "action": "rejected", "commit_id": commit_id}
    except Exception as e:
        return {"error": str(e), "success": False}


# --- Pocket Willow (mobile-friendly, served same-origin) ---

POCKET_HTML = Path(__file__).parent / "neocities" / "index.html"

@app.get("/pocket")
def serve_pocket():
    """Serve pocket Willow from same origin — no CORS / mixed-content issues."""
    if not POCKET_HTML.exists():
        return {"error": "neocities/index.html not found"}
    return FileResponse(POCKET_HTML, media_type="text/html")


# --- Governance Dashboard ---

GOVERNANCE_DASHBOARD = Path(__file__).parent / "governance" / "dashboard.html"

@app.get("/governance")
def serve_governance_dashboard():
    """Serve governance dashboard for dual commit review (admin only)."""
    if not GOVERNANCE_DASHBOARD.exists():
        return {"error": "governance/dashboard.html not found"}
    return FileResponse(GOVERNANCE_DASHBOARD, media_type="text/html")


# --- Static file serving (production) ---

UI_DIST = Path(__file__).parent / "ui" / "dist"

if UI_DIST.exists():
    @app.get("/")
    def serve_index():
        return FileResponse(UI_DIST / "index.html")

    app.mount("/", StaticFiles(directory=str(UI_DIST)), name="static")


if __name__ == "__main__":
    import uvicorn
    print("Willow UI: http://127.0.0.1:8420")
    uvicorn.run(app, host="0.0.0.0", port=8420, log_level="info")
