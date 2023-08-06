from MCPoly.moldraw import molecule
import pytest
import os

@pytest.fixture
def object_moldraw():
    return molecule('Bu', loc='./MCPoly/tests/data_moldraw/')

def test_rectify1(object_moldraw):
    return object_moldraw.sub('Cl',6)

def test_rectify3(object_moldraw):
    return object_moldraw.bind(6,[2,3])

def test_rectify3(object_moldraw):
    return object_moldraw.C('CO',2)

#def test_geoview(object_moldraw):
#    return object_moldraw.geoview()

def test_conformer1(object_moldraw):
    return object_moldraw.conformer(must=True)

def test_conformer2(object_moldraw):
    object_moldraw.conformer(lowenergy=1.2,must=True)
    assert object_moldraw.energy<1.2

def test_conformer3(object_moldraw):
    object_moldraw.conformer(highenergy=1.2,must=True)
    assert object_moldraw.energy>1.2