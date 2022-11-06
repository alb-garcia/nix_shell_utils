
|pic1| |pic2| |pic3| |pic4|

.. |pic1|  image:: https://raw.githubusercontent.com/alb-garcia/nix_shell_utils/main/docs/img/python.svg?
		   
.. |pic2|  image:: https://raw.githubusercontent.com/alb-garcia/nix_shell_utils/main/docs/img/tag.svg?
		   
.. |pic3|  image:: https://raw.githubusercontent.com/alb-garcia/nix_shell_utils/main/docs/img/test.svg?

.. |pic4| image:: https://raw.githubusercontent.com/alb-garcia/nix_shell_utils/main/docs/img/coverage.svg?		   

		  
	   

nix_shell_utils 
==========================================================
simple shell-like commands for Python
---------------------------------------

**nix_shell_utils** is a collection of Python function wrappers around commonly
used shell commands. The idea is to move all the small shell scripts heavily
using ``cp``, ``mkdir``, ``rm`` and shell globbing that tend to be used for automation
into one's Python codebase.

The package is *not* multiplatform: it will only work in unix-like systems (only tested
in Ubuntu & RHEL).

Dependencies
-------------

* Python version required: `3.7+`
* If documentation is to be generated ``sphinx`` and ``sphinx_rtd_theme`` packages are required:

.. code-block:: console

    pip install sphinx sphinx_rtd_theme

Installation
-------------

Simply type ::

  pip install nix_shell_utils

  
Documentation
----------------

Documentation can be found @ `readthedocs <https://nix-shell-utils.readthedocs.io>`_


Examples
------------


* cp, cd, mkdir: the following python
  
.. code-block:: python

    from unix_shell_utils import *
    
    dest = '$PRJ_HOME/sv/src'
    src  = '$PRJ_HOME/gen/sv/out'
    mkdir(dest)         # make destination folder
    with cd(src):       # change to src directory - returns automatically to current folder
        cp('*.sv',dest) # copy all .sv files in src to dest folder
	                             

is equivalent to this shell code:

.. code-block:: console

    dest=$PRJ_HOME/sv/src
    src=$PRJ_HOME/gen/sv/out
    mkdir -p $dest
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

* temporary environment: the code under the ``tmpenv`` context manager

.. code-block:: python

   with tmpenv('HOME', FOO='BAR'):
       print(os.environ['FOO'] # ==> 'BAR'
       ...
       

will modify temporarily the ``os.environ`` in place so that ``HOME`` env variable is
deleted, and a new environment variable ``FOO`` is added. Upon leaving the ``with`` block,
``os.environ`` is returned to its prior state.


Development
---------------

1. clone this repository (or download a zip and unzip it somewhere)

.. code-block:: console

    git clone https://github.com/alb-garcia/nix_shell_utils.git

2. inside the cloned folder, make a editable installation
   
.. code-block:: console

    pip install -e .

3. To run tests (pytest needs to be installed):

.. code-block:: console

    cd test; pytest -vvv


Documentation Generation
---------------------------
    
To generate the documentation (assuming the clone repository lives @ ``$NIX_SHELL_UTILS_DIR``:

.. code-block:: console

    cd $NIX_SHELL_UTILS_DIR/docs
    make html

the documentation can be then accessed @ ``$NIX_SHELL_UTILS_DIR/docs/_build/html/index.htm``
    
