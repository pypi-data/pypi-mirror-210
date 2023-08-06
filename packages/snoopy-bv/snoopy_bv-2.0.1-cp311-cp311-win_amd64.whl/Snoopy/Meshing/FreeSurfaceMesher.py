from Snoopy.Meshing.structuredGrid import createRectangularGrid
from Snoopy.Meshing import Mesh
from Snoopy.Meshing.vtkTools import creatDiskGrid, createFreeSurfaceMesh


class FreeSurface(object):
    """Dataclass holding a free surface paramters
    """

    def generateAroundPoint( self, x_center, y_center ) :
        raise(NotImplementedError)

    def generateAroundMesh( self, hull ) :
        raise(NotImplementedError)

    def generateAroundHstarMesh( self, mesh ) :
        raise(NotImplementedError)



class FreeSurfaceRect(FreeSurface):
    def __init__(self, x=500, y = 500, dx = 10, dy = 10):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy


class FreeSurfacesCirc(FreeSurface):
    def __init__(self, r=500, dx = 10,dy = 10):
        self.r = r
        self.dx = dx
        self.dy = dy



class FreeSurfaceRectPlain(FreeSurfaceRect):

    def generateAroundMesh( self, hull ) :
        """
        """
        x, y, _ = hull.integrate_cob()
        return self.generateAroundPoint( x, y )


    def generateAroundHstarMesh( self, mesh ) :
        """
        """
        hull = mesh.getUnderWaterHullMesh(0)
        return self.generateAroundMesh( hull )


    def generateAroundPoint( self, x_center, y_center ) :
        return createRectangularGrid( x_center-0.5*self.x, x_center+0.5*self.x, self.dx,
                                      y_center-0.5*self.y, y_center+0.5*self.y, self.dy, z=0  )


class FreeSurfaceCircPlain(FreeSurfacesCirc):
    def generateAroundMesh( self, hull ) :
        """
        """
        x, y, _ = hull.integrate_cob()
        return self.generateAroundPoint(  x, y )

    def generateAroundHstarMesh( self, mesh ) :
        """
        """
        hull = mesh.getUnderWaterHullMesh(0)
        return self.generateAroundMesh( hull )

    def generateAroundPoint( self, x_center, y_center ) :
        return Mesh.FromPolydata( creatDiskGrid( self.r, self.dx, self.dy ), polygonHandling="triangulate" )




class FreeSurfaceCircHole(FreeSurfacesCirc):
    def generateAroundMesh( self, hull ) :
        """
        """
        x, y, _ = hull.integrate_cob()
        return createFreeSurfaceMesh( hull, self.r , self.dx, self.dy, x_center = x, y_center = y )

    def generateAroundHstarMesh( self, mesh ) :
        """
        """
        hull = Mesh(mesh.getUnderWaterHullMesh(0))
        return self.generateAroundMesh( hull )



class FreeSurfaceGridGen(FreeSurface):

    def __init__(self, r=500, nx = 50, ny = 50, forceWaterline= False):
        self.r = r
        self.nx = nx
        self.ny = ny
        self.forceWaterline = forceWaterline

    def generateAroundHstarMesh( self, mesh ) :
        """
        """
        from Snoopy.Meshing.gridgenTools import Gridgen_FSCase
        waterline = mesh.extractWaterlineCoords()[0]

        a1 = Gridgen_FSCase.Build( "test", waterline, self.r, ny = self.ny, nx = self.nx, side = +1, forceWaterline = self.forceWaterline, gridgen_path = r"H:\drsvn\gridgen-c\gridgen\gridgen.exe" )
        a1.run()
        fs1 = a1.getOutputMesh()
        a1.clean()

#        a2 = Gridgen_FSCase.Build( "test", waterline, self.r, ny = self.ny, nx = self.nx, side = -1, forceWaterline = self.forceWaterline, gridgen_path = r"H:\drsvn\gridgen-c\gridgen\gridgen.exe" )
#        a2.run()
#        fs2 = a2.getOutputMesh()
#        a2.clean()
#        fs1.append(fs2)
        return fs1



if __name__ == "__main__" :

    from Snoopy import Meshing as msh
    meshFile = r"H:\drsvn\Snoopy\Meshing\Tests\mesh_data\tank.hst"
    h = msh.HydroStarMesh(meshFile, keepSym = False)

#    a = FreeSurfaceRectPlain(x=500, y = 200)
#    fsMesh = a.generateAroundHstarMesh(h)
#
#    a = FreeSurfaceCircPlain(r=200, dx= 10, dy = 5)
#    fsMesh = a.generateAroundHstarMesh(h)
#    fsMesh.vtkView()

    a = FreeSurfaceGridGen(r=400, nx= 40, ny = 40)
    fsMesh = a.generateAroundHstarMesh(h)
    fsMesh.vtkView()





