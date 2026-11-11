# 4. Threat model

A security design is only meaningful when it says what it is defending against — and what it is not.

## Addressed

| Threat | Design response |
|---|---|
| A storage provider or carrier reads the contents | Encrypt to the recipient's public encryption key |
| An envelope is swapped in storage | Verify the sender's signature before opening |
| Ciphertext is altered | Signature failure and/or authenticated-decryption failure |
| A sender is impersonated | Require a valid signature from a pinned signing key |
| A public key is substituted | Pin and compare fingerprints through a separate trusted channel |
| An envelope tricks the recipient into entering a private key | Envelopes are data only; no code travels with them |

## Not addressed

- Theft or copying of a private key from its home.
- Malware or a malicious opening tool on the recipient's device.
- A malicious sender who is already trusted and pinned.
- Metadata exposure: existence, size, timing and claimed sender may be visible.
- A recipient opening early. Possession of the correct private key is sufficient to open; cryptography alone does not enforce a calendar.
- Long-term quantum risk to X25519 and Ed25519. This matters mainly for secrets that must remain confidential for decades.
- Social engineering outside the protocol, such as convincing a participant to replace a pinned fingerprint with an attacker's fingerprint.

## The central lesson

Strong primitives do not rescue weak key handling or dishonest code. In practical systems, key custody, fingerprint verification and tool trust usually decide whether the cryptography gets a chance to work.
