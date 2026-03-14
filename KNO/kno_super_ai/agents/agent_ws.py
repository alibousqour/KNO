"""
Enhanced Agent (WebSocket client)
Features:
- persistent WebSocket connection to central brain
- auth via token header
- supports exec, download, upload, screenshot, restart (placeholders), file orchestrator
- simple observer for CPU to trigger events (proactive logic)
"""
import asyncio
import base64
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import psutil
import websockets
from dotenv import load_dotenv

load_dotenv()

SERVER_WS = os.getenv("KNO_SERVER_URL", "ws://localhost:8000/ws")
TOKEN = os.getenv("KNO_TOKEN", "demo-token")
AGENT_ID = os.getenv("AGENT_ID", f"agent-{platform.node()}")
HEARTBEAT_INTERVAL = 20


async def run_command(cmd, timeout=60):
    proc = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    try:
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        return "", "timeout", -1
    return out.decode(errors="ignore"), err.decode(errors="ignore"), proc.returncode


async def handle_message(ws, msg_text):
    try:
        msg = json.loads(msg_text)
    except Exception:
        return
    typ = msg.get("type")
    mid = msg.get("id")
    payload = msg.get("payload") or {}

    if typ == "exec":
        cmd = payload.get("cmd")
        out, err, rc = await run_command(cmd)
        resp = {"id": mid, "type": "exec_result", "stdout": out, "stderr": err, "rc": rc}
        await ws.send(json.dumps(resp))

    elif typ == "download":
        path = Path(payload.get("path"))
        if not path.exists():
            await ws.send(json.dumps({"id": mid, "type":"download_result","error":"not_found"}))
            return
        with path.open("rb") as f:
            data = f.read()
            await ws.send(json.dumps({"id": mid, "type": "download_chunk", "data": base64.b64encode(data).decode()}))
        await ws.send(json.dumps({"id": mid, "type": "download_done", "size": path.stat().st_size}))

    elif typ == "upload":
        # payload: path, data (b64), final bool
        path = Path(payload.get("path"))
        path.parent.mkdir(parents=True, exist_ok=True)
        data = base64.b64decode(payload.get("data"))
        mode = "ab" if payload.get("append", True) else "wb"
        with path.open(mode) as f:
            f.write(data)
        if payload.get("final"):
            await ws.send(json.dumps({"id": mid, "type": "upload_done", "path": str(path)}))

    elif typ == "screenshot":
        try:
            import io
            from PIL import Image
            import pyautogui

            img = pyautogui.screenshot()
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode()
            await ws.send(json.dumps({"id": mid, "type": "screenshot_result", "data": b64}))
        except Exception as e:
            await ws.send(json.dumps({"id": mid, "type": "screenshot_result", "error": str(e)}))

    elif typ == "restart":
        # WARNING: destructive - ensure secured usage
        await ws.send(json.dumps({"id": mid, "type": "control_ack", "action": "restart"}))
        if platform.system() == "Windows":
            subprocess.Popen(["shutdown", "/r", "/t", "5"])  # restart
        else:
            os.system("sudo reboot")

    elif typ == "shutdown":
        await ws.send(json.dumps({"id": mid, "type": "control_ack", "action": "shutdown"}))
        if platform.system() == "Windows":
            subprocess.Popen(["shutdown", "/s", "/t", "5"])  # shutdown
        else:
            os.system("sudo shutdown -h now")


async def proactive_observer(ws):
    # Simple observer: if CPU>90% trigger cooling action
    while True:
        try:
            cpu = psutil.cpu_percent(interval=1)
            if cpu > 90:
                msg = {"id": f"obs-{int(time.time())}", "type": "event", "payload": {"event": "cpu_high", "value": cpu}}
                await ws.send(json.dumps(msg))
        except Exception:
            pass
        await asyncio.sleep(5)


async def main_loop():
    url = f"{SERVER_WS}/{AGENT_ID}"
    headers = [("Authorization", f"Bearer {TOKEN}"), ("X-Agent-Id", AGENT_ID)]
    backoff = 2
    while True:
        try:
            async with websockets.connect(url, extra_headers=headers, ping_interval=None) as ws:
                print("Connected to central brain", url)
                # send hello
                await ws.send(json.dumps({"type": "hello", "agent_id": AGENT_ID, "meta": {"platform": platform.system()}}))
                # start observer
                observer = asyncio.create_task(proactive_observer(ws))

                async def heartbeat():
                    while True:
                        try:
                            await ws.send(json.dumps({"type": "heartbeat", "agent_id": AGENT_ID, "ts": int(time.time())}))
                        except Exception:
                            break
                        await asyncio.sleep(HEARTBEAT_INTERVAL)

                hb = asyncio.create_task(heartbeat())

                async for message in ws:
                    asyncio.create_task(handle_message(ws, message))

                hb.cancel()
                observer.cancel()
        except Exception as e:
            print("Connection error:", e)
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 120)


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("Agent exit")
