#!/usr/bin/env python3
"""End-to-end smoke test for Sealed Envelope Lab.

Runs entirely in a temporary directory with throwaway keys. It checks:
  1. Alice can seal a file to Bob.
  2. Bob verifies the signature and restores byte-identical contents.
  3. A one-character change to the ciphertext makes opening refuse.
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "sealed_envelope_lab.py"


def run(*args: str, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, str(TOOL), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if expect_success and result.returncode != 0:
        raise AssertionError(f"Command failed: {args}\n{result.stdout}\n{result.stderr}")
    if not expect_success and result.returncode == 0:
        raise AssertionError(f"Command unexpectedly succeeded: {args}\n{result.stdout}")
    return result


def public_value(output: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s+(\S+)", output, re.MULTILINE)
    if not match:
        raise AssertionError(f"Could not find {label!r} in output:\n{output}")
    return match.group(1)


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="sealed-envelope-lab-") as raw_tmp:
        tmp = Path(raw_tmp)
        alice_keys = tmp / "alice-keys.json"
        bob_keys = tmp / "bob-keys.json"

        alice_pubs = run("genkeys", "--owner", "Alice", "--keys", str(alice_keys)).stdout
        bob_pubs = run("genkeys", "--owner", "Bob", "--keys", str(bob_keys)).stdout

        alice_sign_pub = public_value(alice_pubs, "Signing public")
        bob_enc_pub = public_value(bob_pubs, "Encryption public")

        message = tmp / "message.txt"
        original = b"Hello, Bob. This envelope travelled without being read.\n"
        message.write_bytes(original)

        envelope = tmp / "envelope.json"
        run(
            "seal",
            "--keys", str(alice_keys),
            "--to", bob_enc_pub,
            "--file", str(message),
            "--out", str(envelope),
        )

        opened = run(
            "open",
            "--keys", str(bob_keys),
            "--from-sign-pub", alice_sign_pub,
            "--envelope", str(envelope),
            "--outdir", str(tmp / "opened"),
        ).stdout
        assert "Signature: VALID" in opened
        assert (tmp / "opened" / "message.txt").read_bytes() == original

        envelope_data = json.loads(envelope.read_text(encoding="utf-8"))
        ciphertext = envelope_data["ciphertext"]
        replacement = "A" if ciphertext[0] != "A" else "B"
        envelope_data["ciphertext"] = replacement + ciphertext[1:]
        tampered = tmp / "tampered-envelope.json"
        tampered.write_text(json.dumps(envelope_data), encoding="utf-8")

        refused = run(
            "open",
            "--keys", str(bob_keys),
            "--from-sign-pub", alice_sign_pub,
            "--envelope", str(tampered),
            "--outdir", str(tmp / "opened-tampered"),
            expect_success=False,
        )
        assert "SIGNATURE INVALID" in (refused.stdout + refused.stderr)

    print("SMOKE TEST PASSED: round trip verified and tampering refused")


if __name__ == "__main__":
    main()
