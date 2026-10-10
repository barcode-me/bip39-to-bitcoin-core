## Getting started

Set up and env and install `embit`.

```bash
python3 -m venv venv
source venv/bin/activate               
pip3 install -r requirements.txt  
```

## For BIP39 users

A simple python script to convert a BIP39 seedphrase and passphrase into private wallet descriptors ready to import by Bitcoin Core. By default it outputs descriptors for all single-sig script types. Use this if you prefer to backup your wallet using BIP39 or if you want to import your BIP39 seed phrase into bitcoin core.

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

## For bitcoin core users

On the other hand, if you use bitcoin core exclusively you can backup a private descriptor. Contains scripts to backup a bitcoin core private descriptor by extracting the 32 secret bytes from the master xprv and encoding it as a hexadecimal string and also redacting the secret bytes from the descriptor. The redacted descriptor can then backed up separate from the secret 32 bytes such as by encrypting the descriptor and storing them in a secure place. Then the secret bytes can be backed up to paper or metal as a hexadecimal string. There is a recovery script that takes the secret bytes and redacted descriptor and reconstructs the private descriptor to be imported into bitcoin core.

```bash
# 1. create a new wallet
bitcoin-cli createwallet "my-wallet"

# 2. list the private descriptors
bitcoin-cli -rpcwallet=my-wallet listdescriptors true

# 3. redact a private descriptor
python3 redact-core-private-descriptor.py > redacted-descriptor.json

# 4. (optional) encrypt your redacted descriptor with a passphrase using gpg or whatever ecryption tool you want
gpg --symmetric redacted-descriptor.json

# 5. backup your encrypted redacted descriptor securely in multiple places
```

Now when you want to recover the descriptor:

```bash
# 1. decrypt your encrypted redacted descriptor
gpg --decrypt redacted-descriptor.json.gpg

# 2. restore your full private descriptor
python3 restore-core-private-descriptor.py

# 3. import descriptor into bitcoin core
bitcoin-cli -rpcwallet=my-wallet importdescriptors '[
  {"desc": "<receive descriptor w/ checksum>", "active": true, "internal": false, "range": [0, 999], "timestamp": "0"},
  {"desc": "<change descriptor w/ checksum>",  "active": true, "internal": true,  "range": [0, 999], "timestamp": "0"}
]'
```