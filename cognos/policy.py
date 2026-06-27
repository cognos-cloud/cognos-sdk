"""
Policy — governance and security layer for Cognos Cloud agents.

Status: Coming Soon — basic spending limits are live.
Full RBAC and approval workflows are in development.

Usage:
    from cognos import Agent, Policy

    agent = Agent(
        name="finance-agent",
        policy=Policy(
            max_spend_per_day=10.00,
            require_human_approval=["send_payment", "delete_record"],
            allowed_tools=["stripe", "slack"],
        )
    )
"""

from __future__ import annotations


class Policy:
    """
    Defines what an agent is allowed to do.

    Args:
        max_spend_per_day:       Maximum USD spend on LLM calls per day.
                                  Agent pauses and alerts if exceeded.
        max_spend_per_run:       Maximum USD spend per single execution.
        require_human_approval:  List of tool names that require a human
                                  to approve before execution.
        allowed_tools:           Allowlist of tool names. If set, the agent
                                  cannot call any tool not in this list.
        blocked_tools:           Blocklist of tool names the agent can never call.
        allowed_domains:         Restrict web tool to specific domains only.
        max_runs_per_hour:       Rate limit on executions. Useful for webhook
                                  agents that could be triggered excessively.
    """

    def __init__(
        self,
        max_spend_per_day:       float | None = None,
        max_spend_per_run:       float | None = None,
        require_human_approval:  list[str] | None = None,
        allowed_tools:           list[str] | None = None,
        blocked_tools:           list[str] | None = None,
        allowed_domains:         list[str] | None = None,
        max_runs_per_hour:       int | None = None,
    ):
        self.max_spend_per_day      = max_spend_per_day
        self.max_spend_per_run      = max_spend_per_run
        self.require_human_approval = require_human_approval or []
        self.allowed_tools          = allowed_tools
        self.blocked_tools          = blocked_tools or []
        self.allowed_domains        = allowed_domains
        self.max_runs_per_hour      = max_runs_per_hour

    def _payload(self) -> dict:
        return {
            "max_spend_per_day":      self.max_spend_per_day,
            "max_spend_per_run":      self.max_spend_per_run,
            "require_human_approval": self.require_human_approval,
            "allowed_tools":          self.allowed_tools,
            "blocked_tools":          self.blocked_tools,
            "allowed_domains":        self.allowed_domains,
            "max_runs_per_hour":      self.max_runs_per_hour,
        }
