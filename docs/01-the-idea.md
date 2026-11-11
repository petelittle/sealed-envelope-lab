# 1. The idea

Imagine writing a note today that another person will open later. You want four things:

1. Nobody carrying or storing the note can read it early.
2. If somebody swaps or changes it, the recipient can tell.
3. Only the intended recipient can open it.
4. The recipient can restore the original note exactly — not a retyped copy.

A physical envelope gives us the picture, but not the guarantees. Anyone can steam it open, copy the contents and reseal it. A cryptographic sealed envelope turns those wishes into checkable properties.

## Learning by doing

Traditional introductions often begin with a wall of terms: asymmetric cryptography, key exchange, authenticated encryption, digital signatures, hash functions, non-repudiation, threat models.

This lab reverses the order:

1. Perform one complete seal-and-open exercise.
2. Notice what each key actually did.
3. Break the envelope deliberately and watch the tool refuse it.
4. Only then attach the technical names.

The concrete experience becomes the hook on which the vocabulary hangs.

## The exercise in one sentence

The sender encrypts a file to the recipient's **public encryption key** and signs the resulting ciphertext with their own **private signing key**; the recipient first verifies that signature, then opens the envelope with their own **private encryption key**.

## What "sealed" does not mean

Cryptography seals the contents. It does not force a person who legitimately owns the opening key to wait until an agreed time. Timing remains a social promise unless a separate time-based design is added later.

It also does not make a dishonest program honest. That is why envelopes in this project are always inert data, never self-decrypting files or web pages asking for a private key.
