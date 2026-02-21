# SAFE App Integration Specification

Version: 1.0.0
Status: Stable
Last Updated: 2026-02-21

---

## Overview

This specification defines how third-party applications integrate with the SAFE (Session-Authorized, Fully Explicit) framework. Apps that follow this spec provide session-based consent, explicit data stream management, and user-controlled privacy.

---

## Core Principles

1. **Session-based Consent** - Permissions expire when the app closes
2. **Explicit Data Streams** - Each type of data requires separate authorization
3. **User Control** - Users can revoke consent mid-session
4. **Privacy-First** - Local processing preferred over cloud
5. **Zero Retention Default** - Data deleted unless explicitly consented to retain

---

## App Manifest

Every SAFE app must include a `safe-app-manifest.json` file in its root directory.

### Schema

```json
{
  "app_id": "string",              // Unique identifier (kebab-case)
  "name": "string",                 // Human-readable name
  "version": "string",              // Semver (e.g., "1.0.0")
  "safe_version": "string",         // Min SAFE framework version (e.g., ">=2.0.0")
  "description": "string",          // One-line description
  "author": "string",               // Author name
  "data_streams": [                 // Array of data streams
    {
      "id": "string",               // Stream identifier
      "purpose": "string",          // What this stream is used for
      "retention": "session|permanent|custom", // Data retention policy
      "description": "string"       // Detailed explanation
    }
  ],
  "permissions": ["string"],        // Required system permissions
  "privacy_tier": "client_only|hybrid|cloud_optional", // Processing location
  "local_processing": 0.0-1.0,      // Fraction processed locally (0.96 = 96%)
  "entry_point": "string",          // Python module entry (e.g., "app.main:run")
  "license": "string",              // License (e.g., "MIT")
  "repository": "string"            // GitHub URL
}
```

### Example

```json
{
  "app_id": "dating-wellbeing",
  "name": "Dating Wellbeing Analyzer",
  "version": "1.0.0",
  "safe_version": ">=2.0.0",
  "description": "Privacy-first dating profile analysis",
  "author": "Sean Campbell",
  "data_streams": [
    {
      "id": "profiles",
      "purpose": "Analyze dating profiles",
      "retention": "session",
      "description": "Profile data deleted after session ends"
    },
    {
      "id": "patterns",
      "purpose": "Learn red flag patterns",
      "retention": "permanent",
      "description": "Stores anonymized patterns if consented"
    }
  ],
  "permissions": ["local_llm", "image_ocr", "pattern_storage"],
  "privacy_tier": "client_only",
  "local_processing": 0.96,
  "entry_point": "dating_wellbeing.main:app",
  "license": "MIT",
  "repository": "https://github.com/user/safe-app-dating-wellbeing"
}
```

---

## Session Lifecycle

SAFE apps must implement these hooks via a `SAFESession` class:

### 1. Session Start

Called when user opens the app. Returns authorization requests.

```python
def on_session_start(self) -> Dict:
    return {
        "session_id": str,
        "authorization_requests": [
            {
                "stream_id": str,
                "purpose": str,
                "retention": str,
                "required": bool,
                "prompt": str  # User-facing question
            }
        ]
    }
```

### 2. Consent Granted/Denied

Called when user responds to authorization request.

```python
def on_consent_granted(self, stream_id: str, granted: bool) -> Dict:
    # Store consent decision
    # Return status: ok|consent_required|limited_mode
    return {"status": str, "message": str}
```

### 3. Stream Access Check

Called before accessing any data stream.

```python
def can_access_stream(self, stream_id: str) -> bool:
    # Return True only if user granted consent
    return bool
```

### 4. Session End

Called when user closes the app. Performs cleanup.

```python
def on_session_end(self) -> Dict:
    return {
        "session_id": str,
        "ended_at": str,  # ISO 8601
        "cleanup_actions": [
            {
                "action": "delete|retain",
                "stream": str,
                "reason": str
            }
        ]
    }
```

### 5. Mid-Session Revoke

Called when user revokes consent during active session.

```python
def on_revoke(self, stream_id: str) -> Dict:
    # Immediately delete associated data
    return {
        "status": "revoked",
        "stream": str,
        "action": "data_deleted"
    }
```

---

## Data Stream Types

### Session Retention

Data deleted when session ends. Use for sensitive, temporary data.

**Examples:**
- Dating profiles being analyzed
- Screenshots of personal messages
- Temporary calculations

### Permanent Retention

Data stored across sessions. Requires explicit user consent.

**Examples:**
- User preferences
- Learned patterns (anonymized)
- Historical analytics

### Custom Retention

App-defined retention policy (must be documented in manifest).

**Examples:**
- Delete after 7 days
- Delete after user confirms action
- Export then delete

---

## Privacy Tiers

### client_only

All processing happens on user's device. No cloud communication except:
- Free-tier LLM APIs (Gemini, Groq) for compute only
- Public knowledge APIs (Wikipedia, documentation)

### hybrid

Majority local, minimal cloud for specific features.
- Must disclose what goes to cloud
- Must offer local-only fallback

### cloud_optional

Cloud features available but entirely optional.
- App fully functional without cloud
- User explicitly enables cloud features

---

## Permission Types

Apps declare required permissions in manifest:

| Permission | Purpose |
|------------|---------|
| `local_llm` | Use local Ollama models |
| `cloud_llm_free` | Use free-tier cloud LLMs (Gemini, Groq) |
| `image_ocr` | Extract text from images |
| `pattern_storage` | Store user patterns/preferences |
| `file_read` | Read files from user filesystem |
| `file_write` | Write files to user filesystem |
| `network_fetch` | Fetch data from internet |

---

## Compliance Checklist

- [ ] Manifest file present and valid
- [ ] All data streams documented
- [ ] Session lifecycle hooks implemented
- [ ] Consent checked before data access
- [ ] Session data deleted on close
- [ ] Revoke function works mid-session
- [ ] Privacy tier accurately labeled
- [ ] Local processing percentage measured
- [ ] User can decline all optional streams
- [ ] App functions with minimal consent

---

## Installation

SAFE apps should be pip-installable:

```bash
pip install safe-app-{app-id}
```

Apps must include `pyproject.toml` for packaging.

---

## Example Implementation

See reference implementation:
- **Repository:** [safe-app-dating-wellbeing](https://github.com/seancampbell3161/safe-app-dating-wellbeing)
- **Integration:** `safe_integration.py`
- **Manifest:** `safe-app-manifest.json`

---

## Governance

SAFE apps follow the same governance model as SAFE framework:
- Dual Commit (AI proposes, human ratifies)
- Hard Stops (absolute privacy boundaries)
- Session Consent (per-use authorization)

See [SAFE Governance Index](../governance/GOVERNANCE_INDEX.md)

---

**Last Updated:** 2026-02-13
**Maintainer:** Sean Campbell
**Status:** Draft → Community Review

ΔΣ=42
