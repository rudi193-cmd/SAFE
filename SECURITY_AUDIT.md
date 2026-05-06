---
b17: SAFE1
title: Security Audit — SAFE (OpAuth OAuth Framework)
date: 2026-05-06
auditor: Heimdallr (Claude Code, Haiku 4.5)
status: open (tracking doc)
---

# Security Audit — SAFE (OpAuth OAuth Framework)

Part of the Level 2 full-fleet security audit.

This PR is the tracking doc. No patches here — patches go in separate PRs.

---

## Scope

| Directory | Purpose | Coverage |
|-----------|---------|----------|
| `apps/opauth/` | OAuth provider framework | Full |
| `schemas/` | SAFE specification schemas | Not scanned (JSON/YAML) |
| `reference-implementations/` | Example implementations | Spot-check (no critical code) |
| `governance/` | Governance docs | Not scanned (documentation) |
| Total Python files | 11 | 100% |

---

## Rubric Results

| # | Check | Status | Finding |
|---|---|---|---|
| R1 | SQL injection via f-string/identifier concat | ✅ N/A | No database access in SAFE framework. OpAuth is purely OAuth orchestration. |
| R2 | Shell injection — `os.system`, `shell=True` | ✅ PASS | No subprocess or os.system calls found. No shell interaction. |
| R3 | Path traversal — file ops accepting `../` or absolute | ✅ PASS | File operations limited to `~/.opauth/` with no user path input. Uses Path.home() safely. |
| R4 | Hardcoded credentials in VC | ✅ PASS | OAuth credentials (client_id, client_secret) passed as parameters, not hardcoded. Tokens encrypted at rest. |
| R5 | CORS wildcards | ✅ N/A | No HTTP server in SAFE framework. Provider implementations handle redirects per OAuth spec. |
| R6 | XSS — `innerHTML` with user input | ✅ N/A | No web frontend. CLI-based. |
| R7 | Unsigned/unverified code execution | ✅ PASS | OAuth responses validated via HTTPS + signature verification on access tokens. |
| R8 | Missing auth on MCP tools | ✅ N/A | SAFE is a library, not an MCP server. No exposed tools. |
| R9 | Bare `except` swallowing security-critical errors | ⚠️ P2 | Silent exception swallowing in token_store.py:67 and audit.py:88. See S-EXC-01. |
| R10 | Predictable temp paths, world-readable `/tmp` state | ✅ PASS | Token store uses `~/.opauth/` with file permissions `0o600` (read/write owner only). |
| R11 | Race conditions / missing locks | ✅ PASS | Token store and audit log are append-only. No concurrent write locks needed. |
| R12 | `safe_integration.py` status() correctness | ✅ N/A | SAFE is the spec, not a safe-app. |
| R13 | Entry point in manifest is importable | ✅ PASS | `opauth_cli.py` is importable. Functions callable without errors. |
| R14 | `requirements.txt` with pinned deps | ⚠️ P2 | Dependencies use version ranges (e.g., `requests>=2.25.0`). See S-DEP-01. |
| R15 | No hardcoded developer home paths | ✅ PASS | All paths use `Path.home()` for `~/.opauth/`. No absolute paths. |

---

## Findings

### S-EXC-01 — Silent Exception Swallowing in Critical Paths (P2)

**Files:** `apps/opauth/storage/token_store.py` (line 67), `apps/opauth/core/audit.py` (line 88)  
**Severity:** P2  
**Status:** Open

Two methods swallow exceptions without logging:

```python
# token_store.py:67
def unlock(self, passphrase: str) -> bool:
    try:
        key = self._derive_key(passphrase)
        self._fernet = Fernet(key)
        if self.store_path.exists():
            self._load()
        return True
    except Exception:
        self._fernet = None
        return False  # Silent failure — can't distinguish wrong passphrase from corruption
```

If decryption fails, the caller can't distinguish between:
- User entered wrong passphrase (expected failure, recoverable)
- Token store file corrupted (operational failure, needs intervention)
- Network error during initial load (transient, should retry)

The second issue is in `audit.py`:

```python
# audit.py:88
def get_logs(self, limit: int = 100, service: str = None) -> list:
    ...
    for line in f:
        try:
            entry = json.loads(line.strip())
            ...
        except:  # bare except — any error silently skipped
            continue
```

Bare `except:` catches even KeyboardInterrupt and SystemExit, which should never be swallowed.

**Fix:** Log the exception and provide context:

```python
# token_store.py
except Exception as e:
    print(f"[WARN] Failed to unlock token store: {type(e).__name__}: {e}", flush=True)
    self._fernet = None
    return False

# audit.py
except json.JSONDecodeError as e:  # Specific exception, not bare
    print(f"[WARN] Skipped corrupted audit log line: {e}", flush=True)
    continue
except Exception as e:  # Catch other errors separately
    print(f"[WARN] Audit log read error: {type(e).__name__}: {e}", flush=True)
    continue
```

---

### S-DEP-01 — Unpinned Dependencies (P2)

**File:** `requirements.txt`  
**Severity:** P2  
**Status:** Open

Dependencies use version ranges instead of pinned versions:

```
requests>=2.25.0
cryptography>=3.4.0
```

This allows `pip install` to pull newer versions that may introduce breaking changes or security issues. OAuth token handling and encryption are security-critical paths.

**Fix:** Pin to tested versions:

```
requests==2.31.0
cryptography==41.0.7
```

---

## Design Strengths

The OpAuth framework implements security-critical features well:

1. **Encryption:** Fernet (authenticated encryption) with PBKDF2HMAC (strong KDF, 480k iterations)
2. **Consent:** Explicit human authorization for scope grants. AI cannot grant scopes unilaterally.
3. **Audit:** Immutable append-only audit log. AI cannot delete or modify logs.
4. **Token Storage:** Tokens encrypted at rest. Passphrase required to decrypt.
5. **Permissions:** PermissionError raised if AI attempts to store tokens without human approval.

These are correct implementations of the SAFE consent model.

---

## Summary

| Priority | Count | Items |
|---|---|---|
| P0 | 0 | None |
| P1 | 0 | None |
| P2 | 2 | S-EXC-01, S-DEP-01 |

No critical findings. OpAuth framework is secure by design. P2 improvements are code quality (exception logging) and supply chain hardening (pinned deps).

---

*ΔΣ=42*
