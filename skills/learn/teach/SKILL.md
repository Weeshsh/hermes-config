---
name: teach
description: Teach anything so it actually locks in and is understood.
version: 0.2.0
author: amosblomqvist, Hermes Agent
license: CC BY-SA 4.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [teaching, learning, pedagogy, understanding, memory]
    related_skills: [visualize, teach-back-evaluator, retrieve-first-gate, progressive-hint-ladder, obsidian]
---

# Teaching

Two principles. They are not tips — they are how you teach the user, every time. No other teaching methods come close. Apply them to any explanation, from a one-liner to a deep dive.

The goal is never "he can recite the fact." The goal is **understanding**: the fact is derivable from foundations he already accepts, connected into his mental model, and therefore self-preserving. Memorized facts rot. Understood facts don't.

## The Philosophy (Why This Works)

Two brains can hold the same propositions and look identical from the outside. But one holds a pile of **disconnected lone facts** (A). The other holds a few **core truths** from which all those facts are derivable (B), so to it the facts are obviously connected. That connection *is* understanding.

- Connected knowledge > disconnected knowledge
- A graph of dependencies > disjoint lonely nodes
- Understanding > memorizing

Understanding preserves knowledge, compresses it, and is just plain better. Every teaching move below exists to build that dependency graph: **nodes** (Principle i) and **edges** (Principle ii).

The felt goal is **the click**: the moment a pile of lonely facts collapses into a few generating ideas.

## Principle i — Unconditional Truths First

Start from the ground. Lock in the core, **always-true** unconditional truths before anything built on top of them.

Why start here? Not because bottom-up is the "correct" order — because unconditional truths are the *easiest* thing for the brain to accept and lock in. They're safe, so they commit instantly.

- Find the few hard facts he can take at face value — often first principles
- They must be simple enough to be accepted **as-is, without nuance or caveats**
- These can be committed to *instantly and safely*
- Build everything else up from these, explicitly

**Two especially strong forms:**
- **Universal statements** — "all X are Y" or "no X is Y"
- **Real definitions** — genuine definitions anchor understanding

## Principle ii — "How Could I Have Discovered This?"

Facts feel arbitrary when there's no visible reason they *had* to be this way. The fix: make it feel discovered, not decreed.

Walk the user through how they **could have discovered the thing themselves**:
- Start from square one: **why are we even doing this?**
- Motivate every intermediate step
- The output is turning **disconnected propositions → connected propositions**

### Socratic vs Expository — Adaptive

Choose per topic:
- **Socratic** — pose the motivating problem and let them attempt the discovery. Use `clarify` for open-ended questions.
- **Expository** — narrate the motivated discovery path yourself. Use when the topic is beyond cold-reasoning reach.

When unsure, lean Socratic for things they can reason about; otherwise narrate.

## The Process: Probe → Plan → Teach

The two principles are *how* you teach. This is *when* — the shape of a teaching session.

### Accuracy Is Non-Negotiable

**Verify, don't wing it from memory.** The moment you are even slightly unsure of any fact, stop and confirm it with a `delegate_task` to the researcher subagent before you say it. Pausing to verify is always acceptable — accuracy beats flow, every time.

### Phase 1 — Probe

You can't teach without knowing where the user's understanding ends.

**1a. Current level — use `clarify` with quiz-style questions.** Your goal is to locate the *edge* of their understanding. Do NOT assume — actually test it.

- All-correct means the questions were too easy. Escalate until something breaks.
- One wrong answer is not "done" — probe around it to characterize the misconception.
- Map every strand the lesson rests on.

**1b. Learning goal — use `clarify`.** Find out what they actually want taught. "I want to understand LLMs" can mean ten different things.

### Phase 2 — Plan

This is the highest-leverage step. With their level and goal in hand, reason out the best way to teach *this thing*.

- What are the unconditional truths this rests on?
- Which of those do they already hold (from Phase 1)?
- What's the motivated discovery path from those truths to their goal?
- Socratic or expository for each stretch?

**Then present the plan in chat — always, before any teaching:**

1. **The approach** — What we'll cover, in what order, and why.
2. **The dependency map** — A small Mermaid graph showing the teaching order.

```
graph TD
    A[Foundation 1] --> B[Foundation 2]
    B --> C[Concept]
    C --> D[Goal]
```

Then stop and wait for their go-ahead.

### Phase 3 — Teach (The Loop)

Build the dependency graph one **node** at a time. For **every node**:

1. **Motivate** — Frame why we need this node right now.
2. **Establish:**
   - If foundational: state it plainly, at face value.
   - If derived: build it up from what's already established via a motivated move.
3. **Connect** — Make the dependency edge explicit.
4. **Quiz-check** — Confirm the node actually landed with a quick question.

Repeat this full loop per node.

## Formatting — Math Renders as LaTeX

If the user has Obsidian, math renders as LaTeX:
- Inline: `$f(x)$`
- Display: `$$\n f(x) \n$$`

## Tools Reference

| Pi Tool | Hermes Equivalent |
|---------|-------------------|
| `quiz` | `clarify` (for self-check) or custom quiz_engine.py via `execute_code` |
| `ask_user_question` | `clarify` |
| `subagent()` | `delegate_task` |
| `md-log` | `write_file` to Obsidian vault via obsidian skill |

## Invoke Visualization

When a concept is clearer as a picture, use the visualize skill:

```
Use the visualize skill to add a diagram showing [brief concept].
```

This delegates to mermaid-maker or svg-maker subagents.

## Quiz Construction

When building quiz questions (for retrieval practice):

1. Every option is a bare claim — no justification in options
2. Write the correct claim first, then mutate into distractors
3. Each distractor must be a real error they might actually make
4. No asymmetric bolding — either bold nothing, or bold in all options