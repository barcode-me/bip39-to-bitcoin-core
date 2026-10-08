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
python3 convert-bip39-to-core.py 
```