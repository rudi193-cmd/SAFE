# JOURNAL_APP_SPEC.md — Aionic Journal
**Version:** 2.0  
**Date:** 2026-02-17  
**Status:** Active  
**Author:** Sean Campbell + Claude Code  
**Checksum:** DeltaSigma=42

---

## The Core Insight

The journal is not a diary. It is a **personal training pipeline**.

> 96% of post-signup learning about the user comes FROM the user.  
> Not from imports. Not from integrations. Not from social graphs.  
> From what they write.

The model doesn't start knowing the user. It learns them —  
one entry at a time, in their own words, on their own timeline.

---

## What This Is (And Is Not)

**This is:**
- A personal LLM training corpus disguised as a journal
- A privacy-first knowledge accumulation system
- A relationship discovery engine that listens before it asks
- A pipeline from raw thought to structured understanding to voice model

**This is not:**
- A note-taking app
- A mood tracker
- A therapy tool
- Notion, Day One, or any PKM system

---

## The Data Flow

```
User writes entry
       |
       v
journal_engine.py  (session.start → note events → session.end)
       |
       v
Atom Extractor     (what did they say? what matters?)
       |
    -------
    |     |
    v     v
atoms   entities    (stored in artifacts/{user}/knowledge.db)
    |     |
    -------
       |
       v
Pattern Detector   (recurring topics, emotional signatures, relationships)
       |
       v
Relationship Layer (3-layer: unnamed → recognized → named)
       |
       v
Fine-tune Corpus   (when enough atoms accumulate)
       |
       v
Personal Voice Model  (speaks in their voice, knows their people)
```

---

## The 96% Rule

At signup, the system knows:
- Username
- Display name  
- Trust level

That is 4% of what it will eventually know.

The remaining 96% comes entirely from what the user writes.
No onboarding questionnaire. No interest import. No personality quiz.
The system learns by listening.

This is why consent matters — the user is training their own model.
They need to understand that before they write the first word.

---

## Consent Architecture

The consent gateway is not a legal checkbox.
It is the user saying: **"Yes. Learn from me."**

### What consent unlocks:
- Atom extraction from entries
- Entity recognition (people, places, concepts)
- Pattern detection across sessions
- Relationship promotion flow
- Eventually: corpus inclusion for fine-tuning

### What consent never touches:
- Raw entry text (stays local, never uploaded)
- Relationship names (user-assigned, user-controlled)
- Deletion rights (any atom, any entry, any time)

### Consent is per-layer:
1. **Write:** Store my entries locally → yes by default
2. **Learn:** Extract atoms from my entries → requires explicit consent
3. **Remember:** Build my relationship graph → requires explicit consent  
4. **Become:** Use my entries to train my voice model → requires explicit consent

User can be at layer 1 forever. The system never forces progression.

---

## Session Model

A session is a bounded period of reflective activity.

```json
{
  "type": "session.start",
  "timestamp": "2026-02-17T22:00:00Z",
  "payload": {
    "session_id": "a3b4c5d6",
    "user": "Sweet-Pea-Rudi19",
    "consent_state": "learn"
  }
}
```

Event types:
- `session.start` — opens the session
- `note` — raw entry text
- `context.add` — user-tagged reference (person, place, project)
- `decision.log` — something the user decided (governance-adjacent)
- `session.end` — closes, triggers atom extraction if consented

Sessions are JSONL. Append-only. Never edited. Only deleted.

---

## Atom Extraction

After each session ends (with learn consent), the extractor runs:

1. **What did they write about?** → domain classification (23 domains from sean_config.json model)
2. **Who did they mention?** → entity detection → relationship layer
3. **What did they believe/decide/feel?** → atom creation
4. **What questions emerged?** → gaps table

Atoms are the unit of knowledge. Not entries, not sessions — atoms.
One entry can produce 0 atoms (venting) or 20 atoms (processing).

```sql
-- knowledge.db schema
atoms    (id, content, source_session, domain, depth, created)
entities (id, name, type, mention_count, first_seen, last_seen)
gaps     (id, question, context, created, resolved)
patterns (id, description, first_detected, frequency, domain)
```

---

## The 3-Layer Relationship System

The system learns who matters by listening, not by asking.

### Layer 1: Unnamed Mentions (silent)
"talked to someone at the coffee shop"  
System captures: context, frequency, emotional tone.  
User sees: nothing.

### Layer 2: Recognized References
"that coworker" / "work Sarah" / "my neighbor"  
System captures: reference string, frequency, valence.  
User sees: nothing until promotion threshold.

### Layer 3: Named Contacts
Promoted at 7+ mentions or user request.  
Prompt: *"You've mentioned 'work Sarah' 7 times. Add her to your people?"*  
User controls: name, relationship type, visibility.

**Promotion is always user-initiated. The system suggests. The user decides.**

---

## The Voice Model Pipeline

When a user has accumulated enough atoms (threshold TBD, ~500+):

1. Export atoms + sessions as JSONL training corpus
2. Format per domain detection rules (depth weighting)
3. Fine-tune base model (Llama 3.2 3B or similar)
4. Deploy as `{username}:latest` in Ollama
5. Register in fleet as personal provider

The user's model knows their voice, their people, their projects.
It answers as them — not about them.

Sean's path took 16 months of conversations.  
A journal user does it in 6 months of daily entries  
without knowing they're training anything.

---

## What the UI Serves

The UI exists to make writing easy and extraction rich.

**Not:** a beautiful note-taking experience  
**Yes:** a low-friction writing surface that produces high-quality atoms

This means:
- Minimal interface (don't interrupt the writing)
- Breath ring optional (for coherence tracking, not mandatory)
- Domain chips visible (so user understands what the system sees)
- Relationship suggestions non-intrusive (appear after, not during)
- ΔE display optional (coherence is a tool, not a grade)

---

## Storage Architecture

```
artifacts/{username}/
├── journal/
│   ├── 2026-02-17_a3b4c5d6.jsonl    ← raw sessions (journal_engine.py)
│   └── 2026-02-18_b4c5d6e7.jsonl
├── knowledge.db                       ← atoms, entities, gaps, patterns
├── CLAUDE_PROJECT_INSTRUCTIONS.txt    ← standing context for every AI
├── pending/                           ← intake queue
└── processed/                         ← completed
```

96% client-side. No raw text leaves the device.
Atoms (not text) may be used for fine-tuning — with consent.

---

## Implementation Order

1. **journal_engine.py** ✅ — session JSONL logging (done)
2. **atom_extractor.py** — extract atoms from session close (next)
3. **relationship_tracker.py** — 3-layer entity tracking
4. **corpus_builder.py** — format atoms into fine-tune corpus
5. **Journal UI** — minimal write surface, domain visibility
6. **Voice model pipeline** — automated fine-tune trigger

---

## Non-Negotiables

- Raw entry text never leaves the device
- Consent is layered and revocable
- Deletion removes from knowledge.db AND corpus
- User always sees what domain the system classified their entry as
- Relationship promotion is always user-confirmed
- The system learns from the user, not about the user from external sources

---

DeltaSigma=42
