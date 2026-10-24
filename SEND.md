## send and sign a transaction with bitcoin core

1. on online device create unsigned transaction (psbt)

```sh
DESTINATION_ADDRESS="..."
AMOUNT=0.00000000
bitcoin-cli -rpcwallet="my-wallet" -named walletcreatefundedpsbt outputs='[{"'"$DESTINATION_ADDRESS"'": '"$AMOUNT"'}]' options='{"subtractFeeFromOutputs":[0]}' | jq -r '.psbt' > ~/Desktop/unsigned.psbt
```

2. on signer device verify psbt before signing it

```sh
bitcoin-cli decodepsbt "$(cat ~/Desktop/unsigned.psbt)"
```

3. on signer device sign psbt (you might need to load your wallet)

```sh
# (optional) load wallet
bitcoin-cli listwallets
bitcoin-cli loadwallet "my-wallet"

# sign psbt
cat ~/Desktop/unsigned.psbt | bitcoin-cli -rpcwallet="my-wallet" walletprocesspsbt | jq -r '.psbt' > ~/Desktop/signed.psbt
```

4. on the online device decode and verify the signed transaction

```sh
cat ~/Desktop/signed.psbt | bitcoin-cli decodepsbt
```

5. on the online device sign and broadcast the transaction

```sh
cat ~/Desktop/signed.psbt | bitcoin-cli finalizepsbt | jq -r '.hex' | bitcoin-cli sendrawtransaction
```