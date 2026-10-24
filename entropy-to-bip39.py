#!/usr/bin/env python3
"""
Generate a BIP39 mnemonic from cryptographically secure randomness, or from
user-supplied entropy (hex). Run this offline, because the output is a seed phrase.
"""
import argparse
import secrets
import sys
from getpass import getpass
from embit import bip39

WORD_COUNT_TO_BYTES = {12: 16, 24: 32}


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "--words",
      type=int,
      choices=sorted(WORD_COUNT_TO_BYTES),
      required=True,
      help="Number of words in the seed phrase",
  )
  parser.add_argument(
      "--show-input",
      action="store_true",
      help="Echo your custom entropy to the screen as you type it (hidden by default)",
  )
  parser.add_argument(
      "--raw",
      action="store_true",
      help="Print only the mnemonic words to stdout (prompts and messages go to stderr)",
  )
  parser.add_argument(
      "--auto",
      action="store_true",
      help="Skip the entropy prompt and generate the seed phrase from secure randomness",
  )
  args = parser.parse_args()
  out = sys.stderr if args.raw else sys.stdout

  def prompt_input(prompt):
      if not args.show_input:
          return getpass(prompt, stream=out)
      out.write(prompt)
      out.flush()
      return input()

  if not args.show_input and not args.auto:
      print("Input is hidden. Pass --show-input to see what you type.", file=out)

  entropy_bytes = WORD_COUNT_TO_BYTES[args.words]

  custom_entropy = "" if args.auto else prompt_input(
      f"Custom entropy as hex ({entropy_bytes} bytes / {entropy_bytes * 2} hex chars, "
      "leave empty to generate securely): "
  ).strip()

  if custom_entropy:
      try:
          entropy = bytes.fromhex(custom_entropy)
      except ValueError:
          raise SystemExit("Entropy must be a valid hex string")
      if len(entropy) != entropy_bytes:
          raise SystemExit(
              f"Entropy must be exactly {entropy_bytes} bytes "
              f"({entropy_bytes * 2} hex chars) for a {args.words}-word mnemonic, "
              f"got {len(entropy)} bytes"
          )
      print("Using user-supplied entropy.", file=out)
  else:
      entropy = secrets.token_bytes(entropy_bytes)
      print("Using securely generated entropy.", file=out)

  mnemonic = bip39.mnemonic_from_bytes(entropy)

  if args.raw:
      print(mnemonic)
  else:
      print()
      print("Mnemonic:", mnemonic)


if __name__ == "__main__":
  main()
