import numpy as np
from Snoopy import Meshing as msh

def convertPropHull(propHull, symType = msh.SymmetryTypes.NONE, read_coef = False):
    """Convert mesh from HydrpStar mesh storage to Snoopy object.

    Parameters
    ----------
    propHull : np.ndarray
        The mesh in HydroStar storage format
    symType : int, optional
        Symmetry, by default msh.SymmetryTypes.NONE

    Returns
    -------
    Mesh
        The mesh object
    """

    nPanel = len(propHull)
    nodes = np.stack( [ np.hstack( [propHull[:,12],  propHull[:,15],propHull[:,18], propHull[:,21]  ] ),
                        np.hstack( [propHull[:,13],  propHull[:,16],propHull[:,19], propHull[:,22]  ] ),
                        np.hstack( [propHull[:,14],  propHull[:,17],propHull[:,20], propHull[:,23]  ] ),
                      ]).T

    panels = np.arange( 0, nPanel*4,1 ).reshape( 4, nPanel ).T
    
    mesh = msh.Mesh( Vertices = nodes, Quads = panels, Tris = np.zeros((0,3), dtype = int),
                     keepSymmetry = True , symType = symType)
        
    if read_coef : 
        mesh.setPanelsData( propHull[:,11][:,np.newaxis], dataNames = ["POROSITY"], dataTypes = [0] , dataFreqs = [np.nan], dataHeads = [np.nan] )

    return mesh
    


def read_hslec_h5(filename, engine = "h5py", format = "hydrostarmesh"):
    """Read hslec hdf output and convert to Snoopy.Mesh.

    Parameters
    ----------
    filename : str
        Filename
        
    format : str
        If format "hydrostarmesh", the mesh is returned as a ````HydroStarMesh```` object (concatenation of meshes), 
        If format "mesh", the mesh is returned as a ````Mesh````, where belong the panels is then given by "SECTION" data.
        
    Returns
    -------
    msh.HydroStarMesh or msh.Mesh
        The mesh
    """

    # Note: hslec h4 does not fully comply with netcdf4, so that it is more robust to open it with h5py directly
    if engine == "h5py" :
        import h5py
        with h5py.File(filename, "r") as da :
            nbbody = da.attrs["NBBODY"][0]
            hull_symmetry = da.attrs["HULL_SYMMETRY"][0]
            prophull = [ da["PROPHULL"] [ da["N_HULL"][ibody,0] - 1 : da["N_HULL"][ibody,1]] for ibody in range(nbbody) ]
            propont =  [ da["PROPPONT"] [ da["N_PONT"][ibody,0] - 1 : da["N_PONT"][ibody,1]] for ibody in range(nbbody) ]
            proplate = [ da["PROPPLATE"][ da["N_PLATE"][ibody,0] - 1 : da["N_PLATE"][ibody,1]] for ibody in range(nbbody) ]
    else:
        import xarray
        with xarray.open_dataset(filename, engine = engine) as da :
            nbbody = da.attrs["NBBODY"]
            hull_symmetry = da.attrs["HULL_SYMMETRY"]
            prophull = [ da.PROPHULL.values[ da.N_HULL[ibody,0].values-1 : da.N_HULL[ibody,1].values] for ibody in range(nbbody) ]
            propont =  [ da.PROPPONT.values[ da.N_PONT[ibody,0].values-1 : da.N_PONT[ibody,1].values ,:  ] for ibody in range(nbbody) ]
            proplate = [ da.PROPPLATE.values[ da.N_PLATE[ibody,0].values-1 : da.N_PLATE[ibody,1].values ,:  ] for ibody in range(nbbody) ]

    symType = msh.SymmetryTypes.NONE
    if hull_symmetry == 1:
        symType = msh.SymmetryTypes.XZ_PLANE
    elif hull_symmetry == 2:
        symType = msh.SymmetryTypes.XZ_YZ_PLANES

    underWaterHullMeshes = [  convertPropHull(  prophull[ibody] , symType = symType) for ibody in range(nbbody) ]

    aboveWaterHullMeshes = [  convertPropHull( propont[ibody] , symType = symType) for ibody in range(nbbody) ]
    
    plateMeshes = [  convertPropHull( proplate[ibody] , symType = symType ) for ibody in range(nbbody) ]

    # TODO
    tankMeshes = []
    fsMeshes = []

    if format.lower() == "hydrostarmesh":
        return msh.HydroStarMesh( underWaterHullMeshes = underWaterHullMeshes,
                                aboveWaterHullMeshes = aboveWaterHullMeshes,
                                plateMeshes = plateMeshes,
                                fsMeshes = fsMeshes,
                                tankMeshes = tankMeshes,
                                )

    if format.lower() == "mesh":
        total_mesh = None
        for ibd in range(len(underWaterHullMeshes)) :
            for meshList, i_s in [ (underWaterHullMeshes,1) , (aboveWaterHullMeshes,10), (plateMeshes, 40) ,]:
                isection = i_s + ibd
                mesh = meshList[ibd]
                mesh.appendPanelsData( np.full( (mesh.getNPanels()) , isection) , dataName = "SECTION" )
                if total_mesh is None : 
                    total_mesh = mesh
                else :
                    total_mesh.append( mesh )
        return total_mesh
    else:
        raise(Exception(f"{format:} is not an available format"))
                


def read_hslec_waterline_h5(filename, engine = "h5py") :
    if engine == "h5py" :
        import h5py
        with h5py.File(filename, "r") as da :
            sym = da.attrs["HULL_SYMMETRY"][0]
            propwlin = da["PROPWLIN"][:,:]
    else :
        import xarray
        with xarray.open_dataset(filename, engine = engine, phony_dims='access') as da :
            sym = da.attrs["HULL_SYMMETRY"]
            propwlin = da.PROPWLIN.values

    x1_ = propwlin[:,12]
    y1_ = propwlin[:,13]
    x2_ = propwlin[:,15]
    y2_ = propwlin[:,16]

    if sym == 1 :
        x1 = np.concatenate( [x1_, +x2_] )
        x2 = np.concatenate( [x2_, +x1_] )
        y1 = np.concatenate( [y1_, -y2_] )
        y2 = np.concatenate( [y2_, -y1_] )
    else :
        return x1_, y1_, x2_, y2_

    return x1, y1, x2, y2


if __name__ == "__main__" :
    from Snoopy import logger
    logger.setLevel(10)

    filename = rf"{msh.TEST_DATA:}/hslec_b31.h5"
    mesh = read_hslec_h5(filename , format = "mesh")

