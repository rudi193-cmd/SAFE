Still undergoing rewrites.

# SAFE: Session-Authorized, Fully Explicit

A consent framework for applications that handle personal data.

## Why This Exists

Current consent models are broken.

You click "I Agree" once, years ago, to a wall of text no one reads. That click now authorizes perpetual data collection. Your consent from 2019 still governs how your data is used in 2026. This is not meaningful consent.

**SAFE proposes a different model:** consent expires with the session. Each time you use an application, you decide what it can access. When you close the app, those permissions are gone. Tomorrow, it asks again.

This is inconvenient. That's the point. Consent should require intention.

---

## Core Principle

**Users review and authorize data access at the start of each session, not once during initial setup.**

Consent expires with the session. Data is deleted by default. Users own their data.

---

## How It Works

### A Concrete Example

You open an app built on SAFE.

Before showing you anything, it asks:

> "This session, may I access your saved contacts?"

You tap **Yes** or **No**.

You use the app. An hour later, you close it.

That permission is gone. Tomorrow, when you open the app again, it asks again. You might say yes. You might say no. Either way, you decide — every time.

### Session Flow

1. **Start** — App presents authorization request for each data type it needs
2. **During** — App only accesses what you authorized this session
3. **End** — All authorizations expire; data deleted unless explicitly saved

---

## User Rights

1. **Right to Zero Retention** — Decline all data storage
2. **Right to Deletion** — Complete removal on request
3. **Right to Export** — All data in readable format
4. **Right to Audit** — View exactly what the system knows about you
5. **Right to Revoke** — Withdraw authorization mid-session

---

## Data Streams

SAFE organizes personal data into streams. Each stream requires separate authorization.

The specific streams depend on the application. Examples:

| Application | Possible Streams |
|-------------|------------------|
| Journal app | Relationships, Images, Bookmarks, Preferences |
| Fitness app | Health metrics, Location history, Goals |
| Note-taking app | Documents, Tags, Sharing preferences |

The principle is universal: **explicit consent, per stream, per session.**

---

## Pricing Philosophy

**Pay-what-you-can, including $0.**

- No reduced features at $0
- No shame, no second-class service
- Users see actual operational costs
- Trust that most people contribute when able

This is not charity. It is alignment. When users pay what they can, they pay what they value. When they pay nothing, they still deserve the same service — because the point is consent and dignity, not revenue extraction.

---

## Governance Framework

SAFE is governed by a set of explicit principles:

| Document | Purpose |
|----------|---------|
| [GOVERNANCE_INDEX](governance/GOVERNANCE_INDEX.md) | Precedence hierarchy |
| [CHARTER](governance/CHARTER.md) | Foundational authority |
| [HARD_STOPS](governance/HARD_STOPS.md) | Absolute boundaries that cannot be overridden |
| [SESSION_CONSENT](governance/SESSION_CONSENT.md) | Complete protocol specification |
| [DUAL_COMMIT](governance/DUAL_COMMIT.md) | Change requires both proposal and ratification |
| [CONTRIBUTOR_PROTOCOL](governance/CONTRIBUTOR_PROTOCOL.md) | How to contribute |

**Dual Commit** means no unilateral changes: someone proposes, someone else ratifies. Neither acts alone.

**Hard Stops** are absolute limits — things the system will never do, regardless of authorization. Example: no collection of data from children without verified parental consent.

---

## Scope

SAFE applies to any application handling personal data. The examples use AI-mediated apps, but the principles are universal:

- Traditional web apps
- Mobile apps
- AI assistants
- IoT devices
- Any system that stores user data

If it asks for data, it should ask every session.

---

Sugested Donation. $1. 

---

## Implementation

### Reference Implementations

| Implementation | Description |
|----------------|-------------|
| [ethical-review-ui](reference-implementations/ethical-review-ui/) | Consent review interface (React/Vite) |
| [aionic-journal](reference-implementations/aionic-journal/) | Journal application (React/Vite) |

### Schemas

| Schema | Purpose |
|--------|---------|
| [RELATIONSHIP_SCHEMA](docs/RELATIONSHIP_SCHEMA.md) | Relationship tracking model |
| [v2.0.0](schemas/v2.0.0/) | JSON schemas for data interchange |

---

## Status

| Component | Status |
|-----------|--------|
| Specification | Stable |
| Reference Implementation | Available |
| Legal Review | Pending |
| Adoption | Open to any project |

---

## License

MIT License for code. CC-BY-NC for documentation.

---

ΔΣ=42
