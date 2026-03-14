#!/usr/bin/env python3
"""Simple dispatch CLI to send tasks to the central KNO server.

Usage examples:
  python tools/dispatch.py --server http://localhost:8000 --target agent-1 --action exec --cmd "whoami"
  python tools/dispatch.py --server http://localhost:8000 --target agent-1 --action stats
"""
import argparse
import json
import time
import uuid
import requests


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--server", required=True, help="KNO server base URL, e.g. http://localhost:8000")
    p.add_argument("--target", required=True, help="Agent ID target")
    p.add_argument("--action", required=True, choices=["exec", "read_file", "write_file", "delete", "stats"], help="Action to dispatch")
    p.add_argument("--cmd", help="Command for exec")
    p.add_argument("--path", help="Path for file ops")
    p.add_argument("--data_b64", help="Base64 data for write_file")
    p.add_argument("--api-key", help="API key for server auth header")
    args = p.parse_args()

    payload = {"id": str(uuid.uuid4()), "type": "dispatch", "target": args.target, "payload": {}}
    if args.action == "exec":
        payload["type"] = "dispatch"
        payload["action"] = "exec"
        payload["payload"] = {"cmd": args.cmd}
    elif args.action == "stats":
        payload["action"] = "stats"
        payload["payload"] = {}
    elif args.action == "read_file":
        payload["action"] = "read_file"
        payload["payload"] = {"path": args.path}
    elif args.action == "write_file":
        payload["action"] = "write_file"
        payload["payload"] = {"path": args.path, "data_b64": args.data_b64}
    elif args.action == "delete":
        payload["action"] = "delete"
        payload["payload"] = {"path": args.path}

    url = args.server.rstrip("/") + "/dispatch"
    headers = {"Content-Type": "application/json"}
    if args.api_key:
        headers["X-API-KEY"] = args.api_key

    resp = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        print(resp.status_code, resp.json())
    except Exception:
        print(resp.status_code, resp.text)


if __name__ == "__main__":
    main()
