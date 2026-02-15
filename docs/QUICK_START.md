# SAFE Quick Start Guide

## What SAFE Is

SAFE (Session-Authorized, Fully Explicit) is a consent framework that replaces perpetual data agreements with session-based permissions. Instead of clicking "I Agree" once and granting permanent access, you authorize data access at the start of each session. When you close the app, those permissions expire.

This is intentionally inconvenient. Consent should require intention.

## How to Register

Register a new account:

```bash
POST /api/auth/register
{
  "username": "your-username",
  "password": "your-secure-password",
  "user_type": "human"
}
```

Then login:

```bash
POST /api/auth/login
{
  "username": "your-username",
  "password": "your-password"
}
```

You'll receive a JWT token. Include it in subsequent requests:
```
Authorization: Bearer <your-token>
```

## How Consent Works

1. **Start Session** — App requests specific permissions (contacts, location, documents, etc.)
2. **You Decide** — Grant or deny each permission individually
3. **During Session** — App only accesses authorized data
4. **End Session** — All permissions expire, data deleted unless explicitly saved
5. **Tomorrow** — App asks again. You might say yes, you might say no.

Each session is a fresh decision.

## Your Rights

1. **Zero Retention** — Decline all data storage
2. **Deletion** — Complete removal on request
3. **Export** — All your data in readable format
4. **Audit** — View exactly what the system knows about you
5. **Revoke** — Withdraw authorization mid-session

These aren't suggestions. They're guarantees.

## Next Steps

- Read the [governance framework](../governance/GOVERNANCE_INDEX.md)
- Review [hard stops](../governance/HARD_STOPS.md) (absolute boundaries)
- Explore [session consent protocol](../governance/SESSION_CONSENT.md)
- Check [reference implementations](../reference-implementations/)

---

**Suggested Donation:** $1
**Pay what you can, including $0.**

ΔΣ=42
