---
name: visualize
description: Add correct, minimal visuals to lessons — diagrams or geometric pictures.
version: 0.2.0
author: amosblomqvist, Hermes Agent
license: CC BY-SA 4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [visualization, diagrams, teaching, mermaid, svg]
    related_skills: [teach, mermaid-maker, svg-maker]
---

# Visualize

Add a correct, minimal visual to a lesson — a diagram or geometric picture. Use when an idea is genuinely clearer as a picture.

You are the **creative director**. You decide the exact idea and distill it to its fewest carrying elements. A **maker subagent** does the authoring, rendering, and verification.

## When to Visualize

A picture earns its place when it shows something words can't:
- The idea is a **structure or relationship**: dependencies, flow, sequence, state machine, tree
- The idea is **spatial or geometric**: coordinates, geometry, vectors, plots

Do NOT visualize when prose already carries it. A decorative diagram adds noise.

## Choose the Maker

Two subagents, invoked via `delegate_task`:

- **mermaid-maker** — structural/relational: dependency graphs, flowcharts, sequences, state diagrams. Default for dependency-graph pedagogy.
- **svg-maker** — spatial/geometric: coordinates, geometry, number lines, vectors, custom shapes.

Rule of thumb: nodes-and-edges → mermaid. Positions-and-shapes → svg.

## Brief the Maker Well

The most common failure is **cramming**. Before briefing, prune to the fewest elements.

- BAD: "make a diagram about how TCP works"
- GOOD: "graph TD: a node 'packet' at the top; arrows down to 'ordering' and 'retransmit'; both to 'reliable stream'"

If your brief lists more than ~5-7 elements, cut it first.

## Invoke

Use `delegate_task` with a clear task description:

```
delegate_task with goal="Create a Mermaid diagram showing: [brief]. Output the PNG path."
```

For mermaid-maker:
```
delegate_task with goal="Create a Mermaid flowchart showing the relationship between [concepts]. Render to PNG and return the filename."
```

For svg-maker:
```
delegate_task with goal="Create an SVG showing [geometric description]. Include labels at coordinates. Render to PNG and return the filename."
```

## Embed in Lesson

Once the maker returns a filename, embed it using Obsidian wikilink:

```
![[viz-<slug>-<timestamp>.png|500]]
```

Width `|500` is a good default.

## Why This Is Reliable

The maker never returns a picture it hasn't **looked at**, so correctness is verified before it reaches the learner.

## Output Format

The maker returns:
```
RESULT:
filename: viz-<slug>-<timestamp>.png
path: /full/path/to/viz-<slug>-<timestamp>.png
```

If it returns `RESULT: NONE`, simplify the brief or skip the visual.