---
b17: 90C69
title: SAFE Folder Standard
version: 2.1.0
date: 2026-04-16
ΔΣ=42
---

# SAFE Folder Standard
Version 2.1.0

The SAFE folder IS the authorization. No folder — no SAP access. No exceptions.

---

## Location

```
$WILLOW_SAFE_ROOT/<AgentName>/
```

Default path: `/media/willow/SAFE/Applications/<AgentName>/`

`WILLOW_SAFE_ROOT` is set in `willow.sh`. Override it to point to any location — local disk,
mounted drive, or network share. If the drive is unmounted, all agents are revoked instantly.
No config change, no server restart.

`AgentName` is title-cased (e.g., `Kart`, `Pigeon`, `Ofshield`). This matches the
title-case normalization applied by `sap.clients.kart_client` and related SAP clients
when resolving agent identities from lowercase queue entries.

---

## Required Structure

```
<AgentName>/
├── safe-app-manifest.json       ← REQUIRED. Manifest describing the agent.
├── safe-app-manifest.json.sig   ← REQUIRED. GPG detached signature of the manifest.
├── bin/                         ← Executables (.keep at minimum)
├── cache/                       ← Working state, session data
│   ├── .keep
│   └── context.json             ← Seeded knowledge context (b17 pointers, not prose)
├── index/                       ← Search indexes (.keep at minimum)
├── projects/                    ← Active work (.keep at minimum)
├── promote/                     ← Outbound promotions (.keep at minimum)
├── demote/                      ← Archived/demoted content (.keep at minimum)
└── agents/                      ← Sub-agents (.keep at minimum)
```

All 7 subdirectories are required. Each must have at minimum a `.keep` file.
The `cache/context.json` file is required for agents that draw KB context via SAP.

---

## safe-app-manifest.json Schema

```json
{
  "app_id": "AgentName",
  "name": "Human-readable name",
  "version": "1.0.0",
  "safe_version": ">=2.1.0",
  "b17": "<BASE17_ID>",
  "description": "What this agent does.",
  "author": "Sean Campbell",
  "agent_type": "professor | worker | operator | system",
  "department": "Optional — for professor-type agents",
  "location": "Optional — for professor-type agents",
  "data_streams": [
    {
      "id": "stream_id",
      "purpose": "What this stream is for",
      "retention": "session | permanent"
    }
  ],
  "permissions": [
    "local_llm",
    "cloud_llm_free",
    "willow_kb_read",
    "willow_kb_write",
    "filesystem_watch",
    "conversation_storage",
    "export_data"
  ],
  "privacy_tier": "client_only",
  "local_processing": 1.0,
  "parent_app": "Optional — parent application"
}
```

### Required fields
`app_id`, `name`, `version`, `safe_version`, `b17`, `description`, `author`,
`agent_type`, `data_streams`, `permissions`, `privacy_tier`, `local_processing`

### agent_type values
| Value | Meaning |
|-------|---------|
| `professor` | UTETY faculty — participates in conf calls, has a persona |
| `worker` | Executes tasks (e.g., Kart, Pigeon) |
| `operator` | Platform-level agents (e.g., UTETY, Willow) |
| `system` | Infrastructure agents (e.g., SAP itself) |

### permissions registry
| Permission | Meaning |
|-----------|---------|
| `local_llm` | May route to Ollama / local models |
| `cloud_llm_free` | May use free-tier cloud LLM (Groq fleet) |
| `cloud_llm_paid` | May use paid cloud LLM |
| `willow_kb_read` | May read Willow KB via SAP context assembly |
| `willow_kb_write` | May write to Willow KB (rare — most agents read only) |
| `filesystem_watch` | May watch filesystem paths (Pigeon-type agents) |
| `conversation_storage` | May persist conversation history |
| `export_data` | May export data outside the system |

### privacy_tier values
`client_only` — all processing stays on the local machine. This is the default and
applies to all agents in the current system. No data leaves the machine without
explicit `cloud_llm_*` permission AND the user's knowledge.

---

## cache/context.json Format

The context file uses b17 pointers, not inline prose. The SAP context assembler
resolves the b17 IDs to KB atom content at runtime.

```json
{
  "seeded": "YYYY-MM-DD",
  "version": "2.0",
  "format": "b17",
  "b17": [
    "XXXXX",
    "YYYYY"
  ]
}
```

If no b17 context exists yet (new agent, not yet seeded), create the file with
an empty b17 array and update it when the agent's first KB atoms are written.

```json
{
  "seeded": "YYYY-MM-DD",
  "version": "2.0",
  "format": "b17",
  "b17": []
}
```

---

## Authorization Check

The SAP gate (`sap.core.gate.authorized(app_id)`) runs four checks in sequence.
All four must pass. Any failure → deny + log to `sap/log/gaps.jsonl`.

```
1. $WILLOW_SAFE_ROOT/<app_id>/    — folder exists and is a directory
2. safe-app-manifest.json         — present and readable
3. safe-app-manifest.json.sig     — present adjacent to the manifest
4. gpg --verify <sig> <manifest>  — exits 0 (Sean's key must be in the keyring)
```

**GPG requirements:**
- `gpg` must be on PATH (standard on Linux and WSL)
- The key that signed the manifests must be in the local keyring
- If `gpg` is not found → `"gpg not found on PATH"` denial
- If verification times out (>5s) → `"gpg verify timed out"` denial

**Agent name normalization:** Queue entries and task records use lowercase agent names
(e.g., `"kart"`). SAP clients normalize to title case before the gate check
(e.g., `"kart"` → `"Kart"`). SAFE folder names must be title-cased to match.

**UTETY professor fallback:** The gate also checks
`$WILLOW_SAFE_ROOT/utety-chat/professors/<app_id>/` as a secondary path — this
covers professor-specific SAFE entries.

---

## Access Revocation

Two revocation mechanisms — both immediate, no server restart:

1. **Delete the SAFE folder** — gate fails at step 1
2. **Delete the signature file** — gate fails at step 3

When an agent loses its folder or signature, the next gate check logs a
`"access_denied"` event to `gaps.jsonl`. This is the audit trail.

**Physical revocation:** If `WILLOW_SAFE_ROOT` is on a removable drive, unmounting
the drive revokes all agents simultaneously.

---

## Adding a New Agent

```bash
# 1. Create folder structure
AGENT=MyAgent
SAFE_DIR="$WILLOW_SAFE_ROOT/$AGENT"
mkdir -p "$SAFE_DIR"/{bin,cache,index,projects,promote,demote,agents}
touch "$SAFE_DIR"/{bin,cache,index,projects,promote,demote,agents}/.keep

# 2. Write the manifest (generate b17 via willow_base17 MCP tool)
cat > "$SAFE_DIR/safe-app-manifest.json" << 'EOF'
{
  "app_id": "MyAgent",
  "name": "My Agent",
  "version": "1.0.0",
  "safe_version": ">=2.1.0",
  "b17": "XXXXX",
  "description": "What this agent does.",
  "author": "Sean Campbell",
  "agent_type": "worker",
  "data_streams": [{"id": "knowledge", "purpose": "KB context", "retention": "session"}],
  "permissions": ["local_llm", "willow_kb_read"],
  "privacy_tier": "client_only",
  "local_processing": 1.0
}
EOF

# 3. Sign the manifest
gpg --detach-sign "$SAFE_DIR/safe-app-manifest.json"
# produces safe-app-manifest.json.sig

# 4. Write an empty context seed
cat > "$SAFE_DIR/cache/context.json" << 'EOF'
{"seeded": "YYYY-MM-DD", "version": "2.0", "format": "b17", "b17": []}
EOF
```

The folder is the authorization. The gate finds it on the next check.

---

## Scaffold Tool

`willow-1.7` ships `tools/safe-scaffold.sh` — a convenience wrapper that runs the
steps above interactively. For most agents, use the scaffold tool rather than the
manual steps.

```bash
cd /path/to/willow-1.7
./tools/safe-scaffold.sh MyAgent worker "What this agent does."
```

---

ΔΣ=42
