---
name: communication-standard
description: "Uniform JSON schema for inter-agent communication."
---

# Communication Standard

All sub-agents (teacher-agent, calendar-agent) MUST return their final output in the following JSON format:

```json
json
{
  "task_id": "string",
  "agent": "string",
  "status": "success | error | pending",
  "summary": "Brief (1 sentence) summary in English.",
  "data": {
    "detailed_result": "..."
  }
}
```

If a sub-agent fails, the "summary" must contain the error explanation in English.
