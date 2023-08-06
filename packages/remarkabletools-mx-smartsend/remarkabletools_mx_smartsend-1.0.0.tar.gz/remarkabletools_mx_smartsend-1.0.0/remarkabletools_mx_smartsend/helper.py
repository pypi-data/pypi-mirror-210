from typing import List
from remarkabletools_mx_smartsend.token_amount import TokenAmount

def chunks(iterable: List[TokenAmount] , size):
    return [iterable[i:i+size] for i in range(0, len(iterable), size)]
