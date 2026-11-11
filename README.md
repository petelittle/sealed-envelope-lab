# Sealed Envelope Lab

Learn public-key cryptography by sealing a real file, handing the envelope to someone else, and opening it on another side — not by memorising jargon first.

A sealed envelope in this project is a small file that:

- only the intended recipient can open;
- reveals tampering instead of silently delivering changed contents;
- lets anyone holding the sender's pinned public key verify who sealed it, without reading it.

> **Educational project:** This is a learning lab, not a production security product. Do not use it for real secrets. The included tool intentionally implements a small, inspectable version of the design.

## Why an envelope?

Cryptography terms become much easier when each one has a job you have already seen:

| Experience in the lab | Concept it teaches |
|---|---|
| Anyone can seal a message to a public key | Public-key encryption |
| Only one private key can open it | Private-key custody |
| A changed envelope is refused | Authenticated, tamper-evident handling |
| A signature checks out before opening | Digital signatures |
| A short code identifies a public key | Fingerprints |
| A restored file matches its sealed hash | SHA-256 integrity checks |

## Quick start

You need Python 3.10 or newer.

```bash
python -m pip install -r tools/requirements.txt
```

Create two sets of **learning keys** — one for Alice and one for Bob:

```bash
python tools/sealed_envelope_lab.py genkeys --owner Alice --keys alice-keys.json
python tools/sealed_envelope_lab.py genkeys --owner Bob --keys bob-keys.json
```

Print and exchange only the public keys:

```bash
python tools/sealed_envelope_lab.py pubs --keys alice-keys.json
python tools/sealed_envelope_lab.py pubs --keys bob-keys.json
```

In a real exercise, compare the fingerprints through a separate trusted channel before trusting a public key. A public key pasted into the same untrusted place as an envelope can be substituted.

Alice seals the sample message to Bob's **encryption public key**:

```bash
python tools/sealed_envelope_lab.py seal \
  --keys alice-keys.json \
  --to "<Bob's encryption public key>" \
  --file examples/hello-envelope.txt \
  --out envelope.json
```

Bob opens it using Alice's **signing public key**, pinned in advance:

```bash
python tools/sealed_envelope_lab.py open \
  --keys bob-keys.json \
  --from-sign-pub "<Alice's signing public key>" \
  --envelope envelope.json \
  --outdir opened
```

The restored file should match the sample byte-for-byte, and the tool prints the verified SHA-256 digest.

## Run the smoke test

```bash
python tests/smoke_test.py
```

The test uses a temporary directory and throwaway keys. It verifies a complete round trip and confirms that a tampered envelope is refused.

## Repository map

- [`docs/01-the-idea.md`](docs/01-the-idea.md) — the learning idea and the rules of the exercise
- [`docs/02-protocol.md`](docs/02-protocol.md) — the envelope design and the lab implementation
- [`docs/03-key-ceremony.md`](docs/03-key-ceremony.md) — generating, pinning, rotating and retiring keys
- [`docs/04-threat-model.md`](docs/04-threat-model.md) — what this design does and does not protect against
- [`docs/05-trial-record.md`](docs/05-trial-record.md) — a sanitized record of the design exercises
- [`docs/06-roadmap.md`](docs/06-roadmap.md) — how the lab can grow into a series
- [`tools/sealed_envelope_lab.py`](tools/sealed_envelope_lab.py) — the small Python/PyNaCl lab tool
- [`examples/hello-envelope.txt`](examples/hello-envelope.txt) — a harmless sample file to seal

## The non-negotiable rules

1. **Private keys never travel.** Never commit, upload, email or paste them.
2. **Envelopes contain data, never code.** A sealed envelope must not ask you to run or trust it.
3. **Never type a private key into a received file or web page.** That pattern is indistinguishable from phishing.
4. **Verify the signature before opening.**
5. **Pin public-key fingerprints through a separate trusted channel.**
6. **If a private encryption key is lost, envelopes addressed to it are lost.** There is no locksmith in this design.

See [`SECURITY.md`](SECURITY.md) before adapting the tool.

## Project status

Path 1, version 0.2 of the design: public-key sealed envelopes using libsodium primitives through PyNaCl. The protocol has been exercised in a local simulation and in a two-device exchange using disposable test keys. Real-world key storage, backup and long-term operation remain open design questions and are deliberately not hidden.
