from .. import *
from .base import *

class FAppBar(FBase):
    def update(self, prev):
        if prev and hasattr(prev, "ui"):
            self.ui = prev.ui
        else:
            self.ui = ft.AppBar()
        super().update(prev)
