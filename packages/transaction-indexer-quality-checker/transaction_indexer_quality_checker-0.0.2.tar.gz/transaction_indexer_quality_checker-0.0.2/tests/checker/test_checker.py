import unittest
import logging
import os
from dotenv import load_dotenv
from checker.checker import checker


class CheckerTest(unittest.TestCase):

    def test_checker_init(self):
        load_dotenv()
        log_level = os.getenv('LOG_LEVEL')
        balance_in_usd_percentage_threshold = float(
            os.getenv('BALANCE_IN_USD_PERCENTAGE_THRESHOLD'))
        safe_domain = os.getenv('SAFE_DOMAIN')
        palmera_domain = os.getenv('PALMERA_DOMAIN')
        addresses = ["0x2A6e9ceAccf5F9a8507f935fD54329C9CAb28062", "0x6b0D87E634E9e7c33D9F154fB78F8425778bf2b6",
                     "0x6F5464383c7F599C936883ff03Fcfe8d9BDcc0c8", "0x9bCaaF47786962ABB382a6245CdFB67f88EbFF94",]
        chain_id = "1"
        checker(safe_domain, palmera_domain, log_level,
                balance_in_usd_percentage_threshold, addresses, chain_id)
