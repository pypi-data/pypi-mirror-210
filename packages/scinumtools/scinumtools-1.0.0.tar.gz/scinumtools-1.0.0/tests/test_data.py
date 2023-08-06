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
