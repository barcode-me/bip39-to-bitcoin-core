#!/usr/bin/env python3
"""
BIP39 mnemonic + passphrase -> BIP84 (native segwit, P2WPKH) xprv descriptors.
Run this offline, because the output contains private keys.
"""
import argparse
from getpass import getpass
from embit import bip39, bip32
from embit.networks import NETWORKS

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
      "--show-input",
      action="store_true",
      help="Echo the mnemonic and passphrase to the screen as you type them (hidden by default)",
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

  path = "84h/0h/0h"
  acct = root.derive(f"m/{path}")
  xprv = acct.to_base58(version=net["xprv"])
  xpub = acct.to_public().to_base58(version=net["xpub"])

  origin = f"[{fingerprint}/{path}]"
  receive = f"wpkh({origin}{xprv}/0/*)"
  change  = f"wpkh({origin}{xprv}/1/*)"
  watch   = f"wpkh({origin}{xpub}/0/*)"

  print("Master fingerprint:", fingerprint)
  print("Receive :", receive)
  print("Change  :", change)
  print("Watch-only receive:", watch)

if __name__ == "__main__":
  main()

