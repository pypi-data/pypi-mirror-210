run_model = """from botcity.core import DesktopBot
import tags as tg  # noqa: E261, F401
import blocks as bls
from ambient.tolls.utils import Nf


def run():
    class Bot(DesktopBot):
        def action(self, execution=None):
            nf = Nf(self)
            bls.firsth_block(self, nf)

    Bot.main()
"""
