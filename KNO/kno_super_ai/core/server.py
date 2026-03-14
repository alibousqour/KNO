import asyncio
import json
import logging
import os
import time
from collections import deque
from typing import Dict, Optional

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from kno_super_ai.shared_protocols.protocols import DispatchMessage

log = logging.getLogger("kno_super_ai.core")
logging.basicConfig(level=logging.INFO)

# API key expected by agents
SERVER_API_KEY = os.getenv("KNO_API_KEY", "")
# Rate limiting / circuit breaker settings
DISPATCH_RATE_LIMIT = int(os.getenv("DISPATCH_RATE_LIMIT", "20"))
DISPATCH_RATE_WINDOW = int(os.getenv("DISPATCH_RATE_WINDOW", "60"))
DISPATCH_BLOCK_SECONDS = int(os.getenv("DISPATCH_BLOCK_SECONDS", "300"))

# Failed auth blocking by IP
AUTH_FAIL_THRESHOLD = int(os.getenv("AUTH_FAIL_THRESHOLD", "5"))
AUTH_BLOCK_SECONDS = int(os.getenv("AUTH_BLOCK_SECONDS", "300"))

# runtime structures
dispatch_history: Dict[str, deque] = {}  # target -> deque of timestamps
blocked_targets: Dict[str, float] = {}  # target -> unblock_ts
failed_auth: Dict[str, Dict] = {}  # ip -> {count, until}
blocked_ips: Dict[str, float] = {}

app = FastAPI(title="KNO Super AI - Central Brain")


class ConnectionManager:
    def __init__(self):
        # agent_id -> websocket
        self.active: Dict[str, WebSocket] = {}
        self.meta: Dict[str, Dict] = {}

        async def connect(self, agent_id: str, websocket: WebSocket):
            await websocket.accept()
            self.active[agent_id] = websocket
            self.meta[agent_id] = {"last_seen": time.time(), "state": "connected"}
            log.info(f"Agent connected: {agent_id}")

    def disconnect(self, agent_id: str):
        if agent_id in self.active:
            del self.active[agent_id]
        self.meta[agent_id] = {"last_seen": time.time(), "state": "disconnected"}
        log.info(f"Agent disconnected: {agent_id}")

    async def send_to(self, agent_id: str, message: Dict):
        ws = self.active.get(agent_id)
        if not ws:
            raise LookupError("Agent not connected")
        await ws.send_text(json.dumps(message))


manager = ConnectionManager()


@app.websocket("/ws/{agent_id}")
async def agent_ws(websocket: WebSocket, agent_id: str):
    # Validate API key from header `X-API-KEY`
    try:
        # headers available before accept in Starlette WebSocket
        provided_key = websocket.headers.get("x-api-key")
        client_ip = websocket.client.host if websocket.client else None
        # check blocked ip
        if client_ip and blocked_ips.get(client_ip, 0) > time.time():
            log.warning(f"Blocking connection from blocked IP {client_ip}")
            await websocket.close(code=4003)
            return
        if SERVER_API_KEY:
            if not provided_key or provided_key != SERVER_API_KEY:
                log.warning(f"Rejected connection for {agent_id}: invalid API key from {websocket.client}")
                # increment failed auth for IP
                client_ip = websocket.client.host if websocket.client else None
                if client_ip:
                    entry = failed_auth.setdefault(client_ip, {"count": 0, "until": 0})
                    entry["count"] += 1
                    if entry["count"] >= AUTH_FAIL_THRESHOLD:
                        blocked_ips[client_ip] = time.time() + AUTH_BLOCK_SECONDS
                        entry["until"] = blocked_ips[client_ip]
                        log.warning(f"IP {client_ip} blocked until {entry['until']}")
                await websocket.close(code=4003)
                return

        await manager.connect(agent_id, websocket)
        while True:
            try:
                text = await websocket.receive_text()
            except WebSocketDisconnect:
                manager.disconnect(agent_id)
                break
            except Exception:
                manager.disconnect(agent_id)
                break
            # update last_seen
            manager.meta.setdefault(agent_id, {})["last_seen"] = time.time()
            # simple logging and echo
            log.debug(f"RX from {agent_id}: {text}")
    finally:
        manager.disconnect(agent_id)


@app.get("/agents")
async def list_agents():
    """Return connected agents metadata."""
    return JSONResponse({"connected": list(manager.active.keys()), "meta": manager.meta})


class DispatchRequest(BaseModel):
    id: str
    type: str
    target: Optional[str]
    payload: Optional[dict]
    action: Optional[str]


@app.post("/dispatch")
async def dispatch_task(req: DispatchRequest, request: Request):
    # Basic API key validation for HTTP dispatch
    provided_key = request.headers.get("x-api-key")
    client_ip = request.client.host if request.client else None
    if SERVER_API_KEY:
        if not provided_key or provided_key != SERVER_API_KEY:
            # increment failed auth for IP
            if client_ip:
                entry = failed_auth.setdefault(client_ip, {"count": 0, "until": 0})
                entry["count"] += 1
                if entry["count"] >= AUTH_FAIL_THRESHOLD:
                    blocked_ips[client_ip] = time.time() + AUTH_BLOCK_SECONDS
                    entry["until"] = blocked_ips[client_ip]
                    log.warning(f"IP {client_ip} blocked until {entry['until']}")
            raise HTTPException(status_code=403, detail="invalid_api_key")

    if not req.target:
        raise HTTPException(status_code=400, detail="Missing target agent")

    # Rate limit by target
    now = time.time()
    # cleanup expired blocks
    if blocked_targets.get(req.target, 0) > now:
        return JSONResponse({"status": "blocked", "target": req.target, "until": blocked_targets[req.target]})

    dq = dispatch_history.setdefault(req.target, deque())
    # remove timestamps outside window
    while dq and dq[0] < now - DISPATCH_RATE_WINDOW:
        dq.popleft()
    dq.append(now)
    if len(dq) > DISPATCH_RATE_LIMIT:
        blocked_targets[req.target] = now + DISPATCH_BLOCK_SECONDS
        # attempt to notify the agent to enter circuit-break state
        try:
            ctrl_msg = {"id": f"ctrl-{int(time.time())}", "type": "control", "action": "circuit_break", "payload": {"duration": DISPATCH_BLOCK_SECONDS}}
            await manager.send_to(req.target, ctrl_msg)
        except Exception:
            pass
        return JSONResponse({"status": "rate_limited", "target": req.target, "blocked_until": blocked_targets[req.target]})

    msg = {"id": req.id, "type": req.type, "action": req.action, "payload": req.payload}
    try:
        await manager.send_to(req.target, msg)
    except LookupError:
        return JSONResponse({"status": "agent_offline", "target": req.target})
    return JSONResponse({"status": "sent", "target": req.target})


@app.get("/blocks")
async def get_blocks():
    return JSONResponse({"blocked_targets": blocked_targets, "blocked_ips": blocked_ips})


async def self_healing_monitor(interval: int = 15):
    # Periodically examine manager.meta, log agents offline for > threshold
    while True:
        now = time.time()
        for aid, info in list(manager.meta.items()):
            last = info.get("last_seen", 0)
            if info.get("state") == "connected" and now - last > 60:
                log.warning(f"Agent {aid} appears offline (last_seen={last}) - marking disconnected")
                manager.meta[aid]["state"] = "suspected_offline"
        await asyncio.sleep(interval)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(self_healing_monitor())
    log.info("Self-healing monitor started")

# mount static dashboard
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    @app.get("/")
    async def index():
        return FileResponse(os.path.join(static_dir, "index.html"))
