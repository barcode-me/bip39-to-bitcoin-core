#!/usr/bin/env python3
"""
BIP39 mnemonic + passphrase -> xprv descriptors for Bitcoin Core.
Run this offline, because the output contains private keys.
"""
import argparse
from getpass import getpass
from embit import bip39, bip32
from embit.descriptor import Descriptor
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
  if passphrase:
    print("Using a BIP39 passphrase.")
  else:
    print("No BIP39 passphrase.")

  net = NETWORKS["main"]
  seed_no_passphrase = bip39.mnemonic_to_seed(mnemonic, password="")
  root_no_passphrase = bip32.HDKey.from_seed(seed_no_passphrase, version=net["xprv"])

  seed = bip39.mnemonic_to_seed(mnemonic, password=passphrase)
  root = bip32.HDKey.from_seed(seed, version=net["xprv"])

  master_xprv = root.to_base58()
  fingerprint = root.my_fingerprint.hex()
  fingerprint_no_passphrase = root_no_passphrase.my_fingerprint.hex()
  script_types = SCRIPT_TYPES if args.type == "all" else [
    t for t in SCRIPT_TYPES if t["key"] == args.type
  ]

  print("Master fingerprint (no passphrase):", fingerprint_no_passphrase)
  print("Master fingerprint:", fingerprint)

  for script_type in script_types:
    receive = Descriptor.from_string(
      script_type["wrap"].format(f"[{fingerprint}/{script_type['purpose']}/0h/0h]{master_xprv}/0/*")
    )
    change = Descriptor.from_string(
      script_type["wrap"].format(f"[{fingerprint}/{script_type['purpose']}/0h/0h]{master_xprv}/1/*")
    )

    print()
    print(f"-- {script_type['name']} --")
    print("Receive :", receive)
    print("Change  :", change)

if __name__ == "__main__":
  main()
