# Security notes

Sealed Envelope Lab is an educational project. It is designed to make a small set of cryptographic guarantees visible and testable; it is not a finished secure-messaging or secure-file-transfer product.

## Do not use for real secrets

Do not seal passwords, financial records, identity documents, private communications or anything whose disclosure would cause harm. Use a maintained, independently reviewed product for real secrets.

## Important limitations

- The lab tool encrypts a framed payload directly with a libsodium sealed box. The broader protocol in `docs/02-protocol.md` describes a hybrid design for larger files: a fresh random file key, authenticated encryption, and wrapping that file key to the recipient.
- The tool does not solve endpoint security. Malware or a compromised tool on either device defeats the exercise.
- Public keys are not self-proving. Fingerprints must be compared through a separate trusted channel before use.
- Metadata is not hidden: observers may learn that an envelope exists, its approximate size, its timing and its claimed sender.
- Losing a private encryption key makes matching envelopes permanently unopenable.
- A possibly copied private key must be treated as compromised, not merely lost.
- The cryptography used here is not post-quantum cryptography.

## Key-file safety

- Generate keys locally.
- Never commit key files to Git. The repository `.gitignore` excludes common local key, envelope and output names, but ignore rules are not a substitute for checking `git status` before every commit.
- Never paste a private key into a web page, document, chat or received HTML file.
- Delete disposable learning keys when an exercise is finished, unless the exercise intentionally studies key loss.

## Reporting problems

For this learning repository, open an issue describing the problem without including any private key, real envelope or sensitive file contents.
