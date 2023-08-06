import requests
import logging
from .api_interface import APIInteface


class TransactionAPIinterface(APIInteface):
    def __init__(self, domain: str = "https://safe-transaction-mainnet.safe.global", log: logging.Logger = logging):
        self.log = log
        if domain is None:
            raise ValueError("domain cannot be None")
        super().__init__(domain, "tx_indexer_svc", "v1")

    def is_expected_response(self, res: requests.Response):
        if res.status_code > 299:
            self.log.warning(f"Received non-200s reponse from domain: {self.domain}")
            return False
        else:
            return True


    def get_safe(self, address: str) -> dict:
        res = requests.get(f"{self.base_url}/safes/{address}")

        if self.is_expected_response(res):
            return res.json()

    def get_transactions_from_safe(self, address: str) -> dict:
        res = requests.get(f"{self.base_url}/safes/{address}/all-transactions/?executed=true")
        if self.is_expected_response(res):
            return res.json()

    def get_complete_list_of_transactions_from_safe(self, address: str) -> list:
        res = self.get_transactions_from_safe(address)
        transactions = res["results"]
        while res["next"]:
            res = requests.get(res["next"])
            res = res.json()
            transactions.extend(res["results"])
        return transactions

    def get_balances_for_safe(self, address: str) -> list:
        res = requests.get(f"{self.base_url}/safes/{address}/balances")
        if self.is_expected_response(res):
            return res.json()

    def get_balances_in_usd_for_safe(self, address: str) -> list:
        res = requests.get(f"{self.base_url}/safes/{address}/balances/usd")
        if self.is_expected_response(res):
            return res.json()
