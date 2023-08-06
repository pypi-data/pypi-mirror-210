current_version = "0.0.11"
from .dbx import Dbx as imported_DBX

class Dbx(imported_DBX):
    def __init__(self, **kw):
        super().__init__(**kw)