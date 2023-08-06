import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from Snoopy import Spectral as sp
import _TimeDomain


class ReconstructionWif_pyABC() :

    def __str__(self):
        s = "Number of components = {}".format( self.nbwave )

        return s

    @property
    def nbwave(self):
        return len(self.getWif().getFrequencies())

    @classmethod
    def Read_HOS_WaveMaker(cls, filename ) :
        data = np.loadtxt( filename, delimiter = "," , usecols = [1,2,4] )
        return cls(  data[:,0] * 2*np.pi , data[:,1] , data[:,2] )

    def plot(self, ax=None, tMin=0., tMax=1000., tStep=1.):
        """ Plot the frequency content
        """
        if ax is None :
            _, ax = plt.subplots()
        xs = np.linspace(tMin, tMax, int((tMax-tMin)/tStep))
        ax.plot(xs, self(xs))
        return ax

    @classmethod
    def FromWifAndRao(  cls , wif , rao ):
        #TODO, move in c++
        cvalueRao = rao.interpValues( wif.freq , wif.head )
        cvalueWif = wif.getCvalues()
        cvalue = cvalueRao * cvalueWif
        return cls(  wif.getEncounterFrequencies( rao.speed ) , cvalue  )


    def evalSe( self , time, *args, **kwargs ) :
        """
        Same as evalDf , but return pandas series, ensure that data is 1D
        """
        return self.evalDf(time, *args, **kwargs).iloc[:,0]

    def evalDf( self, time, *args, **kwargs  ) :
        """Return pandas dataframe, with time as index
        """
        return pd.DataFrame( index = time , data = self( time,*args, **kwargs  ), columns = sp.modesIntsToNames( self.getModes() ) )

    def getModes(self) :
        return [0]


# Python class is before, otherwise CPP methods that implement a throw("NotImplemented") would be prefered
class ReconstructionWif(ReconstructionWif_pyABC, _TimeDomain.ReconstructionWif): 
	
    pass

class ReconstructionWifLocal(ReconstructionWif_pyABC, _TimeDomain.ReconstructionWifLocal):
    """Wif time reconstruction class in local"""

    def getElevation_DF(self , time, x , y = 0.):
        S , T = np.meshgrid( x , time  )
        res = self(  T , S , y  )
        df = pd.DataFrame(index = time , columns = x , data = res)
        df.columns.name = "X"
        df.index.name = "Time"
        return df


class ReconstructionRao(_TimeDomain.ReconstructionRao, ReconstructionWif_pyABC):
    """First order time reconstruction class"""

class ReconstructionRaoLocal(_TimeDomain.ReconstructionRaoLocal, ReconstructionWif_pyABC):
    """First order time reconstruction class in local"""
    def getModes(self) :
        return _TimeDomain.ReconstructionRaoLocal.getModes(self)
