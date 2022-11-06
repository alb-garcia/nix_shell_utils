#!/usr/bin/env python
# runs sphinx and shows in firefox
from nix_shell_utils import *

with cd('./docs'):
    runc('make clean')
    runc('make html')
    runc('firefox ./_build/html/index.html')
    

    
