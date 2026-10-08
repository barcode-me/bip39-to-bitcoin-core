#!/usr/bin/env python3
"""
BIP39 mnemonic + passphrase -> xprv descriptors for Bitcoin Core.
Run this offline, because the output contains private keys.
"""
import argparse
from getpass import getpass
from embit import bip39, bip32
from embit.networks import NETWORKS

# Address Standard, BIP purpose, descriptor template (receive/change path filled in below)
SCRIPT_TYPES = [
    {
        "key": "legacy",
        "name": "Legacy (P2PKH)",
        "purpose": "44h",
        "wrap": "pkh({})",
    },
    {
        "key": "nested-segwit",
        "name": "Nested SegWit (P2SH-P2WPKH)",
        "purpose": "49h",
        "wrap": "sh(wpkh({}))",
    },
    {
        "key": "native-segwit",
        "name": "Native SegWit (P2WPKH)",
        "purpose": "84h",
        "wrap": "wpkh({})",
    },
    {
        "key": "taproot",
        "name": "Taproot (P2TR)",
        "purpose": "86h",
        "wrap": "tr({})",
    },
]


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "--show-input",
      action="store_true",
      help="Echo the mnemonic and passphrase to the screen as you type them (hidden by default)",
  )
  parser.add_argument(
      "--type",
      choices=[t["key"] for t in SCRIPT_TYPES] + ["all"],
      default="all",
      help="Which script type(s) to derive descriptors for (default: all)",
  )
  args = parser.parse_args()
  prompt_input = input if args.show_input else getpass
  if not args.show_input:
      print("Input is hidden. Pass --show-input to see what you type.")

  mnemonic = " ".join(prompt_input("Mnemonic: ").strip().lower().split())

  if not bip39.mnemonic_is_valid(mnemonic):
      raise SystemExit("Invalid BIP39 mnemonic (bad word or checksum)")

  passphrase = prompt_input("BIP39 passphrase (empty for none):")
  net = NETWORKS["main"]
  seed = bip39.mnemonic_to_seed(mnemonic, password=passphrase)
  root = bip32.HDKey.from_seed(seed, version=net["xprv"])
  fingerprint = root.my_fingerprint.hex()

  print("Master fingerprint:", fingerprint)

  script_types = SCRIPT_TYPES if args.type == "all" else [
      t for t in SCRIPT_TYPES if t["key"] == args.type
  ]

  for script_type in script_types:
      path = f"{script_type['purpose']}/0h/0h"
      acct = root.derive(f"m/{path}")
      xprv = acct.to_base58(version=net["xprv"])
      xpub = acct.to_public().to_base58(version=net["xpub"])

      origin = f"[{fingerprint}/{path}]"
      receive = script_type["wrap"].format(f"{origin}{xprv}/0/*")
      change = script_type["wrap"].format(f"{origin}{xprv}/1/*")
      watch = script_type["wrap"].format(f"{origin}{xpub}/0/*")

      print()
      print(f"-- {script_type['name']} (m/{path}) --")
      print("Receive :", receive)
      print("Change  :", change)
      print("Watch-only receive:", watch)


if __name__ == "__main__":
  main()

