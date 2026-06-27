# cognos-sdk

The Python SDK for Cognos Cloud.

```bash
pip install cognos
```

## Usage

```python
from cognos import Agent

agent = Agent(
    name="my-agent",
    model="gpt-4o",
    memory=True,
    tools=["web", "slack"],
    cron="0 9 * * *",
)

agent.deploy()
```

See the [SDK reference](../docs/sdk.md) for full documentation.
