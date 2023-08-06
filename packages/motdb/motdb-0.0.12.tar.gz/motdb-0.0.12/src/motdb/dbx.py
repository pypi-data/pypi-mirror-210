# batteries included imports
from collections import namedtuple
from pathlib import Path as P
from types import SimpleNamespace

# pypi imports

# custom imports
from .tools.cli_tools import Cli, is_venv, get_venv_path
from .tools.path_tools import resolve, resolve_dir, parent
from .tools.load_tools import load_toml, load_cfg
        

class DB:
  """ Base Database Class """
  def __init__(self, **kw):
    cfg = load_cfg( kw.get('cfg') )
    self.type = kw.get('type') or cfg.get('default', {}).get('type')

  def test(self):
    print(f"I'm {self.type}")


class DB_sqlite3(DB):
  def __init__(self, **kw):
    super().__init__(**kw)
    self.type = 'sqlite3'


class DB_mysql(DB):
  def __init__(self, **kw):
    super().__init__(**kw)
    self.type = 'mysql'


class DB_factory:
  def __init__(self, db_type='sqlite3', **kw):
    
    match db_type:
      case 'sqlite3':
        _db = DB_sqlite3(**kw)
      case 'mysql':
        _db = DB_mysql(**kw)
      case _:
        _db = DB_sqlite3(**kw)
    
    # inherit not private method overrides from specific db instances
    self.__dict__.update( { k:v for k,v in _db.__dict__.items() if not k.startswith('_') } )

    ''' Sample dbx.toml
    [default]
    type = 'sqlite3'
    mysql_port = 3306
    mssql_port = 1433
    user = 'commonly_defined_username'

    [sqlite3]
    host1.user = 'some_username_in_db@host1' # accessed as cfg.get('sqlite3.host')
    '''

  def get_db(self, db_type=None):
    db_type = db_type or self.type
    self.__init__(db_type)
    return self


class Dbx(DB):
  def __init__(self, **kw):
    super().__init__(**kw)
    # set cfg/params
    cfg = globals().get('cfg') or {}
    self.cfg = kw['cfg'] = load_cfg( kw.get('cfg') or cfg ) # cfg=dict or cfg=path-to-.toml
    db_type = kw.get('type') or self.cfg.get('type')
    db_type = db_type or self.cfg.get('default',{}).get('type') or 'sqlite3'
     
    # inherit non-private method overrides from specific db instances
    _DB = DB_factory( db_type, **kw )
    self.update_dbx( _DB )

    default = self.cfg.get('default') or {}
    if self.cfg.get(self.type) and isinstance( self.cfg.get(self.type), dict ):
      print('here')
      self.update_dbx( self.cfg.get(self.type) )
    elif isinstance( default, dict ):
      self.update_dbx( default )


  def update_dbx(self, dict_prms):
    # set non-private method overrides
    _dict_prms = dict_prms if not hasattr(dict_prms,'__dict__') else dict_prms.__dict__
    self.__dict__.update( { k:v for k,v in _dict_prms.items() if not k.startswith('_') } )
    