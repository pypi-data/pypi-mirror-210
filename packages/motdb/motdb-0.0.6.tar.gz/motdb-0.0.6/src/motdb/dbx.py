# batteries included imports

# pypi imports
import tomli

# custom imports
from motdb.tools.cli_tools import Cli

# load toml
with open("cfg.toml", "rb") as f:
    cfg = tomli.load(f)

class DB:
    """ Base Database Class """
    def __init__(self, *kw):
        self.type = cfg.default.get('type') or 'mysql'