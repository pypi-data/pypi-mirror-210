# load_tools version 0.1.1motdb
# batteries included imports
import sys
from pathlib import Path as P
from types import SimpleNamespace
from typing import Any

# pypi imports
import tomli

# custom imports
from .cli_tools import is_venv, get_venv_path
from .path_tools import parent


# load toml
def load_toml(f=''):
  dict_cfg = {}
  try:

    path_toml = P(f)
    if not path_toml.is_file():

      if is_venv():
        venv = get_venv_path()
        venv_parent = parent(venv)
        path_parent = P(venv_parent)
        path_cfgs = [ i.name for i in path_parent.iterdir() if i.name == 'dbx.toml' ]
        if path_cfgs:
          with open(path_cfgs[0], 'rb') as f:
            dict_cfg = tomli.load(f)
      else:
        curr_path = P(sys.path[0])
        path_cfgs = [ i.name for i in curr_path.iterdir() if i.name == 'dbx.toml' ]
        if path_cfgs:
          with open(path_cfgs[0], 'rb') as f:
            dict_cfg = tomli.load(f)
    else:
      with open(path_cfgs[0], 'rb') as f:
        dict_cfg = tomli.load(f)
    
  except Exception as e:
      print(str(e))

  finally:
    return dict_cfg
  

def load_cfg(cfg=None):
  dict_cfg = {}
  try:
    if not cfg:
      dict_cfg = load_cfg( cfg or '' )
    elif not isinstance( cfg, dict ):
      dict_cfg = {}
    else:
      dict_cfg = cfg
  except Exception as e:
    print(str(e))
  finally:
    return dict_cfg
  



