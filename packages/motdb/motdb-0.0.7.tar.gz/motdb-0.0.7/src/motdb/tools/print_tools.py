# print_tools version 1.1
# examples:
# from tools.print_tools import *
# from tools.print_tools import pplog
from pprint import PrettyPrinter

# ansicolors and some symbols
###################################################################################################

# Reset
RST="\033[0m"           # Text Reset

# Regular Colors
Black="\033[0;30m"      # Black
Red="\033[0;31m"        # Red
Green="\033[0;32m"      # Green
Yellow="\033[0;33m"     # Yellow
Blue="\033[0;34m"       # Blue
Purple="\033[0;35m"     # Purple
Cyan="\033[0;36m"       # Cyan
White="\033[0;37m"      # White

# Bold
BBlack="\033[1;30m"     # Black
BRed="\033[1;31m"       # Red
BGreen="\033[1;32m"     # Green
BYellow="\033[1;33m"    # Yellow
BBlue="\033[1;34m"      # Blue
BPurple="\033[1;35m"    # Purple
BCyan="\033[1;36m"      # Cyan
BWhite="\033[1;37m"     # White

# Background
BGBlack="\033[40m"      # Black
BGRed="\033[41m"        # Red
BGGreen="\033[42m"      # Green
BGYellow="\033[43m"     # Yellow
BGBlue="\033[44m"       # Blue
BGPurple="\033[45m"     # Purple
BGCyan="\033[46m"       # Cyan
BGWhite="\033[47m"      # White

# Underline
ULBlack="\033[4;30m"      # Black
ULRed="\033[4;31m"        # Red
ULGreen="\033[4;32m"      # Green
ULYellow="\033[4;33m"     # Yellow
ULBlue="\033[4;34m"       # Blue
ULPurple="\033[4;35m"     # Purple
ULCyan="\033[4;36m"       # Cyan
ULWhite="\033[4;37m"      # White

# Symbols
checkmark='\u2713'
crossmark='\u2717'

# cursor
mvup="\033[A"
mvdown="\033[B"
clearln="\33[2K\r"



# Functions
###################################################################################################
width, indent, margin = 50, 4, 0
from pprint import PrettyPrinter
pr = print

def pp(msg='', w=0, i=0):
    w = w or width
    i = i or indent
    _pr = PrettyPrinter( indent=i, width=w ).pprint
    _pr( msg )

def pf(msg='', w=0, i=0):
    w = w or width
    i = i or indent
    _pf = PrettyPrinter( indent=i, width=w ).pformat
    return _pf( msg )

def ppd(o, w=0, i=0):
    _o = [ i for i in dir(o) if not i.startswith('__') ]
    pp( _o, w, i )

def newsprint(mls='', w=40, m=0, i=0, return_txt=False):
    w = w or width
    i = i or indent
    m = m or margin
    """ Prints Multi-line-strings (mls) as newsprint
        - inserts newlines accoring to width (w) and spaces according to margin (m).
        - steps
            1. Drop in mls/multi-line-string = ''' blah blah blah '''
            2. run newsprint(mls) or newsprint(mls,80) etc
        - example:
            mls = '''
            - steps
                1. Drop in mls/multi-line-string = ``` blah blah blah ```
                2. run newsprint(mls) or newsprint(mls,30,2) etc
            '''
            newsprint(mls,30,2) =>
              - steps
              1. Drop in
              mls/multi-line-string =
              ``` blah blah blah ```
              2. run newsprint(mls)
              or newsprint(mls,30,2)
              etc
    """
    newspf = PrettyPrinter( indent=i, width=w ).pformat
    strcols = newspf( mls )
    strcols = strcols.strip()
    if strcols[-1] == ')':
        strcols = strcols[:-1]
    if strcols[0] == '(':
        strcols = strcols[1:]
    if not return_txt:
        for line in strcols.splitlines():
            newsline = line.replace("'","").replace('\\n','').rstrip()
            newsline = " "*m + newsline
            print(newsline)
    else:
        news_list = []
        for line in strcols.splitlines():
            newsline = line.replace("'","").replace('\\n','').rstrip()
            newsline = " "*m + newsline
            news_list.append(newsline)
        return '\n'.join(news_list)

def pplog(msg='', log_lvl=0, title='', w=88, i=4, logger=None):
    debug = 0 if not 'debug' in locals() else debug
    if log_lvl > debug:
        return
    log = logger or print
    w = w or width
    i = i or indent
    if title:
        log("\n"+"*"*w)
        leftspcs = int(0.5*(w - len(title)))
        log(f"{' '*leftspcs}{title}")
        log("*"*w)
    if not msg:
        # only log title
        return
    _pf = PrettyPrinter( indent=i, width=w ).pformat
    #logmsg = _pf( msg )
    logmsg = msg if not logger else _pf( msg )
    #logmsg = logmsg.strip().strip('(').strip(')')
    logmsg = logmsg.strip('(').strip(')')
    for line in logmsg.splitlines():
        #line = re.sub( re.escape('\n'), '', line )
        print(f'{line[:w]}\n')
        remains = line[w:]
        while remains:
            dbl = i*2
            log(f'{" "*dbl}{remains[:w-dbl]}')
            remains = remains[w-dbl:]

import re
def strip_ansi(strs):
    re_ansi = re.compile(r'\x1b[^m]*m')
    if isinstance(strs, str):
        cleaned = re_ansi.sub('', strs)
    elif isinstance(strs, (list,tuple)):
        cleaned = [ strip_ansi(s) for s in strs ]
        if isinstance(strs,tuple):
            cleaned = tuple(cleaned)
    elif isinstance(strs, set):
        cleaned = { strip_ansi(s) for s in strs }
    elif isinstance(strs, dict):
        cleaned = { strip_ansi(k):strip_ansi(v) for k,v in strs }
    else:
        cleaned = strs
    return cleaned


exec_mainpr = '''
def mainpr(self, msg):
    """ if __name__ == '__main__': print(msg) """
    if __name__ == '__main__':
        print(msg)
'''

exec_mainpp = '''
def mainpp(self, msg):
    """ if __name__ == '__main__': pp(msg) """
    if __name__ == '__main__':
        pp(msg)
'''

import re
def left_shift_ss(ss=''):
    """ Counts spaces at beginning of each line
        so SQL Statement (ss) can be printed
        left shifted to margin
    """
    sslns = [ ln for ln in ss.splitlines() if ln.strip() ]
    ct = min( re.match(' *',ln).span()[-1] for ln in sslns )
    ss = '\n'.join( ln[ct:] if ln[0:ct] == ' '*ct else ln for ln in sslns )
    print(f'\n{ss}\n')
    return ss