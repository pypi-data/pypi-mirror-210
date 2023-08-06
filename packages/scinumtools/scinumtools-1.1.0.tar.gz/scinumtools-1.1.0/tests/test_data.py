import numpy as np
import os
import sys
sys.path.insert(0, 'src')

from scinumtools.data import *

def test_caching():

    file_cache = "tests/cached_data.npy"

    if os.path.isfile(file_cache):
        os.remove(file_cache)
    assert not os.path.isfile(file_cache)
    
    @CachedFunction(file_cache)
    def read_data(a, b):
        return dict(a=a, b=b)

    data = read_data('foo','bar')
    
    assert data == dict(a='foo', b='bar')
    assert os.path.isfile(file_cache)
    
    data = read_data('foo2','bar2')

    assert data == dict(a='foo', b='bar')

def test_normalizing():

    xlen = 10
    ylen = 10
    data = np.linspace(1,xlen*ylen,xlen*ylen).reshape(xlen,ylen) - 10

    with NormalizeData() as n:
        for row in data:
            n.append(row)
        linnorm = n.linnorm()
        lognorm = n.lognorm()

    assert linnorm.vmin == -9.
    assert linnorm.vmax == 90.0
    assert lognorm.vmin == 0
    assert lognorm.vmax == 1.954242509439325

def test_list_to_grid():

    data = range(7)
    ncols = 2
    grid = []
    for row in ListToGrid(data,ncols):
        grid.append(row)
    assert grid == [
        (0, 0, 0, 0),
        (1, 0, 1, 1),
        (2, 1, 0, 2),
        (3, 1, 1, 3),
        (4, 2, 0, 4),
        (5, 2, 1, 5),
        (6, 3, 0, 6)
    ]
