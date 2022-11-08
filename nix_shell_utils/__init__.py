from __future__ import annotations

"""
==================
nix_shell_utils
==================

**nix_shell_utils** is a collection of wrappers for shell commands that are used frequently in shell scripts.
"""

from subprocess import CompletedProcess, run as sprun
import os
import glob
from typing import List
from contextlib import contextmanager
import sys
import shlex


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
    elif isinstance(dest, str):
        for s in src:
            run(fr'\cp {s} {dest}')
    else:
        for s,d in zip(src,dest):
            run(fr'\cp {s} {d}')

@contextmanager            
def cd(path: str):
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
    try:
        yield
    finally:
        os.chdir(old_dir)
    

def rm(path: str) -> None:
    """ executes shell command ``rm -rf path``,effectively removing ``path`` silently.

    Arguments:
        path : the path to remove.
    """
    
    run(f'rm -rf {path}')

def ln(src: str, dest: str) -> None:
    """ runs shell command ``ln -s src dest``.
    
    Arguments:
        src : source path of the link
        dest : the path that will link to ``src``
    """
    run(f'ln -s {src} {dest}')
        
def sed(cmd: str, file: str) -> CompletedProcess:
    """ executes shell command ```sed -i cmd file```
    
    Arguments:
        cmd  : sed command to be executed (e.g. ``s/foo/bar/g``)
        file : file where the sed command is executed in place.
    """
    return run(f'sed {cmd} {file}', quiet = False)

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
    return list([pj(root,f) for f in files])

def pj(*paths: str, leaf: bool = True) -> str:
    """ join a number of paths into a single one.

    Examples::
    
        >>> pj('/home/foo', 'bar', 'a.txt')
        ==> '/home/foo/bar/a.txt'`
    """
    joint_path = ''
    for (i,p) in enumerate(paths):
        # if i != 0 and p[0] == '/':
        #     p = p[1:]
            
        if p != '':
            if p[-1] == '/':
                joint_path += p
            else:
                joint_path += p + '/'

    if leaf and joint_path != '':
        return joint_path[:-1]
    else:
        return joint_path

def pwd() -> str:
    """ short hand for ``os.getcwd()``."""
    return os.getcwd()


def runc(cmd: str,echo: bool = True, blocking: bool = False) -> int:
    """ runs the shell command ``cmd`` in `console mode`.

    **runc** is a wrapper of ``subprocess.run`` with the following defaults:

    * by default, it prints the shell command executed in ``stdout``
    * it prints the outputs and errors of the commmand in ``stdout`` and ``stderr``
    * it returns the results return code of the command.

    Arguments:
        cmd : the command by the ``sh`` shell.
        echo : if ``True``, ``cmd`` is printed in ``stdout``.
        blocking : if ``True``, a ``CalledProcessError`` exception is thrown if the command fails (return code different from ``0``).

    Returns:
        the return code of the shell command executed.
        
    """
    if echo:
        print(cmd)
    c =  sprun(cmd,
               shell = True,
               capture_output = False,
               check = blocking,
               universal_newlines=True)
    
    return c.returncode

def source(filename: str) -> None:
    runc(f'. {filename}')
    
def run(cmd: str, blocking: bool = False, quiet: bool = True) -> CompletedProcess:
    """ runs a shell command with a ``subprocess.run`` wrapper with sensible defaults.

    Example::

        >>> c = run('cpu-info')
        cpu-info
        Packages:
                0: Intel Celeron 6305
        Microarchitectures:
                2x unknown
        Cores:
                0: 1 processor (0), Intel unknown
                1: 1 processor (1), Intel unknown
        Logical processors (System ID):
                0 (0): APIC ID 0x00000000
                1 (1): APIC ID 0x00000002

        >>> print(c.stdout)
        Packages:
                0: Intel Celeron 6305
        Microarchitectures:
                2x unknown
        Cores:
                0: 1 processor (0), Intel unknown
                1: 1 processor (1), Intel unknown
        Logical processors (System ID):
                0 (0): APIC ID 0x00000000
                1 (1): APIC ID 0x00000002

        >>> print(c.returncode)
        0
    
    Arguments:
        cmd : the command to be run
        blocking: if ``True``, an exception is thrown if the command exit code != 0
        quiet: if ``False``, ``stdout``, ``stderr`` and an echo of the command executed is printed.
    Returns: a :class:``subprocess.CompletedProcess`` object containing exit code, and the command executed (at least).
    """
    if not quiet:
        print(cmd)
    c = sprun(cmd,
              shell = True,
              capture_output = True,
              check = blocking,
              universal_newlines=True)
        
    if not quiet:
        if c.stdout != '':
            print(c.stdout, end = '', file = sys.stdout)
        if c.stderr != '':
            print(c.stderr, end = '', file = sys.stderr)
            
    return c
def lrun(*cmds: str, blocking: bool = False, quiet: bool = True) -> List[CompletedProcess]:
    results = []
    
    for cmd in cmds:
        results.append(run(cmd,blocking = blocking, quiet = quiet))
        
    return results
        

def runopt(cmd: str, blocking: bool = False, quiet: bool = True) -> CompletedProcess:
    """ runs a shell command with a ``subprocess.run`` wrapper with sensible defaults.

    Example::

        >>> c = run('cpu-info')
        cpu-info
        Packages:
                0: Intel Celeron 6305
        Microarchitectures:
                2x unknown
        Cores:
                0: 1 processor (0), Intel unknown
                1: 1 processor (1), Intel unknown
        Logical processors (System ID):
                0 (0): APIC ID 0x00000000
                1 (1): APIC ID 0x00000002

        >>> print(c.stdout)
        Packages:
                0: Intel Celeron 6305
        Microarchitectures:
                2x unknown
        Cores:
                0: 1 processor (0), Intel unknown
                1: 1 processor (1), Intel unknown
        Logical processors (System ID):
                0 (0): APIC ID 0x00000000
                1 (1): APIC ID 0x00000002

        >>> print(c.returncode)
        0
    
    Arguments:
        cmd : the command to be run
        blocking: if ``True``, an exception is thrown if the command exit code != 0
        quiet: if ``False``, ``stdout``, ``stderr`` and an echo of the command executed is printed.
    Returns: a :class:``subprocess.CompletedProcess`` object containing exit code, and the command executed (at least).
    """
    if not quiet:
        print(cmd)
    args = shlex.split(cmd)
    c = sprun(args = args,
              shell = False,
              capture_output = True,
              check = blocking,
              universal_newlines=True)
        
    if not quiet:
        if c.stdout != '':
            print(c.stdout, end = '', file = sys.stdout)
        if c.stderr != '':
            print(c.stderr, end = '', file = sys.stderr)
            
    return c

@contextmanager
def tmpenv(*remove: str, **update: str):
    """  context manager to temporarily update the os.environ shell environment in place.

    Example::
        
        with tmpenv('HOME', FOO='BAR', FOOD='SPAM'):
            print('HOME' in os.environ.keys) # => False
            print(os.environ['FOO']) # => 'BAR'
            print(os.environ['FOOD']) # => 'SPAM'

        print('HOME' in os.environ.keys) # => True
        print('FOO' in os.environ.keys) # => False
        print('FOOD' in os.environ.keys) # => False

    The ``os.environ`` dictionary is updated in-place so that the modification
    is sure to work in all situations.

    Arguments:
        remove : environment variable to remove
        update : environment variables and values to add/update
    """
    env = os.environ
    update = update or {}
    remove = remove or ()

    # List of environment variables being updated or removed.
    stomped = (set(update.keys()) | set(remove)) & set(env.keys())
    # Environment variables and values to restore on exit.
    update_after = {k: env[k] for k in stomped}
    # Environment variables and values to remove on exit.
    remove_after = frozenset(k for k in update if k not in env)

    try:
        env.update(update)
        [env.pop(k, None) for k in remove]
        yield
    finally:
        env.update(update_after)
        [env.pop(k) for k in remove_after]



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

