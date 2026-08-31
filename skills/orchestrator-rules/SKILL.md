---
name: orchestrator-rules
description: "Use to route tasks to sub-agents based on user intent."
---

# Orchestrator Routing Rules

Hermes serves as the central Orchestrator. Route tasks automatically based on the following:

## Routing Table
| Intent / Keyword | Destination Agent |
| :--- | :--- |
| Notion, egzamin, nauka, study | `teacher-agent` |
| Kalendarz, wydarzenia, planowanie dnia | `calendar-agent` |

## Delegation Procedure
1. Identify the intent.
2. If it matches a destination, format the task data according to the `communication-standard` skill.
3. Use `delegate_task` with the formatted context.
