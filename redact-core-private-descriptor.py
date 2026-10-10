import json
import re
import sys

EXTENDED_PRIVATE_KEY = re.compile(r"(?:xprv|tprv)[1-9A-HJ-NP-Za-km-z]{107}(?![1-9A-HJ-NP-Za-km-z])")

def base58_decode(value: str) -> bytes:
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    n = 0
    for char in value:
        n = n * 58 + alphabet.index(char)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return b"\x00" * (len(value) - len(value.lstrip("1"))) + raw


def redact_xprv(xprv: str) -> tuple[str, str]:
    full_hex = base58_decode(xprv).hex()
    return full_hex[:92] + "_" * 64 + full_hex[156:], full_hex[92:156]


def redact_descriptors(data: dict | list) -> tuple[dict | list, str]:
    def collect_keys(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "desc" and isinstance(item, str):
                    yield from EXTENDED_PRIVATE_KEY.findall(item)
                else:
                    yield from collect_keys(item)
        elif isinstance(value, list):
            for item in value:
                yield from collect_keys(item)

    keys = set(collect_keys(data))
    if len(keys) > 1:
        raise ValueError(
            "Multiple distinct xprv/tprv keys found. "
            "Pass only descriptors containing a single shared extended private key."
        )
    replacements = {}

    def replace_key(match: re.Match) -> str:
        key = match.group(0)
        if key not in replacements:
            redacted_hex, _ = redact_xprv(key)
            replacements[key] = redacted_hex
        return replacements[key]

    def visit(value):
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if key == "desc":
                    if not isinstance(item, str):
                        raise ValueError("Descriptor 'desc' must be text.")
                    redacted, count = EXTENDED_PRIVATE_KEY.subn(replace_key, item)
                    if count == 0:
                        raise ValueError(
                            "Descriptor was not redacted: no xprv or tprv found. "
                            "Use the output of listdescriptors true."
                        )
                    result[key] = redacted
                else:
                    result[key] = visit(item)
            return result
        if isinstance(value, list):
            return [visit(item) for item in value]
        return value

    redacted = visit(data)
    if not keys:
        raise ValueError("No extended private key found in descriptors.")
    _, secret_hex = redact_xprv(next(iter(keys)))
    return redacted, secret_hex


def main() -> None:
    print(f"Enter the bitcoin core private descriptor, then send EOF (Ctrl-D):", file=sys.stderr)
    data = json.load(sys.stdin)
    redacted, secret_hex = redact_descriptors(data)
    output = (json.dumps(redacted, indent=2) + "\n").encode("utf-8")

    print(f"\nsecret hex: {secret_hex}\n", file=sys.stderr)
    sys.stdout.buffer.write(output)


if __name__ == "__main__":
    main()
