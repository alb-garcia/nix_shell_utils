#!/usr/bin/env python
# upload to pypi
from nix_shell_utils import *

rm('./dist')
runc('python -m build')
runc('python -m twine upload ./dist/*')
    
