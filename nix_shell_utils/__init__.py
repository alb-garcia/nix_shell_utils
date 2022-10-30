"""
==================
nix_shell_utils
==================

**nix_shell_utils** is a collection of wrappers for shell commands that are used frequently in shell scripts.

Very often, Python scripts are supported by small shell scripts, heavy with cp,rm,mkdir... as these tasks are
where the shell excels at. The idea behind of *nix_shell_utils* is to move those shell scripts into your Python 
codebase.
"""

from subprocess import CompletedProcess, run as sprun
import os
import glob
from typing import List


def mkdir(path: str | List[str]) -> None:
    """ runs shell command ```mkdir -p path``` for a single or multiple paths.
    
    Arguments:
        path : either a single path or a list of paths (which will be created by mkdir)

    """
    if isinstance(path, str):
        run(fr'\mkdir -p {path}')
    else:
        for p in path:
            run(fr'\mkdir -p {p}')

def cp(src: str | List[str], dest: str | List[str]) -> None:
    """ runs shell command ``\cp src dest``.
    
    If ``src,dest`` are lists of strings, ``\cp src dest`` will be run with
    each pair of source and destination paths (up to the length of the shortest list).

    Arguments:
        src  : either a source path or a list of source paths (strings)
        dest : either a destination path or a list of destination paths
    """
    if isinstance(src, str) and isinstance(dest, str):
        run(fr'\cp {src} {dest}')
    elif isinstance(src, str):
        for d in dest:
            run(fr'\cp {src} {d}')
    else:
        for s,d in zip(src,dest):
            run(fr'\cp {s} {d}')

def cd(path: str) -> str:
    """ changes Python current working directory, returning the previous one.

    ``path`` can contain ``~`` or environment variables, they are expanded prior
    to apply the change of working directory.

    Arguments: 
        path : the new Python execution folder

    Returns: previous Python working directory
    """
    if path == '':
        path = os.path.expandvars('$HOME')
    old_dir = os.getcwd()
    os.chdir(str(expand(path))) # str cast for static type checking
    return old_dir

def rm(path: str) -> None:
    """ executes shell command ``rm -rf path``,effectively removing ``path``silently."""
    
    run(f'\rm -rf {path}')

def ln(src: str, dest: str) -> None:
    """ runs shell command ``ln -s src dest``.
    
    Arguments:
        src : source path of the link
        dest : the path that will link to ``src``
    """
    run(f'ln -s {src} {dest}')
        
def sed(cmd: str, file: str) -> None:
    """ executes shell command ```sed -i cmd file```
    
    Arguments:
        cmd  : sed command to be executed (e.g. ``s/foo/bar/g``)
        file : file where the sed command is executed in place.
    """
    run(f'sed -i {cmd} {file}', quiet = False)

def basename(path):
    """ returns the basename of the input path.

    Example::
        
        >>> basename('/home/foo/bar.py')
            ==> 'bar.py'
    """
    return os.path.basename(path)

def stem(fname):
    """ returns the stem of the basename in the path (i.e. removes suffixes).

    The stem is considered to be the part of the basename between its beginning and the first dot.
    (note the difference with standard library pathlib.path
    Example::

        >>> stem('/home/foo/bar.py')
            'bar'

        >>> stem('/home/foo/foo.py.old')
            'foo'
    """
    
    return basename(fname).split('.')[0]

def bglob(path: str):
    """ returns a list of the basenames resulting from globbing ``path``.

    Assume folder ``/home/foo`` contains files ``a.txt, b.log, c.txt``

    Examples::

        >>> bglob('/home/foo/*.txt')
        ==> ['a.txt', 'c.txt']

        >>> bglob('/home/foo/a*')
        ==> ['a.txt']
    """
    p = str(expand(path)) # str cast for static type checking
    return list([basename(f) for f in glob.glob(p)]) 

def aglob(path: str) -> List[str]:
    """ returns a list of absolute paths resulting from globbing ``path``.

    Examples(Assume folder ``/home/foo`` contains files ``a.txt, b.log, c.txt``)::

        >>> cd('/home/foo')
        >>> bglob('*.txt')
        ==> ['/home/foo/a.txt', '/home/foo/c.txt']

        >>> bglob('a*')
        ==> ['/home/foo/a.txt']
    """
    
    p = str(expand(path)) # str cast for static type checking
    return list([os.path.abspath(f) for f in glob.glob(p)]) 


def root_files(files: List[str], root: str) -> List[str]:
    """ takes a list of files, and prepends them with a ``root`` path.
    
    Example::

        >>> flist = ['a.txt', 'b.txt', 'c.log']
        >>> root_files(flist, '/home/foo/bar'
        ==> ['/home/foo/bar/a.txt', '/home/foo/bar/b.txt', '/home/foo/bar/c.log']

    Arguments:
        files : list of files to be prepended by the root path
        root: : the root path files are prepended by.

    Returns: a list of files prepended by the ``root`` path.
    """
    return list([pjoin(root,f) for f in files])

def pjoin(*paths: str, leaf: bool = True) -> str:
    """ join a number of paths into a single one.

    Examples::
    
        >>> pjoin('/home/foo', 'bar', 'a.txt')
        ==> '/home/foo/bar/a.txt'`
    """
    joint_path = ''
    for p in paths:
        if p[-1] == '/':
            joint_path += p
        else:
            joint_path += p + '/'
    if leaf:
        return joint_path[:-1]
    else:
        return joint_path

def pwd() -> str:
    """ short hand for ``os.getcwd()``."""
    return os.getcwd()

def run(cmd: str, blocking: bool = True, quiet: bool = False) -> CompletedProcess:
    """ wrapper of stdlib's ``subprocess.run`` with reasonable defaults.

    Arguments:
        cmd : the command to be run
        blocking: if ``True``, an exception is thrown if the command exit code != 0
        quiet: if ``True``, the return object contains stdout, stderr. If not, stdout/err are displayed normally.
    Returns: a :class:``subprocess.CompletedProcess`` object containing exit code, and the command executed (at least).
    """
    
    return sprun(cmd,
                 shell = True,
                 capture_output = quiet,
                 check = blocking,
                 universal_newlines=True)

def expand(cmd: str | List[str]) -> str | List[str]:
    """ expands environment variables and home (``~``) from the input command/path.

    Examples (assume username = mario) ::

        >>> expand('/home/${USER}/prj')
        ==> '/home/mario/prj'

        >>> expand('~/prj')
        ==> '/home/mario/prj'

        >>> expand('$HOME/prj')
        ==> '/home/mario/prj'

        >>> expand(['$HOME/prj', '~/prj'])
        ==> ['/home/mario/prj', '/home/mario/prj']

    Arguments:
       cmd : either a string to be expanded or a list of strings to be expanded.

    Returns: if ``cmd`` was a string, it returns the expanded string. If ``cmd`` was
             a list of strings, it returns a list of expanded strings.

    """    
    if isinstance(cmd, str):
        return os.path.expanduser(os.path.expandvars(cmd))
    else:
        return list([os.path.expanduser(os.path.expandvars(c)) for c in cmd])

