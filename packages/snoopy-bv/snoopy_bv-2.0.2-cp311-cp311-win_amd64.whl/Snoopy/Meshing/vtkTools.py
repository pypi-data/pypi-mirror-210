import numpy as np
import h5py
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from Snoopy import Meshing as msh
from Snoopy import logger

from .waterline import getHalfCircDomain


def extractWaterLine(hullPolydata, x_center = 0.0, side = +1):
    """Extract waterline from wetted hull
    Works using vtkFeatureEdges and vtkContourLoopExtraction

    return arrays of waterline nodes (xyz)
    """

    #--- Retrieve waterline
    wl = vtk.vtkFeatureEdges()
    wl.SetInputData( hullPolydata )
    wl.BoundaryEdgesOn()
    wl.FeatureEdgesOff()
    wl.NonManifoldEdgesOff()
    wl.ManifoldEdgesOff()
    wl.Update()
    loops = vtk.vtkContourLoopExtraction()
    loops.SetInputConnection(wl.GetOutputPort())
    loops.Update()
    loops_p = loops.GetOutput()
    vtk_to_numpy(  loops_p.GetPoints().GetData() )
    idList = vtk.vtkIdList()
    loops_p.GetCellPoints(0, idList)
    nId = [idList.GetId(i) for i in range( idList.GetNumberOfIds() )]
    orderedCoord = vtk_to_numpy(  wl.GetOutput().GetPoints().GetData() ) [nId]

    return orderedCoord

def createHalfFreeSurfaceMesh_polydata( hullPolydata, R , dx, dy, x_center = 0., y_center = 0. , side = +1, orderedCoord = None) :
    """Create circulat free-surface mesh around a simple hull.

    :param Mesh hullMesh : hull mesh (full)
    :param float R : Radius of the free surface
    :param float dx : cell size
    :param float dy : cell size
    :param float x_center : free-surface center
    :param float y_center : free-surface center

    """
    #--- Create background free-surface mesh
    rect = createRectangularGrid( x_min = x_center - 2*R,
                                  x_max = x_center + 2*R,
                                  dx = dx,
                                  y_min = y_center - 2*R,
                                  y_max = y_center + 2*R,
                                  dy = dy )

    if orderedCoord is None:
        orderedCoord = extractWaterLine( hullPolydata, side = side )

    res = getHalfCircDomain( orderedCoord, r=R , n=100,  side = side, x_center = x_center, y_center = y_center )

    cont = createPolygon(res)
    cookie = vtk.vtkCookieCutter()
    cookie.SetInputData(rect)
    cookie.SetLoopsData(cont)
    cookie.Update()

    return cookie.GetOutput()


def createFreeSurfaceMesh( *args, **kwargs ):
    """
    Create a full free surface mesh around the hull, using cookieCutter

    :param Mesh hullMesh : hull mesh (full)
    :param float R : Radius of the free surface
    :param float dx : cell size
    :param float dy : cell size
    :param float x_center : free-surface center
    :param float y_center : free-surface center
    """

    fs1 = createHalfFreeSurfaceMesh(*args, side = +1, **kwargs)
    fs2 = createHalfFreeSurfaceMesh(*args, side = -1, **kwargs)
    fs1.append(fs2)
    return fs1


def createHalfFreeSurfaceMesh( hullMesh, R , dx, dy, x_center = 0., y_center = 0., side = +1, orderedCoord = None ) :
    """ Create circulat free-surface mesh around a hull.

    :param Mesh hullMesh : hull mesh (full)
    :param float R : Radius of the free surface
    :param float dx : cell size
    :param float dy : cell size
    :param float x_center : free-surface center
    :param float y_center : free-surface center
    """
    polydata = createHalfFreeSurfaceMesh_polydata(hullMesh.toVtkPolyData(), R, dx, dy, x_center, y_center, side=side, orderedCoord = orderedCoord )
    return msh.Mesh.FromPolydata(polydata, polygonHandling = "triangulate")


def createPolygon( pointsArray ):
    """
    Create polydata with one polygon from ordered list of points
    """

    nTot = len(pointsArray)
    loops = vtk.vtkPolyData()
    loopPts = vtk.vtkPoints()
    loopPolys = vtk.vtkCellArray()
    loops.SetPoints(loopPts)
    loops.SetPolys(loopPolys)
    loopPts.SetNumberOfPoints(nTot)
    loopPolys.InsertNextCell(nTot)
    for i in range(nTot) :
        loopPts.SetPoint( i, pointsArray[i,:]  )
        loopPolys.InsertCellPoint(i)
    return loops


def createRectangularGrid(x_min, x_max, dx, y_min, y_max, dy):
    """
    Create a rectangular grid polydata
    """

    x_dim = int((x_max - x_min) / dx)
    y_dim = int((y_max - y_min) / dy)

    planeSource = vtk.vtkPlaneSource()
    planeSource.SetOrigin(x_min, y_min, 0.0)
    planeSource.SetPoint1(x_max, y_min, 0.0)
    planeSource.SetPoint2(x_min, y_max, 0.0)
    planeSource.SetXResolution(x_dim)
    planeSource.SetYResolution(y_dim)
    planeSource.Update()

    return planeSource.GetOutput()

def creatDiskGrid( r, dx, dy, x_center = 0, y_center = 0 ) :

    rect = createRectangularGrid( -r, +r, dx, -r, +r, dy )
    n_circ = 100
    circle = np.zeros( (n_circ,3), dtype = float )
    angle = np.linspace(0 , 2*np.pi, n_circ, endpoint = False)
    circle[:,0] = r*np.cos( angle )
    circle[:,1] = r*np.sin( angle )
    cont = createPolygon(circle)

    cookie = vtk.vtkCookieCutter()
    cookie.SetInputData(rect)
    cookie.SetLoopsData(cont)
    cookie.Update()
    return cookie.GetOutput()



#---------------------------------------------------------------------#

def write_vtkUnstructuredGrid_vtkhdf(ugrid, filename):
    """Write to HDF vtk format

    Parameters
    ----------
    ugrid : vtk.vtkUnstructuredGrid
        Input data in format vtk.vtkUnstructuredGrid 
    filename : str
        Filename.
    """
    if not isinstance(ugrid, vtk.vtkUnstructuredGrid):
        raise TypeError(f"Expect in put as vtkUnstructuredGrid, {type(ugrid)} received!")

    logger.debug(f"Going to write vtkUnstructeredGrid to : {filename}")

    with  h5py.File( filename , mode = "w") as nf : 
        dset = nf.create_group( "VTKHDF" )
        
        dset.attrs.create("Type", np.string_("UnstructuredGrid"))
        dset.attrs["Version"] = [1, 0]

        cells = ugrid.GetCells()
        dset.create_dataset("NumberOfConnectivityIds", 
                            data  = np.asarray([cells.GetNumberOfConnectivityIds()]), 
                            dtype = np.int64)
        dset.create_dataset("NumberOfPoints", 
                            data  = np.asarray([ugrid.GetNumberOfPoints()]), 
                            dtype = np.int64)
        dset.create_dataset("NumberOfCells", 
                            data  = np.asarray([cells.GetNumberOfCells()]), 
                            dtype = np.int64)
        dset.create_dataset("Points", data  = vtk_to_numpy(ugrid.GetPoints().GetData())  )   
        dset.create_dataset("Connectivity", data  = vtk_to_numpy(cells.GetConnectivityArray()))
        dset.create_dataset("Offsets", data  =  vtk_to_numpy(cells.GetOffsetsArray()))
        dset.create_dataset("Types",   data  =  vtk_to_numpy(ugrid.GetCellTypesArray()))
        all_attribute_types = ["PointData", "CellData", "FieldData"]
        for attribute_type_enum,attribute_type_name in enumerate(all_attribute_types):
            field_data = ugrid.GetAttributesAsFieldData(attribute_type_enum)
            nb_array =  field_data.GetNumberOfArrays() 
            if nb_array > 0:

                field_data_group = dset.create_group(attribute_type_name)
                # only for POINT and CELL attributes
                if attribute_type_enum < 2:
                    for i in range(nb_array):
                        array = field_data.GetArray(i)

                        if array:
                            anp = vtk_to_numpy(array)
                            field_data_group.create_dataset(array.GetName(), anp.shape, anp.dtype, data = anp)
                            
                    #for field_type in ["Scalars", "Vectors", "Normals", "Tensors", "TCoords"]:
                    #    array = getattr(field_data, "Get{}".format(field_type))()
                    #    print("Get:", field_type, array)
                    #    if array:
                    #        field_data_group.attrs.create(field_type, np.string_(array.GetName()))
            

            # FIELD attribute
            if attribute_type_enum == 2:
                for i in range(nb_array):
                    array = field_data.GetArray(i)
                    if not array:
                        array = field_data.GetAbstractArray(i)
                        if array.GetClassName() == "vtkStringArray":
                            dtype = h5py.special_dtype(vlen=bytes)
                            dset = field_data_group.create_dataset(
                                array.GetName(),
                                (array.GetNumberOfValues(),), dtype)
                            for index in range(array.GetNumberOfValues()):
                                dset[index] = array.GetValue(index)
                        else:
                            # don't know how to handle this yet. Just skip it.
                            print("Error: Don't know how to write "
                                  "an array of type {}".format(
                                      array.GetClassName()))
                    else:
                        anp = vtk_to_numpy(array)
                        dset = field_data_group.create_dataset(
                            array.GetName(), anp.shape, anp.dtype)
                        dset[0:] = anp


