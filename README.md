# Auth0 AI Tester

A testing application for Auth0 for AI Agents and LangChain.

## Prerequisites

- [Auth0](https://auth0.com/ai) Tenant
- [OpenAI](https://openai.com/) API Key
- [Tavily](https://www.tavily.com/) API Key

### Auth0 Tenant Setup

- Create a Regular Web Application.
  - Alllowed Callback URLs: `http://localhost:8000/auth/callback`
  - Allowed Logout URLs: `http://localhost:8000/`
  - Advanced > Grant Types: `Authorization Code`, `Refresh Token`, `Client Initiated Backchannel Authentication (CIBA)`, `Token Vault`
  - Connection: `Username-Password-Authentication` database
- Create an API.
  - Identifier: `https://api.test/`
  - Allow Offline Access: `true`
  - Permission: `test:ciba` (Test Client Initiated Backchannel Authentication (CIBA))
- Create a test user in `Username-Password-Authentication` database.
  - Enroll [Auth0 Guardian (Push Notification) MFA](https://auth0.com/docs/secure/multi-factor-authentication/auth0-guardian)
  - Permission: `test:ciba`

## Quickstart

- Rename `.env.example` to `.env` and fill in the required values.
  - See [auth0-fastapi](https://github.com/auth0/auth0-fastapi) to learn about the Auth0-related values.
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `cd app`
- `langgraph dev`
- `python app.py`
