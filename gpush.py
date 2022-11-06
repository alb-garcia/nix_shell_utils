#!/usr/bin/env python

from nix_shell_utils import *

runc('git status')
runc('git add .')
runc("git commit -m 'dev change up'")
runc("git push")
    

    
