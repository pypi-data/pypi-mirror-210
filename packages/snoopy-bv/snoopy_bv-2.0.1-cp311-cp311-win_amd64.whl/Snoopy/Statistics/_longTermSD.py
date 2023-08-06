"""Convenience functions to compute long-term value with RAOs

Compare to class "LongTerm" and "LongTermSpectral", it handles the spectral moments calculation

LongTermRao

LongTermQuadDamping

longTermSD

"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from Snoopy import Spectral as sp
from Snoopy import Statistics as st
from Snoopy import logger


class LongTermRaoABC():
    """Abstract class that contains common function to calculate long-term response from RAOs.
    """

    def __init__(self, * , ssList, dss, nModes, sht_engine = "SpectralMoments") :
        """Compute long-term value, using scatter-diagram and RAO as input.

        Parameters
        ----------
        ssList : list
            list of seastate
        dss : float, optional
            Sea-state duration. The default is 10800.
        """

        self.ssList = ssList
        self._ssProb = np.array( [ ss.probability for ss in self.ssList ] )
        self._m0s_m2s = None
        self._spectralStats = None
        self._lt = None
        self._dss = dss
        self.nModes = nModes


    @property
    def dss(self):
        return self._dss


    @dss.setter
    def dss(self, dss):
        self._dss = dss
        if self._lt is not None:
            for i in range(self.nModes) :
                self._lt[i].dss = dss
        return self._dss


    def _compute_m0s_m2s(self):
        #TO BE IMPLEMENTED IN CHILD-CLASS, Return m0s and m2s
        raise(NotImplementedError)


    @property
    def m0s_m2s(self):
        """Return m0s and m2s.

        Returns
        -------
        tuple
            ( m0s, m2s )

        """
        if self._m0s_m2s is None:
            logger.info("Running short-term calculation")
            self._m0s_m2s = self._compute_m0s_m2s()

        return self._m0s_m2s


    @property
    def spectralStats(self):
        if self._spectralStats is None :
            self._spectralStats = sp.SpectralStats( *self.m0s_m2s )
        return self._spectralStats


    @m0s_m2s.setter
    def m0s_m2s(self, m0s_m2s):
        #TODO: check ?
        self._m0s_m2s = m0s_m2s


    @property
    def longTerm(self):
        if self._lt is None :
            m0s, m2s = self.m0s_m2s
            shtStats = sp.SpectralStats( m0 = m0s[:,:] , m2 = m2s[:,:] )
            self._lt = [st.LongTermSpectral( shtStats.Rs[:,i] , shtStats.Rtz[:,i], probabilityList = self._ssProb, dss = self.dss ) for i in range(self.nModes) ]
        return self._lt


    def _get_default_i_rao(self, i_rao) :
        if i_rao is None :
            if (self.nModes == 1) :
                return 0
            else :
                raise(ValueError("Index of RAO should be provided" ) )
        else :
            return i_rao

    def x_to_p(self, x, *args, **kwargs):
        """Return non-exceedance probability of x.

        Parameters
        ----------
        x: float
            Respones Value
        duration: float
            Long term duration (in year)

        Returns
        -------
        list
            Non-exceedance probability (on all 'mode' in the RAO)
        """
        return [lt.x_to_p(x, *args, **kwargs) for lt in self.longTerm ]


    def pcycle_to_x(self , p , *args, **kwargs) :
        """Value at given cycle exceedance probability.

        Parameters
        ----------
        pcycle : float
            Cycle exceedance probability

        Returns
        -------
        x : float
            Level with exceedance probability of pcycle
        """
        return [lt.pcycle_to_x(p, *args, **kwargs) for lt in self.longTerm ]


    def rp_to_x(self,rp):
        """Compute return values corresponding to return period rp.

        Parameters
        ----------
        rp : float
            Return period, in year.

        Returns
        -------
        list(float)
            Return values
        """
        return [lt.rp_to_x(rp) for lt in self.longTerm ]


    def p_to_x(self, p, *args, **kwargs):
        """Return the non-exceedance probability of x in duration (year).

        Parameters
        ----------
        x: float
            Respones Value
        duration: float
            Long term duration (in year)

        Returns
        -------
        list(float)
            cdf  (i.e.  P( x < X )  )
        """
        return [lt.p_to_x(p, *args, **kwargs) for lt in self.longTerm ]


    def longTermSingle(self, i_rao = None):
        """Return the underlying "LongTerm" class, for a single RAO."""

        i_rao = self._get_default_i_rao(i_rao)
        return self.longTerm[i_rao]




class LongTermRao(LongTermRaoABC):
    """Calculate long-term response from RAOs.
    """

    def __init__(self, rao, ssList, dss, sht_engine = "SpectralMoments") :
        """Compute long-term value, using scatter-diagram and RAO as input.

        Parameters
        ----------
        rao : sp.Rao
            RAO, ready for spectral calculation (symmetrized). Can contain several 'mode'
        ssList : list
            list of seastate
        dss : float, optional
            Sea-state duration. The default is 10800.

        """

        self.rao = rao
        self.sht_engine = sht_engine


        LongTermRaoABC.__init__(self, dss = dss, ssList = ssList, nModes = self.rao.getNModes())


    def _compute_m0s_m2s(self):
        smom = sp.SpectralMoments(  self.ssList , self.rao )
        m0 = smom.getM0s()
        m2 = smom.getM2s()
        return m0, m2





class LongTermQuadDamping( LongTermRao ) :

    def __init__( self, ssList, rao_sl, raos, bLin, bQuad, dss ):

        self.rao_sl = rao_sl
        self.raos = raos

        self.bLin = bLin
        self.bQuad = bQuad

        LongTermRaoABC.__init__( self, ssList = ssList, dss = dss, nModes = len(raos) )

    def _compute_m0s_m2s(self):
        for ss in self.ssList :
            smom = sp.SpectralMomentsSL( self.ssList , self.rao_sl, self.raos , self.bLin, self.bQuad)
            m0 = smom.getM0s()
            m2 = smom.getM2s()
            return m0, m2





class LongTermSD( LongTermRao ):

    def __init__(self, rao , sd, nb_hstep, gamma, spreadingType = sp.SpreadingType.No, 
                 spreadingValue = 3., dss = 10800, sht_engine = "SpectralMoments", num_threads = 1):
        """Compute long-term value, using scatter-diagram and RAO as input.

        Parameters
        ----------
        rao : sp.Rao
            RAO, ready for spectral calculation (symmetrized). Can contain several 'mode'
        sd : DiscreteSD
            The scatter diagram
        nb_hstep : integer
            Number of heading step (36 would lead to a 10 degree step).
        gamma : float
            gamma value for Jonswap spectrum.
        spreadingType : sp.spreadingType
            Spreading type
        spreadingValue : float
            Spreading value
        dss : float, optional
            Sea-state duration. The default is 10800.

        Example
        -------
        >>> lt_sd = LongTermSD(rao, rec34_SD, 36 , 1.5, spreadingType = sp.SpreadingType.Cosn, spreadingValue=3.0)
        >>> extreme_25_years = lt_sd.rp_to_x(25.0)
        """

        self.sd = sd
        self.nb_hstep = nb_hstep
        ssList = self.sd.to_seastate_list(headingList=nb_hstep , gamma = gamma , spreadingType=spreadingType, spreadingValue = spreadingValue)
        self.ss_df = sp.SeaStatesDF.FromSeaStateList( ssList )
        self.num_threads = num_threads

        LongTermRao.__init__(self, rao , ssList = ssList, sht_engine = sht_engine, dss = dss )



    def _compute_m0s_m2s(self) :
        return self.ss_df.computeSpectral(self.rao, linear_hs=True, progressBar=True, engine = self.sht_engine, num_threads=self.num_threads)



    def contribution_df(self, x, i_rao = None, melt = False):
        """Return contribution as dataframe.

        Parameters
        ----------
        x : float or array
            Extreme value
        i_rao : int or None, optional
            Index of RAO of interest. The default is None.

        Returns
        -------
        pd.DataFrame
            Sea-state dataframe with contribution added as "Contribution_RAO_i" column

        """

        res = self.ss_df.copy()

        if hasattr(x, "__len__") :
            c_name = [ f"Contribution_RAO_{i:}" for i in range(len(x)) ]
            for i, x_ in enumerate(x):
                res.loc[:,c_name[i]] = self.longTerm[i].contribution(x_)

            if melt :
                return pd.melt( res, value_vars = c_name , var_name = "RAO", id_vars = self.ss_df.columns, value_name = "Contribution" )


        else :
            i_rao = self._get_default_i_rao(i_rao)
            res.loc[:,f"Contribution_RAO_{i_rao:}"] = self.longTerm[i_rao].contribution(x)
        return res


    def plot_contribution( self, x, how = "heading" , i_rao = None, ax = None, **kwargs):
        from Snoopy import PyplotTools as dplt
        if ax is None :
            fig, ax = plt.subplots()

        i_rao = self._get_default_i_rao(i_rao)

        contrib_df = self.contribution_df( x , i_rao = i_rao )

        if how == "heading" :
            contrib_df.groupby("Heading_0").sum().loc[ : , f"Contribution_RAO_{i_rao:}" ].plot(ax=ax, **kwargs)
        elif how == "hs_tp" :
            df = contrib_df.groupby( ["hs_0", "tp_0"] ).sum().loc[ : , f"Contribution_RAO_{i_rao:}" ].unstack()
            dplt.dfSurface(df, ax=ax, **kwargs)

        else:
            raise(ValueError( f"'how must be within ['heading' , 'hs_tp'']. Got : {how:}" ))



if __name__ ==  "__main__" :

    from Snoopy.Dataset import rec34_SD

    rao = sp.Rao( f"{sp.TEST_DATA:}/my_10.rao").getRaoForSpectral()

    raos = sp.Rao( [ sp.Rao( f"{sp.TEST_DATA:}/my_10.rao").getRaoForSpectral(),  sp.Rao( f"{sp.TEST_DATA:}/my_10.rao").getRaoForSpectral() ] )

    lt_sd = LongTermSD(rao, rec34_SD, 36 , 1.5, spreadingType = sp.SpreadingType.Cosn, spreadingValue=3.0)

    lt_sd.rp_to_x(25.0)

    lt_sd.plot_contribution( lt_sd.rp_to_x( 25.0), how = "heading" )
    lt_sd.plot_contribution( lt_sd.rp_to_x( 25.0), how = "hs_tp" )

