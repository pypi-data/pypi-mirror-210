import numpy as np
import sys
sys.path.insert(0, 'src')

import scinumtools as snt

def test_row_collector_list():
    columns = ['col1','col2','col3']
    with snt.structs.RowCollector(columns) as rc:
        rc.append([1,2,3])
        rc.append([4,5,6])
        rc.append([7,8,9])
        assert rc.col1 == [1,4,7]
        assert rc.col2 == [2,5,8]
        assert rc.col3 == [3,6,9]

def test_row_collector_array():
    columns = {'col1':dict(dtype=str),'col2':dict(dtype=float),'col3':dict(dtype=bool)}
    with snt.structs.RowCollector(columns) as rc:
        rc.append([1,2,3])
        rc.append([4,5,6])
        rc.append([7,8,0])
        np.testing.assert_equal(rc.col1, ['1','4','7'])
        np.testing.assert_equal(rc.col2, [2,5,8])
        np.testing.assert_equal(rc.col3, [True,True,False])
