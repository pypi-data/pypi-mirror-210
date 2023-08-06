# path_tools version 0.1.1motdb
# This only works for the {project_dir}/app/tools/path_tools.py pattern
boilerplate_to_be_pasted = '''
###### Only append paths to INCLUDES below; Must include TOOLS  ###################################
import sys; THISF = __file__; THISD = THISF.rsplit("/",1)[0]; TOOLS=f'{THISD}';
INCLUDES = [ TOOLS ]; sys.path.append(TOOLS);
import path_tools; INCLUDES = path_tools.include_paths( INCLUDES, THISF, sys );
###################################################################################################
'''

###################################################################################################
# Uses {project_dir}/app/tools/path_tools.py pattern
# Allows relative pathing regardless of where calling from
# In each file, include the contents of 'boilerplate_to_be_pasted' ensuring TOOLS is correct
# Add relative paths to the boilerplate_to_be_pasted's INCLUDES list as needed
###################################################################################################
import sys; THISF = __file__; THISD = THISF.rsplit("/",1)[0]; TOOLS=f'{THISD}';
PKGHOME = f'{THISD}/..' # edit this as relative path; resolved after the functions below
###################################################################################################

from pathlib import Path as P;

def resolve(f):
    f = str( P( f ).resolve() )
    return f

def resolve_dir(d):
    p = P( d )
    if p.is_file():
        d = resolve(d).rsplit('/',1)[0]
    elif p.is_dir():
        d = resolve(d)
    return d

def parent(o):
    p = P( o )
    if p.is_file():
        return resolve_dir( o )
    elif p.is_dir():
        return resolve_dir( f'{o.rstrip("/")}/..' )

###################################################################################################
PKGHOME = resolve_dir(PKGHOME)
TOOLS = resolve_dir(TOOLS)
###################################################################################################

def include_paths(_includes, calling_file, _sys):
    # ensure includes is a list
    includes = _includes if isinstance(_includes,list) else [ _includes ]

    # ensure TOOLS path present in _includes
    passed_tools_dir = [ p for p in _includes if resolve_dir(p)==TOOLS ]
    if not passed_tools_dir:
        err = 'The 1st paramter must include the path_tools.py directory (TOOLS)'
        err += f'\n\nExample boilerplate to be pasted as necessary:\n{boilerplate_to_be_pasted}'
        raise Exception(err)

    # calling_file required; __file__ is generally sent as the calling file
    if not calling_file.startswith('/'):
        err = 'Exception in include_paths: '
        err += f'The 2nd parameter must start with "/", '
        err += f'e.g., include_paths( INCLUDES, __file__, sys ) works since '
        err += f'__file__ always gets resolved to absolute path.'
        err += f'\n\nExample boilerplate to be pasted as necessary:\n{boilerplate_to_be_pasted}'
        raise Exception(err)
    
    # _sys must be passed by referenced having been imported locally by the caller
    if not type(_sys)==type(sys):
        err = '_sys must be passed by referenced having been imported locally by the caller'
        err += f'\n\nExample boilerplate to be pasted as necessary:\n{boilerplate_to_be_pasted}'
        raise Exception(err)

    # resolve relative path of caller to absolute paths of file and directory
    calling_file = resolve(calling_file)
    calling_dir = resolve_dir(calling_file)

    # resolve relative path of included paths to their absolute paths
    includes = [ p if p.startswith('/') else f'{calling_dir}/{p}' for p in includes ]
    includes = [ resolve_dir(p) for p in includes ]
    
    from print_tools import pp, pf
    #print(f'1: {pf(_sys.path)}')

    # remove initially added relative path to tools; adding TOOLS back later
    _sys.path = [ p for p in _sys.path if not p in passed_tools_dir ]
    #print(f'2: {pf(_sys.path)}')
    
    # add resolved paths if not already present in the passed sys.path
    _ = [ _sys.path.append(p) for p in includes if not p in _sys.path ]
    #print(f'3: {pf(_sys.path)}')

    # add TOOLS as 2nd search paramter - will be removed as duplicate if called from tools dir
    _sys.path.insert( 1, TOOLS )
    #print(f'4: {pf(_sys.path)}')

    # remove most recent duplicates
    _sys.path.reverse()
    for p in _sys.path:
        while _sys.path.count(p) > 1:
            _sys.path.remove(p)
    _sys.path.reverse()
    #print(f'5: {pf(_sys.path)}')

    # return resolved paths
    return includes
