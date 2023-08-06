import numpy as np
from scipy.stats import rayleigh, norm
from matplotlib import pyplot as plt
import pandas as pd
import _Spectral
from Snoopy import Statistics as st
from Snoopy import Spectral as sp


class ResponseSpectrumABC() :

    @property
    def seaState(self):
        return self.getSeaState()

    def getSe(self):
        if len(self.getModes() == 1 ):
            return pd.Series( index = self.getFrequencies(), data = self.get()[:,0] )
        else :
            raise(Exception( "Only 1D data for responseSpectrum.getSe(). Check responseSpectrum.getModes()" ))

    def plot(self, ax = None, *args, **kwargs):
        if ax is None :
            fig , ax = plt.subplots()
        ax.plot( self.rao.freq , self.get() , *args, **kwargs )
        ax.set_xlabel("Wave frequency (rad/s)")
        ax.set_ylim(bottom = 0.0)
        return ax

    def computeMoment(self) :
        """ Compute spectral moment
        Now in the C++. Temporarily kept for checking purpose
        """
        spec = self.get()
        dw = self.freq[1] - self.freq[0]
        m0 = np.sum(spec[:]) * dw
        m2 = np.sum(spec[:] * self.freq[:]**2 ) * dw
        return m0,m2

    def getDf(self) :
        return pd.DataFrame( index = self.getFrequencies(), data = self.get(), columns = self.modesNames )

    @property
    def modesNames(self):
        if hasattr(self, "getModes") :
            return sp.modesDf.reset_index().set_index("INT_CODE").loc[  self.getModes() , "NAME" ].values
        else :
            return None

    def to_DataFrame(self):
        """Convert to pd.DataFrame object
        """

        return pd.DataFrame( index = pd.Index(self.getFrequencies(), name = "Frequency") , data = self.get() , columns = self.modesNames )


class ResponseSpectrum( ResponseSpectrumABC , _Spectral.ResponseSpectrum ):


    @property
    def rao(self):
        return self.getRao()

    @property
    def freq(self):
        return self.rao.freq


    def computePy( self  ) :
        """ Compute and return response spectrum
        Now moved to c++ (self.get return the response spectrum, lazy evaluation )
        """
        res = np.zeros( (self.rao.nbfreq), dtype = float )
        for spec in self.seaState.spectrums :
            #No spreading
            if spec.spreading_type == _Spectral.SpreadingType.No :
                w_ = self.rao.freq
                sw_ = spec.compute(w_)
                ihead = (np.abs(self.rao.head - spec.heading)).argmin()
                #Compute response spectrum
                res[:] += self.rao.module[:,ihead]**2 * sw_[:]
            elif spec.spreading_type == _Spectral.SpreadingType.Cosn :
                raise(NotImplementedError)
            else :
                raise(NotImplementedError)
        return res

    def getMaxDistribution(self, imode = -1):
        """ Single amplitude maxima distribution

        Returns:
            scipy.stats like distribution: Single amplitude maxima distribution (contains .cdf, .pdf...  attributes).

        """
        return st.rayleigh_c( self.getM0(imode)**0.5 )

    def getRangeDistribution(self, imode = -1):
        """ Double amplitude maxima distribution

        Returns:
            scipy.stats like distribution: Single amplitude maxima distribution (contains .cdf, .pdf...  attributes).

        """
        return st.rayleigh_c( self.getM0(imode)**0.5 * 2.)

    def getDistribution(self, imode = -1 ):
        return norm( loc = 0. , scale = self.getM0(imode)**0.5 )

    def getRs(self, imode = -1):
        """Return significant response (range)
        """
        return 4.004 * self.getM0(imode)**0.5


    def getSpectralStats( self, imode = -1 ):
        """ Return SpectalStats instance
        """
        return sp.SpectralStats( *self.getM0M2() )


    def getTz(self, imode = -1):
        """Return mean up-crossing period
        """
        m0, m2 = self.getM0M2(imode)
        if m2 < 1e-12 :
            return np.nan
        return 2*np.pi * (m0/m2)**0.5




class ResponseSpectrum2nd( ResponseSpectrumABC, _Spectral.ResponseSpectrum2nd) :

    def __init__( self, seaState , rao ) :
        _Spectral.ResponseSpectrum2nd.__init__(self , seaState, rao)

    @property
    def qtf(self):
        return self.getQtf()

    def getSe(self):
        return pd.Series( index = self.getFrequencies(), data = self.get() )

    def getNewmanSe(self, *args, **kwargs):
        return pd.Series( index = self.getFrequencies(), data = self.getNewman(*args, **kwargs) )

    def plot(self, ax = None, *args, **kwargs):
        if ax is None :
            fig , ax = plt.subplots()
        ax.plot( self.getFrequencies() , self.get(),  *args, **kwargs)
        ax.set_xlabel("Wave frequency (rad/s)")
        return ax

