import numpy as np
import pandas as pd
from textwrap import dedent
import sys
sys.path.insert(0, 'src')

from scinumtools.structs import *

def test_row_collector_list():
    columns = ['col1','col2','col3']
    with RowCollector(columns) as rc:
        rc.append([1,2,3])
        rc.append([4,5,6])
        rc.append([7,8,9])
        assert rc.col1 == [1,4,7]
        assert rc.col2 == [2,5,8]
        assert rc.col3 == [3,6,9]
        assert rc.to_dict() == dict(
            col1 = [1,4,7],
            col2 = [2,5,8],
            col3 = [3,6,9],
        )
        pd.testing.assert_frame_equal(
            rc.to_dataframe(),
            pd.DataFrame(dict(
                col1 = [1,4,7],
                col2 = [2,5,8],
                col3 = [3,6,9],
            ))
        )
        assert rc.to_text() == dedent("""\
               col1  col2  col3
            0     1     2     3
            1     4     5     6
            2     7     8     9
        """.rstrip())

def test_row_collector_array():
    columns = {'col1':dict(dtype=str),'col2':dict(dtype=float),'col3':dict(dtype=bool)}
    with RowCollector(columns) as rc:
        rc.append([1,2,3])
        rc.append([4,5,6])
        rc.append([7,8,0])
        np.testing.assert_equal(rc.col1, ['1','4','7'])
        np.testing.assert_equal(rc.col2, [2,5,8])
        np.testing.assert_equal(rc.col3, [True,True,False])
        np.testing.assert_equal(rc.to_dict(), dict(
            col1 = ['1','4','7'], 
            col2 = [2,5,8],
            col3 = [True,True,False],
        ))
        pd.testing.assert_frame_equal(
            rc.to_dataframe(),
            pd.DataFrame(dict(
                col1 = ['1','4','7'],
                col2 = [2.,5.,8.],
                col3 = [True,True,False],
            ))
        )
        assert rc.to_text() == dedent("""\
              col1  col2   col3
            0    1   2.0   True
            1    4   5.0   True
            2    7   8.0  False
        """.rstrip())

def test_parameter_list():
    def test(params):
        assert params[0].a == 1
        assert params[1]['a'] == 4
        for param in params:
            assert param['a'] in [1,4]
        for index,settings in params.items():
            assert param['b'] in [2,5]        
    # append values
    with ParameterList(['a','b','c']) as params:
        params.append([1, 2, 3])
        params.append([4, 5, 6])
        test(params)
    # direct value insertion
    params = ParameterList(['a','b','c'],[
        [1, 2, 3],
        [4, 5, 6]
    ])
    test(params)

def test_parameter_dict():
    def test(params):
        assert params['d'].a == 1
        assert params['e']['a'] == 4
        for param in params:
            assert param['a'] in [1,4]
        for index,settings in params.items():
            assert param['b'] in [2,5]
    # append values
    with ParameterDict(['a','b','c']) as params:
        params['d'] = [1, 2, 3]
        params.append( 'e', [4, 5, 6] )
        test(params)
    # direct value insertion
    params = ParameterDict(['a','b','c'],{
        'd': [1, 2, 3],
        'e': [4, 5, 6]
    })
    test(params)
