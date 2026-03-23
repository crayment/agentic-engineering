---
name: recruit-junior
description: Frame an agent as a junior engineer who looks things up, cites sources, and doesn't rely on potentially stale training knowledge. Use instead of "you are an expert in X" when you want fresh, grounded research over confident guessing.
trigger_phrases:
  - recruit a junior
  - junior engineer
tags:
  - research
---

# Recruit a Junior

Most agent prompting advice tells you to declare the agent an expert: "You are a senior engineer with 20 years of experience in Rust." The theory is that authority framing unlocks better answers.

The problem: it also unlocks confident guessing. A "senior engineer" relies on pattern recognition and past experience. They may not look things up. They may not acknowledge when their training data is stale. They answer fast and sound sure — which is exactly what you don't want when the landscape moves quickly.

**Flip it.** Frame the agent as a junior who is new to the area. Juniors look things up. Juniors cite sources. Juniors ask before assuming. That's the behavior you actually want from a research or investigation task.

## When to Use This

Use this framing when you want an agent to:

- Research a library, framework, or tool it may have outdated knowledge about
- Compare options without anchoring on the first thing it recognizes
- Investigate a bug or behavior that may have changed since its training cutoff
- Make recommendations that need to be grounded in current docs, not memory

Do not use this framing for pure code generation or refactoring tasks where research is not the point.

## The Framing

When creating the agent, open with something like:

> You are a junior engineer assigned to research [topic]. You are not expected to already know the answers — your job is to look things up and report back with citations. Use your tools (web search, documentation lookup, etc.) to find current information. Do not rely on what you already know if you can verify it. Cite your sources.

Adapt it to the task. The key elements are:

1. **Junior framing** — removes the pressure to already know, creates space to look things up
2. **Explicit tool use expectation** — makes searching the default, not a fallback
3. **Cite sources** — forces grounding and lets you evaluate the quality of the evidence
4. **Current information** — signals that staleness is a risk you care about

## Full Example Prompt

```
You are a junior engineer on this team. You've been asked to research [specific question or topic].

You are not expected to already know the answer. Your job is to:
- Use your tools to find current, up-to-date information
- Cite every source you rely on (doc page, search result, etc.)
- Clearly distinguish what you found vs. what you're inferring
- Flag anything where the information might be out of date or where sources disagreed

Do not skip the research step because you think you already know. Look it up anyway — things change.

Present your findings as a structured report.
```

## Why This Works

- LLMs trained on large corpora will pattern-match to what they've seen most. "Expert" framing reinforces that tendency.
- "Junior" framing activates a different learned behavior: looking things up, being careful, asking questions.
- Requiring citations forces the model to actually invoke search tools rather than generating plausible-sounding answers from memory.
- "Things change" is a useful reminder that the model's training cutoff is real and recent docs may contradict its priors.

## What to Watch For

- A junior framing can produce more hedging language. That's usually fine — but if the agent is being overly uncertain about things it clearly found in current docs, you can follow up with: "You found the source. Trust it."
- If the agent still skips tool use, make it more explicit: "Before answering anything, run a search and share what you found."
- Junior framing works best on investigation and research agents. For an agent implementing a plan you've already decided on, just give it the plan.
