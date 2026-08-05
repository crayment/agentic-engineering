---
name: software-principles
description: "Core software development principles: code for readability and changeability, compose with values over inheritance, apply DRY wisely, test for confidence, and crash loudly on unexpected conditions."
trigger_phrases:
  - software principles
  - coding principles
  - engineering principles
  - golden rules
tags:
  - principles
  - architecture
---

# Software Principles

- GOLDEN RULE: Code is written to be easy to read, understand, and above all, change.
  - Most other rules stem directly from this principle.
- Simple made Easy (Rich Hickey)
  - Rich Hickey distinguishes "simple" from "easy" by defining simple as the opposite of complex, meaning a system is clear, unentangled, and objective, while easy is the opposite of hard and is subjective, convenient, and at hand. An easy solution today might introduce future complexity that makes it hard to understand, debug, or change later, whereas simple solutions, though potentially harder initially, lead to long-term robustness and reliability.
- DRY can be evil
  - The right application of DRY is for things that change for the same reason. This is when abstraction helps.
  - The wrong abstraction is worse than no abstraction. Removing repetition when things change for different reasons does not serve us.
- Compose with values, don't inherit by default
  - Prefer assembling behavior from small, explicit pieces at the call site (functions, closures, data + injected dependencies) over deep class hierarchies and global registries.
  - "Lego bricks": each piece has a narrow job; the caller chooses which bricks snap together. Varying behavior means passing different values, not subclass overrides.
  - Inject dependencies; don't construct them inside. Tests supply fakes at the seam.
  - Outcome types beat special cases: express branches as returned data (e.g. a tagged union) rather than code that switches on names or class types.
  - The deletion test: if removing your abstraction just spreads the same per-variant logic everywhere, it wasn't earning its keep. If removing it forces every caller to reimplement orchestration, it was.
  - When inheritance is fine: framework extension points with one clear hook and hidden orchestration, ORM models, typed UI base components — especially when the framework owns the lifecycle.
  - When registries are fine: discovery across plugin boundaries you do not control — not for two in-repo features that could pass a list.
  - Simple over easy applies here: subclassing feels easy; explicit wiring is often simpler to change because the assembly is visible in one place.
- Testing
  - Tests should serve this principle: make code easier to change confidently.
  - Compromises exist. We cannot test everything.
  - Prioritizing speed pays dividends.
- When it is good to crash
  - Handle edge cases that are world breaking. A crash can trigger monitoring systems so the team becomes aware and fixes it. Silently bypassing unexpected conditions means the problem may never be noticed.
  - If a value is expected to exist at a point in the code, make it required and log if it is missing. If it is world breaking, crash. This principle can be applied broadly.
- Follow the boy scout rule. Always try to leave the campground a bit cleaner than you found it.
