run_model = """from botcity.core import DesktopBot
import tags as tg  # noqa: E261, F401
import ambient.tolls.clicks as cl
from ambient.tolls.utils import remove_self_necessity, take_click_types


def run():
    class Bot(DesktopBot):
        def action(self, execution=None):
            nf = take_click_types(
                tuple([remove_self_necessity(self, f) for f in cl.click_functions])
            )
            find, click, clickIfPossible = nf

    Bot.main()
"""
