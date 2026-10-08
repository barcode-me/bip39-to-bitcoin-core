A simple python script to convert a BIP39 seedphrase and passphrase into private wallet descriptors ready to import by Bitcoin Core. By default it outputs descriptors for all single-sig script types:

| Address Standard | Derivation Path (BIP) | Prefix | Script Type |
|---|---|---|---|
| Legacy (P2PKH) | m/44'/0'/0'/... | 1... | Pay-to-PubKey-Hash |
| Nested SegWit (P2SH-P2WPKH) | m/49'/0'/0'/... | 3... | Pay-to-Script-Hash |
| Native SegWit (P2WPKH) | m/84'/0'/0'/... | bc1q... | Pay-to-Witness-PubKey-Hash |
| Taproot (P2TR) | m/86'/0'/0'/... | bc1p... | Pay-to-Taproot |

Use `--type` to limit output to a single script type (`legacy`, `nested-segwit`, `native-segwit`, `taproot`, or `all` — the default).

```bash
python3 -m venv venv
source venv/bin/activate               
pip3 install -r requirements.txt  
```

Then you can run the script:

```bash
# 1. Create a new seed phrase
python3 entropy-to-bip39.py --words 12

# 2. Get the private descriptors for the seed phrase and passphrase
python3 convert-bip39-to-core.py --show-input

# 3. Create empty wallet: wallet_name, disable_private_keys, blank, passphrase, avoid_reuse, descriptors
bitcoin-cli createwallet "my-wallet" false true "" false true

# 4. Make sure your descriptors have a checksum.
bitcoin-cli getdescriptorinfo $DESCRIPTOR

# 5. Import the private descriptors:
bitcoin-cli -rpcwallet=my-wallet importdescriptors '[
  {"desc": "<receive descriptor w/ checksum>", "active": true, "internal": false, "range": [0, 999], "timestamp": "0"},
  {"desc": "<change descriptor w/ checksum>",  "active": true, "internal": true,  "range": [0, 999], "timestamp": "0"}
]'
```