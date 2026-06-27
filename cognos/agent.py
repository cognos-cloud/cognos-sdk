"""
Agent — the core Cognos Cloud primitive.

Usage:
    from cognos import Agent

    agent = Agent(
        name="my-agent",
        model="gpt-4o",
        memory=True,
        tools=["web", "slack"],
        cron="0 9 * * *",
    )

    agent.deploy()
"""

from __future__ import annotations

from typing import Callable
from .client import CognosClient
from .memory import Memory
from .policy import Policy


class Agent:
    """
    Defines an autonomous AI agent and its deployment configuration.

    Args:
        name:         Unique identifier for this agent. Used in the dashboard URL
                      and API endpoint path.
        model:        LLM model string. Supports OpenAI, Anthropic, Google, and
                      local models via Ollama. Defaults to "gpt-4o".
        memory:       Enable persistent memory across sessions. When True, the
                      agent reads prior context on startup and writes new items
                      after each run. Defaults to False.
        tools:        List of tool names to make available to the agent. Can also
                      accept functions decorated with @tool. Built-in tools:
                      "web", "slack", "github", "discord", "postgresql", "notion",
                      "gmail", "stripe", "solana", "ethereum".
        cron:         Cron expression for scheduled execution. e.g. "0 9 * * *"
                      runs every day at 9am UTC. Optional.
        endpoint:     Custom API path for webhook triggers. e.g. "/webhook/github".
                      Defaults to /agents/{name}/run.
        instructions: System prompt that defines the agent's persona and behaviour.
        policy:       Policy config controlling spending limits, tool permissions,
                      and human approval gates.
    """

    def __init__(
        self,
        name: str,
        model: str = "gpt-4o",
        memory: bool = False,
        tools: list[str | Callable] | None = None,
        cron: str | None = None,
        endpoint: str | None = None,
        instructions: str = "",
        policy: Policy | None = None,
    ):
        self.name         = name
        self.model        = model
        self.memory       = memory
        self.tools        = tools or []
        self.cron         = cron
        self.endpoint     = endpoint
        self.instructions = instructions
        self.policy       = policy
        self._client      = CognosClient()

    # ── Deployment ────────────────────────────────────────────────────────────

    def deploy(self) -> None:
        """
        Package, upload, and start the agent on Cognos Cloud.

        What happens:
          1. Packages the current project directory
          2. Uploads source to Cognos Cloud
          3. Provisions a dedicated runtime container
          4. Attaches memory store if memory=True
          5. Registers tools and cron schedule
          6. Starts the container and runs a health check
          7. Prints the live dashboard URL and API endpoint

        Raises:
            AuthError:    Not logged in. Run `cognos login` first.
            DeployError:  Deployment failed. Check logs with `cognos logs`.
        """
        self._client.deploy(self._payload())

    def start(self) -> None:
        """Start a previously stopped agent."""
        self._client.post(f"/agents/{self.name}/start")

    def stop(self) -> None:
        """Stop a running agent gracefully."""
        self._client.post(f"/agents/{self.name}/stop")

    def restart(self) -> None:
        """Restart the agent runtime."""
        self._client.post(f"/agents/{self.name}/restart")

    def logs(self, tail: int = 100, follow: bool = False) -> None:
        """
        Stream or print logs from the running agent.

        Args:
            tail:   Number of recent log lines to fetch. Defaults to 100.
            follow: If True, stream logs continuously (like `tail -f`).
        """
        self._client.logs(self.name, tail=tail, follow=follow)

    def delete(self) -> None:
        """
        Delete the agent and all associated resources.

        This is irreversible. Memory, logs, and the runtime container
        will be permanently removed.
        """
        self._client.delete(f"/agents/{self.name}")

    # ── Internal ──────────────────────────────────────────────────────────────

    def _payload(self) -> dict:
        tool_names = []
        for t in self.tools:
            if callable(t) and hasattr(t, "_cognos_tool_name"):
                tool_names.append(t._cognos_tool_name)
            elif isinstance(t, str):
                tool_names.append(t)

        return {
            "name":         self.name,
            "model":        self.model,
            "memory":       self.memory,
            "tools":        tool_names,
            "cron":         self.cron,
            "endpoint":     self.endpoint,
            "instructions": self.instructions,
            "policy":       self.policy._payload() if self.policy else None,
        }

    def __repr__(self) -> str:
        return f"Agent(name={self.name!r}, model={self.model!r}, memory={self.memory})"
