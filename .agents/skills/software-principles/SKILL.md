---
name: software-principles
description: Core software development principles: code for readability and changeability, apply DRY wisely, test for confidence, and crash loudly on unexpected conditions.
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
- Testing
  - Tests should serve this principle: make code easier to change confidently.
  - Compromises exist. We cannot test everything.
  - Prioritizing speed pays dividends.
- When it is good to crash
  - Handle edge cases that are world breaking. A crash can trigger monitoring systems so the team becomes aware and fixes it. Silently bypassing unexpected conditions means the problem may never be noticed.
  - If a value is expected to exist at a point in the code, make it required and log if it is missing. If it is world breaking, crash. This principle can be applied broadly.
- Follow the boy scout rule. Always try to leave the campground a bit cleaner than you found it.
