from matplotlib.colors import Normalize, LogNorm
import numpy as np

from ..structs import ArrayCollector

class NormalizeData:

    _collector: ArrayCollector
    
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, tb):
        pass

    def __init__(self):
        self._collector = ArrayCollector(['vminpos','vmin','vmax'])

    def append(self, data):
        datapos = data[data>0]
        if len(datapos):
            vminpos = np.nanmin(datapos)
        else:
            vminpos = np.nan
        self._collector.append([vminpos,np.min(data),np.max(data)])

    def linnorm(self):
        return Normalize(
            vmin=np.nanmin(self._collector.vmin), 
            vmax=np.nanmax(self._collector.vmax)
        )

    def lognorm(self):
        return LogNorm(
            vmin=np.log10(np.nanmin(self._collector.vminpos)), 
            vmax=np.log10(np.nanmax(self._collector.vmax))
        )

def ListToGrid(data, ncols):
    for i,d in enumerate(data):
        yield (i,int(i/ncols),int(i%ncols),d)
    
