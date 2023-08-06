import logging
from comparer import Comparer

def checker(safe_domain, palmera_domain, log_level, balance_in_usd_percentage_threshold, addresses, chain_id):
    logging.basicConfig(level=log_level)
    comp = Comparer(domain_a=safe_domain, domain_b=palmera_domain, log=logging,
                    balance_in_usd_percentage_threshold=balance_in_usd_percentage_threshold)
    comp.compare_safes_for_chain(chain_id=chain_id, addresses=addresses)

