import numpy as np

def round_nearest(x, a):
    """Round number with a given precision

    Parameters
    ----------
    x : float (or numpy array)
        Array to round
    a : float, optional
        Precision

    Example
    -------
    >>> round_nearest(0.014 , 0.01)
    0.01

    >>> round_nearest( 4.3333 , 0.05)
    4.35
    """

    return np.round(np.round(x / a) * a, -int( np.floor(np.log10(a))))


def is_multiple( array , dx , tol = 1e-10):
    """Check if all element in array are multiple of dx.

    Due to floating point arithmetic, this can generally be only approximate.

    Parameters
    ----------
    array : array like
        Array to check
    dx : float
        Multiple to check for
    tol : float, optional
        Tolerance. The default is 1e-10

    Returns
    -------
    dx : Bool
        True if dx is a multiple of all element in array.
    """

    r = np.mod(array , dx)
    return (np.isclose( r, 0 ) | np.isclose(r , dx, atol = tol)).all()




def get_dx( array, dx=None, eps = 1e-3, raise_exception=False ):
    """Check if array is evenly spaced

    Parameters
    ----------
    array : TYPE
        DESCRIPTION.
    dx : float, optional
            Check if dx is the step. The default is None.
    eps : float, optional
            Tolerance. The default is 0.001

    Returns
    -------
    dx : float or None
        Step, if any, None otherwise

    """
    n = len(array)
    if n <= 1 :
        return None

    if dx is None :
        dx = ( np.max( array ) - np.min(array)) / (n-1)

    # Check that all frequency are multiple of df
    check = (np.diff(array) - dx) < eps

    if check.all() :
        return dx
    else :
        if raise_exception : 
            raise(Exception( "Array must be evenly spaced to retrieve 'dx'" ))
        return None

def edges_from_center(array):
    """Return edges from bin centers
    Check that data are evenly spaced

    Parameters
    ----------
    array : array
        Centers

    Returns
    -------
    array
        edges
    """
    dx = get_dx( array )

    if dx is None :
        raise(Exception( f"{array:} is not evenly spaced" ))

    return np.append( [array[0]-0.5*dx] , [  array + 0.5*dx]  )



if __name__ == "__main__" :

    #Quick test :
    array = np.array([ 0.5 , 1.5 , 2.5, 3.5 ])
    print (edges_from_center( array ))



