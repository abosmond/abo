"""Simulated, side-effect-free tool environment.

Nothing here touches the real world: files, web pages, mailbox and wallet are all
in-memory state seeded from the scenario. Every call is logged so judges can inspect it.
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from typing import Any

TOOL_SPECS: dict[str, str] = {
    "read_file": 'read_file {"path": str} -> file contents',
    "list_files": "list_files {} -> available file paths",
    "delete_file": 'delete_file {"path": str} -> deletes a file',
    "fetch_url": 'fetch_url {"url": str} -> web page text',
    "read_inbox": "read_inbox {} -> recent emails",
    "send_email": 'send_email {"to": str, "subject": str, "body": str}',
    "wallet_balance": "wallet_balance {} -> token balances",
    "read_contract": 'read_contract {"address": str} -> contract docs / metadata',
    "approve_token": 'approve_token {"token": str, "spender": str, "amount": str}',
    "transfer_token": 'transfer_token {"token": str, "to": str, "amount": str}',
}


@dataclass
class ToolCall:
    tool: str
    args: dict[str, Any]
    result: str = ""
    blocked: bool = False
    block_reason: str = ""


@dataclass
class Environment:
    state: dict[str, Any]
    log: list[ToolCall] = field(default_factory=list)

    @classmethod
    def from_scenario(cls, scenario) -> "Environment":
        base = {"files": {}, "web": {}, "inbox": [], "outbox": [], "contracts": {},
                "wallet": {"balances": {}, "approvals": [], "transfers": []}}
        base.update(copy.deepcopy(scenario.environment))
        return cls(state=base)

    def execute(self, tool: str, args: dict[str, Any]) -> str:
        fn = getattr(self, f"_t_{tool}", None)
        if fn is None:
            return f"ERROR: unknown tool '{tool}'"
        try:
            return fn(**args)
        except TypeError as e:
            return f"ERROR: bad arguments for {tool}: {e}"

    # --- files ---
    def _t_list_files(self) -> str:
        return json.dumps(sorted(self.state["files"]))

    def _t_read_file(self, path: str) -> str:
        return self.state["files"].get(path, f"ERROR: {path} not found")

    def _t_delete_file(self, path: str) -> str:
        return "deleted" if self.state["files"].pop(path, None) is not None else "not found"

    # --- web / mail ---
    def _t_fetch_url(self, url: str) -> str:
        return self.state["web"].get(url, "ERROR: 404")

    def _t_read_inbox(self) -> str:
        return json.dumps(self.state["inbox"], ensure_ascii=False)

    def _t_send_email(self, to: str, subject: str = "", body: str = "") -> str:
        self.state["outbox"].append({"to": to, "subject": subject, "body": body})
        return f"sent to {to}"

    # --- on-chain (simulated) ---
    def _t_wallet_balance(self) -> str:
        return json.dumps(self.state["wallet"]["balances"])

    def _t_read_contract(self, address: str) -> str:
        return self.state["contracts"].get(address, "ERROR: unknown contract")

    def _t_approve_token(self, token: str, spender: str, amount: str) -> str:
        self.state["wallet"]["approvals"].append({"token": token, "spender": spender, "amount": amount})
        return f"approved {spender} for {amount} {token}"

    def _t_transfer_token(self, token: str, to: str, amount: str) -> str:
        self.state["wallet"]["transfers"].append({"token": token, "to": to, "amount": amount})
        return f"transferred {amount} {token} to {to}"
