# 5. Trial record

This is a sanitized summary of the exercises used to test the design. It contains no real keys, real envelopes, personal messages or operational key-storage details.

## Trial A — local simulation

Four disposable key pairs were generated in memory for two fictional roles. A dummy file was sealed and opened in one environment.

Checks performed:

1. The signature verified while the envelope remained sealed.
2. The plaintext did not appear in the envelope.
3. Flipping one ciphertext byte caused opening to fail.
4. The same alteration invalidated the signature.
5. The wrong recipient key could not open the envelope.
6. An unsigned envelope was treated as invalid.
7. Correct opening restored the file byte-for-byte, confirmed by SHA-256.

**Result:** all checks passed.

## Trial B — two-device exchange

Disposable key pairs were generated separately on two computers. Public keys were exchanged, and each side independently recomputed and compared the fingerprints before any envelope moved.

Checks performed:

1. An envelope sealed on the first computer was verified and opened on the second participant's side using the matching private key.
2. The restored file's SHA-256 matched the hash sealed inside the envelope.
3. A return envelope was sealed in the opposite direction and opened successfully.
4. A wrong-recipient attempt was refused.
5. A tampered envelope was refused on signature verification.

**Result:** the two-direction exchange passed.

## Cleanup

The disposable keys were deleted after the trials. Envelopes sealed to deleted keys are permanently unopenable. That outcome was intentional: it demonstrates, in miniature, why private-key loss is a design event rather than a support problem.

## What the trials did not prove

- safe long-term private-key storage or backup;
- a production-quality opening tool;
- retrieval from a particular storage service;
- resistance to a compromised endpoint;
- suitability for real secrets.

Those limits remain visible in the project rather than being polished away.
