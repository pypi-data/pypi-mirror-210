import logging
from . import clicks as cl
from typing import TypeVar


def notify(text):

    logging.basicConfig(
        handlers=[
            logging.FileHandler(
                filename="./logs/log_records.txt", encoding="utf-8", mode="a+"
            )
        ],
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%F %A %T",
        level=logging.INFO,
    )
    print(text)
    logging.info(text)


C = TypeVar("C")


def remove_self_necessity(
    self,
    func: C,
) -> C:
    def wrapper(*args, **kwargs):
        return func(self, *args, **kwargs)

    return wrapper


def take_click_types(thing):
    S = TypeVar("S")

    TIPO_CERTO = (cl.find, cl.click, cl.clickIfPossible, cl.awaitItGoOut)

    def take_type(nf, type: S) -> S:
        return nf

    return take_type(tuple(thing), TIPO_CERTO)


def getClickFunctions(self):
    return take_click_types(
        [remove_self_necessity(self, f) for f in cl.click_functions]
    )


class Nf:
    def __init__(self, Self):
        self.find, self.click, self.clickIfPossible, self.awaitItGoOut = getClickFunctions(Self)
