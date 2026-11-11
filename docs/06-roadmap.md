# 6. Roadmap: growing the lab into a series

Sealed Envelope works well as the first project in a learn-by-building cryptography series. Each later project should introduce one new idea through another concrete object.

## Project 1 — Sealed Envelope

Public-key encryption, signatures, fingerprints, key loss and tool trust.

## Possible next projects

### Project 2 — Fingerprint ceremony

A tiny tool and checklist for exchanging, pronouncing, comparing and pinning public-key fingerprints. Focus: identity is a procedure, not a file format.

### Project 3 — Hash commitments

Publish a hash today and reveal the original content later. Focus: a commitment can prove something existed in a particular form without revealing it — and why a salt matters.

### Project 4 — Commit–reveal

Two or more participants commit first and reveal later, so nobody can quietly change their answer after seeing everyone else's. Focus: fairness protocols.

### Project 5 — Signed releases

Sign a tool or document, publish the signature separately, and verify it with an independent verifier. Focus: a signature proves origin and integrity, not that code is good.

### Project 6 — Time and envelopes

Study why ordinary encryption cannot force a key holder to wait. Compare social opening times, trusted timestamping, time-lock puzzles and public randomness beacons. Focus: locking information is different from locking money.

### Project 7 — A second implementation

Rebuild the same envelope idea in another language while keeping the test vectors and threat model stable. Focus: separating a protocol from one implementation of it.

## Series rule

Every project must end with something the learner can run, break, repair and explain in plain language. Jargon is introduced only after it names an experience the learner has already had.
