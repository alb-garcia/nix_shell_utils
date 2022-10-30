
nix_shell_utils - simple shell-like commands for Python
==========================================================

**nix_shell_utils** is a collection of Python function wrappers around commonly
used shell commands. The idea is to move all the small shell scripts heavily
using ``cp``, ``mkdir``, ``rm`` and shell globbing that tend to be used for automation
into one's Python codebase.

Dependencies
-------------

* None
* Python version required: `3.10+`

Installation
-------------
TBD

Examples
------------

* Assume we have a ``generate_headers(path)`` function that generates some C-code files
  in a given path.

.. code-block:: python

    from unix_shell_utils import *
    
    PRJ_DIR = '$PROJECT_HOME'           # we can use env variables when defining paths
    OUT_DIR =   pj(PRJ_DIR, 'out/h')    # pj => path-join 
    BUILD_DIR = pj(PRJ_DIR, 'build')
    INSTALL_DIR = '/install/h'

    mkdir([OUT_DIR,BUILD_DIR])          # can make a list of dirs (creating intermediate dirs)
                                        # command is silent if dirs already exist
    
    generate_code(OUT_DIR)
    
    cp(pj(OUT_DIR, '*.h'), install_dir) # can use globbing as in the shell
		rm(pj(BUILD_DIR, '*'))
    

Package Documentation
===========================================

.. toctree::
   :maxdepth: 1
   :caption: Contents:

   nix_shell_utils

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
