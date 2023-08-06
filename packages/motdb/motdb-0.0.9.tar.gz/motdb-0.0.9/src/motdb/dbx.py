# batteries included imports
from collections import namedtuple
from pathlib import Path as P

# pypi imports
import tomli

# custom imports
from motdb.tools.cli_tools import Cli
from motdb.tools.path_tools import resolve, resolve_dir, THISD

# load toml
cfg = {}
def load_toml():
  global cfg
  try:
    
    path_toml = P('dbx.toml')
    
    if not path_toml.is_file():
      from motdb.samples import sample
      cli = Cli()
      print(THISD)
      with open('dbx.toml','wb') as f:
         f.write(sample.toml_file+'\n')

    with open("dbx.toml", "rb") as f:
        cfg = tomli.load(f)

  except Exception as e:
     print(str(e))

class DB:
    """ Base Database Class """
    def __init__(self, *kw):
        load_toml()
        #default = namedtuple('default',['type'])
        self.type = cfg.get('default').get('type')