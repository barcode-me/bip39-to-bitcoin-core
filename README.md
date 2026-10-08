A simple python script to convert a BIP39 seedphrase and passphrase into a private wallet descriptor ready to import by Bitcoin Core. This script only supports creating private descriptors for Native Segwit Single Sig wallets.

```bash
python3 -m venv venv
source venv/bin/activate               
pip3 install -r requirements.txt  
```

Then you can run the script:

```bash
python3 convert-bip39-to-core.py 
```