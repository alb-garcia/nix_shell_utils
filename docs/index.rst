nix_shell_utils 
==========================================================
simple shell-like commands for Python
---------------------------------------


:doc:`nix_shell_utils.rst`


**nix_shell_utils** is a collection of Python function wrappers around commonly
used shell commands. The idea is to move all the small shell scripts heavily
using ``cp``, ``mkdir``, ``rm`` and shell globbing that tend to be used for automation
into one's Python codebase.

Dependencies
-------------

* Python version required: `3.10+`
* If documentation is to be generated ``sphinx`` and ``sphinx_rtd_theme`` packages are required:

.. code-block:: console

    pip install sphinx sphinx_rtd_theme

Installation
-------------
1. clone this repository (or download a zip and unzip it somewhere)

.. code-block:: console

    git clone https://github.com/alb-garcia/nix_shell_utils.git

2. inside the cloned folder, install:
   
.. code-block:: console

    pip install .


Examples
------------


* the following python
  
.. code-block:: python

    from unix_shell_utils import *
    
    dest = '$PRJ_HOME/sv/src'
    src  = '$PRJ_HOME/gen/sv/out'
    mkdir(dest)         # make destination folder
    with cd(src):       # change to src directory - returns automatically to current folder
        cp('*.sv',dest) # copy all systemverilog files in src to dest folder
	                             

is equivalent to this shell code:

.. code-block:: console

    dest=$PRJ_HOME/sv/src
    src=$PRJ_HOME/gen/sv/out
    mkdir -p $PRJ_HOME/sv/src
    curdir=$PWD
    cd $src
    cp *.sv $dest
    cd $curdir

* removing files: the following code

.. code-block:: python

    with cd('$PRJ_HOME/logs/'):
        rm('*.log')

is equivalent to the following shell commands:

.. code-block:: console

    curdir=$PWD
    cd $PRJ_HOME/logs
    rm -rf *.log
    cd $curdir

Documentation
----------------
    
To generate the documentation (assuming the clone repository lives @ $NIX_SHELL_UTILS_DIR:

.. code-block:: console

    cd $NIX_SHELL_UTILS_DIR/docs
    make html

the documentation can be then accessed @ ``$NIX_SHELL_UTILS_DIR/docs/_build/html/index.htm``
    
Package Documentation
===========================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:

   nix_shell_utils



     
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
