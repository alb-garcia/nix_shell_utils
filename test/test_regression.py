"""Regression tests"""

from nix_shell_utils import *
import pytest
import os

def test_cd():
    expected = os.getcwd() + '/test_dir1/test_dir2'
    os.system('mkdir -p ./test_dir1/test_dir2')
    od = cd('./test_dir1/test_dir2')
    od = cd(od)
    os.system('rm -rf ./test_dir1')
    assert od == expected

def test_cd2():
    with pytest.raises(FileNotFoundError):
            cd('./this_path_does_not_exist')

def test_cd3():
    expected = os.getcwd()
    od = cd('..')
    assert od == expected

def test_cd4():
    expected = os.path.expandvars('$HOME')
    cd('')
    assert os.getcwd() == expected
    
def test_mkdir():
    cdir = os.getcwd()
    expected = cdir + '/test_dir1/test_dir2'
    mkdir('./test_dir1/test_dir2')
    od = cd('./test_dir1/test_dir2')
    od = cd(od)
    assert od == expected

def test_mkdir2():
    cdir = os.getcwd()
    expected = [cdir + '/test_dir1/test_dir2', cdir + '/test_dir3/test_dir4']
    mkdir(['./test_dir1/test_dir2', './test_dir3/test_dir4'])
    od = cd('./test_dir1/test_dir2')
    first = cd(od)
    od = cd('./test_dir3/test_dir4')
    second = cd(od)
    assert [first,second] == expected

