import hashlib
import json
from pathlib import Path
import re
import sys

REDACTED_KEY = re.compile(
    r"(?<![0-9a-fA-F_])[0-9a-fA-F]{92}_{64}[0-9a-fA-F]{8}(?![0-9a-fA-F_])"
)
CURVE_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

def parse_secret_hex(text: str) -> tuple[str, bytes]:
    normalized = "".join(text.split())
    match = re.fullmatch(r"([0-9a-fA-F]{64})", normalized)
    if not match:
        raise ValueError("Expected 64 data hex characters (32 bytes).")
    return bytes.fromhex(match[0])

def base58_encode(raw: bytes) -> str:
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    number = int.from_bytes(raw, "big")
    encoded = ""
    while number:
        number, remainder = divmod(number, 58)
        encoded = alphabet[remainder] + encoded
    return "1" * (len(raw) - len(raw.lstrip(b"\x00"))) + encoded

def restore_descriptors(data: dict | list, secret: bytes) -> dict | list:
    if len(secret) != 32 or not 1 <= int.from_bytes(secret, "big") < CURVE_ORDER:
        raise ValueError("Secret must be a valid 32-byte private key.")
    replacements = {}
    descriptor_count = 0

    def restore_key(match: re.Match) -> str:
        template = match.group(0).lower()
        if template not in replacements:
            if replacements:
                raise ValueError("Multiple distinct redacted keys found; supply a single-key backup.")
            raw = bytes.fromhex(template[:92] + secret.hex() + template[156:])
            if raw[:4] not in (bytes.fromhex("0488ade4"), bytes.fromhex("04358394")) or raw[45] != 0:
                raise ValueError("Invalid extended private key template.")
            replacements[template] = base58_encode(raw)
        return replacements[template]

    def visit(value):
        nonlocal descriptor_count
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if key == "desc":
                    if not isinstance(item, str):
                        raise ValueError("Descriptor 'desc' must be text.")
                    restored, count = REDACTED_KEY.subn(restore_key, item)
                    if count == 0 or "_" in restored:
                        raise ValueError("Descriptor must contain a valid redacted key template.")
                    descriptor_count += 1
                    result[key] = restored
                else:
                    result[key] = visit(item)
            return result
        if isinstance(value, list):
            return [visit(item) for item in value]
        return value

    restored = visit(data)
    if descriptor_count == 0:
        raise ValueError("No descriptors found in backup.")
    return restored


def main() -> None:
    print(f"Enter the decrypted secret 32 byte secret hex (spaces allowed), then send EOF (Ctrl-D):", file=sys.stderr)
    secret = parse_secret_hex(sys.stdin.read())
    print(f"\n\nEnter the redacted private descriptor, then send EOF (Ctrl-D):", file=sys.stderr)
    data = json.load(sys.stdin)
    restored = restore_descriptors(data, secret)

    print(json.dumps(restored, indent=2))


if __name__ == "__main__":
    main()
