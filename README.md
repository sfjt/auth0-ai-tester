# Auth0 AI Tester

A testing application for Auth0 for AI Agents and LangChain.

## Prerequisites

- [OpenAI](https://openai.com/) API Key
- [Auth0](https://auth0.com/ai) Tenant
- [Tavily](https://www.tavily.com/) API Key

## Quickstart

- Rename `.env.example` to `.env` and fill in the required values.
  - See [auth0-fastapi](https://github.com/auth0/auth0-fastapi) to learn about the Auth0-related values.
- `python -m venv .venv`
- `source .venv/bin/activate`
- `pip install -r requirements.txt`
- `python -m app`
