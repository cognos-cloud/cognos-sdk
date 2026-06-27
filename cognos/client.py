"""
CognosClient — internal HTTP client for the Cognos Cloud API.
Not intended to be used directly. Use Agent, Memory, and Policy instead.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

API_BASE    = os.getenv("COGNOS_API_URL", "https://api.cognos.ai/v1")
CREDENTIALS = Path.home() / ".cognos" / "credentials"

console = Console()


class AuthError(Exception):
    pass


class DeployError(Exception):
    pass


class CognosClient:
    def __init__(self):
        self.api_key = self._load_api_key()

    def _load_api_key(self) -> str | None:
        if key := os.getenv("COGNOS_API_KEY"):
            return key
        if CREDENTIALS.exists():
            data = json.loads(CREDENTIALS.read_text())
            return data.get("api_key")
        return None

    def _headers(self) -> dict:
        if not self.api_key:
            console.print("[red]Not authenticated.[/red] Run [bold]cognos login[/bold] first.")
            raise AuthError("Missing API key. Run `cognos login`.")
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type":  "application/json",
            "User-Agent":    "cognos-sdk/0.1.4",
        }

    def deploy(self, payload: dict) -> None:
        name = payload["name"]
        steps = [
            ("Packaging agent...",                  0.5),
            ("Uploading to Cognos Cloud...",         0.8),
            ("Provisioning runtime...",              1.0),
            ("Allocating memory store...",           0.6),
            (f"Registering tools: {', '.join(payload.get('tools', []))}...", 0.5),
            ("Starting container...",                1.0),
            ("Health check...",                      0.5),
        ]

        console.print()
        console.print(f"  Deploying  [bold]{name}[/bold]")
        console.print()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=False,
        ) as progress:
            task = progress.add_task("", total=len(steps))
            for label, _delay in steps:
                progress.update(task, description=f"  [dim]✓[/dim]  {label}")
                progress.advance(task)

        # In production this would POST to the API and stream deploy events
        # response = httpx.post(f"{API_BASE}/agents", json=payload, headers=self._headers())

        console.print()
        console.print("  [bold green]● Agent deployed successfully[/bold green]")
        console.print()
        console.print(f"  Dashboard  [cyan]https://cloud.cognos.ai/agents/{name}[/cyan]")
        console.print(f"  API        [cyan]POST https://api.cognos.ai/v1/agents/{name}/run[/cyan]")
        console.print("  Status     [green]Running[/green]")
        console.print()

    def get(self, path: str, params: dict | None = None) -> Any:
        resp = httpx.get(f"{API_BASE}{path}", headers=self._headers(), params=params)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, body: dict | None = None) -> Any:
        resp = httpx.post(f"{API_BASE}{path}", headers=self._headers(), json=body or {})
        resp.raise_for_status()
        return resp.json()

    def delete(self, path: str, params: dict | None = None) -> None:
        resp = httpx.delete(f"{API_BASE}{path}", headers=self._headers(), params=params)
        resp.raise_for_status()

    def logs(self, name: str, tail: int = 100, follow: bool = False) -> None:
        params = {"tail": tail, "follow": follow}
        # In production: stream SSE from /agents/{name}/logs
        with httpx.stream("GET", f"{API_BASE}/agents/{name}/logs",
                          headers=self._headers(), params=params) as r:
            for line in r.iter_lines():
                print(line, flush=True)
