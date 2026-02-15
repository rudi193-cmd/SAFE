# SAFE Quick Start Guide

Welcome to the SAFE (Session Consent Framework for Endpoints) ecosystem, a secure and private way to manage user data and consent. In this quick start guide, we'll walk you through the basics of SAFE and get you started with your journey.

### What is SAFE?

SAFE is a session-based consent framework designed to make it easy for users to grant and revoke access to their data. It's built on top of a cryptographic hash table (CHT), ensuring that all data are encrypted and linked to user consent. This framework streamlines data management and protects user rights while promoting transparency.

### Getting Started: Register and Authenticate

To begin, you'll need to register and authenticate with SAFE. You can do this by sending a GET request to the `/api/auth/register` endpoint. This endpoint will guide you through the registration process. 

In the request body, send the required fields, such as 
**email, password, name (first_name , last_name),** etc.

```bash
GET https://example.com/api/auth/register HTTP/1.1
Content-Type: application/json

{
    "email": "example@example.com",
    "password": "strongpassword",
    "name": {
        "first_name": "John",
        "last_name": "Doe"
    }
}
```
After completing the registration and authentication process, you'll receive a verification email with a verification link.

### Consent in SAFE

In SAFE, users hold sole decision-making power over their data. Consent is explicit, per-session, and can be revoked at any time. 

When you request access to a user's data, you'll be presented with options to accept or decline access. This ensures that users have complete control over their data, and the user itself, retains all decision power. 

On every request access to user data you generate a signed session id that will be stored and updated on user device.


### User Rights

As a user, you have the right to:

- **Zero retention**: SAFE does not store any data for extended periods.
- **Data deletion**: Safely delete data at any time, with the option to undelete within a specified time frame.
- **Export data**: Export data at any time, giving you control over data reuse and distribution.
- **Audit logs**: Access detailed logs of all data access and consent events.
- **Revoke access**: Revoke consent at any time, restricting access to your data.

### Next Steps: Dive into SAFE Governance

The SAFE framework is governed by a set of policies and guidelines. To truly understand the SAFE ecosystem and your place within it, we recommend:

- Delving into the SAFE Governance Document
- Exploring best practices for integrating SAFE into your own ecosystem
- Participating in online communities and forums to collaborate with fellow SAFE developers

That's a quick start guide to the SAFE ecosystem! We're excited to have you on board. Stay informed and advocate for data ownership and consent in our collective journey to protect user rights.