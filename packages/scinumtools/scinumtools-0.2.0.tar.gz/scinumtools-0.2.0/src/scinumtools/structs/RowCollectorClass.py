from dataclasses import dataclass
import numpy as np
import pandas as pd
from typing import Union

@dataclass
class RowCollector:
    """ RowCollector class collect table rows and transform them into one of available formats

    Example of use:

    ..code-block::
    
        import scinumtools as snt
        
        with snt.structs.RowCollector(['col1','col2','col3']) as rc:
             rc.append([1,2,3])
             rc.append([4,5,6])
             data = rc.to_dict()
    
    :param columns: This can be either a list of column names or a dictionary with column array settings
    """
    _numpy: bool
    _columns: list
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, tb):
        pass
    
    def __init__(self, columns: Union[list,dict]):
        self._columns = []
        if isinstance(columns,list):
            # Columns are standard python lists
            self._numpy = False
            for column in columns:
                setattr(self,column,[])
                self._columns.append(column)
        elif isinstance(columns,dict):
            # Columns are numpy arrays
            self._numpy = True
            for column, kwargs in columns.items():
                setattr(self,column,np.array([],**kwargs))
                self._columns.append(column)
        else:
            raise Exception("Columns parameter can be either a list of column names or a dictionary of column numpy settings.")
        
    def append(self, values: list):
        """ Append a single row

        :param values: List of values for each column
        """
        if self._numpy:
            for n, name in enumerate(self._columns):
                data = getattr(self,name)
                new = np.array(values[n],dtype=data.dtype)
                setattr(self,name, np.append(data,new) )
        else:
            for n, name in enumerate(self._columns):
                getattr(self,name).append(values[n])
                
    def to_dict(self):
        """ Convert class data to a dictionary of lists/arrays
        """
        data = {}
        for name in self._columns:
            data[name] = getattr(self,name)
        return data
    
    def to_dataframe(self, columns: Union[list,dict]=None):
        """ Convert class data to a pandas data frame

        :param columns: This can be either a list of columns or a dictionary of column:title pairs. If not set, all coumns are being taken.
        """
        if isinstance(columns,dict):
            return pd.DataFrame({title:getattr(self,name) for name,title in columns.items()})
        elif isinstance(columns,list):
            return pd.DataFrame({name:getattr(self,name) for name in columns})
        else:
            return pd.DataFrame({name:getattr(self,name) for name in self._columns})
        
    def to_text(self, **kwargs):
        """ Convert class data to a text using pandas dataframe

        :param kwargs: kwargs of DataFrame's to_string() method
        """
        return self.to_dataframe().to_string(**kwargs)
