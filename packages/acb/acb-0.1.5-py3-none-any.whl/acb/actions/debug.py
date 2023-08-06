from inspect import getmodule
from inspect import stack
from pathlib import Path
from pprint import pformat
from time import time

from aioconsole import aprint
from icecream import colorizedStderrPrint
from icecream import ic
from loguru import logger

from acb.config import ac


def get_mod():
    mod_logger = stack()[3][0]
    mod = getmodule(mod_logger)
    mod.name = Path(mod.__file__).stem
    return mod


def log_debug(s):
    mod = get_mod()
    if ac.debug[mod.name]:
        if ac.deployed or ac.debug.production:
            return logger.patch(lambda record: record.update(name=mod.__name__)).debug(
                s
            )
        return colorizedStderrPrint(s)


ic.configureOutput(prefix="    debug:  ", includeContext=True, outputFunction=log_debug)
if ac.deployed or ac.debug.production:
    ic.configureOutput(prefix="", includeContext=False, outputFunction=log_debug)


async def apformat(obj, sort_dicts: bool = False) -> None:  # make purple
    mod = get_mod()
    if not ac.deployed and not ac.debug.production and ac.debug[mod.name]:
        await aprint(pformat(obj, sort_dicts=sort_dicts))


def timeit(func):
    def wrapped(*args, **kwargs):
        start = time()
        result = func(*args, **kwargs)
        end = time()
        logger.debug(f"Function '{func.__name__}' executed in {end - start} s")
        return result

    return wrapped
