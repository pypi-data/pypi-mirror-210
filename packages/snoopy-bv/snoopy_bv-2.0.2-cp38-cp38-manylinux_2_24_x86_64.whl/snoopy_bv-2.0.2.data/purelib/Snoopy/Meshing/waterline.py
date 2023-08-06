"""
   Module to works on waterline
"""

from matplotlib import pyplot as plt
from Snoopy import Meshing as msh
from Snoopy import logger
import numpy as np


class Waterline(object) :

    def __init__(self , coords, segments, sym = 0 ) :
        """Waterline class. contains the description of a mesh waterline

        Parameters
        ----------
        coords : np.ndarray
            Coordinates of the waterline segments

        segments : np.ndarray
            Connectivity between coordinates

        sym : integer, optional
            0 : Full wateline
            1 : half waterline (symmetric y>0)
            2 : portside waterline
            3 : starboard waterline
            The default is True.

        Returns
        -------
        None.

        """
        self.coords = coords
        self.segments = segments
        self.sym = sym

        self._computeNormals()

    @classmethod
    def Read_hstarH5( cls, filename ):
        """Waterline from hslec h5 output

        filename : str
            hslec h5 output

        Returns
        -------
        Waterline

        """
        import xarray
        ds = xarray.open_dataset( filename )

        proplin = ds.PROPWLIN.values
        n = len(proplin)
        coords = np.empty( (2*n , 2), dtype = float )
        coords[:,:] = np.nan

        coords[::2,0] = proplin[ : , 12]
        coords[1::2,0] = proplin[ : , 15]
        coords[::2,1] = proplin[ : , 13]
        coords[1::2,1] = proplin[ : , 16]
        segments = np.arange(0 , 2*n , 1).reshape( n , 2 )

        return cls( coords, segments )


    def Extract_from_mesh(self , mesh , tol , z = 0.0) :
        """Construct waterline from Snoopy mesh

        Parameters
        ----------
        mesh : Snoopy.Meshing.Mesh
            Snoopy hull mesh
        tol : TYPE
            DESCRIPTION.
        z : TYPE, optional
            DESCRIPTION. The default is 0.0.

        Returns
        -------
        Waterline

        """


    def _computeNormals(self):
        """Compute waterline normals
        """
        logger.warning( "Waterline normals not yet implemnted" )
        self._normals = None


    def plot(self , ax = None, normals = True) :

        if ax is None :
            fig , ax = plt.subplots()

        for seg in self.segments :
            ax.plot( self.coords[ seg , 0 ] , self.coords[ seg , 1 ] , "-o"  )

        return ax


    def order(self):
        """
        Order the waterline nodes

        """
        raise(NotImplementedError)


    def mergeCoincidentNodes(self, tol = 1e-5):
        """
        """
        raise(NotImplementedError)



    def extractLoops():
        """Extract continous loops from waterline

        (eg : in case of ship with moonpool, there is two loops)

        """

        raise(NotImplementedError)


    def getHalfWaterline(self, side = +1) :
        """Cut waterline in two, if necessary additional point is added at y=0

        Parameters
        ----------
        side : float, optional
            +1 to get portside waterline (y>0)
            -1 to get starboard waterline (y<0).
            The default is +1.

        Returns
        -------
        Waterline

        """
        if self.sym != 0 :
            return self
        else:
            raise(NotImplementedError)


    def isTight( self  ) :
        """Check if waterline is tight (no holes)

        Returns
        -------
        Bool
            True if tight, false otherwise
        """
        raise(NotImplementedError)



    @property
    def orderedCoordinates( self , endPoints ) :
        """ Return list of coordinates, in ordered fashion

        Parameters
        ----------
        endPoints : bool
            If true, the last point duplicate the first one

        Returns
        -------
        np.ndarray
            Ordered coordinates of waterline

        """







eps = 1e-3
def getHalfWaterline( waterLineCoords , side = +1 ) :
    """
    return the one sided waterline, sorted in increasing x
    """

    #In case the mesh is not symmetric, point should be added at z=0
    tmp_ = add_y0_points(waterLineCoords)

    half = waterLineCoords[ np.where( tmp_[:,1]*side > -eps) ]

    #Start from aft central point
    symPlaneId = np.where( np.abs( half[:,1] ) < eps )[0]
    startNode = symPlaneId[ np.argmin(  half[symPlaneId,0] ) ]

    if half[(startNode+1) % len(half) , 1] == 0 :
        startNode += 1

    half = np.roll( half, -startNode , axis = 0)

    if half[0,0] > half[-1,0] :
        return half[::-1]
    else :
        return half


def add_y0_points( waterLineCoords, y = 0.0 ) :

    if len(np.where( abs(waterLineCoords[:,1]) < eps )[0]) == 2 :
        return waterLineCoords


    print (len(np.where( abs(waterLineCoords[:,1]) < eps )[0]))
    raise(NotImplementedError)

    #Interpolate at y = 0
    #TODO
    #closed set of point
    closed = np.vstack( [ waterLineCoords , waterLineCoords[0,:] ] )
    diff = (closed[:,1]-y) * (closed[:,1]-y) > 0



def getHalfCircDomain( waterLineCoords, r , side = +1, n = None, x_center = 0.0, y_center = 0.0 , close = False) :
    """
    Add circle around half waterline
    """

    half = getHalfWaterline(waterLineCoords, side = side )

    if n is None :
        n = len(half)

    i = np.linspace( 0, np.pi, n  )
    circle = np.full( (n, half.shape[1]) , 0.0 )
    circle[:,0] = r * np.cos( i ) + x_center
    circle[:,1] = side * r * np.sin( i ) + y_center
    res = np.concatenate( [ half, circle ] )

    if close :
        res = np.vstack( [ res, res[0,:] ] )

    return res


# -----------------------------------------------------------------------------
def inside_wl(x,y,x1_wl,y1_wl,x2_wl,y2_wl) :
    """Check if point is inside waterline
    Args:
        x (float): DESCRIPTION.
        y (float): DESCRIPTION.
        x1wl (np.array): x coordinates of first point
        y1_wl (np.array): y coordinates of first point
        x2_wl (np.array): x coordinates of second point
        y2_wl (np.array): y coordinates of second point

    Returns:
        bool : True if inside, False if outside

    """
    xmin = min(np.min(x1_wl),np.min(x2_wl))
    xmax = max(np.max(x1_wl),np.max(x2_wl))
    ymin = min(np.min(y1_wl),np.min(y2_wl))
    ymax = max(np.max(y1_wl),np.max(y2_wl))

    expr = (xmin < x < xmax) and (ymin < y < ymax)

    tol = 1e-6

    if (not expr):
        return False
    cut  = 0
    cutp = 0
    ne  = np.size(x1_wl)
    for i in range(ne):
        yemin  = min(y1_wl[i],y2_wl[i])
        yemax  = max(y1_wl[i],y2_wl[i])
        expr   = (yemin <= y <= yemax)
        if(expr):
            # savoir si le pt est a gauche ou a droite du segment
            if( y1_wl[i] <= y2_wl[i] ):
                px0 = x1_wl[i]
                px1 = x2_wl[i]
                py0 = y1_wl[i]
                py1 = y2_wl[i]
            else:
                px0 = x2_wl[i]
                px1 = x1_wl[i]
                py0 = y2_wl[i]
                py1 = y1_wl[i]
            u    = np.array([ px0 - x , py0 - y])
            u1   = np.array([ px1 - x , py1 - y])
            d    = np.cross(u, u1)
            if (d >= tol):
                if ( abs(y - py0) <= tol or abs(y - py0) <= tol ):
                    cutp = cutp + 1
                    cut  = cut  + 1
                else:
                    cut = cut + 1
    return ( (cut - cutp) % 2 == 1 )




if __name__ == "__main__" :

    from matplotlib import pyplot as plt
    meshFile = r"D:\Etudes\SSSRI_FishFarm\notop\notop.hst"



    mesh = msh.Mesh( msh.HydroStarMesh( meshFile ).getUnderWaterHullMesh(0) )
    waterLineCoords = mesh.extractWaterlineCoords()

    plt.plot( waterLineCoords[:,0], waterLineCoords[:,1] , "-o")

