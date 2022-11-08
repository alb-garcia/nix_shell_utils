#!/usr/bin/env python

project= 'nix_shell_utils'

from nix_shell_utils import run, cd ,sed, runc, source, rm
import re
import sys
re_failed= re.compile(r'FAILED')
re_cov = re.compile(rf'^TOTAL.*\D(\d+)%')
re_version = re.compile(r'version\s*=\s*"(\d+\.\d+\.\d+)"')

def check(msg = 'continue'):
    yes_no = input(f"{msg} [y/n]? ").lower()

    if not yes_no in ['y','yes']:
        print("Release aborted. Exiting...")
        sys.exit(1)


print('\n-- runing tests with coverage\n')


with cd('./test'):
    c = run('pytest --cov-report term-missing --cov=nix_shell_utils', quiet = False)

test_result = 'passing'
for line in c.stdout.splitlines():
    m = re_failed.match(line) #no walrus operator to support Python 3.7
    if m != None:
        test_result = "FAILING"

    m = re_cov.match(line) #no walrus operator to support Python 3.7
    if m != None:
        coverage = int(m.groups()[0])

check()
print('\n-- generating documentation locally\n')

with cd('./docs'):
    runc('make clean')
    runc('make html')
    runc('firefox ./_build/html/index.html')

check()


c = sed('-n /version/p', 'pyproject.toml')
m = re_version.match(c.stdout.strip())

if m != None:
    cur_version = m.groups()[0]
    print(f'\n-- current version: {cur_version}\n')

new_version = input('new version (X.Y.Z)? ')    

check(f'modify project files with version {new_version}')

with cd('./docs'):
    sed(f'-i "s/--value=[0-9]\+/--value={coverage}/g"', 'genbadges')
    sed(f'-i "s/[0-9]\+\.[0-9]\+\.[0-9]\+/{new_version}/g"', 'genbadges')
    sed(f'-i "s/passing\|FAILING/{test_result}/g"', 'genbadges')
    source('./genbadges')
    sed(f'-i "s/[0-9]\+\.[0-9]\+\.[0-9]\+/{new_version}/g"', 'conf.py')    

sed(f'-i "0,/[0-9]\+\.[0-9]\+\.[0-9]/s/[0-9]\+\.[0-9]\+\.[0-9]\+/{new_version}/g"', 'pyproject.toml')

comment = input("git commit comment? ")

print('\n-- commiting and pushing git repo\n')

# clean emacs files
rm('*~')
with cd('docs'): rm('*~')
with cd('nix_shell_utils'): rm('*~')


runc('git status')
runc('git add .')
runc(f"git commit -m '{comment}'")
runc("git push --tags")

check('upload to pypi.org')
print('\n-- releasing package \n')

rm('./dist')
runc('python -m build')
runc('python -m twine upload ./dist/*')

