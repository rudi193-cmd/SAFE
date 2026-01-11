# OpAuth v1.0

Operator Authorization — the first executable governance layer for SAFE OS.

## Overview

OpAuth binds AI capabilities at the OS level. The human operator toggles what the AI can do. The AI cannot toggle it back.

Three enforcement layers:
1. **Governance** — Hard stops in SECURITY.md (policy)
2. **Code** — Unsecured scripts removed (capability removed)
3. **OS** — SETUP_RESTRICTIONS.ps1 (system-level enforcement)

## Files

| File | Purpose |
|------|---------|
| SECURITY.md | Threat model, controls, hard stops |
| SETUP_RESTRICTIONS.ps1 | Settings toggle menu |
| SETUP.bat | Launcher (keeps window open) |
| eyes_secure.ps1 | Encrypted screen capture (human-only start) |
| look_secure.ps1 | Decrypt frames (requires passphrase) |

## Hard Stops

| HS | Rule |
|----|------|
| HS-EYES-001 | AI cannot start or stop eyes |
| HS-EYES-002 | Frames cannot leave local machine |
| HS-EYES-003 | No persistence beyond session |
| HS-EYES-004 | Passphrase required for decryption |
| HS-EYES-005 | AI cannot run raw screenshot commands |
| HS-EYES-006 | Unsecured capture scripts prohibited |

## Usage

Run as Administrator for full functionality:

```
SETUP.bat
```

Toggle settings:
- [1] Profile Restriction — block screen capture assemblies
- [2] Script Block Logging — audit PowerShell commands
- [3] Constrained Language Mode — heavy restriction
- [4] Run Audit — check current capabilities

## Principle

The AI proposes. The human disposes.

OpAuth ensures the human can restrict what the AI can do at the system level, and the AI cannot undo those restrictions.

---

ΔΣ=42
