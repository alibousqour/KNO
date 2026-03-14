"""
KNO Remote Agent (Async WebSocket Worker) - Enhanced

Features added:
- Circuit breaker handling (honor server "circuit_break" commands)
- Proactive observer: sends High_Resource_Alert when CPU>85% or RAM>90%
- File chunking for downloads and chunked upload with resume support (offset)
- Throttling for notifications to avoid flooding the server
"""
import asyncio
import aiofiles
import base64
import json
import os
import shlex
import signal
import sys
import time
from pathlib import Path
from typing import Any, Dict

import psutil
import websockets
from dotenv import load_dotenv

load_dotenv()

KNO_SERVER_URL = os.getenv("KNO_SERVER_URL", "ws://localhost:8000/ws")
API_KEY = os.getenv("API_KEY", "demo-key")
AGENT_ID = os.getenv("AGENT_ID", f"agent-{os.uname().nodename if hasattr(os, 'uname') else os.getenv('COMPUTERNAME','pc')}")
ALLOW_SHELL_EXEC = os.getenv("ALLOW_SHELL_EXEC", "false").lower() in ("1", "true", "yes")

HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "20"))
BACKOFF_INITIAL = float(os.getenv("BACKOFF_INITIAL", "2"))
BACKOFF_MAX = float(os.getenv("BACKOFF_MAX", "120"))

# Agent-side circuit breaker state
agent_blocked_until = 0.0
# throttle notifications (seconds)
NOTIFY_THROTTLE = float(os.getenv("NOTIFY_THROTTLE", "10"))
last_notify_ts = 0.0

# file chunk settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", str(64 * 1024)))


async def read_file(path: str) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"error": "not_found"}
    try:
        async with aiofiles.open(p, "rb") as f:
            data = await f.read()
        return {"path": str(p), "data_b64": base64.b64encode(data).decode(), "size": p.stat().st_size}
    except Exception as e:
        return {"error": str(e)}


async def run_subprocess(cmd: str, timeout: int = 30) -> Dict[str, Any]:
    if not ALLOW_SHELL_EXEC:
        try:
            parts = shlex.split(cmd)
        except Exception:
            return {"error": "invalid_command_format"}
        proc = await asyncio.create_subprocess_exec(*parts, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    else:
        proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return {"stdout": "", "stderr": "timeout", "rc": -1}
    return {"stdout": out.decode(errors="ignore"), "stderr": err.decode(errors="ignore"), "rc": proc.returncode}


async def gather_system_stats() -> Dict[str, Any]:
    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.5)
    return {"cpu_percent": cpu, "mem_total": mem.total, "mem_used": mem.used, "mem_percent": mem.percent}


async def handle_command(ws, message: str):
    global agent_blocked_until, last_notify_ts
    try:
        msg = json.loads(message)
    except Exception:
        await ws.send(json.dumps({"type": "error", "error": "invalid_json"}))
        return

    mid = msg.get("id")
    action = msg.get("action")
    payload = msg.get("payload") or {}

    # If agent is under circuit break, ignore most commands
    if time.time() < agent_blocked_until and action not in ("stats", "heartbeat"):
        await ws.send(json.dumps({"id": mid, "type": "error", "error": "agent_blocked"}))
        return

    if action == "read_file":
        path = payload.get("path")
        result = await read_file(path)
        await ws.send(json.dumps({"id": mid, "type": "read_file_result", "result": result}))

    elif action == "write_file":
        # For large uploads, server should use upload_init and upload_chunk messages
        path = payload.get("path")
        data_b64 = payload.get("data_b64")
        append = payload.get("append", False)
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        try:
            async with aiofiles.open(p, "ab" if append else "wb") as f:
                await f.write(base64.b64decode(data_b64))
            await ws.send(json.dumps({"id": mid, "type": "write_file_result", "result": {"path": str(p), "size": p.stat().st_size}}))
        except Exception as e:
            await ws.send(json.dumps({"id": mid, "type": "write_file_result", "result": {"error": str(e)}}))

    elif action == "delete":
        path = payload.get("path")
        p = Path(path)
        try:
            if p.is_dir():
                for child in p.rglob("*"):
                    if child.is_file():
                        child.unlink()
                p.rmdir()
            elif p.exists():
                p.unlink()
            else:
                await ws.send(json.dumps({"id": mid, "type": "delete_result", "result": {"error": "not_found"}}))
                return
            await ws.send(json.dumps({"id": mid, "type": "delete_result", "result": {"deleted": str(p)}}))
        except Exception as e:
            await ws.send(json.dumps({"id": mid, "type": "delete_result", "result": {"error": str(e)}}))

    elif action == "exec":
        cmd = payload.get("cmd")
        timeout = int(payload.get("timeout", 30))
        res = await run_subprocess(cmd, timeout=timeout)
        await ws.send(json.dumps({"id": mid, "type": "exec_result", "result": res}))

    elif action == "stats":
        stats = await gather_system_stats()
        await ws.send(json.dumps({"id": mid, "type": "stats_result", "result": stats}))

    elif action == "download":
        path = Path(payload.get("path"))
        chunk_size = int(payload.get("chunk_size", CHUNK_SIZE))
        if not path.exists():
            await ws.send(json.dumps({"id": mid, "type": "download_result", "error": "not_found"}))
            return
        try:
            with path.open("rb") as f:
                seq = 0
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    msg = {"id": mid, "type": "download_chunk", "seq": seq, "data": base64.b64encode(chunk).decode()}
                    await ws.send(json.dumps(msg))
                    seq += 1
            await ws.send(json.dumps({"id": mid, "type": "download_done", "size": path.stat().st_size}))
        except Exception as e:
            await ws.send(json.dumps({"id": mid, "type": "download_result", "error": str(e)}))

    elif action == "upload_init":
        # Server initiates upload: respond current size
        path = Path(payload.get("path"))
        path.parent.mkdir(parents=True, exist_ok=True)
        cur_size = path.stat().st_size if path.exists() else 0
        await ws.send(json.dumps({"id": mid, "type": "upload_init_ack", "path": str(path), "current_size": cur_size}))

    elif action == "upload_chunk":
        path = Path(payload.get("path"))
        offset = int(payload.get("offset", 0))
        data_b64 = payload.get("data")
        data = base64.b64decode(data_b64)

        def write_at_offset(p, off, bts):
            mode = "r+b" if p.exists() else "wb"
            with open(p, mode) as f:
                f.seek(off)
                f.write(bts)

        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, write_at_offset, path, offset, data)
            if payload.get("final"):
                await ws.send(json.dumps({"id": mid, "type": "upload_done", "path": str(path)}))
            else:
                await ws.send(json.dumps({"id": mid, "type": "upload_chunk_ack", "offset": offset + len(data)}))
        except Exception as e:
            await ws.send(json.dumps({"id": mid, "type": "upload_error", "error": str(e)}))

    elif action == "circuit_break":
        duration = int(payload.get("duration", 60))
        agent_blocked_until = time.time() + duration
        await ws.send(json.dumps({"id": mid, "type": "circuit_ack", "blocked_until": agent_blocked_until}))

    else:
        await ws.send(json.dumps({"id": mid, "type": "error", "error": "unknown_action"}))


async def heartbeat_task(ws):
    while True:
        try:
            await ws.send(json.dumps({"type": "heartbeat", "agent_id": AGENT_ID, "ts": int(time.time())}))
        except Exception:
            break
        await asyncio.sleep(HEARTBEAT_INTERVAL)


async def proactive_observer(ws):
    global last_notify_ts
    while True:
        try:
            cpu = psutil.cpu_percent(interval=0.5)
            mem = psutil.virtual_memory()
            now = time.time()
            if (cpu > 85 or mem.percent > 90) and (now - last_notify_ts >= NOTIFY_THROTTLE):
                last_notify_ts = now
                payload = {"cpu": cpu, "mem_percent": mem.percent}
                msg = {"id": f"alert-{int(time.time())}", "type": "High_Resource_Alert", "payload": payload}
                try:
                    await ws.send(json.dumps(msg))
                except Exception:
                    pass
        except Exception:
            pass
        await asyncio.sleep(5)


async def connect_and_listen():
    url = f"{KNO_SERVER_URL}/{AGENT_ID}"
    headers = [("X-API-KEY", API_KEY), ("X-Agent-Id", AGENT_ID)]
    backoff = BACKOFF_INITIAL
    while True:
        try:
            async with websockets.connect(url, extra_headers=headers, ping_interval=None) as ws:
                await ws.send(json.dumps({"type": "hello", "agent_id": AGENT_ID, "meta": {"platform": sys.platform}}))
                hb = asyncio.create_task(heartbeat_task(ws))
                observer = asyncio.create_task(proactive_observer(ws))

                async for message in ws:
                    asyncio.create_task(handle_command(ws, message))

                hb.cancel()
                observer.cancel()
        except Exception as e:
            print(f"[remote_agent] connection error: {e} — reconnecting in {backoff}s")
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, BACKOFF_MAX)


def run():
    try:
        asyncio.run(connect_and_listen())
    except KeyboardInterrupt:
        print("Agent stopped by user")


if __name__ == "__main__":
    run()
