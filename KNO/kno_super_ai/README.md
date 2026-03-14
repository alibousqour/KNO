# KNO Super AI — Core scaffold

This directory contains a modular scaffold for the KNO Super AI integration:

- `core/` – FastAPI + WebSocket central brain with Task Dispatcher and Self-Healing Monitor.
- `agents/` – Enhanced multi-platform agent (WebSocket client) that runs on endpoints.
- `bridge/` – IoT bridge modules (MQTT/Home Assistant) to control local smart devices.
- `shared_protocols/` – Pydantic message schemas used between server and agents.

Quick start

1. Create a virtualenv and install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r kno_super_ai/requirements.txt
```

2. Run server:

```bash
uvicorn kno_super_ai.core.server:app --reload --port 8000
```

3. Run agent (example):

```bash
python kno_super_ai/agents/agent_ws.py
```

Security & notes

- The scaffold uses tokens from `.env`. Keep tokens secret and enable TLS for production (wss/https).
- The agent supports file transfers, exec, screenshot, and system control commands. Use an allowlist in production.
