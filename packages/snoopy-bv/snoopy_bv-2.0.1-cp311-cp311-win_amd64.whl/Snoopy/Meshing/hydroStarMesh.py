import os
import numpy as np
from Snoopy.Meshing import Mesh
import _Meshing
from Snoopy import Meshing as msh
from Snoopy import logger

"""
Mesh dictionary key syntax
(NUMPANEL , ibody, sym)
(NUMFPONT , ibody)
(NUMFTANK , itank, sym, zfs, x, y , z, rho)
"""



symDict = {
            _Meshing.SymmetryTypes.NONE : 0,
            _Meshing.SymmetryTypes.XZ_PLANE : 1,
            _Meshing.SymmetryTypes.XZ_YZ_PLANES : 2,
          }


def mergeMeshes( mesh1, mesh2, offset1 = [0,0,0], offset2 = [0,0,0] ) :
    """Merge two single body mesh in one 2 body mesh
    """
    logger.debug("Merging meshes")

    _mesh1 = msh.HydroStarMesh(mesh1)
    _mesh1.offset( offset1 )

    _mesh2 = msh.HydroStarMesh(mesh2)
    _mesh2.offset( offset2 )

    mergedMesh = msh.HydroStarMesh( underWaterHullMeshes = [ _mesh1.getUnderWaterHullMesh(0), _mesh2.getUnderWaterHullMesh(0) ] ,
                                    aboveWaterHullMeshes = [ _mesh1.getAboveWaterHullMesh(0), _mesh2.getAboveWaterHullMesh(0) ] ,
                                    plateMeshes          = [ _mesh1.getPlateMesh(0), _mesh2.getPlateMesh(0) ] ,
                                    fsMeshes             = [ _mesh1.getFsMesh(0), _mesh2.getFsMesh(0) ] ,
                                    tankMeshes           = [ _mesh1.getTankMesh(i) for i in range(_mesh1.getNbTank()) ] + [ _mesh2.getTankMesh(i) for i in range(_mesh2.getNbTank()) ]
                                   )

    return mergedMesh





class HydroStarMesh( _Meshing.HydroStarMesh ):

    def __str__(self) :

        s = ""
        for ibody in range(self.getNbBody()) :
            temp = """
#----- Body {:} -----#
Number of wetted panels : {:}  {:}
Number of above panels  : {:}
Number of plate         : {:}  {}
Center of Buyancy       : {:.2f} , {:.2f}, {:.2f}
Symmetry                : {:}
#--------------------------#
"""

            dataRange = msh.Mesh(self.getUnderWaterHullMesh(ibody)).getDataRange()
            if dataRange[0] == dataRange[1] == np.nan :
                dataRange_str = ""
            else :
                dataRange_str = "Porosity range ({:.1f}, {:.1f})".format(*dataRange)


            dataRangePlate_str = ""

            if len(self.getPlateMesh(ibody).getPanelsData() > 0):
                dataRangePlate = np.min(self.getPlateMesh(ibody).getPanelsData()), np.max(self.getPlateMesh(ibody).getPanelsData())
                if not (dataRangePlate[0] == dataRangePlate[1] == 0.) :
                    dataRangePlate_str = "Porosity range ({:.1f}, {:.1f})".format(*dataRangePlate)

            s += temp.format( ibody+1, self.getUnderWaterHullMesh(ibody).getNPanels(), dataRange_str,
                             self.getAboveWaterHullMesh(ibody).getNPanels() ,
                             self.getPlateMesh(ibody).getNPanels(), dataRangePlate_str,
                             *self.getUnderWaterHullMesh(ibody).integrate_cob(),
                             self.getUnderWaterHullMesh(ibody).sym
                             )

        return s

    def __init__(self, *args, **kwargs) :
        _Meshing.HydroStarMesh.__init__( self , *args, **kwargs )
        self._updateMeshDict()


    @property
    def nbbody(self):
        return self.getNbBody()

    def getMesh(self):
        return Mesh(super().getMesh())

    def getNPanels(self):
        return np.sum( [self.getUnderWaterHullMesh(ibody).getNPanels() for ibody in range(self.getNbBody()) ])

    def getBounds(self):
        b = []
        for ibody in range(self.getNbBody()):
            b.append(Mesh(self.getHullMesh(ibody)).getBounds())

        b = np.array(b)

        return  [(min(b[::,0,0]), max(b[::,0,1])),
                 (min(b[::,1,0]), max(b[::,1,1])),
                 (min(b[::,2,0]), max(b[::,2,1]))]

    def append(self, *args, **kwargs):
        _Meshing.HydroStarMesh.append(self, *args, **kwargs)
        self._updateMeshDict()

    def _updateMeshDict(self):

        #self.meshDict = {}
        self._meshDict = {}
        for ibody in range( self.getNbBody() ) :
            #self.meshDict[ ("NUMPANEL", ibody+1) ] = lambda : Mesh(self.getUnderWaterHullMesh(ibody))
            #self.meshDict[ ("NUMFPONT", ibody+1) ] = lambda : Mesh(self.getAboveWaterHullMesh(ibody))
            #self.meshDict[ ("NUMFPLATE", ibody+1)] = lambda : Mesh(self.getPlateMesh(ibody))
            self._meshDict[ ("NUMPANEL", ibody+1) ] = self.getUnderWaterHullMesh(ibody)
            self._meshDict[ ("NUMFPONT", ibody+1) ] = self.getAboveWaterHullMesh(ibody)
            self._meshDict[ ("NUMFPLATE", ibody+1)] = self.getPlateMesh(ibody)

        for itank in range( self.getNbTank() ):
            self._meshDict[ ("NUMFTANK", itank+1)] = self.getTankMesh(itank)



    def clean(self, tolerance):
        for mesh in self._meshDict.values() :
            mesh.clean(tolerance)


    def offset_py(self, coords):
        for mesh in self._meshDict.values() :
            mesh.offset(coords)


    def offsetBody(self, coords, body):
        for (part, ibody), mesh in self._meshDict.items():
            if ibody == body :
                mesh.offset(coords)


    def write(self, filename, hstarKeyword = None) :
        """
        Write HydroStar mesh
        """

        logger.debug(f"Writting mesh to {filename:}")

        p = os.path.abspath( os.path.dirname(filename) )
        if not os.path.exists( p ) :
            os.makedirs( p )

        offset = {}
        startPanel = {}
        endPanel = {}
        s_nodes = ""
        i = 1
        for meshKey, mesh in self._meshDict.items() :
            offset[meshKey] = i
            for n in mesh.nodes :
                s_nodes += "{:} {:.5e} {:.5e} {:.5e}\n" .format( i , *n)
                i += 1

        s_panels = ""
        ipanel = 1
        for meshKey, mesh in self._meshDict.items() :
            logger.debug(f"Writting {meshKey:} in {filename:}")
            startPanel[meshKey] = ipanel
            data = mesh.getPanelsData()
            ip = 0
            for n in mesh.tris :
                n_off = n + offset[meshKey]
                s_panels += "{} {} {} {} {} {}\n".format( ipanel, *n_off, n_off[-1],  "" if data.shape[1] == 0 or data[ip,0] == 0. else data[ip,0] )
                ipanel += 1
                ip += 1

            for n in mesh.quads :
                n_off = n + offset[meshKey]
                s_panels += "{} {} {} {} {} {}\n".format( ipanel, *n_off, "" if data.shape[1] == 0 or data[ip,0] == 0. else data[ip,0] )
                ipanel += 1
                ip += 1
            endPanel[meshKey] = ipanel-1


        with open(filename, "w") as f :
            f.write("NBBODY {:}\n".format(self.getNbBody()))

            if self.getNbTank() > 0 :
                f.write("NBTANK {:}\n".format(self.getNbTank()))

            for ibody in range(self.getNbBody()) :
                f.write( "SYMMETRY_BODY {:} {:}\n".format( ibody+1, symDict[ self.getUnderWaterHullMesh(ibody).sym ] ) )

            for meshKey, mesh in self._meshDict.items() :
                if endPanel[meshKey] > startPanel[meshKey] :
                    f.write( "{:} {:} {:} {:}\n".format( meshKey[0], meshKey[1] , startPanel[meshKey], endPanel[meshKey] ) )

            if hstarKeyword is not None :
                f.write( "\n" + hstarKeyword + "\n")

            f.write( "COORDINATES\n{:}ENDCOORDINATES\n".format(s_nodes) )
            f.write( "PANEL TYPE 1\n{:}ENDPANEL\n".format(s_panels))
            f.write( "ENDFILE")

        return s_panels


    def extractWaterline(self):
        return [ msh.Mesh(self.getUnderWaterHullMesh(ib)).extractWaterline() for ib in range(self.getNbBody()) ]

    def extractWaterlineCoords(self):
        return [ msh.Mesh(self.getUnderWaterHullMesh(ib)).extractWaterlineCoords() for ib in range(self.getNbBody()) ]

    def plotWaterline(self, ax = None):
        from matplotlib import pyplot as plt
        if ax is None :
            fig, ax = plt.subplots()
        for ib in range(self.getNbBody()) :
            xy = msh.Mesh(self.getUnderWaterHullMesh(ib)).extractWaterlineCoords()
            ax.plot( xy[:,0], xy[:,1] , "o-" )
        return ax


#Make C++ wrapped function return the python subclass.
for method in ["getTankMesh", "getUnderWaterHullMesh"]:
    def makeFun(method):
        fun = getattr(_Meshing.HydroStarMesh, method)
        def newFun(*args,**kwargs) :
            return Mesh(fun(*args, **kwargs))
        newFun.__doc__ = fun.__doc__
        return newFun
    setattr(HydroStarMesh, method + "Copy", makeFun(method))


