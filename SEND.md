## send and sign a transaction with bitcoin core

0. set up some vars

```sh
WALLET_NAME="..."
BTC_DATA_DIR="..." # default is ~/.bitcoin
DESTINATION_ADDRESS="..."
AMOUNT=0.00000000
```

1. on online device create unsigned transaction (psbt)

```sh
bitcoin-cli -datadir=$BTC_DATA_DIR -rpcwallet=$WALLET_NAME -named walletcreatefundedpsbt outputs='[{"'"$DESTINATION_ADDRESS"'": '"$AMOUNT"'}]' options='{"subtractFeeFromOutputs":[0]}' | jq -r '.psbt' > ~/Desktop/unsigned.psbt
```

2. on signer device verify psbt before signing it

```sh
cat ~/Desktop/unsigned.psbt | bitcoin-cli -datadir=$BTC_DATA_DIR -stdin decodepsbt
```

3. on signer device sign psbt (you might need to load your wallet)

```sh
# (optional) load wallet
bitcoin-cli -datadir=$BTC_DATA_DIR listwallets
bitcoin-cli -datadir=$BTC_DATA_DIR loadwallet $WALLET_NAME

# sign psbt
cat ~/Desktop/unsigned.psbt | bitcoin-cli -datadir=$BTC_DATA_DIR -rpcwallet=$WALLET_NAME -stdin walletprocesspsbt | jq -r '.psbt' > ~/Desktop/signed.psbt
```

4. on the online device decode and verify the signed transaction

```sh
cat ~/Desktop/signed.psbt | bitcoin-cli -datadir=$BTC_DATA_DIR -stdin decodepsbt
```

5. on the online device sign and broadcast the transaction

```sh
cat ~/Desktop/signed.psbt | bitcoin-cli -datadir=$BTC_DATA_DIR -stdin finalizepsbt | jq -r '.hex' | bitcoin-cli -datadir=$BTC_DATA_DIR -stdin sendrawtransaction
```
