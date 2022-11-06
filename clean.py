#!/usr/bin/env python
# clean the place from emacs temp files
from nix_shell_utils import *

rm('*~')
with cd('docs'): rm('*~')
with cd('nix_shell_utils'): rm('*~')


    

    
