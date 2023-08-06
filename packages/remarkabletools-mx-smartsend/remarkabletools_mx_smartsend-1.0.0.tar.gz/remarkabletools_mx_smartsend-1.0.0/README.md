# Mx.NET.SDK.SmartSend
⚡ MultiversX SmartSend Python SDK: Library for interacting with Smart Send contracts on MultiversX blockchain

## How to install?
The content is delivered via PyPI package:
##### [remarkabletools_mx_smartsend](https://pypi.org/project/remarkabletools-mx-smartsend/)

## Main Features
- Create EGLD/Token/MetaESDT/NFT/SFT transactions for Smart Send contracts

## Quick start guide
### Basic example
```python
provider = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")
account = provider.get_account(Address.from_bech32("MY_ADDRESS"))
network_config = provider.get_network_config()
config = DefaultTransactionBuildersConfiguration(network_config.chain_id)

smart_send = SmartSend(account, config, "MY_CONTRACT_BECH32_ADDRESS")

input_transactions: List[TokenAmount] = []
for i in range(1, 10):
    input_transactions.append(TokenAmount("RECEIVER_ADDRESS", TokenPayment.egld_from_amount(f"0.0{i}"))) # TokenPayment can also be fungible_from_amount / meta_esdt_from_amount / non_fungible / semi_fungible

try:
    # You can sync the account before creating transactions (to have the latest nonce)
    # account = provider.get_account(Address.from_bech32("MY_ADDRESS")) # get account data from network
    # smart_send.sync(account) # sync account

    txs = smart_send.create_egld_transactions(input_transactions) # or create_token_transactions / create_metaesdt_transactions / create_nft_transactions / create_sft_transactions
    # sign and send txs
except Exception as ex:
    print(ex)
```

### Advanced example
*The following example is using a wallet __signer__ that should not be used in production, only in private!*
```python
provider = ProxyNetworkProvider("https://devnet-gateway.multiversx.com")
account = provider.get_account(Address.from_bech32("MY_ADDRESS"))
network_config = provider.get_network_config()
config = DefaultTransactionBuildersConfiguration(network_config.chain_id)

signer = UserSigner.from_pem_file(Path("/path/wallet.pem"))

smart_send = SmartSend(account, config, "MY_CONTRACT_ADDRESS")

input_transactions: List[TokenAmount] = []
for i in range(1, 10):
    input_transactions.append(TokenAmount("RECEIVER_ADDRESS", TokenPayment.egld_from_amount(f"0.0{i}")))

try:
    txs = smart_send.create_egld_transactions(input_transactions)
    for tx in txs:
        tx.signature = signer.sign(tx)

    response = provider.send_transactions(txs)
    print(response)
except Exception as ex:
    print(ex)
```
