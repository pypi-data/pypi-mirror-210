import os
import logging
import numpy as np
import pandas as pd
from vtk.util import numpy_support
from Snoopy import Geometry as geo
from Snoopy import logger
import _Meshing


class Mesh(_Meshing.Mesh):
    @property
    def nbpanels(self):
        return len(self.quads) + len(self.tris)

    @property
    def nbtris(self):
        return len(self.tris)

    @property
    def nbquads(self):
        return len(self.quads)

    @property
    def nbnodes(self):
        return len(self.nodes)


    @property
    def hasPanelData(self):
        return self.getPanelsData().shape[1] > 0

    def getDataRange(self) :
        if self.hasPanelData:
            return np.min(self.getPanelsData()), np.max(self.getPanelsData())
        else :
            return [np.nan , np.nan]


    def getMetaDataDF(self):
        
        return pd.DataFrame(data = 
                    {"frequency"    : self.getDataFreqs(),
                     "heading"      : self.getDataHeads(),
                     "data_name"    : self.getDataNames(),
                     "data_type"    : self.getDataTypes()})



    def appendPanelsData(self , data, dataName, dataType = 0, dataFreq= np.nan, dataHead = np.nan) :
        """Append panel data, inplace
        
        Parameters
        ----------
        data : np.ndarray
            The data to add  (n_panels)
        dataName : str 
            Name of the field
        dataType : TYPE, optional
            DESCRIPTION. The default is 0.
        dataFreq : TYPE, optional
            DESCRIPTION. The default is np.nan.
        dataHead : TYPE, optional
            DESCRIPTION. The default is np.nan.
        """
        
        if len(self.getDataNames()) == 0 :
            self.setPanelsData( panelsData = data[: , np.newaxis] ,
                                dataNames = [dataName],
                                dataTypes = [dataType],
                                dataFreqs = [dataFreq],
                                dataHeads = [dataHead],
                              )
        else : 
            self.setPanelsData( panelsData = np.append(  self.getPanelsData() , data[: , np.newaxis], axis = 1 ) ,
                                dataNames = self.getDataNames() + [dataName],
                                dataTypes = np.append( self.getDataTypes() , dataType),
                                dataFreqs = np.append( self.getDataFreqs() , dataFreq),
                                dataHeads = np.append( self.getDataHeads() , dataHead),
                               )


    def get_radiation_coef(self):
        return self.integrate_fields_xarray("PRESSURE_RAD",
                                            dimension   = ["heading" , "frequency","mode_j"])

    def get_excitation_force(self):
        all_data_names = self.getDataNames()
        if "PRESSURE_EXC" in  all_data_names:
            force =  self.integrate_fields_xarray("PRESSURE_EXC", dimension   = ["heading" , "frequency"])
        elif ("PRESSURE_DIF" in all_data_names) and ("PRESSURE_INC" in all_data_names): 
            force = self.integrate_fields_xarray("PRESSURE_DIF", dimension   = ["heading" , "frequency"]) 
            force += self.integrate_fields_xarray("PRESSURE_INC", dimension   = ["heading" , "frequency"])
        else:
            raise ValueError("Can't find excitation force stored! Either 'PRESSURE_EXC' "+
                             "or both 'PRESSURE_DIF' and 'PRESSURE_INC' must be present!")
        return force

    def get_froude_krylov_force(self):
        return self.integrate_fields_xarray("PRESSURE_INC",
                                            dimension   = ["heading" , "frequency"])

    def get_diffraction_force(self):
        return self.integrate_fields_xarray("PRESSURE_DIF",
                                            dimension   = ["heading" , "frequency"])



    def integrate_fields_xarray(self,data_name,
                                dimension   = ["heading" , "frequency","mode_j"],
                                is_real     = False   ):
        """Integrate fields with generalized normal, and return integrated coefficient as xarray.DataArray.
        
        This can be used to get hydrodynamic coefficients (added-mass, wave-damping and excitation forces) from decomposed pressure. The metadata are used to reshape and determine the coordinates of the DataArray.
        
        Parameters
        ----------
        data_name : str
            keep only line which have data_name match this value 

        dimension : list, optional
            Reshape the integrated value in to the given dimension 
            Attention after integration, there will be another dimension added (corresponding to the 6 values of the generalized normals).

        is_real : boolean, optional
            Expect real data or complex data, by default we chose complex. 
            is_real == True: real data
            is_real == False: complex data
            
            If data are considered complex, it is assumed that real and imaginary part are identified by "self.dataTypes", even number being real part and odd number the imaginary part.

        Returns
        -------
        xa_output
            xarray.Dataset
            
        Example
        -------
        
        >>> mesh.getMetaDataDF()
              frequency  heading     data_name  data_type
        0           0.1      0.0  PRESSURE_DIF          1
        1           0.1     45.0  PRESSURE_DIF          1
                ...      ...           ...        ...
        1258        1.8    180.0  PRESSURE_RAD          8
        1259        1.8    180.0  PRESSURE_RAD         10
        
        >>> mesh.integrate_fields_xarray("PRESSURE_RAD", dimension = [ "heading", "frequency", "mode_i" ])
        >>> <xarray.DataArray (heading: 5, frequency: 18, mode_i: 6, mode_j: 6)>
        array([[[[ 1.13425997e+02+1.06272362e-01j,
                  -4.21884749e-15-8.80372164e-17j,
        ...
                   3.20142135e-09-3.85625754e-10j,
                   3.89495936e+07+1.06003669e+07j]]]])
        Coordinates:
          * frequency  (frequency) float64 0.1 0.2 0.3 0.4 0.5 ... 1.4 1.5 1.6 1.7 1.8
          * heading    (heading) float64 0.0 45.0 90.0 135.0 180.0
          * mode_i     (mode_i) int32 0 1 2 3 4 5
          * mode_j     (mode_j) int64 0 1 2 3 4 5
        """

        def _data_type_to_mode_j(xarrayIn):
            final = xarrayIn.assign_coords({"data_type": np.floor(xarrayIn.data_type/2).astype(int)})
            final = final.rename({"data_type":"mode_j"})
            return final

        metadata = self.getMetaDataDF()
        data = self.getPanelsData()
        
        data_filtered = pd.DataFrame.copy(metadata.loc[metadata.data_name == data_name,:])
        index_list = data_filtered.index
        nb_data = len(index_list)

        if (nb_data==0):
            raise ValueError(f"Found no data of type {data_name} stored!")
        if self.nbpanels == 0:
            # Return zero for empty mesh
            if is_real:
                integrated_values = np.zeros((6,nb_data),dtype = float)
            else:
                integrated_values = np.zeros((6,nb_data),dtype = complex)
        else:
            integrated_values = self.integrate_fields(index_list)
        data = pd.DataFrame(integrated_values,
                            index = pd.Index( range(0,6) , name = "mode_i" ), 
                            columns = data_filtered.set_index( ["frequency" , "heading", "data_type"] ).index )
        res = data.transpose().stack().to_xarray()
        data_is_real = (res.data_type.values%2).astype(bool)
        if is_real:
            final = _data_type_to_mode_j(res[:,:,data_is_real,:])
        else:
            data_is_imag = np.logical_not(data_is_real)
            real_part = _data_type_to_mode_j(res[:,:,data_is_real,:])
            
            imag_part = _data_type_to_mode_j(res[:,:,data_is_imag,:])
            final = real_part + 1j*imag_part
            
        for dim in ["heading" , "frequency","mode_j"]:
            if dim not in dimension: # This dimension ('dim') is not present in requested dimension
                # So the data should not depend on dimension 'dim'  => Raise if have more than 1 value
                if len(final[dim]) > 1:
                    raise RuntimeError( f"Requested dimension is independant of '{dim}', "+\
                                        f"but this object stored {len(final[dim])} values  of '{dim}'")
                # Drop the dimension 'dim'
                final = final.isel({dim:0},drop = True)
        # Cosmetic, if there are no "mode_j", rename "mode_i" => "mode"
        if "mode_j" not in dimension:
            final = final.rename({"mode_i":"mode"})
            dimension.append("mode")
        else:
            # Insert mode_i before mode_j
            dimension.insert(dimension.index("mode_j"),"mode_i")
        # Rearrange as requested!
        final = final.transpose(*dimension)
        return final


    def integrate_volume_py(self, direction = 2, nbGP = 1) :
        r"""Compute and return the mesh volume.
        
        param direction : integration direction (0=>x, 1=>y, 2=>z)

        V = $\int_{M} n_x * x * ds$  (for direction=0)
        """
        if nbGP is not None :
            self.refreshGaussPoints(nbGP)
        gp = self.getGaussPoints()
        normals = self.getNormalsAtGaussPoints()
        weight = self.getGaussWiWjdetJ()
        return np.sum(gp[:,direction] * normals[:,direction] * weight)
    
    
    def integrate_waterPlaneArea(self, nbGP = 1):
        if nbGP is not None :
            self.refreshGaussPoints(nbGP)
        normals = self.getNormalsAtGaussPoints()
        weight = self.getGaussWiWjdetJ()
        return -np.sum(normals[:,2] * weight)
    
    
    def integrate_stiffness_matrix(self , output_ref_point,  
                                    ref_frame = "body-fixed",
                                    is_hull_closed = True,
                                    is_hydrostatic_equilibrium = False):
        """Integrate hydrostatic stiffness matrix.
        
        Parameters
        ----------
        output_ref_point : np.ndarray (3).
            Reference point.
            
        ref_frame : str
            "body-fixed" (translate and rotate with the ship), or "hydro" (only translate with the ship)
        
        is_hull_closed : bool, optional
            use the fact that hull is closed, to analytically remove some terms. The default is False.

        is_hydrostatic_equilibrium : bool
            If True, terms that will be balanced by gravity stiffness are removed. ([3,5] , [4,5])

        Returns
        -------
        np.ndarray(6,6)
            Hydrostatic stiffness matrix (pressure part only).
        """
        from Snoopy import Mechanics as mcn
        
        if self.nbpanels == 0:
            # Empty mesh, return zeros
            return np.zeros((6,6),dtype=float)
        
        normal_ref_point = self.getRefPoint()
                
        res = np.zeros( (6,6), dtype = float )

        normalsAtGaussPoints    = self.getNormalsAtGaussPoints()
        weight                  = self.getGaussWiWjdetJ()
        gaussPoints             = self.getGaussPoints()
        axoi =  ( gaussPoints[:,0]  - normal_ref_point[0] )
        ayoi =  ( gaussPoints[:,1]  - normal_ref_point[1] )
            
        for i in range(6):
            res[i,2] -= np.sum( weight *  normalsAtGaussPoints[:,i] )
            res[i,3] -= np.sum( ayoi*weight *  normalsAtGaussPoints[:,i] )
            res[i,4] = np.sum( axoi*weight *  normalsAtGaussPoints[:,i] )
        if ref_frame == "body-fixed" : 
            return mcn.matrans3(res, origin = normal_ref_point, destination= output_ref_point)

        elif ref_frame == "hydro" :  

            if is_hull_closed:  # If hull is closed, some terms should be 0.0
                list_mode =  [2,3,4]
                # Motion z_1, force Fx = Fy = 0, moment Mz = 0
                logger.debug(f'Term 0,2 and 1,2 and 5,2 should be zero: {res[0,2]} , {res[1,2]} and  {res[5,2]}')
                res[0,2] = 0.
                res[1,2] = 0.
                res[5,2] = 0.

                # Motion theta_x, Fx =  0, M_y = 0
                logger.debug(f'Term 0-3 and 4-3 should be zero: {res[0,3]} and {res[4,3]}')
                res[0,3] = 0.
                res[4,3] = 0
                
                # Motion theta_y, Fy  = 0, M_x = 0
                logger.debug(f'Term 1-4 and 3-4 should be zero: {res[1,4]} and {res[3,4]}')

                res[1,4] = 0.
                res[3,4] = 0.
            else:
                list_mode = range(6)

            # Need to add another term because of rotating frame
            res2 = np.zeros( (6,6), dtype = float )                
            vec = np.zeros( (6,), dtype = float )

            for i in list_mode:
                vec[i] = -np.sum( gaussPoints[:,2]*weight *  normalsAtGaussPoints[:,i] ) 
            def _vect_to_mat(vec):
                mat = np.zeros((3,3), dtype = vec.dtype)
                mat[0,1] = vec[2]
                mat[0,2] = - vec[1]
                mat[1,0] = - vec[2]
                mat[1,2] = vec[0]
                mat[2,0] = vec[1]
                mat[2,1] = -vec[0]
                return mat

            res2[:3,3:] = _vect_to_mat(vec[:3])
            res2[3:,3:] = _vect_to_mat(vec[3:])

            res_total = res + res2

            if is_hull_closed:
                logger.debug(f'Balance in hydrostatic in body-fixed reference frame of term 1 3: {res2[1,3]} vs {res[1,3]} ')
                logger.debug(f'Balance in hydrostatic in body-fixed reference frame of term 0 4: {res2[0,4]} vs {res[0,4]} ')
                logger.debug(f'Balance in hydrostatic in body-fixed reference frame of term 5 3: {res2[5,3]} vs {res[5,3]} ')

                res_total[1,3] = 0
                res_total[0,4] = 0
                res_total[5,3] = 0

            if is_hydrostatic_equilibrium:
                # In hydrostatic equilibrium, CoB and CoG are aligned vertically, 
                # so the terms (3,5) and (4,5) are canceled in both hydrostatic and gravity:
                # But we can only take off these terms if ref_point = CoB or ref_point = CoG
                # The gravity stiffness has then to be calculated consistently!
                cob =self.integrate_cob()
                res_total = mcn.matrans3(res_total, origin = normal_ref_point, destination= cob)
                logger.debug(f'Hydrostatic term (3,5) and (4,5) are balanced with gravity: {res_total[3,5]} and {res_total[4,5]}')

                res_total[3,5] = 0.
                res_total[4,5] = 0.
                res_total = mcn.matrans3(res_total, origin = cob, destination = output_ref_point)
            else: 
                res_total = mcn.matrans3(res_total, origin = normal_ref_point, destination = output_ref_point)

            return res_total
        else :
            raise(Exception("ref_frame {ref_frame:} not recognized"))



    def integrate_cob_py(self, nbGP = 1):
        """Compute and return the center of buoyancy (Assuming closed hull, with free-surface at z=0)
        """
        if nbGP is not None :
            self.refreshGaussPoints(nbGP)

        volume = self.integrate_volume(nbGP =nbGP)
        gp = self.getGaussPoints()
        normals = self.getNormalsAtGaussPoints()
        weight = self.getGaussWiWjdetJ()
        x = np.sum(gp[:,2] * normals[:,2] * gp[:,0] * weight)
        y = np.sum(gp[:,2] * normals[:,2] * gp[:,1] * weight)
        z = np.sum(0.5*(gp[:,0] * normals[:,0] + gp[:,1] * normals[:,1]) * gp[:,2] * weight)
        return np.array([x,y,z]) / volume
    
    def integrate_waterPlaneCenter(self, nbGP = 1):
        Sw = self.integrate_waterPlaneArea(nbGP = nbGP)
        Aw = np.zeros(3,dtype='float')
        
        if nbGP is not None :
            self.refreshGaussPoints(nbGP)
        gp = self.getGaussPoints()
        normals = self.getNormalsAtGaussPoints()
        weight = self.getGaussWiWjdetJ()
        
        Aw[0:2] = -np.sum(gp[:,0:2] * (normals[:,2] * weight).reshape(-1,1), axis=0) / Sw
        
        return Aw
    

    def write(self, filename, *args, **kwargs):

        p = os.path.dirname(filename)
        if p and not os.path.exists( p ) :
            os.makedirs( p )

        if os.path.splitext(filename)[-1] in [".hst",".hs0"] :
            self.writeHydroStar(filename, *args, **kwargs)
        else :
            _Meshing.Mesh.write(self, filename, *args, **kwargs)


    
    def write_vtk_hdf(self, filename):
        """Write to HDF vtk format

        Parameters
        ----------
        filename : str
            Filename.
        """

        from .vtkTools import write_vtkUnstructuredGrid_vtkhdf
        write_vtkUnstructuredGrid_vtkhdf(self.toVtkUnstructuredGrid(),filename)


    @staticmethod
    def _read_with_vtk( filename , reader, read_all_vector = False, read_all_scalar = False, **kwargs):
        r = reader()
        r.SetFileName(filename)
        if read_all_vector:
            r.ReadAllVectorsOn()
        if read_all_scalar:
            r.ReadAllScalarsOn()
        r.Update()
        return Mesh.FromPolydata( r.GetOutput(),**kwargs )
    

    @classmethod
    def ReadVtu(cls, filename, polygonHandling = "raise", BV_convention = False):
        """Read .vtu files

        Parameters
        ----------
        filename : str
            Filename

        Returns
        -------
        msh.Mesh
            Read mesh
        """
        import vtk
        return cls._read_with_vtk(  filename , 
                                    reader = vtk.vtkXMLUnstructuredGridReader, 
                                    polygonHandling  = polygonHandling,
                                    BV_convention = BV_convention)
    
    @classmethod
    def ReadVTK(cls,filename, polygonHandling = "raise", BV_convention = False ):
        from vtk import vtkUnstructuredGridReader 
        return cls._read_with_vtk(filename, vtkUnstructuredGridReader, 
                                polygonHandling = polygonHandling,
                                read_all_vector = True, read_all_scalar = True,
                                BV_convention = BV_convention)


    @classmethod
    def ReadHdf(cls, filename, polygonHandling = "raise", BV_convention = True):
        """Read .hdf files

        Parameters
        ----------
        filename : str
            Filename

        Returns
        -------
        msh.Mesh
            Read mesh
        """
        import vtk
        
        if not os.path.exists(filename):
            raise(Exception(f"{filename:} does not exists"))

        obj = cls._read_with_vtk(  filename , reader = vtk.vtkHDFReader, 
                                    polygonHandling = polygonHandling,
                                    BV_convention    = BV_convention)
                                    
        # ATTENTION: ref_position is at CoB
        obj.setRefPoint(obj.integrate_cob())
        return obj
       


    def writeHydroStar(self, filename, panelType=1):
        """Write to HydroStar format.

        Parameters
        ----------
        filename : str
            The file name
        panelType : TYPE, optional
            PANEL_TYPE. The default is 1 (the panels have an "id").      
        """

        s_nodes = ""
        for i, n in enumerate(self.nodes) :
            s_nodes += "{:} {:.5e} {:.5e} {:.5e}\n" .format( i+1 , *n)

        def output_str(s_panels, ipanel, n_off):
            if panelType == 0: s_panels += ("{:5d}" *(len(n_off)-1) +"{:5d}").format(*n_off)
            else: s_panels += ("{:5d} " *len(n_off) +"{:5d}").format(ipanel, *n_off)
            if self.hasPanelsData():
                pd_ = self.getPanelsData()
                if len(n_off) == 3:
                    s_panels += " {:5d}".format(n_off[-1])
                s_panels += (" {:18.11f}"*pd_.shape[1]).format(*pd_[ipanel -1,:])
            s_panels += "\n"
            return s_panels
        s_panels = ""
        ipanel = 1
        for n in self.tris :
            n_off = n + 1
            #if panelType == 0: s_panels += "{} {} {}\n".format( *n_off )
            #else:  s_panels += "{} {} {} {}\n".format( ipanel, *n_off )
            s_panels = output_str(s_panels, ipanel, n_off)
            ipanel += 1
        for n in self.quads :
            n_off = n + 1
            #if panelType == 0: s_panels += "{} {} {} {}\n".format( *n_off )
            #else: s_panels += "{} {} {} {} {}\n".format( ipanel, *n_off )
            s_panels = output_str(s_panels, ipanel, n_off)
            ipanel += 1


        with open(filename, "w") as f :
            f.write( "NUMPANEL 1 1 {}\n".format(self.nbpanels))
            if hasattr(self, 'sym'):
                if self.sym == _Meshing.SymmetryTypes.XZ_PLANE:
                    f.write("SYMMETRY 1 1\n")
                elif self.sym == _Meshing.SymmetryTypes.NONE:
                    pass    # symmetry 0, no need to write
                else:
                    f.write(f"Given symmetry: {self.sym} is not taken into account yet.")
            f.write( "COORDINATES\n{:}ENDCOORDINATES\n".format(s_nodes) )
            if panelType == 0: f.write( "PANEL TYPE 0\n{:}ENDPANEL\n".format(s_panels))
            else: f.write( "PANEL TYPE 1\n{:}ENDPANEL\n".format(s_panels))
            f.write( "ENDFILE")


    def writeMsh( self, filename  ):
        """Write to msh (Moloh)."""

        s_nodes = ""
        for i, n in enumerate(self.nodes) :
            s_nodes += "{:} {:.5e} {:.5e} {:.5e}\n" .format( i+1 , *n)


        s_panels = ""
        ipanel = 1
        for n in self.quads :
            n_off = n + 1
            s_panels += "{} {} {} {} {} 1 0\n".format( ipanel, *n_off )
            ipanel += 1

        for n in self.tris :
            n_off = n + 1
            s_panels += "{} {} {} {} {} 1 0\n".format( ipanel, *n_off, n_off[-1] )
            ipanel += 1

        with open(filename, "w") as f :
            f.write( "NODES\n{:}ENDNODES\n".format(s_nodes) )
            f.write( "PANELS\n{:}ENDPANELS\n".format(s_panels))
            f.write( "GROUPS\n1 Hull\nENDGROUPS")

        return



    def getCb(self):
        dims = [ a[1]-a[0] for a in self.getBounds() ]
        return self.integrate_volume() / np.prod( dims )


    def __str__(self) :
        """
        """

        if self.nbnodes == 0 :
            return "Empty mesh"

        s = """
#------- Mesh object ------------------------#
Number of nodes  : {:}
Number of panels : {:}  ({:} QUAD and {:} TRIS)
Length      : {:.1f}
Beam        : {:.1f}
Draft/Depth : {:.1f}
Volume      : {:.1f}
Bounds : x=[{:8.2f},{:8.2f}]
         y=[{:8.2f},{:8.2f}]
         z=[{:8.2f},{:8.2f}]
#--------------------------------------------#"""
        return s.format( self.nbnodes, self.nbpanels, self.nbquads, self.nbtris,
                         self.getBounds()[0][1] - self.getBounds()[0][0],
                         self.getBounds()[1][1] - self.getBounds()[1][0],
                         self.getBounds()[2][1] - self.getBounds()[2][0],
                         self.integrate_volume(),
                         *[item for sublist in self.getBounds() for item in sublist] )


    def getBounds(self) :
        return [(np.min(self.nodes[:,0]), np.max(self.nodes[:,0])) ,
                (np.min(self.nodes[:,1]), np.max(self.nodes[:,1])) ,
                (np.min(self.nodes[:,2]), np.max(self.nodes[:,2])) ]



    def rotateAxis( self, axis=[0.,1.,0.], angle=0. ):
        """ Rotate a mesh around axis given by vector (angle in radians)

        """
        if angle != 0.:
            v = geo.Vector(axis)
            v.normalise()
            rmat = np.transpose(geo.AxisAndAngle(v,angle).getMatrix())

            self.setVertices( np.matmul(self.getVertices(),rmat) )

    def rotateZYX( self, center=[0.,0.,0.], angle=[0.,0.,0.] ):
        """ Rotate a mesh around center with Euler angles [roll, pitch, yaw] (angle in radians)

        """
        if any(angle) != 0.:
            rmat = geo.EulerAngles_XYZ_e(*angle).getMatrix()

            #Apply rotation around center : V' = [rmat]*[V-center] + center
            self.offset([-1.*i for i in center])
            self.setVertices( np.transpose(np.matmul(rmat,np.transpose(self.getVertices()))) )
            self.offset(center)

    def convertToVtk(mesh, offset=(0., 0., 0.), format = "vtkPolyData"):
        """Copy mesh to vtk polydata structure.
        
        Possible performance improvement : Set all at once using vtk.util.numpy_support ?
        """
        import vtk

        if format == "vtkPolyData":
            vtkdata = vtk.vtkPolyData()
            cells = vtk.vtkCellArray()
            vtkdata.SetPolys(cells)
        elif format == "vtkUnstructuredGrid":
            vtkdata = vtk.vtkUnstructuredGrid()
        else:
            raise NotImplementedError(f"Format {format} is not supported. Only vtkPolyData or vtkUnstructuredGrid for now!")

        # Fill up points 
        points = vtk.vtkPoints()
        for xyz in mesh.nodes:
            points.InsertNextPoint( xyz + offset)
        vtkdata.SetPoints(points)

        # Fill up cells
        for panel in mesh.tris :
            vtkdata.InsertNextCell( vtk.VTK_TRIANGLE, 3, panel  )
        for panel in mesh.quads :
            vtkdata.InsertNextCell( vtk.VTK_QUAD, 4, panel  )


        if mesh.hasPanelsData():
            from .hydro_names import get_full_dataname_metadata
            panelsData      = mesh.getPanelsData()
            panelsMetaData  = mesh.getMetaDataDF()
            all_full_name = get_full_dataname_metadata(panelsMetaData)
            

            for index,full_name in enumerate(all_full_name):
                scalar = numpy_support.numpy_to_vtk(panelsData[:,index])
                scalar.SetName(full_name)
                vtkdata.GetCellData().AddArray( scalar )
            
            for colname in panelsMetaData:
                col = panelsMetaData[colname]
                if "name" in colname:
                    array = vtk.vtkStringArray()
                    for item in col:
                        array.InsertNextValue(item)
                    array.SetName(colname)
                else:
                    array = numpy_support.numpy_to_vtk(col.to_numpy())
                    array.SetName(colname)
                vtkdata.GetFieldData().AddArray(array)

        return vtkdata

    def toVtkPolyData(self, offset=(0., 0., 0.)):
        return self.convertToVtk(offset,format = "vtkPolyData")

    def toVtkUnstructuredGrid(self,offset=(0., 0., 0.)):
        obj = self.convertToVtk(offset=offset,format = "vtkUnstructuredGrid")
        return obj


    def vtkView(self, *args, **kwargs) :
        """ Display mesh with vtk
        """
        from .vtkView import viewPolyData
        viewPolyData(self.toVtkPolyData(), *args, **kwargs)

    def toImage(self, outputFile, **kwargs):
        from .vtkView import polydataPicture
        polydataPicture(self.toVtkPolyData(), outputFile = outputFile, **kwargs)


    @classmethod
    def FromPolydata(cls, polydata, polygonHandling = "raise", BV_convention = True):
        """Create Snoopy Mesh from vtk polydata."""
        import vtk
        from vtk.util import numpy_support
        points = polydata.GetPoints()

        etris = np.zeros( (0,3), dtype = int)
        equads = np.zeros( (0,4), dtype = int)

        if points is None :
            return cls( Vertices = np.zeros( (0,3), dtype = float ), Tris = etris, Quads = equads  )
        elif polydata.GetPoints().GetNumberOfPoints() == 0:
            return cls( Vertices = np.zeros( (0,3), dtype = float ), Tris = etris, Quads = equads  )

        all_cell_data = polydata.GetCellData()
        nb_data = all_cell_data.GetNumberOfArrays()

        nodes = numpy_support.vtk_to_numpy(  points.GetData() )

        # Get cell data
        idList = vtk.vtkIdList()
        quads = []
        tris = []
        notHandled = []
        # Stored index as numeric to filter later

        quadIds = []
        triIds  = [] 
        for ipanel in range(polydata.GetNumberOfCells()):
            polydata.GetCellPoints(ipanel, idList)

            nNodes = idList.GetNumberOfIds()

            nodesId = [idList.GetId(i) for i in range(nNodes)]

            if nNodes == 4:
                quads.append( nodesId )
                quadIds.append(ipanel)
            elif nNodes == 3:
                tris.append( nodesId )
                triIds.append(ipanel)
            elif polygonHandling == "raise":
                raise RuntimeError("Encounter polygons, the conversion to snoopy mesh object might have trouble")
            elif polygonHandling == "triangulate" :  # Polygon, to be triangulated
                if nb_data > 0:
                    logger.warning("Encounter polygons, the conversion to snoopy mesh object might have trouble, panelsData will be wrong")
                nodesId = np.array(nodesId)
                notHandled.append( ipanel )
                triangleIds = vtk.vtkIdList()
                polydata.GetCell(ipanel).Triangulate(triangleIds)
                for itri in range( triangleIds.GetNumberOfIds() // 3 ):
                    subId = [ triangleIds.GetId( itri*3 + 0 ), triangleIds.GetId( itri*3 + 1 ), triangleIds.GetId( itri*3 + 2 ) ]
                    tris.append( nodesId[subId] )

        if len(tris) == 0:
            tris = etris
        else :
            tris = np.array(tris, dtype = int)

        if len(quads) == 0:
            quads = equads
        else :
            quads = np.array(quads, dtype = int)

        #----- Handle cells data. First Tris, then Quads
        metadata = {}
        
        flatten_cell_data = []
        data_name_list = []
        for i in range(nb_data) : 
            extracted_array = all_cell_data.GetArray(i)
            array = numpy_support.vtk_to_numpy (extracted_array)
            
            if len(array.shape) == 1:
                flatten_cell_data.append(array)
                data_name_list.append(extracted_array.GetName())
            elif len(array.shape) == 2:
                for ii in range(array.shape[1]):
                    flatten_cell_data.append(array[:,ii])
                    data_name_list.append(extracted_array.GetName()+f"_{ii}")
                
            else:
                raise NotImplementedError("This routine is not yet ready to read multidimensioned array")


        nb_flatten_cell_data = len(flatten_cell_data)
        panel_data = np.zeros( ( len(tris) + len(quads), nb_flatten_cell_data ) )
        for iarray, array  in enumerate(flatten_cell_data):
            panel_data[: , iarray] = np.concatenate([array[triIds],array[quadIds]])
        

        if BV_convention:
            allFieldData = polydata.GetFieldData()
            nbFieldData = allFieldData.GetNumberOfArrays()
            for ifield in range(nbFieldData):
                field = allFieldData.GetAbstractArray(ifield)
                fieldname = field.GetName()
                if fieldname == "data_name":
                    data_name = []
                    for ii in range(field.GetNumberOfValues()):
                        data_name.append(field.GetValue(ii))
                    metadata["dataNames"] = data_name
                elif fieldname == "data_type":
                    metadata["dataTypes"] = numpy_support.vtk_to_numpy(field)
                elif fieldname == "frequency":
                    metadata["dataFreqs"] = numpy_support.vtk_to_numpy(field)
                elif fieldname == "heading":
                    metadata["dataHeads"] = numpy_support.vtk_to_numpy(field)
            obj = cls( Vertices = nodes, Tris = tris, Quads = quads, panelsData = panel_data  )
            if len(metadata.keys()) == 4:
                obj.setPanelsMetadata(**metadata)

        else:
            if nb_flatten_cell_data > 1:
                obj = cls( Vertices = nodes, Tris = tris, Quads = quads, panelsData = panel_data  )
                obj.setDataNames(data_name_list)
            else:
                obj = cls( Vertices = nodes, Tris = tris, Quads = quads )
        return obj

            

        





    def extractWaterLineSegments(self, eps=1e-4):
        #Extract all segments
        seg = self.getSegments()

        #Segments at z=0
        zSeg = np.max( np.abs(self.nodes[:,2][seg]) , axis = 1)
        waterline = seg[ np.where( zSeg < eps )[0]]
        return waterline



    def checkTightWaterlines( self , waterline ) :
        """


        Parameters
        ----------
        waterline : np.ndarray
            Waterline segments (nodes connectivity)

        Returns
        -------
        bool
            True if waterline is closed.

        """

        wl = waterline.flatten()
        unique, counts = np.unique(wl, return_counts=True)

        id_free = np.where( counts != 2 )
        if len (id_free[0]) == 0 :
            return True
        else :
            logger.debug( self.nodes[ unique[id_free] ]  )
            return False



    def extractWaterLineLoops(self, eps=1e-4):
        """ Regroup waterline per loops


        Parameters
        ----------
        eps : TYPE, optional
            DESCRIPTION. The default is 1e-4.

        Returns
        -------
        list_loop : list
            List of waterline closed loops

        """
        waterline = self.extractWaterLineSegments(eps)

        if not self.checkTightWaterlines(waterline) :
            raise(Exception( "Can not clear waterplane, waterline is not closed" ))

        logger.debug( f"{len(waterline):} waterline segments extracted" )

        #Check loops are closed :
        if not (np.sort( waterline[:,0] ) == np.sort( waterline[:,1] )).all():
            logger.info( "Waterline is not closed" )
            return []

        #TO DO : optimize (with sorting ?)
        done = []
        list_loop = []
        while len(done) != len(waterline):
            for iSegNotDone in range(len(waterline)) :
                if iSegNotDone not in done :
                    break
            loop = [ waterline[ iSegNotDone  ] ]
            done.append(iSegNotDone)
            while loop[0][0] != loop[-1][1] :
                ic = np.where( waterline[:,0] == loop[-1][1] )[0][0]
                loop.append( waterline[ic] )
                done.append(ic)
            list_loop.append(loop)
        return list_loop


    def extractWaterline(self, eps = 1e-4):
        """ Extract waterline from hull mesh.
        Return array of node ids.
        """

        waterline = self.extractWaterLineSegments(eps)


        orderWaterLine = np.empty( waterline.shape, dtype = int )
        if self.sym == _Meshing.SymmetryTypes.NONE:
            #Ensure continous contour
            startSeg = 0
            orderWaterLine[0,:] = waterline[startSeg,:]
            for i in range(1, len(waterline) ) :
                ic_ = np.where( waterline[:,0] == orderWaterLine[i-1,1] )[0]
                if len(ic_) == 0:
                    raise Exception("ERROR: Something wrong with the waterline. It is not continuous!")
                ic = ic_[0]
                orderWaterLine[i,:] = waterline[ic,:]

            #Start from aft central point
            symPlane = np.where( np.abs(self.nodes[ orderWaterLine[:,0], 1 ]) < eps )[0]
            if len(symPlane) > 0:
                startNode = orderWaterLine[symPlane[ np.argmax(  self.nodes[orderWaterLine[symPlane,0], 0]  ) ],0]
                orderWaterLine = np.roll( orderWaterLine, -np.where(orderWaterLine[:,0] == startNode)[0][0] , axis = 0)
        else:
            # Here, waterline is for a mesh with symmetry 1 or 2. It means
            # that the waterline is not closed. In this case, by starting from the very
            # first segment we will obtain only 1 chunk, which may not be the full waterline
            nSegments = waterline.shape[0]
            # for each segment on the waterline we may find the previous (if exist) and the next
            # if exist connected segment(s)
            # segments: array of the previous and the next segments
            # since segment's number is non-negative, -1 means that it does not have
            # previous or/and next segment
            segments = -np.ones( (nSegments, 2), dtype = int )
            # loop for all segments
            for i in range(nSegments):
                # does segment[i] has predecessor?
                if segments[i, 0] < 0:  # it is not defined yet
                    ic_ = np.where( waterline[:,1] == waterline[i,0] )[0]
                    if len(ic_) > 0:
                        ic = ic_[0]
                        segments[ i, 0] = ic    # if segment[i] has predecessor segment[ic]
                        segments[ic, 1] = i     # then segment[ic] has successor segment[i]
                # does segment[i] has successor?
                if segments[i, 1] < 0:  # if it not defined yet
                    ic_ = np.where( waterline[:,0] == waterline[i,1] )[0]
                    if len(ic_) > 0:
                        ic = ic_[0]
                        segments[ i, 1] = ic    # if segment[i] has successor segment[ic]
                        segments[ic, 0] = i     # then segment[ic] has predecessor segment[i]
            for i in range(nSegments):
                logger.debug(f"segment {i:} with nodes {waterline[i,:]:} => {segments[i, 0]:} <- {i:} <= {segments[i, 1]:}")
            # Connecting the segments to the chains
            orderedChains = []                                      # list of all chains (chunks)
            orderedChain = -np.empty( (nSegments), dtype = int )    # the very first chain
            orderedChainCount = 0                                   # number of segments in the chain
            # for all segments, search a segment, which does not have predecessor
            for i in range(nSegments):
                if segments[i, 0] >= 0: continue    # segment has 'parent' (predecessor)
                # segment does not have a parent
                orderedChain[orderedChainCount] = i                 # this segment becomes the first in the chain
                orderedChainCount += 1                              # number of segments is 1
                nextSegment = segments[i, 1]                        # successor of the segment[i]
                while nextSegment >= 0:                             # while the segment has successor
                    orderedChain[orderedChainCount] = nextSegment   # add this segment to the chain
                    orderedChainCount += 1                          # increase number of segments in the chain by 1
                    nextSegment = segments[nextSegment, 1]          # and define its successor
                # At this stage, we collected all segments for the current chunk
                # and chained them
                orderedChains.append( (orderedChain, orderedChainCount) )   # add the chain to the list of chains
                orderedChain = -np.empty( nSegments, dtype = int )          # create a new chain
                orderedChainCount = 0                                       # and set its count to be 0 => no any segments in the chain
            # logger.debug
            if logger.getEffectiveLevel() <= logging.DEBUG:
                for oc in orderedChains:
                    logger.debug(f"{oc[0][0:oc[1]]:} has {oc[1]:} segments")
            # At this point, orederedChains consists of all chunks of the waterline
            # Normally, orderedChains should have only 1 chain which corresponds to the full waterline
            # in case there are more than 1 chains, the error will be raised
            # but the following block is still create other waterline chunks in order
            # to see what is wrong during the debug.
            for ioc, oc_ in enumerate(orderedChains):
                oc  = oc_[0]    # oc = (chain,
                noc = oc_[1]    #       count)
                orderWaterLine_ = -np.empty( (noc, waterline.shape[1]), dtype = int )
                for i in range(noc):
                    orderWaterLine_[i,:] = waterline[oc[i],:]
                if ioc == 0: orderWaterLine = orderWaterLine_.copy()    # only for the first chunk we keep data
                # logger.debug
                if logger.getEffectiveLevel() <= logging.DEBUG:
                    for i in range(noc):
                        if i != 0: s +=f" -> "
                        else: s = "  "
                        s += f"{orderWaterLine_[i, :]:}"
                    logger.debug(s)
            # Here is the check whether we obtain more than 1 chunks (waterline consists of 2 non connected chunks)
            if len(orderedChains) > 1:
                logger.critical(f"ERROR: For a symmetric case found more than 1 chunks of the waterline")
                if logger.getEffectiveLevel() > logging.DEBUG:
                    logger.critical("Set DEBUG logger level for more details")
                quit()

        return orderWaterLine


    def extractWaterlineCoords(self, eps = 1e-4):
        """ Return waterline, as table of coordinates xyz
        """
        nodesId = self.extractWaterline(eps=eps)
        # to keep the compatibility with the previous code:
        # if the waterline is closed => sym = 0 we will not duplicate the latest point
        if nodesId[-1,1] == nodesId[0, 0]:
            return self.nodes[ nodesId[:,0] ]
        # otherwise add the end point
        return self.nodes[ np.append(nodesId[:,0], nodesId[-1,1]) ]


    def getWaterlineBound( self ):
        """Return waterline bounds
        """

        nodes = self.extractWaterlineCoords()

        return [ (np.min( nodes[:,0] ), np.max( nodes[:,0])   ),
                 (np.min( nodes[:,1] ), np.max( nodes[:,1] )  ),
                 (np.min( nodes[:,2] ), np.max( nodes[:,2] )  )]



    def plotWaterline(self, ax=None, eps = 1e-4, **kwargs):
        from matplotlib import pyplot as plt
        if ax is None :
            fig, ax = plt.subplots()

        orderWaterLine = self.extractWaterline(eps = eps)
        ax.plot( self.nodes[ orderWaterLine.flatten() , 0 ], self.nodes[ orderWaterLine.flatten() , 1 ], "-", **kwargs )
        return ax

    def plotWaterlineLoops(self, ax=None, eps = 1e-4, **kwargs):
        from matplotlib import pyplot as plt
        if ax is None :
            fig, ax = plt.subplots()
        loops = self.extractWaterLineLoops()
        for loop in loops :
            for seg in loop:
                ax.plot( self.nodes[seg][:,0], self.nodes[seg][:,1], "-" )
        return ax


    def plot2D(self, *args, **kwargs):
        """Plot surface mesh (z coordinates ignored) with matplotlib
        """
        from Snoopy.PyplotTools import plotMesh
        return plotMesh( self.nodes, self.quads, self.tris, *args, **kwargs)


    def getCutMesh(self,*args,**kwargs):
        m = Mesh(super().getCutMesh(*args,**kwargs))
        if m.getNPanels()>0 : 
            m.setRefPoint(self.getRefPoint())
        return m
    


#Make C++ wrapped function return the python subclass. Warning : Make a copy
for method in ["getCutMesh"]:
    def makeFun(method):
        fun = getattr(_Meshing.Mesh, method)
        def newFun(*args,**kwargs) :
            return Mesh(fun(*args, **kwargs))
        newFun.__doc__ = fun.__doc__
        return newFun
    setattr(Mesh, method+"Copy", makeFun(method))




