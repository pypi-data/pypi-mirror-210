import pandas as pd
import numpy as np
from scipy.optimize import root_scalar, minimize
from scipy.stats import genextreme
from scipy import stats
from matplotlib import pyplot as plt
from datetime import timedelta
from Snoopy.PyplotTools import distPlot
from Snoopy import logger
from copy import deepcopy
from Snoopy import Statistics as st
from scipy.special import gamma


def findMaxInAllBlock( se , block_size, start = None  ):
    """

    Parameters
    ----------
    se : pd.Series
        Time series to analyse
    block_size : float
        Block size
    start : float
        Start point (by default, minimum index of se)
    Returns
    -------
    iblockMax : np.ndarray
        index (label) of maxima localtion

    """
    #Get maxima per block

    if start is None :
        t = se.index[0]
    else:
        t = start
    iblockMax = []
    
    while t + block_size <= se.index[-1] + (se.index[-1]-se.index[-2]) :
        b = se.loc[ t : t + block_size ]
        if len(b) == 0 :
            iblockMax.append( np.nan )
        else :
            iblockMax.append( b.idxmax() )
        t += block_size
    
    iblockMax = np.array(iblockMax)
    
    if np.isnan(iblockMax.sum()):
        raise(Exception("block_size too small (found empty blocks)"))
    return iblockMax


def gradZpTGEV( coefs, yp ):
    """
    Gradient calculation for delta method's in use for CI
    """
    xi, _, sigma = coefs
    xi = -xi
    res = np.zeros((3))
    res[2] = 1
    res[1] = -(xi**-1)*(1-(yp**-xi) )
    res[0] = sigma*( xi**-2) *( 1-(yp**-xi) ) - sigma * (xi**-1) * (yp**-xi) * np.log(yp)
    return(res)


#Functions in use for Method of Moments
def skewness_GEV(c):  
    """Analytical skewness of GEV.
    
    Parameters
    ----------
    c : float
        shape parameter c.

    Returns
    -------
    float
        skewness derivative
    
    Notes
    -----
    gamma = Riemann's gamma function
    Coded with Scipy shape parameter convention (c -> = -c)
    """
    G1 = gamma( 1 + c )
    G2 = gamma( 1 + 2*c )
    G3 = gamma( 1 + 3*c )
    return -( G3 - 3 * G2 * G1 + 2 * G1**3 ) / (G2 - G1**2)**(3/2) 




def d_skewness_GEV(c):
    """Approx. derivative of skewness of GEV.
    
    Parameters
    ----------
    c : float
        shape parameter c.

    Returns
    -------
    float
        skewness derivative
        
    Notes
    -----
    gamma = Riemann's gamma function
    Coded with Scipy shape parameter convention (c -> = -c)
    """

    df = 0.01
    G1 = gamma( 1 + c )
    G2 = gamma( 1 + 2*c )
    G3 = gamma( 1 + 3*c )
    
    G1_df =  gamma( 1 + c+df )
    G2_df =  gamma( 1 + 2*(c+df) )
    G3_df =  gamma( 1 + 3*(c+df) )

    Sk  =  -( G3 - 3 * G2 * G1 + 2 * G1**3 ) / (G2 - G1**2)**(3/2)
    Sk_df = -( G3_df - 3 * G2_df * G1_df + 2 * G1_df**3 ) / (G2_df - G1_df**2)**(3/2)
    
    return( (Sk_df - Sk)/df )

def skew_to_shape(sk):
    """Extraction of shape parameter from Skewness
    Sk = skewness (maybe be an estimate) of the distribution (MoM)
    """
    c = root_scalar( lambda x : skewness_GEV(x) - sk ,  fprime = d_skewness_GEV, method = 'newton', bracket = (-3, 0), x0 = 1, xtol = 1e-2, maxiter = 8 )
    return(c.root)

def var_to_scale(var, c):
    """
    Compute scale parameter from Variance (MoM), knowing shape parameter (f.e already extracted from skewness)
    """
    G1 = gamma(1 + c)
    G2 = gamma(1 + 2*c)
    return (  ( var * c**2 / ( G2 - G1**2 ) )**0.5  )

def E_to_loc(E, c, scale):
    """
    Compute loc parameter from expectancy (MoM), knowing shape and scale parameters (f.e already extracted from skewness and then variance)
    """
    G1 = gamma(1 + c)
    return ( E +  scale * ( G1 - 1) / c )

def MoM_sample_to_params(Xi):
    """
    Return MoM estimators of c, scale and loc from sample Xi
    """
    E = np.mean(Xi)
    var = np.mean( (Xi - E)**2) 
    skew = np.mean(  ( (Xi - E)/var**0.5 )**3  )
    
    c = skew_to_shape(skew)
    scale = var_to_scale(var, c)
    loc = E_to_loc(E, c, scale)
    return( c, loc, scale, )
    



class BM(object):


    def __str__(self):

        s = f"""
        Block size : {self.block_size:}
        Duration   : {self.block_size * self.n:}
        """
        return s

    def __init__( self, maxima, block_size=None, variant = (0., 0.)):
        """Construct the BM object ("BlockMaxima"), directly from maxima.

        Parameters
        ----------
        maxima : np.ndarray
            Maxima per block
        block_size : float
            block size - size of blocks expressed in time unit
        variant : tuple
            Variant used for the emprical quantile estimation, default is (0., 0.), which corresponds to i / (n+1)
        """

        self.block_size = block_size

        self.max = np.sort(maxima)

        self.n = len(self.max)  #number of blocks
        
        
                    
        self._variant = variant

        self._bootstrap_objects = []
        # Return level class
        
        self.rl = st.ReturnLevel( maxima, duration = block_size * self.n , variant = variant)
        
        self._time_convert = None

        self._time_label = ""
        

    @classmethod
    def FromTimeSeries( cls, se , block_size=None , nb_block=None, time_convert = None, variant = (0., 0.)):
        """Create BM analysis using time series as input.

        Parameters
        ----------
        se : pd.Series
            Series to analysed, might be float or time indexed.
        block_size : float or timedelta (consistent with indexes type !)
            Size of the block:
                    if TS is time indexed : size of unit in corresponding float unit (i.e if 1 float = 3h and block size of 1 day, blocksize = 24/3)
                    if TS is float indexed : size of unit in timedelta
        nb_block : int
            alternative argument defining the total number of blocks
        time_convert : same as se.index
            Factor in use to convert time units to time range of interrest.
            Useful to get results directly in years. All plots and function will used the converted unit.
            If time entry is float with 1 = 3h and desired time unit is year, time_convert = 365 * 24 (time of interrest) / 3 (entry)
        """
        
        _se = se.copy(deep = True)
        
        
        if (bool(block_size) + bool(nb_block)) != 1 :
            raise(ValueError("You stipulate block_size or nb_block, and not both."))
            

        if time_convert is not None:
            _se.index = (_se.index - _se.index[0]) / time_convert
        else : 
            time_convert = 1.0
            
        if block_size is None :
            block_size = (se.index[-1]-se.index[0]) / nb_block
        else :
            if time_convert is not None:
                block_size /= time_convert            
            
        max_time = findMaxInAllBlock( _se, block_size )
        # handle NaN ?
        # max_time = t_max_[~np.isnan(max_time)]
        
        max_position = _se.index.get_indexer( max_time )
        
        BM = cls(maxima = _se.iloc[max_position].values, block_size = block_size, variant = variant)

        # Store original pointer to orignal time-series, associated maxima for plotting purpose
        BM._se = se
        BM._se_max = se.iloc[max_position]
        BM._time_convert = time_convert
        return(BM)

    
    def rp_to_x_empirical(self , rp ):
        """Interpolate to get value at RP (no fit).
        """
        return self.rl.rp_to_x(rp)

    def x_to_rp_empirical(self , x ):
        """Interpolate to get return period from a given return level (no fit)
        """
        return self.rl.x_to_rp(x)
            

    def plot_blocks(self, ax=None):
        """Plot time trace, together with maxima per block.
        """

        if ax is None :
            fig , ax = plt.subplots()
            
        if not hasattr( self, "_se" ) : 
            raise(Exception("Plotting time-series is only available when BM is constructed from a time-series."))

        ax.plot( self._se.index, self._se.values  )
        ax.plot( self._se_max.index, self._se_max.values, marker = "s" , linestyle = "" )

        t = self._se.index[0]
        c = True
        while t + self.block_size * self._time_convert <= self._se.index[-1] :
            ax.axvspan( t , t + self.block_size * self._time_convert , alpha = 0.2 if c else 0.3, color='red')
            t += self.block_size * self._time_convert
            c = not c
            
        xlabel = "Time"
        if self._time_label != "":
            xlabel += f" in {self._time_label}"
        ax.set( xlabel = xlabel)
        
        return ax

    def plot_rp_data(self, **kwargs ):
        """Plot empirical distribution with regard to return period.

        Parameters
        ----------
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        rp_range : np.ndarray, "auto" or None
            Range on which to plot the fitted distribution. If None, fit is not plotted. The default is "auto"
        kwargs : dict
            Argument passed to plt.plot() for data
        Returns
        -------
        ax : TYPE
            DESCRIPTION.
        """
        ax = self.rl.plot( **kwargs )
        if self._time_label != "":
            ax.set_xlabel("Return Period in " + self._time_label)
        return(ax)
            

class BM_GEV( BM ):
    
    def __init__( self, maxima, block_size=None, fit_kwds = {"method" : "minimize_mle" }, variant=  (0., 0.) ):
        """Construct the BM object ("BlockMaxima") with build-in GEV fit, directly from maxima.

        Parameters
        ----------
        maxima : np.ndarray
            Maxima per block
        block_size : float
            block size - size of blocks expressed in time unit
        fit_kwds : dict
            optional argument to specify method in use for fitting (default : {"method" : "mle" })
        variant : tuple
            Variant used for the emprical quantile estimation, default is (0., 0.), which corresponds to i / (n+1)
        """
        BM.__init__(self, maxima, block_size=block_size, variant = (0., 0.))
    
        self._fitted = None
        
        self._hessian = None
        self._invHess = None

        self.fit_kwds = fit_kwds
        if self.fit_kwds["method"] == "minimize_mle":
            self._fit_kwargs = {"method" : "Nelder-Mead"}
        
        
    def _fit(self, *args, **kwargs):
        guess_mm = MoM_sample_to_params(self.max)

        if self.fit_kwds["method"] == "minimize_mle":
            logger.debug( "Fitting GEV to data using C++ nnlf" )
            res = minimize( st.geneextreme_c.nnlf, x0 = [guess_mm[0], guess_mm[1], guess_mm[2],  ], args = (self.max,), **self._fit_kwargs )
            _coefs = [res.x[0], res.x[1], res.x[2] ]
            self._fitted = genextreme( *_coefs )

        else:
            logger.debug( "Fitting GEV to data using Scipy nnlf" )
            fitOptions = deepcopy(self.fit_kwds)
            fitOptions.update(kwargs)
            _coefs = genextreme.fit(self.max , guess_mm[0], loc = guess_mm[1], scale = guess_mm[2], **fitOptions) #TDI - dist.fit_scaled
            self._fitted = genextreme( *_coefs )
        return _coefs   
    
    
    @property
    def fitted(self):
        """
        Returns
        -------
        scipy.stats.rv_frozen
            Fitted distribution (MLE)

        """
        if self._fitted is None :
            self._fit()
        return self._fitted
    
    @property
    def coefs(self) :
        return self.fitted.args

    @property
    def shape(self):
        return self.fitted.args[0]

    @property
    def scale(self):
        return self.fitted.args[2]
    
    def x_to_rp( self, x ):
        """Calculate return period from return value acc. to fitted distribution

        Parameters
        ----------
        x : float or np.ndarray
            Return value

        Returns
        -------
        float or np.ndarray
            return period
        """
        return -self.block_size / np.log( self.fitted.cdf(x) )


    def rp_to_x(self, rp) :
        """Provide return value at RP acc. to fitted distribution
        
        Parameters
        ----------
        rp : float or array
            Return period.

        Returns
        -------
        float or np.ndarray
             Return value
        """
        return self.fitted.ppf( np.exp( -self.block_size / rp )  )
    
    def rp_to_rel_ci(self, rp, ci_level=0.95, ci_type="bootstrap"):
        """Provides the relative error on x for a given RP and a given confidence-level
        Parameters 
        ----------
        rp : float or array
            Return period.
        ci_level : in [0, 1], 
            Confidence-level
        ci_type : str
            Method in use to compute Confidence Intervals
        Returns
        -------
            float,
        Relative error on Return Value at a given confidence-Level
        """
        x = self.rp_to_x(rp)
        xci = self.rp_to_xci(rp=rp, ci_level=ci_level, ci_type=ci_type)
        return( np.mean([xci[1]-x, x-xci[0]]) /x )
    
    def bootstrap(self, n = 1000):
        """Bootstrap the POT analysis

        Parameters
        ----------
        n : int, optional
            Number of re-sample. The default is 1000.
        """
        logger.debug(f"Bootstrapping with n = {n:}")
        for i in range(n) : 
            self._bootstrap_objects.append( self.__class__( np.random.choice( self.max , size = len(self.max)  ) ,
                                                            block_size = self.block_size,
                                                            variant = self._variant,
                                                            fit_kwds = self.fit_kwds)  )
        
    
    def get_hessian(self, eps = 0.0001):
        """Num. approx. of Hessian matrix of nnlf at (_coefs, x_i) based on finite diff.
        Parameters : 
            eps : step used in finite diff. (default is 0.0001)
        Returns
            Hessian matrix of nnle (NOTE : take care of convention in use for parameters, scipy differs from Coles !)
        -------
        """
        if self._hessian is None :
            self.hessian(eps=eps)
        return self._hessian

    def hessian(self, eps=0.0001):
        """Calculation of hessian matrix of nnlf at (_coefs, x_i) based on finite differences
        eps : step used in finite difference (same for all directions)
        
        return  : approx hessian matrix 
        """
        hessian = np.zeros((len(self.coefs), len(self.coefs)))
        
        def fun(x):
            return( genextreme.nnlf(  x,  self.max ) )
        
        x0 = self.coefs
        for i in range(len(self.coefs)):
            for j in range(len(self.coefs)):
                e_i = np.zeros(len(self.coefs))
                e_i[i] = 1
                e_j = np.zeros(len(self.coefs))
                e_j[j] = 1
                hessian[i,j] = 1/(4*eps**2) * (   fun(x0+eps*e_i+eps*e_j) - fun(x0+eps*e_i-eps*e_j) - fun(x0-eps*e_i+eps*e_j) + fun(x0-eps*e_i-eps*e_j)   )
        for i,j in [(0,1), (0,2), (1,0), (2,0)]:
            hessian[i,j] = - hessian[i,j] #dshape --> -dshape 
        self._hessian = hessian
                
    def inv_Hess(self):
        if self._invHess is None :
            self._invHess = np.linalg.inv(self.get_hessian())
        return self._invHess
    
    @property
    def nnlf(self, coefs) :
        """negative log-likelihood function evaluated at given coefs."""
        return genextreme.nnlf(  coefs,  self.max )
    
    

    def plot_fit(self, ax = None, alphap = 0.4, betap = 0.4, **kwargs):
        if ax is None :
            fig , ax = plt.subplots()
        distPlot( self.max , frozenDist = self.fitted , ax=ax, alphap = alphap , betap = betap, **kwargs )
        return ax
       
    
    def plot_rp_fit(self, ax = None, rp_range = None, **kwargs ):
        """ Plot fitte and empirical distribution with regard to return period

        Parameters
        ----------
        ax : TYPE, optional
            DESCRIPTION. The default is None.
        rp_range : np.ndarray, "auto" or None
            Range on which to plot the fitted distribution. If None, fit is not plotted. The default is "auto"
        kwargs : dict
            Argument passed to plt.plot() for fitted distribution

        Returns
        -------
        ax : TYPE
            DESCRIPTION.
        """

        if ax is None :
            fig , ax = plt.subplots()

        if rp_range is None : 
            _x = self.rl.empirical_rp
            rp_range = np.logspace(  np.log10( np.min( _x ) ) , np.log10(np.max( _x ))*1.05   , 200 )
        
        ax.plot(  rp_range , self.rp_to_x( rp_range  ), **kwargs )

        xlabel = "Return period"

        if self._time_label != "":
             xlabel += f" in {self._time_label}"
        ax.set_xscale("log")
        ax.set_xlabel(xlabel)
        ax.grid(visible=True)
        
        return ax
    


    def rp_to_xci(self, rp ,  ci_level = 0.95, ci_type = "delta", n_bootstrap = 100 ):        

         rp = np.array(rp)        
         ci_type = ci_type.lower()
         
         if ci_type == "bootstrap":
             if len(self._bootstrap_objects) < n_bootstrap :
                 self.bootstrap( n_bootstrap - len(self._bootstrap_objects) )
             alpha_ci= 1 - ci_level
             v = [ b.rp_to_x( np.array(rp)) for b in self._bootstrap_objects ]
             x_low = np.quantile(v , alpha_ci/2 , axis = 0, method = "weibull")
             x_high = np.quantile(v ,  1-alpha_ci/2 , axis = 0, method = "weibull")
             return x_low, x_high, rp
         
         
         if ci_type == "delta":
             #Compute the confidence interval
             #Get inverse of Hessian matrix
             VarMatrix = self.inv_Hess()
    
             rp_min = self.block_size
             #Do not compute minimum rp
             rp = rp[rp > rp_min]
             #-------  Delta method
             #Comute coefficient from confidence level assuming the asymptotic normal distribution
             coefNorm = stats.norm.ppf( 0.5*(1. - ci_level) )
             
             Zp = self.rp_to_x( rp )
             p = 1 - np.exp(-self.block_size / rp)
             yp = -np.log( 1 - p )
             
             x_low = np.zeros(rp.shape)
             x_high = np.zeros(rp.shape)

             
             for i in range(rp.size) :
                 dZpT =  gradZpTGEV( self.coefs, yp[i] )
                 Y = np.matmul(  dZpT , VarMatrix)
                 VarZp = np.matmul( Y , dZpT )     
                 x_low[i] = Zp[i] + coefNorm*(VarZp**0.5)
                 x_high[i] = Zp[i] - coefNorm*(VarZp**0.5)
             return(x_low, x_high, rp)
                 

    def plot_rp_ci(self, rp_range = "auto" ,  ci_level = 0.95, ci_type = "delta", plot_type= "fill_between", alpha=0.25, ax=None, n_bootstrap = 100, **kwargs):
        """Plot confidence interval.

        Parameters
        ----------
        rp_range : np.ndarray or "auto", optional
            Return period range. The default is "auto".
        ci_level : float, optional
            DESCRIPTION. The default is 0.95.
        ci_type : str, optional
            DESCRIPTION. The default is "delta".
        plot_type : str, optional
            DESCRIPTION. The default is "fill_between".
        alpha : float, optional
            Opacity for CI plot. The default is 0.25.
        ax : plt.Axes, optional
            Where to plot. The default is None.
        n_bootstrap : int, optional
            Number of sample for bootstrapping. The default is 100.
        **kwargs : any
            Extre argument passed to ax.plot, or to ax.fill_between

        Returns
        -------
        ax : plt.Axes
            The plot
        """
        
        if ax is None :
            fig, ax= plt.subplots()
        
        if (rp_range is None ) or (str(rp_range) == "auto") : 
            _x = self.rl.empirical_rp
            rp_range = np.logspace(  np.log10( np.min( _x ) ) , np.log10(np.max( _x ))*1.05 , 200 )
        
        x_low, x_high, rp_range = self.rp_to_xci( rp = rp_range, ci_level=ci_level , ci_type = ci_type, n_bootstrap = n_bootstrap )
        
        if plot_type == "fill_between":
            ax.fill_between( rp_range, x_low, x_high, alpha = alpha, label=  f"{ci_type} - CI,  level = {ci_level}", **kwargs)

        elif plot_type == "plot":
            ax.plot(x_low, label = f"Min + level = {ci_level}")
            ax.plot(x_high, label = f"Max + level = {ci_level}")
    
        xlabel = "Return period"
        if self._time_label != "":
             xlabel += f" in {self._time_label}"   
        ax.set_xlabel(xlabel)
        ax.legend()
        ax.set_xscale("log")
        return ax
    

if __name__ == "__main__" : 

    from Snoopy.TimeDomain import TEST_DIR
    
    data = pd.read_csv( f"{TEST_DIR}/hs.csv", index_col = 0 , parse_dates = True ).hs  
    
    #Example 1 : bm_gev + TS with time index by 3h
    bm = BM_GEV.FromTimeSeries( se = data, block_size = timedelta(days=100), time_convert = timedelta(days=365.24) )
    #block_size --> en timedelta
    bm._time_label = "years"
    fig, ax = plt.subplots()
    bm.plot_blocks(ax=ax)
    
    fig, ax = plt.subplots()
    bm.plot_rp_data(ax=ax)
    bm.plot_rp_fit(ax=ax)
    bm.plot_rp_ci(ax=ax, ci_level=0.9, ci_type = "bootstrap", color = "blue")
    bm.plot_rp_ci(ax=ax, ci_level=0.9, ci_type = "delta", color = "orange")
    ax.set_xlim([None, 100])
    ax.set_ylim([0, 25])
    bm.rp_to_x( 10 )
    
    #Example 2 : bm_gev + TS with float index (here 1 float = 3 hours)
    data_ = data.copy(deep = True)
    data_.index = np.linspace(0, (data_.index[-1] - data_.index[0]).total_seconds()/3600/3, data_.index.size )
    
    bm = BM_GEV.FromTimeSeries( se = data_, block_size = 100*24/3, time_convert = 365*24/3 )
    bm._time_label = "years"
    fig, ax = plt.subplots()
    bm.plot_rp_data(ax=ax)
    bm.plot_rp_fit(ax=ax)
    bm.plot_rp_ci(ax=ax, ci_level=0.9, ci_type = "bootstrap", color = "blue")
    bm.plot_rp_ci(ax=ax, ci_level=0.9, ci_type = "delta", color = "orange")
    ax.set_ylim([0, 25])
    ax.set_xlim([None, 100])
    bm.rp_to_x( 10 )
    
