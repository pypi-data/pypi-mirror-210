from MCPoly.lmpset import mould
import re
import os
import pytest

@pytest.fixture
def atoms():
    return mould('Poly1',loc='./data_lmpset/')

def test_cube(atoms):
    opath=os.getcwd()
    os.chdir('./MCPoly/tests')
    atoms.cube(6,5,6,5,3,5)
    os.chdir(opath)
    fl=open('./MCPoly/tests/data_lmpset/Poly1_663.data','r')
    i1=0
    i2=0
    i3=0
    i4=0
    i5=0
    i6=0
    i7=0
    i8=0
    i9=0
    for line in fl:
        a=re.search('972 atoms',line)
        if a:
            i1=1
        b=re.search('1404 angles',line)
        if b:
            i2=1
        c=re.search('432 impropers',line)
        if c:
            i3=1
        d=re.search('4 atom types',line)
        if d:
            i4=1
        e=re.search('4 bond types',line)
        if e:
            i5=1
        f=re.search('4 dihedral types',line)
        if f:
            i6=1
        g=re.search('0.00000 53.32948 xlo xhi',line)
        if g:
            i7=1
        h=re.search('0.00000 54.87382 ylo yhi',line)
        if h:
            i8=1
        i=re.search('0.00000 26.46613 zlo zhi',line)
        if i:
            i9=1
            break
    fl.close()
    assert i1*i2*i3*i4*i5*i6*i7*i8*i9!=0

@pytest.fixture
def atoms():
    return mould('Poly1',loc='./data_lmpset/')

def test_brick_xy(atoms):
    opath=os.getcwd()
    os.chdir('./MCPoly/tests')
    atoms.brick(6,5,6,5,4,5,xpattern='y')
    os.chdir(opath)
    fl=open('./MCPoly/tests/data_lmpset/Poly1_664_brickxy.data','r')
    i1=0
    i2=0
    i3=0
    i4=0
    i5=0
    i6=0
    i7=0
    i8=0
    i9=0
    for line in fl:
        a=re.search('1188 atoms',line)
        if a:
            i1=1
        b=re.search('1056 bonds',line)
        if b:
            i2=1
        c=re.search('1584 dihedrals',line)
        if c:
            i3=1
        d=re.search('4 atom types',line)
        if d:
            i4=1
        e=re.search('5 angle types',line)
        if e:
            i5=1
        f=re.search('1 improper types',line)
        if f:
            i6=1
        g=re.search('0.00000 53.32948 xlo xhi',line)
        if g:
            i7=1
        h=re.search('0.00000 54.87382 ylo yhi',line)
        if h:
            i8=1
        i=re.search('0.00000 36.95484 zlo zhi',line)
        if i:
            i9=1
            break
    fl.close()
    assert i1*i2*i3*i4*i5*i6*i7*i8*i9!=0

@pytest.fixture
def atoms():
    return mould('Poly1',loc='./data_lmpset/')

def test_brick_yz(atoms):
    opath=os.getcwd()
    os.chdir('./MCPoly/tests')
    atoms.brick(6,5,6,5,4,5,ypattern='z')
    os.chdir(opath)
    fl=open('./MCPoly/tests/data_lmpset/Poly1_664_brickyz.data','r')
    i1=0
    i2=0
    i3=0
    i4=0
    i5=0
    i6=0
    i7=0
    i8=0
    i9=0
    for line in fl:
        a=re.search('1134 atoms',line)
        if a:
            i1=1
        b=re.search('1008 bonds',line)
        if b:
            i2=1
        c=re.search('1512 dihedrals',line)
        if c:
            i3=1
        d=re.search('4 atom types',line)
        if d:
            i4=1
        e=re.search('5 angle types',line)
        if e:
            i5=1
        f=re.search('1 improper types',line)
        if f:
            i6=1
        g=re.search('0.00000 53.32948 xlo xhi',line)
        if g:
            i7=1
        h=re.search('0.00000 54.87382 ylo yhi',line)
        if h:
            i8=1
        i=re.search('0.00000 36.95484 zlo zhi',line)
        if i:
            i9=1
            break
    fl.close()
    assert i1*i2*i3*i4*i5*i6*i7*i8*i9!=0

@pytest.fixture
def atoms():
    return mould('Poly1',loc='./data_lmpset/')

def test_brick_zx(atoms):
    opath=os.getcwd()
    os.chdir('./MCPoly/tests')
    atoms.brick(6,5,6,5,4,5,zpattern='x')
    os.chdir(opath)
    fl=open('./MCPoly/tests/data_lmpset/Poly1_664_brickzx.data','r')
    i1=0
    i2=0
    i3=0
    i4=0
    i5=0
    i6=0
    i7=0
    i8=0
    i9=0
    for line in fl:
        a=re.search('1188 atoms',line)
        if a:
            i1=1
        b=re.search('1056 bonds',line)
        if b:
            i2=1
        c=re.search('1584 dihedrals',line)
        if c:
            i3=1
        d=re.search('4 atom types',line)
        if d:
            i4=1
        e=re.search('5 angle types',line)
        if e:
            i5=1
        f=re.search('1 improper types',line)
        if f:
            i6=1
        g=re.search('0.00000 53.32948 xlo xhi',line)
        if g:
            i7=1
        h=re.search('0.00000 54.87382 ylo yhi',line)
        if h:
            i8=1
        i=re.search('0.00000 36.95484 zlo zhi',line)
        if i:
            i9=1
            break
    fl.close()
    assert i1*i2*i3*i4*i5*i6*i7*i8*i9!=0