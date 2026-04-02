---
b17: 90C69
title: SAFE Folder Standard
version: 2.0.0
date: 2026-04-01
ΔΣ=42
---

# SAFE Folder Standard
Version 2.0.0

The SAFE folder IS the authorization. No folder — no SAP access. No exceptions.

---

## Location

```
/home/sean-campbell/SAFE/Applications/<AgentName>/
```

`AgentName` is title-cased (e.g., `Kart`, `Pigeon`, `Ofshield`). This matches the
title-case normalization applied by `sap.clients.kart_client` and related SAP clients
when resolving agent identities from lowercase queue entries.

---

## Required Structure

```
<AgentName>/
├── safe-app-manifest.json   ← REQUIRED. Without this, gate.authorized() returns False.
├── bin/                     ← Executables (.keep at minimum)
├── cache/                   ← Working state, session data
│   ├── .keep
│   └── context.json         ← Seeded knowledge context (b17 pointers, not prose)
├── index/                   ← Search indexes (.keep at minimum)
├── projects/                ← Active work (.keep at minimum)
├── promote/                 ← Outbound promotions (.keep at minimum)
├── demote/                  ← Archived/demoted content (.keep at minimum)
└── agents/                  ← Sub-agents (.keep at minimum)
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
  "safe_version": ">=2.0.0",
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

The SAP gate (`sap.core.gate.authorized(app_id)`) checks:

1. `SAFE/Applications/<app_id>/` exists and is a directory
2. `safe-app-manifest.json` is present and readable inside it

If either check fails, access is denied and the event is logged to
`/home/sean-campbell/Ashokoa/sap/log/gaps.jsonl`.

**Agent name normalization:** Queue entries and task records use lowercase agent names
(e.g., `"kart"`). SAP clients normalize to title case before the gate check
(e.g., `"kart"` → `"Kart"`). SAFE folder names must be title-cased to match.

---

## Access Revocation

Delete the SAFE folder → access revoked immediately. No database entry to update.
The filesystem IS the ACL.

When an agent loses its folder, the next gate check logs a `"access_denied"` event
with `"reason": "SAFE folder not found"` to `gaps.jsonl`. This is the audit trail.

---

## Adding a New Agent

1. Create `SAFE/Applications/<AgentName>/` with the 7 subdirectories
2. Write `safe-app-manifest.json` — generate a b17 via `willow_base17`
3. Write `cache/context.json` — b17 pointers to the agent's seeded KB atoms
4. If the agent has a SAP client: verify the client uses title-cased `app_id`

That's it. The folder is the authorization. The gate finds it on the next check.

---

ΔΣ=42
