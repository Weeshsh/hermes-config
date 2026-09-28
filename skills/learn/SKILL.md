---
name: learn
description: AI-powered learning system with evidence-based pedagogy.
version: 0.1.0
author: amosblomqvist, Hermes Agent
license: CC BY-SA 4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [learning, education, teaching, pedagogy, memory, spaced-repetition]
    related_skills: [teach, visualize, teach-back-evaluator, retrieve-first-gate, progressive-hint-ladder, retrieval-practice-generator, obsidian]
---

# Learn System

An AI-powered personal learning system based on evidence-based pedagogy. Adapts the teaching philosophy from amosblomqvist/learn for Hermes Agent.

## What It Does

Teaches you anything so it actually locks in and is understood — not just memorized. Uses a proven 3-phase process:
1. **Probe** — assess your current level and learning goal
2. **Plan** — map the dependency graph from foundations to goal
3. **Teach** — build understanding one node at a time

## Components

### Core Skills

- **teach** — The main teaching methodology (unconditional truths + motivated discovery)
- **visualize** — Add diagrams and visuals to lessons (delegates to maker agents)

### Helper Skills (installed separately)

- `teach-back-evaluator` — Evaluate if you understood
- `retrieve-first-gate` — Check prior knowledge before teaching
- `progressive-hint-ladder` — Provide graduated hints
- `retrieval-practice-generator` — Generate recall questions
- `obsidian` — Write notes to your Obsidian vault

### Subagents (via delegate_task)

- **researcher** — Verify facts before teaching
- **mermaid-maker** — Create Mermaid diagrams
- **svg-maker** — Create precise SVG diagrams

## How to Use

When you want to learn something:

1. Start a conversation with the teach skill loaded
2. The teacher will probe your current level with questions
3. They'll present a learning plan with a dependency map
4. Once you approve, they teach node-by-node with visuals where helpful

## Prerequisites

### Required
None — the system works out of the box.

### Optional
- `obsidian` skill — if you want lessons saved to an Obsidian vault (otherwise saves to `~/learn-notes/`)
- `mmdc` (Mermaid CLI) — for diagram rendering (`npm install -g @mermaid-js/mermaid-cli`)
- `rsvg-convert` or ImageMagick — for SVG rendering

### Helper skills (recommended):
```bash
hermes skills install education/teach-back-evaluator
hermes skills install education/retrieve-first-gate
hermes skills install education/progressive-hint-ladder
hermes skills install education/retrieval-practice-generator
```

Obsidian skill (optional):
```bash
hermes skills install note-taking/obsidian
```

## Quick Reference

The teach system uses these patterns:

- **Probe**: Ask questions to find the edge of your understanding
- **Plan**: Present dependency graph before teaching
- **Teach loop**: For each node: motivate → establish → connect → quiz-check
- **Visualize**: `delegate_task` to mermaid-maker or svg-maker
- **Quiz**: Use `clarify` or `execute_code` with quiz_engine.py