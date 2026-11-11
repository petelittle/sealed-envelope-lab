#!/usr/bin/env python3
"""
Sealed Envelope Lab - a small hands-on cryptography exercise.

This teaching tool uses PyNaCl (libsodium) to demonstrate:
  * X25519 sealed boxes: encrypt so only the recipient can open
  * Ed25519 signatures: prove who sealed an envelope and detect changes
  * SHA-256: verify the restored bytes against a hash sealed inside

Commands:
  genkeys   create a local key file containing two key pairs
  pubs      print only the public keys and their fingerprints
  seal      seal a small file to a recipient's public encryption key
  open      verify and open an envelope addressed to you

EDUCATIONAL USE ONLY. Keys generated here are learning keys. Do not use this
tool for real secrets, and never commit a key file to version control.
"""

import argparse
import base64
import binascii
import hashlib
import json
import mimetypes
import os
import struct
import sys
from pathlib import Path

from nacl.exceptions import BadSignatureError, CryptoError
from nacl.public import PrivateKey, PublicKey, SealedBox
from nacl.signing import SigningKey, VerifyKey

FORMAT = "sealed-envelope/lab-v1"
KEY_FORMAT = "sealed-envelope/lab-keys-v1"


def b64e(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def b64d(text: str, field: str) -> bytes:
    try:
        return base64.b64decode(text.encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError, AttributeError) as exc:
        raise ValueError(f"Invalid base64 in {field}") from exc


def fingerprint(public_key: bytes) -> str:
    """A short, human-checkable fingerprint of a public key."""
    hexed = hashlib.sha256(public_key).hexdigest()[:32]
    return " ".join(hexed[i : i + 4] for i in range(0, 32, 4))


def load_keys(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("format") != KEY_FORMAT:
        raise ValueError("This is not a Sealed Envelope Lab key file")
    return data


def write_private_json(path: str, data: dict) -> None:
    """Write a key file without overwriting, tightening permissions where possible."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")


def cmd_genkeys(args) -> None:
    if os.path.exists(args.keys):
        sys.exit(f"Refusing to overwrite existing key file: {args.keys}")

    signing_key = SigningKey.generate()  # Ed25519
    encryption_key = PrivateKey.generate()  # X25519
    data = {
        "format": KEY_FORMAT,
        "owner": args.owner,
        "warning": "LEARNING KEYS ONLY - NEVER COMMIT OR SHARE THE PRIVATE KEYS IN THIS FILE",
        "sign_pub": b64e(bytes(signing_key.verify_key)),
        "sign_priv": b64e(bytes(signing_key)),
        "enc_pub": b64e(bytes(encryption_key.public_key)),
        "enc_priv": b64e(bytes(encryption_key)),
    }
    write_private_json(args.keys, data)
    print(f"Learning keys for {args.owner} written to {args.keys}")
    cmd_pubs(args)


def cmd_pubs(args) -> None:
    keys = load_keys(args.keys)
    sign_pub = b64d(keys["sign_pub"], "sign_pub")
    enc_pub = b64d(keys["enc_pub"], "enc_pub")
    print(f"Owner:             {keys['owner']}")
    print(f"Signing public:    {keys['sign_pub']}")
    print(f"  fingerprint:     {fingerprint(sign_pub)}")
    print(f"Encryption public: {keys['enc_pub']}")
    print(f"  fingerprint:     {fingerprint(enc_pub)}")
    print("Public keys and fingerprints may be shared. Private keys must stay local.")


def cmd_seal(args) -> None:
    sender = load_keys(args.keys)
    source = Path(args.file)
    data = source.read_bytes()

    header = {
        "filename": source.name,
        "media_type": mimetypes.guess_type(source.name)[0] or "application/octet-stream",
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    header_bytes = json.dumps(header, separators=(",", ":")).encode("utf-8")
    payload = struct.pack(">I", len(header_bytes)) + header_bytes + data

    recipient_public = b64d(args.to, "--to")
    if len(recipient_public) != 32:
        raise ValueError("Recipient encryption public key must decode to 32 bytes")

    ciphertext = SealedBox(PublicKey(recipient_public)).encrypt(payload)
    signing_key = SigningKey(b64d(sender["sign_priv"], "sign_priv"))
    signature = signing_key.sign(ciphertext).signature

    envelope = {
        "format": FORMAT,
        "version": 1,
        "sender": sender["owner"],
        "sender_sign_fingerprint": fingerprint(b64d(sender["sign_pub"], "sign_pub")),
        "recipient_enc_fingerprint": fingerprint(recipient_public),
        "ciphertext": b64e(ciphertext),
        "signature": b64e(signature),
    }
    if os.path.exists(args.out):
        sys.exit(f"Refusing to overwrite existing envelope: {args.out}")
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(envelope, handle, indent=2)
        handle.write("\n")

    print(f"Sealed {header['filename']} ({len(data)} bytes)")
    print(f"Content SHA-256: {header['sha256']}")
    print(f"Envelope written to {args.out}")


def safe_output_name(raw_name: str) -> str:
    name = Path(raw_name).name
    if name in {"", ".", ".."} or "/" in raw_name or "\\" in raw_name:
        raise ValueError("Envelope contains an unsafe filename")
    return name


def cmd_open(args) -> None:
    recipient = load_keys(args.keys)
    with open(args.envelope, "r", encoding="utf-8") as handle:
        envelope = json.load(handle)

    if envelope.get("format") != FORMAT:
        sys.exit("Not a Sealed Envelope Lab envelope - refusing.")

    sender_public = b64d(args.from_sign_pub, "--from-sign-pub")
    if len(sender_public) != 32:
        sys.exit("Sender signing public key must decode to 32 bytes - refusing.")
    if envelope.get("sender_sign_fingerprint") != fingerprint(sender_public):
        sys.exit("Sender fingerprint mismatch - refusing.")

    ciphertext = b64d(envelope["ciphertext"], "ciphertext")
    signature = b64d(envelope["signature"], "signature")
    try:
        VerifyKey(sender_public).verify(ciphertext, signature)
    except BadSignatureError:
        sys.exit("SIGNATURE INVALID - the envelope was altered or signed by another key. Refusing.")
    print("Signature: VALID")

    recipient_private = b64d(recipient["enc_priv"], "enc_priv")
    if envelope.get("recipient_enc_fingerprint") != fingerprint(
        b64d(recipient["enc_pub"], "enc_pub")
    ):
        sys.exit("Recipient fingerprint mismatch - refusing.")
    try:
        payload = SealedBox(PrivateKey(recipient_private)).decrypt(ciphertext)
    except CryptoError:
        sys.exit("DECRYPTION FAILED - this envelope is not addressed to your encryption key.")

    if len(payload) < 4:
        sys.exit("Envelope payload is malformed - refusing.")
    (header_len,) = struct.unpack(">I", payload[:4])
    header_end = 4 + header_len
    if header_len <= 0 or header_end > len(payload):
        sys.exit("Envelope payload is malformed - refusing.")
    header = json.loads(payload[4:header_end].decode("utf-8"))
    data = payload[header_end:]

    digest = hashlib.sha256(data).hexdigest()
    if digest != header.get("sha256"):
        sys.exit("CONTENT HASH MISMATCH - restored bytes differ from the sealed original.")

    filename = safe_output_name(header.get("filename", ""))
    os.makedirs(args.outdir, exist_ok=True)
    output_path = os.path.join(args.outdir, filename)
    if os.path.exists(output_path):
        sys.exit(f"Refusing to overwrite existing file: {output_path}")
    with open(output_path, "wb") as handle:
        handle.write(data)

    print(f"Opened: {output_path} ({len(data)} bytes, type {header.get('media_type')})")
    print(f"SHA-256 verified: {digest}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sealed Envelope Lab (educational use only)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    genkeys = subparsers.add_parser("genkeys", help="create local learning keys")
    genkeys.add_argument("--owner", required=True)
    genkeys.add_argument("--keys", required=True)
    genkeys.set_defaults(fn=cmd_genkeys)

    pubs = subparsers.add_parser("pubs", help="print public keys and fingerprints")
    pubs.add_argument("--keys", required=True)
    pubs.set_defaults(fn=cmd_pubs)

    seal = subparsers.add_parser("seal", help="seal a small file")
    seal.add_argument("--keys", required=True)
    seal.add_argument("--to", required=True, help="recipient encryption public key (base64)")
    seal.add_argument("--file", required=True)
    seal.add_argument("--out", required=True)
    seal.set_defaults(fn=cmd_seal)

    opener = subparsers.add_parser("open", help="verify and open an envelope")
    opener.add_argument("--keys", required=True)
    opener.add_argument(
        "--from-sign-pub",
        required=True,
        help="sender signing public key (base64), pinned through a separate trusted channel",
    )
    opener.add_argument("--envelope", required=True)
    opener.add_argument("--outdir", required=True)
    opener.set_defaults(fn=cmd_open)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        args.fn(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        sys.exit(f"Error: {exc}")


if __name__ == "__main__":
    main()
