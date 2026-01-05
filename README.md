# SAFE: Session-Authorized, Fully Explicit

A legal and technical framework for user data handling in AI-mediated applications.

## Core Principle

**Users review and authorize all data access permissions at the start of each session, not once during initial setup.**

Consent expires with the session. Data is deleted by default. Users own their data.

---

## What's Included

### Governance Framework

| Document | Purpose |
|----------|---------|
| `governance/SESSION_CONSENT.md` | Complete SAFE protocol specification |
| `governance/DUAL_COMMIT.md` | AI proposes, human ratifies model |
| `governance/HARD_STOPS.md` | Five absolute boundaries |
| `governance/HARD_STOPS_GROUNDING.md` | Biographical precedent for hard stops |

### Data Schemas

| Schema | Purpose |
|--------|---------|
| `docs/RELATIONSHIP_SCHEMA.md` | Three-layer relationship tracking model |
| `schemas/v2.0.0/` | JSON schemas for input, output, transforms |

### Reference Implementations

| Implementation | Description |
|----------------|-------------|
| `reference-implementations/ethical-review-ui/` | Ethical review interface (React/Vite) |
| `reference-implementations/aionic-journal/` | Journal application (React/Vite) |

---

## SAFE Protocol Summary

### Four Data Streams

All user data falls into one of four streams, each requiring explicit session authorization:

| Stream | Contains |
|--------|----------|
| **Relationships** | Names, roles, connection descriptions |
| **Images** | Uploaded files, screenshots, visual data |
| **Bookmarks** | URLs, references, resources |
| **Dating** | Preferences, choices, partner selection |

### Session Flow

1. **Start** — System presents authorization request
2. **During** — Only access authorized streams
3. **End** — All authorizations expire, data deleted unless explicitly saved

### Pricing Model

**Pay-what-you-can, including $0.**

- No reduced features at $0
- No shame, no second-class service
- Users see actual operational costs
- Trust that most people contribute when able

---

## User Rights

1. **Right to Zero Retention** — Decline all data storage
2. **Right to Deletion** — Complete removal on request
3. **Right to Export** — All data in readable format
4. **Right to Audit** — View exactly what system knows
5. **Right to Revoke** — Mid-session authorization withdrawal

---

## Integration

SAFE integrates with the Dual Commit governance model:

| Governance Concept | SAFE Integration |
|-------------------|------------------|
| Dual Commit | User consent = human ratification |
| Hard Stops | Absolute limits (e.g., children's data protection) |
| Unknown Variable Directive | Halt if consent state unclear |

---

## License

MIT License for code. CC-BY-NC for documentation.

---

## Status

| Component | Status |
|-----------|--------|
| Specification | STABLE |
| Reference Implementation | Available |
| Legal Review | Pending |
| Adoption | Open to any project |
