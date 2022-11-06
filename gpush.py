#!/usr/bin/env python
# pushes all changes into origin (for small modifications) until 1.0.0
from nix_shell_utils import *

runc('git status')
runc('git add .')
runc("git commit -m 'dev small modification'")
runc("git push")
    

    
