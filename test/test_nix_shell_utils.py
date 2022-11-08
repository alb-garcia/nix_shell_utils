"""Regression tests"""

from nix_shell_utils import *
import pytest
import os
import subprocess


def test_pj():
    expect1 = 'foo/bar'
    expect2 = 'foo/bar/'
    expect3 = 'foo/bar/spam'
    expect4 = 'foo/bar/spam/'
    assert pj('foo','bar') == expect1
    assert pj('foo','bar',leaf = False) == expect2
    assert pj('foo', 'bar', 'spam') == expect3
    assert pj('foo', 'bar', 'spam', leaf = False) == expect4
    assert pj('','foo','','bar','') == expect1
    assert pj('','','') == ''

def test_pwd():
    assert pwd() == os.getcwd()
    
def test_cd():
    old_dir = os.getcwd()

    expected = os.getcwd() + '/test_dir1/test_dir2'

    os.system('mkdir -p ./test_dir1/test_dir2')
    with cd('./test_dir1/test_dir2'):
        assert os.getcwd() == expected

    assert os.getcwd() == old_dir
    
    with pytest.raises(FileNotFoundError):
            with cd('./this_path_does_not_exist'):
                pass

    #check paths with environment variables, '~' expansion
    expected = os.path.expandvars('$HOME')
    
    with cd('~'):
        assert os.getcwd() == expected
    assert os.getcwd() == old_dir

    with cd('$HOME'):
        assert os.getcwd() == expected
    assert os.getcwd() == old_dir

    # cd('') should take you $HOME
    expected = os.path.expandvars('$HOME')
    with cd(''):
        assert os.getcwd() == expected

    assert os.getcwd() == old_dir
    
def test_mkdir():
    cdir = os.getcwd()
    expected = cdir + '/test_dir1/test_dir2'
    mkdir('./test_dir1/test_dir2')
    
    with cd('./test_dir1/test_dir2'):
        assert os.getcwd() == expected

    os.system('rm -rf test_dir1')

    expected = [cdir + '/test_dir1/test_dir2', cdir + '/test_dir3/test_dir4']
    
    mkdir(['./test_dir1/test_dir2', './test_dir3/test_dir4'])
    
    with cd('./test_dir1/test_dir2'):
        assert expected[0] == os.getcwd()

    with cd('./test_dir3/test_dir4'):
        assert expected[1] == os.getcwd()
        
    os.system('rm  -rf test_dir1')
    os.system('rm  -rf test_dir3')    

    

def test_root_files():
    files = ['foo', 'spam']
    files1 = ['/foo', '/spam']
    
    expect1 = ['/foo/bar/foo', '/foo/bar/spam']
    assert root_files(files, '/foo/bar') == expect1
    assert root_files(files, '/foo/bar/') == expect1
    assert root_files(files, '') == files
    #assert root_files(files1, '/foo/bar') == expect1
    #assert root_files(files1, '/foo/bar/') == expect1
    # assert root_files(files1, '') == files1

def test_bglob():
    files = ['aaa.txt', 'baa.txt', 'aaa.log', 'baa.log', 'bbb.log', 'baa.cmd']
    os.system('mkdir test_bglob')
    for f in files:
        os.system(f'touch test_bglob/{f}')
    
    with cd('test_bglob'):
        assert bglob('*.cmd') == ['baa.cmd']

        txt = bglob('*.txt')
        assert 'aaa.txt' in txt and 'baa.txt' in txt

        txt = bglob('aaa.*')
        assert 'aaa.txt' in txt and 'aaa.log' in txt

        assert bglob('ccc.*') == []


        print(os.getcwd())
        txt = bglob('./*')
        assert set(txt) == set(['aaa.txt','baa.txt','aaa.log','baa.log','bbb.log','baa.cmd'])
        os.system('rm -rf *.txt *.log *.cmd')
    
    os.system('rm -rf ./test_bglob')

def test_aglob():
    files = ['aaa.txt', 'baa.txt', 'aaa.log', 'baa.log', 'bbb.log', 'baa.cmd']
    os.system('mkdir test_aglob')
    for f in files:
        os.system(f'touch test_aglob/{f}')
    
    with cd('test_aglob'):
        ap = os.path.abspath('.')
        assert aglob('*.cmd') == [ap + '/' + 'baa.cmd']

        txt = aglob('*.txt')
        assert ap + '/' + 'aaa.txt' in txt and ap + '/' + 'baa.txt' in txt

        txt = aglob('aaa.*')
        assert ap + '/' + 'aaa.txt' in txt and ap + '/' + 'aaa.log' in txt

        assert aglob('ccc.*') == []

        txt = aglob('./*')
        s = set([ap + '/' + f for f in ['aaa.txt','baa.txt','aaa.log','baa.log','bbb.log','baa.cmd']])
        assert set(txt) == s
        os.system('rm -rf *.txt *.log *.cmd')

    os.system('rm -rf ./test_aglob')

def test_basename():
    assert basename('/foo/bar/') == ''
    assert basename('/foo/bar/spam') == 'spam'
    assert basename('foo') == 'foo'
    assert basename('/foo/bar/spam.py') == 'spam.py'
    assert basename('') == ''
    assert basename('foo/bar') == 'bar'


def test_stem():
    assert stem('') == ''
    assert stem('foo.py') == 'foo'
    assert stem('foo.py.keep') == 'foo'
    assert stem('/home/foo/bar.py.txt') == 'bar'
    assert stem('/home/foo/bar/') == ''
    assert stem('home/foo.py.txt') == 'foo'

def test_expand():
    home = os.environ['HOME']
    os.environ['PROJECT'] = 'PROJECT'
    assert home == expand('$HOME')
    assert home == expand('~')
    assert home + '/PROJECT/foo' == expand('~/$PROJECT/foo')
    assert [home, home + '/PROJECT/foo'] == expand(['$HOME', '~/$PROJECT/foo'])
    os.unsetenv('PROJECT')

def test_rm():
    mkdir('test1_dir')
    rm('test1_dir')
    with pytest.raises(FileNotFoundError):
        with cd('./test1_dir'):
            pass
    rm('does_not_exist/at/all') #silently does nothing


def test_cp():
    srcdir = 'test_cp_src'
    dstdir = 'test_cp_dst'
    files  = ['t1','t2','t3','t4']
    mkdir(srcdir)
    mkdir(dstdir)

    with cd(srcdir):
        for f in files: os.system(f'touch {f}')

    rsfiles = root_files(files, pj(pwd(), srcdir))
    rdfiles = root_files(files, pj(pwd(), dstdir))    
    
    for rf in rsfiles:
        cp(rf,dstdir)

    with cd(dstdir):
        for f in files:
            assert os.path.isfile(f) == True
            rm(f)

    cp(rsfiles, dstdir)
    
    with cd(dstdir):
        for f in files:
            assert os.path.isfile(f) == True
            rm(f)
            
    cp(pj(pwd(), srcdir, '*'), [dstdir,dstdir,dstdir])

    with cd(dstdir):
        for f in files:
            assert os.path.isfile(f) == True
            rm(f)
    
    cp(rsfiles, rdfiles)
    
    with cd(dstdir):
        for f in files:
            assert os.path.isfile(f) == True
            rm(f)

    rm('test_cp_*')
    
def test_ln():
    expected = pj(os.getcwd(), 'test1_dir/test2_dir')
    mkdir('test1_dir/test2_dir')
    ln('test1_dir/test2_dir', 'link')
    with cd('link'):
        assert pwd() == expected

    rm('test1_dir')
    rm('link')

def test_sed():
    sed('-i s/sed/awk/g', 'original.txt')
    fo = open('original.txt', 'r')
    fm = open('modified.txt', 'r')
    los = fo.readlines()
    lms = fm.readlines()

    for (lo,lm) in zip(los,lms):
        assert lo == lm

    cp('original_again.txt','original.txt')

def test_runc():
    assert runc('echo SPAM') == 0
    assert runc('does/not/exist') != 0

    with pytest.raises(subprocess.CalledProcessError):
            runc('does_not_exist', blocking = True)
            
def test_run():
    c = run('echo SPAM', quiet = False)
    assert c.stdout == 'SPAM\n'
    assert c.stderr == ''
    assert c.args == 'echo SPAM'
    with pytest.raises(subprocess.CalledProcessError):
        run('does_not_exist', blocking = True)

    c = run('does not exist', quiet = False)
    assert c.stdout == ''
    assert c.stderr == '/bin/sh: 1: does: not found\n'
    assert c.returncode == 127


def test_tmpenv():
    with tmpenv('HOME', FOO='BAR'):
        with pytest.raises(KeyError):
            home = os.environ['HOME']
        assert os.environ['FOO'] == 'BAR'

    with pytest.raises(KeyError):
        home = os.environ['FOO']

    assert os.environ['HOME'] == expand('~')
        
