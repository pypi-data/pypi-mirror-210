from Snoopy import Meshing as msh
import numpy as np


def getQuadsConnectivity( nx, ny ) :
    quads = np.empty( ((nx-1)*(ny-1),4), dtype = int )
    rangex = np.arange(nx-1, dtype = int)
    rangey = np.arange(ny-1, dtype = int)
    for iy in rangey:
        ipanel = rangex + iy * (nx-1)
        quads[ ipanel ,0] = rangex + nx * iy
        quads[ ipanel ,1] = 1 + rangex + nx * iy
        quads[ ipanel ,2] = 1 + rangex + nx * (iy + 1)
        quads[ ipanel ,3] = rangex + nx * (iy + 1)
    return quads


def createRectangularGrid( x_min, x_max, dx, y_min, y_max, dy, z=0  ):
    """ Return rectangular grid mesh
    """

    nx = int((x_max-x_min) / dx)
    ny = int((x_max-x_min) / dy)
    X, Y = np.meshgrid(  np.linspace(x_min, x_max, nx),  np.linspace(y_min, y_max, ny) )
    nodes = np.stack( [X.flatten(), Y.flatten(), np.full(len(Y.flatten()),z )] ).T

    quads = getQuadsConnectivity( nx, ny )


    return msh.Mesh( Vertices = nodes, Quads = quads, Tris = np.zeros((0,3), dtype = float)  )
