import sys
sys.path.insert(0,'/Users/mfsteele/Git/motdb/src')
#import motdb
from motdb.tools.print_tools import pp, ppd
from motdb import Dbx

db = Dbx()
db1 = Dbx(cfg='dbx.toml')
db2 = Dbx(cfg='s.toml')


pp(f'{db.type=}')
pp(f'{db1.type=}')
pp(f'{db2.type=}')
