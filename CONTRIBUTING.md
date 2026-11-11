# Contributing

Contributions should preserve the project's purpose: make cryptography understandable through one concrete, inspectable exercise.

## Principles

- Prefer plain language before terminology, then introduce the precise term.
- Keep examples fictional and harmless.
- Never add a real private key, a real sealed envelope, a real message, a credential or personal data to an example, test, screenshot or issue.
- Do not invent new cryptography. Use documented libsodium constructions.
- Keep the tool small enough for a learner to read.
- Add a test whenever a claimed guarantee changes.

## Before opening a pull request

1. Run `python tests/smoke_test.py`.
2. Check `git status` and inspect every file being committed.
3. Search the change for `PRIVATE`, private-key file names and accidental local paths.
4. State clearly whether the change affects the teaching design, the lab implementation, or both.
