#!/usr/bin/env python

project= 'nix_shell_utils'

from nix_shell_utils import run, cd ,sed, runc, source, rm, lrun
import re
import sys

re_cov = re.compile(rf'^TOTAL.*\D(\d+)%')
re_version = re.compile(r'version\s*=\s*"(\d+\.\d+\.\d+)"')

def check(msg = 'continue'):
    yes_no = input(f"{msg} [y/n]? ").lower()

    if not yes_no in ['y','yes']:
        print("Release aborted. Exiting...")
        sys.exit(1)


print('\n----- runing tests with coverage -----\n')


with cd('./test'):
    c = run('pytest --cov-report term-missing --cov=nix_shell_utils', quiet = False)


for line in c.stdout.splitlines():
    m = re_cov.match(line) #no walrus operator to support Python 3.7
    if m != None:
        coverage = int(m.groups()[0])

check()
print('\n----- generating documentation locally -----\n')

with cd('./docs'):
    runc('make clean')
    runc('make html')
    runc('firefox ./_build/html/index.html')
    
check()
# get and show current version from pyproject.toml
c = sed('-n /version/p', 'pyproject.toml')
m = re_version.match(c.stdout.strip())

if m != None:
    cur_version = m.groups()[0]
    print(f'\n-- current version: {cur_version}\n')

# prompt for new version and tag comment
new_version = input('new version (X.Y.Z)? ')    
tcomment     = input('tag comment ?')

check(f'modify project files with version {new_version}')

ver_re = '[0-9]\+\.[0-9]\+\.[0-9]\+'
with cd('./docs'):
    # change coeverage and tag local badges generation script
    sed(f'-i "s/--value=[0-9]\+/--value={coverage}/g"', 'genbadges')
    sed(f'-i "s/{ver_re}/{new_version}/g"', 'genbadges')
    
    source('./genbadges') # generate local badges

    # change conf.py version
    sed(f'-i "s/{ver_re}/{new_version}/g"', 'conf.py')    

# change pyproject version
sed(f'-i "0,/{ver_re}/s/{ver_re}/{new_version}/g"', 'pyproject.toml')


# clean emacs files
rm('*~')
with cd('docs'): rm('*~')
with cd('nix_shell_utils'): rm('*~')


# show status in command line before proceed
runc('git status')
check()

# add/commit/push/tag/push-tag

comment = input("git commit comment? ")
print('\n------ commiting and pushing git repo -----\n')
lrun('git add .', f"git commit -m '{comment}'", "git push")
print('\n------ taggin repo -----\n')
runc( 'git add .')
runc(f"git commit -m '{comment}'")
runc( "git push")
runc(f'git tag -m "{tcomment}" {new_version}')
runc( "git push --tags")

# check and upload to pypi.org
check('upload to pypi.org')
print('\n----- releasing package -----\n')

rm('./dist')
runc('python -m build')
runc('python -m twine upload ./dist/*')
