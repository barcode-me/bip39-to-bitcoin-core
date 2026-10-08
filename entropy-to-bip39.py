#!/usr/bin/env python3
"""
Generate a BIP39 mnemonic from cryptographically secure randomness, or from
user-supplied entropy (hex). Run this offline, because the output is a seed phrase.
"""
import argparse
import secrets
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
  args = parser.parse_args()
  prompt_input = input if args.show_input else getpass
  if not args.show_input:
      print("Input is hidden. Pass --show-input to see what you type.")

  entropy_bytes = WORD_COUNT_TO_BYTES[args.words]

  custom_entropy = prompt_input(
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
      print("Using user-supplied entropy.")
  else:
      entropy = secrets.token_bytes(entropy_bytes)
      print("Using securely generated entropy.")

  mnemonic = bip39.mnemonic_from_bytes(entropy)

  print()
  print("Mnemonic:", mnemonic)


if __name__ == "__main__":
  main()
