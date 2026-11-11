# 2. Protocol

## Roles and keys

Each participant holds two separate key pairs:

| Purpose | Primitive | Public half | Private half |
|---|---|---|---|
| Signing | Ed25519 | May be shared and pinned | Never leaves its owner |
| Encryption | X25519 | May be shared and pinned | Never leaves its owner |

Signing and encryption keys are kept separate so that a problem with one role does not automatically become a problem with the other.

## The broader envelope design

For a general-purpose implementation, especially with larger files:

1. Put the original filename and media type in a small internal header.
2. Generate a fresh random file key.
3. Encrypt the header and file bytes with XChaCha20-Poly1305 authenticated encryption.
4. Wrap the file key to the recipient's X25519 public key using a libsodium sealed box.
5. Assemble a data-only envelope containing the wrapped key and ciphertext.
6. Sign the complete envelope with the sender's Ed25519 private signing key.
7. Store or carry the envelope anywhere. Its carrier does not need to be trusted with the contents.

The recipient reverses the process:

1. Verify the signature with the sender's pinned public signing key.
2. Refuse the envelope if the signature is absent or invalid.
3. Unwrap the file key using the recipient's private encryption key.
4. Decrypt and let the authenticated-encryption check reject altered ciphertext.
5. Verify the restored bytes against the content hash sealed inside.
6. Restore the original filename and type.

## The included lab implementation

The Python tool in this repository is a deliberately small teaching implementation for short files. It frames the filename, media type and SHA-256 hash with the file bytes, then encrypts that framed payload directly with a sealed box and signs the ciphertext.

That simplification makes the code easier to inspect, but it is not the preferred construction for large files or a production tool. The distinction is intentional and documented so learners can see where a lab ends and a fuller implementation begins.

## Why sign the ciphertext?

Signing the ciphertext — encrypt-then-sign — means a carrier or recipient can verify the envelope while it is still sealed. The tradeoff is that the sender's identity is visible from the signature. For this learning design, that visibility is acceptable and useful.

## Hash is not a signature

A SHA-256 hash is a fingerprint of exact bytes. It is useful when the expected hash reaches you through a trusted route. By itself, it proves neither authorship nor protection against substitution: an attacker who can replace a file may also replace the hash displayed beside it.

A digital signature binds bytes to the holder of a private signing key. Verification with the corresponding public key shows both that the bytes are unchanged since signing and that they were signed by that key holder.
