import random
import numpy as np
from texttable import Texttable


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)

def args_print(args, logger):
    _dict = vars(args)
    table = Texttable()
    table.add_row(["Parameter", "Value"])
    for k in _dict:
        table.add_row([k, _dict[k]])
    logger.info(table.draw())
