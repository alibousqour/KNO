from pydantic import BaseModel
from typing import Any, Dict, Optional


class AgentHello(BaseModel):
    type: str = "hello"
    agent_id: str
    meta: Optional[Dict[str, Any]] = None


class Heartbeat(BaseModel):
    type: str = "heartbeat"
    agent_id: str
    ts: int


class DispatchMessage(BaseModel):
    id: str
    type: str  # e.g., exec, download, upload, restart
    target: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class ExecResult(BaseModel):
    id: str
    type: str = "exec_result"
    stdout: Optional[str]
    stderr: Optional[str]
    rc: int
