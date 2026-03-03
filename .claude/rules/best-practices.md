## Self-Documenting Code

Readable code supersedes static documentation, as the latter quickly becomes outdated. Never add comments that explain what the code does; instead, refactor the code to make its purpose clear.

## Single Responsibility Principle

Each function or module should have one, and only one, reason to change. This enhances maintainability and testability.

## DRY Principle

Avoid code duplication by abstracting repeated logic into reusable functions or modules. No amount of code duplication is acceptable.

## Functional Programming Practices

For maintainability, the codebase emphasizes functional patterns with pure functions and immutable data transformations over imperative loops and state mutations. The latter are forbidden.
- Do NOT use for loops. Instead of for loops, use:
  - Generator expressions for lazy evaluation.
  - List/dict/set comprehensions for data transformation.
  - `itertools.consume` for side-effect-only iterations.
- Do NOT use while loops. Instead of while loops, use:
  - Generator functions with `yield` for stateful iteration.
  - `itertools.takewhile`/`dropwhile`/`count` for conditional sequences.
  - `functools.reduce`/`itertools.accumulate` for totalization.
  - Recursive functions for complex logic.
- Do NOT use `map`. Instead of `map`, use:
  - Generator expressions for lazy evaluation.
  - Comprehensions for immediate materialization.
- Do NOT use `filter`. Instead of `filter`, use:
  - Generator expressions for lazy evaluation.
  - Comprehensions for immediate materialization.