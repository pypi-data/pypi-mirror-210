from typing import Optional, List

from remarkabletools_mx_smartsend.constants import *
from remarkabletools_mx_smartsend.helper import *
from remarkabletools_mx_smartsend.token_amount import *

from multiversx_sdk_network_providers.accounts import AccountOnNetwork

from multiversx_sdk_core import Address, AccountNonceHolder, Transaction, TokenPayment
from multiversx_sdk_core.transaction_builders import DefaultTransactionBuildersConfiguration
from multiversx_sdk_core.transaction_builders import ContractCallBuilder


class SmartSend:
    def __init__(self,
                 account: AccountOnNetwork,
                 config: DefaultTransactionBuildersConfiguration,
                 smart_send_contract: Optional[str] = None,
                 chunk_limit: Optional[int] = 100):
        self.account_address = account.address
        self.account_nonce = AccountNonceHolder(account.nonce)
        self.config = config
        self.smart_send_contract = smart_send_contract
        self.chunk_limit = chunk_limit

    def sync(self, account: AccountOnNetwork):
        self.account_address = account.address
        self.account_nonce = AccountNonceHolder(account.nonce)

    def set_chunk_limit(self, limit: int):
        self.chunk_limit = limit

    def set_smart_send_contract_address(self, address: str):
        self.smart_send_contract = address

    def create_egld_transactions(self, input_transactions: List[TokenAmount], gas_per_tx: int = 600000, contract_address: str = None) -> List[Transaction]:
        if (contract_address != None):
            smart_send_contract_address = Address.from_bech32(contract_address)
        else:
            if (self.smart_send_contract != None):
                smart_send_contract_address = Address.from_bech32(
                    self.smart_send_contract)
            else:
                raise Exception("Smart Send Contract address is not set")

        transactions_chunks: List[List[TokenAmount]] = chunks(
            input_transactions, self.chunk_limit)
        transaction_requests: List[Transaction] = []
        for chunk in transactions_chunks:
            if (len(chunk) < 7):
                gas_limit = 4000000
            else:
                gas_limit = len(chunk) * gas_per_tx

            arguments = []
            for tx in chunk:
                arguments.append(tx.address)
                arguments.append(tx.amount.amount_as_integer)

            amounts = sum(i.amount.amount_as_integer for i in chunk)
            amount: TokenPayment = TokenPayment.egld_from_integer(amounts)

            tx = ContractCallBuilder(
                self.config,
                contract=smart_send_contract_address,
                function_name=SMART_SEND_METHOD,
                call_arguments=arguments,
                caller=self.account_address,
                nonce=self.account_nonce.get_nonce_then_increment(),
                value=amount,
                gas_limit=gas_limit
            )
            transaction = tx.build()
            transaction_requests.append(transaction)

        return transaction_requests

    def create_token_transactions(self, input_transactions: List[TokenAmount], gas_per_tx: int = 900000, contract_address: str = None) -> List[Transaction]:
        if (contract_address != None):
            smart_send_contract_address = Address.from_bech32(contract_address)
        else:
            if (self.smart_send_contract != None):
                smart_send_contract_address = Address.from_bech32(
                    self.smart_send_contract)
            else:
                raise Exception("Smart Send Contract address is not set")

        token_identifier = input_transactions[0].amount.token_identifier
        num_decimals = input_transactions[0].amount.num_decimals

        transactions_chunks: List[List[TokenAmount]] = chunks(
            input_transactions, self.chunk_limit)
        transaction_requests: List[Transaction] = []
        for chunk in transactions_chunks:
            if (len(chunk) < 7):
                gas_limit = 6000000
            else:
                gas_limit = len(chunk) * gas_per_tx

            arguments = []
            for tx in chunk:
                arguments.append(tx.address)
                arguments.append(tx.amount.amount_as_integer)

            amounts = sum(i.amount.amount_as_integer for i in chunk)
            amount: TokenPayment = TokenPayment.fungible_from_integer(
                token_identifier, amounts, num_decimals)

            tx = ContractCallBuilder(
                self.config,
                contract=smart_send_contract_address,
                function_name=SMART_SEND_METHOD,
                call_arguments=arguments,
                caller=self.account_address,
                nonce=self.account_nonce.get_nonce_then_increment(),
                esdt_transfers=[amount],
                gas_limit=gas_limit
            )
            transaction = tx.build()
            transaction_requests.append(transaction)

        return transaction_requests

    def create_metaesdt_transactions(self, input_transactions: List[TokenAmount], gas_per_tx: int = 900000, contract_address: str = None) -> List[Transaction]:
        if (contract_address != None):
            smart_send_contract_address = Address.from_bech32(contract_address)
        else:
            if (self.smart_send_contract != None):
                smart_send_contract_address = Address.from_bech32(
                    self.smart_send_contract)
            else:
                raise Exception("Smart Send Contract address is not set")

        token_identifier = input_transactions[0].amount.token_identifier
        token_nonce = input_transactions[0].amount.token_nonce
        num_decimals = input_transactions[0].amount.num_decimals

        transactions_chunks: List[List[TokenAmount]] = chunks(
            input_transactions, self.chunk_limit)
        transaction_requests: List[Transaction] = []
        for chunk in transactions_chunks:
            if (len(chunk) < 7):
                gas_limit = 6000000
            else:
                gas_limit = len(chunk) * gas_per_tx

            arguments = []
            for tx in chunk:
                arguments.append(tx.address)
                arguments.append(tx.amount.amount_as_integer)

            amounts = sum(i.amount.amount_as_integer for i in chunk)
            amount: TokenPayment = TokenPayment.meta_esdt_from_integer(
                token_identifier, token_nonce, amounts, num_decimals)

            tx = ContractCallBuilder(
                self.config,
                contract=smart_send_contract_address,
                function_name=SMART_SEND_METHOD,
                call_arguments=arguments,
                caller=self.account_address,
                nonce=self.account_nonce.get_nonce_then_increment(),
                esdt_transfers=[amount],
                gas_limit=gas_limit
            )
            transaction = tx.build()
            transaction_requests.append(transaction)

        return transaction_requests

    def create_nft_transactions(self, input_transactions: List[TokenAmount], gas_per_tx: int = 900000, contract_address: str = None) -> List[Transaction]:
        if (contract_address != None):
            smart_send_contract_address = Address.from_bech32(contract_address)
        else:
            if (self.smart_send_contract != None):
                smart_send_contract_address = Address.from_bech32(
                    self.smart_send_contract)
            else:
                raise Exception("Smart Send Contract address is not set")

        transactions_chunks: List[List[TokenAmount]] = chunks(
            input_transactions, self.chunk_limit)
        transaction_requests: List[Transaction] = []
        for chunk in transactions_chunks:
            if (len(chunk) < 7):
                gas_limit = 6000000
            else:
                gas_limit = len(chunk) * gas_per_tx

            nfts = []
            arguments = []
            for tx in chunk:
                nfts.append(TokenPayment.non_fungible(
                    tx.amount.token_identifier, tx.amount.token_nonce))

                arguments.append(tx.address)
                arguments.append(tx.amount.token_identifier)
                arguments.append(tx.amount.token_nonce)

            tx = ContractCallBuilder(
                self.config,
                contract=smart_send_contract_address,
                function_name=SMART_SEND_NFT_METHOD,
                call_arguments=arguments,
                caller=self.account_address,
                nonce=self.account_nonce.get_nonce_then_increment(),
                esdt_transfers=nfts,
                gas_limit=gas_limit
            )
            transaction = tx.build()
            transaction_requests.append(transaction)

        return transaction_requests

    def create_sft_transactions(self, input_transactions: List[TokenAmount], gas_per_tx: int = 900000, contract_address: str = None) -> List[Transaction]:
        if (contract_address != None):
            smart_send_contract_address = Address.from_bech32(contract_address)
        else:
            if (self.smart_send_contract != None):
                smart_send_contract_address = Address.from_bech32(
                    self.smart_send_contract)
            else:
                raise Exception("Smart Send Contract address is not set")

        token_identifier = input_transactions[0].amount.token_identifier
        token_nonce = input_transactions[0].amount.token_nonce

        transactions_chunks: List[List[TokenAmount]] = chunks(
            input_transactions, self.chunk_limit)
        transaction_requests: List[Transaction] = []
        for chunk in transactions_chunks:
            if (len(chunk) < 7):
                gas_limit = 6000000
            else:
                gas_limit = len(chunk) * gas_per_tx

            arguments = []
            for tx in chunk:
                arguments.append(tx.address)
                arguments.append(tx.amount.amount_as_integer)

            amounts = sum(i.amount.amount_as_integer for i in chunk)
            amount: TokenPayment = TokenPayment.semi_fungible(
                token_identifier, token_nonce, amounts)

            tx = ContractCallBuilder(
                self.config,
                contract=smart_send_contract_address,
                function_name=SMART_SEND_SFT_METHOD,
                call_arguments=arguments,
                caller=self.account_address,
                nonce=self.account_nonce.get_nonce_then_increment(),
                esdt_transfers=[amount],
                gas_limit=gas_limit
            )
            transaction = tx.build()
            transaction_requests.append(transaction)

        return transaction_requests
