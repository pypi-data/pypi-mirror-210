import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
from Snoopy.Mechanics import matrans3,vectran3
from Snoopy import Spectral as sp
from Snoopy import logger
from Snoopy.Reader.input_mcn_parser import parse_input_mcn


def _get_hydro_data():

    content_df = pd.read_csv( f"{os.path.dirname(os.path.abspath(__file__)):}/hydro_data.csv" , index_col = 0  )
    content_df["TYPE"] = pd.Categorical(content_df["TYPE"], ["attribute", "coordinate", "variable"])
    return content_df.sort_values("TYPE")


@xr.register_dataset_accessor("hydro")
class HydroCoef():
    """Class to handle the hydrodynamic coefficients. 
    
    We store everithing in xarray Dataset, with the following addition : 
        - mandatory convention (not an convention anymore...)
        - Manipulation specific to the fact that we deal with hydrodynamic coefficient

    Note
    ----
    All quantities are expressed at the "ref_point". 
    """
    
    KIND = None
    

    
    # The dataframe that contains the "convention" of the different field names and shape
    content_df = _get_hydro_data()

    def __init__(self, data):
        self._data = data


    @staticmethod
    def coordinate_helpers( nb_body = 1):
        def_coords = { "mode_i" : np.arange(1,7) ,
                       "mode_j" : np.arange(1,7) ,
                       "mode" : np.arange(1,7) ,
                       "body" : np.arange(1,nb_body+1),
                       "body_i" : np.arange(1,nb_body+1),
                       "body_j" : np.arange(1,nb_body+1),
                       "xy":  ["x" , "y"] ,
                       "xyz": ["x" , "y", "z"] ,
                     }
        return def_coords

    def get_transposed(self):
        ds = self._data
        for var in ds.data_vars:
            if var in self.content_df.index.values:
                ds[var] = ds[var].transpose(  *TransDims(ds[var].dims).ordered_dims )
        return ds
    

    @property
    def nbbody(self):
        return self._data.attrs["nb_body"]
    
    
    @property
    def encounter_frequency(self):
        """Encounter frequency is a derived input that can be computed thank to dispersion relation.
        
        Return
        ------
        np.ndarray
           we[ nb_heading, nb_frequency] 
        """
        data = self._data
        if "frequency" in data and "heading" in data and "depth" in data.attrs:
            frequency = data.frequency
            heading   = data.heading
            depth     = data.attrs.get("depth",0.0)
            nb_head   = len(heading)
            nb_freq   = len(frequency)
            encounter_frequency = np.zeros((nb_head,nb_freq),dtype='float64')
            
            for i_freq,freq in enumerate(frequency):
                for i_head,head in enumerate(heading):
                    encounter_frequency[i_head,i_freq] = \
                            sp.w2we( freq , head*np.pi/180, self._data.attrs["speed"], depth =  depth)
            
            return xr.DataArray(data = encounter_frequency,
                                coords = [self._data.heading,self._data.frequency])
        else:
            raise RuntimeError(f"Object {self} doesn't have enough information to compute encounter frequency")

    

    @property
    def wave_length(self):
        data = self._data
        if "frequency" in data and "depth" in data:
            wl = sp.w2l(data["frequency"], depth = data["depth"]) 
            return xr.DataArray(data = wl, coords = [self._data.frequency])
        
        raise RuntimeError(f"Object {self} doesn't have enough information to compute wave length")


    def get_at_ref_point(self , ref_point) : 
        """Return the dataset expressed at another reference point.
        
        The original dataset is not modified
        
        Parameters
        ----------
        ref_point : np.ndarray(3)
            The new reference point.

        Returns
        -------
        Dataset
            The moved dataset
        """
        if self.nbbody > 1:
            raise NotImplementedError("This function can't be used to change refpoint of multibody system!")
        
        
        old_ref_point = self._data.ref_point[0,:].values
        new_ref_point = np.asarray(ref_point).reshape(3,)
        if np.allclose(old_ref_point,new_ref_point):
            return self._data
        else:
            ds = self._data.copy(True) #To be sure that original dataset is not modified. 
            logger.debug(f"Changing ref_point from {old_ref_point} to {new_ref_point}")
            for var in self.content_df.query( "TRANS in ['load_vector', 'motion_vector' , 'matrix' ]").index.values:
                if var in ds.data_vars : 
                    kind = self.content_df.loc[var, "TRANS"]
                    isMotion = "motion" in kind
                    logger.debug(f"            -> {var:} {isMotion:}")
                    
                    trans_dims = TransDims( self._data[var].dims )
                    # da = ds[var].transpose( *trans_dims.ordered_dims )

                    # Stack all dimension 
                    da = ds[var].stack( all_but_mode = trans_dims.other_dims )
                    
                    if kind == "matrix" : 
                        for i in range(da.shape[-1]) :
                            da.values[:,:,i] = matrans3(da.values[:,:,i], origin = old_ref_point, 
                                                        destination = new_ref_point)
                    elif "vector" in kind :
                        for i in range(da.shape[-1]) :
                            da.values[:,i] = vectran3(  da.values[:,i], origin = old_ref_point, 
                                                        destination = new_ref_point, isMotion = isMotion)

                    # Unstack
                    ds[var] = da.unstack().transpose( *trans_dims.original_dims )

            ds["ref_point"].values[0,:] = ref_point

            return ds


    def get_at_ref_wave(self, ref_wave):
        # TODO: implement phase shift when set to new wave reference point.
        raise NotImplementedError("Setting a new value for ref_wave is not yet implemented!")

        
    def check( self, kind = None ):
        """Check if necessary content is present, and warn for content which is not handled.

        Returns
        -------
        bool
            Return False if content is missing, True if everything is there
        """
        if kind is None:
            kind = self.KIND
        
        if kind is not None:
            m = self.missing_content(kind = kind)
            n_miss = np.sum( [len(v) for k , v in m.items()] )
            if n_miss > 0:
                logger.error( f"Missing content :\n{m:}" )
                return False

        nh = self.not_handled_content()
        if len(nh) > 0 : 
            logger.warning(f"Not handled content :\n{nh:}")
            
        return True
                
        
    def missing_content(self, kind ):
        """Check that the dataset contains the necessary information.
        
        Returns
        -------
        dict
            Missing attributes and variables
        """
        missing = {"attrs" : [] , "var" : []}
        for k in self.content_df.query( f"TYPE=='attr' and {kind:}==2" ).index.values:
            if k not in self._data.attrs.keys() : 
                missing["attrs"].append( k )
                
        for k in self.content_df.query( f"TYPE=='variable' and {kind:}==2" ).index.values:
            if k not in self._data.data_vars.keys() : 
                missing["var"].append( k )
        return missing
    
    
    def not_handled_content(self):
        """Return list of dataarray which are not handled. 
        
        Data not handled will not be process by, for instance `get_at_ref_point()`

        Returns
        -------
        list
            Not handled variables
        """

        return [k for k in self._data.data_vars if k not in self.content_df.index]

    

    def convert_to_complex(self, drop = True):
        """Convert _re and _im to complex.
        """
        ds = self._data.copy()
        for a in self._data.data_vars.keys() :
            if a[-3:] == "_re" :
                logger.debug(f"Converting {a:} and _im to complex")
                ds[a[:-3]] = self._data[ a ] + 1j * self._data[ a.replace("_re" , "_im") ]
                if drop : 
                    ds = ds.drop_vars( [a, a.replace("_re" , "_im") ] )
        return ds

    def convert_to_real(self, drop = True):
        """Convert complex to _re and _im.
        """
        ds = self._data.copy()
        for a in ds.data_vars.keys() :
            #if a in self.content_df.query("COMPLEX == True").index.values:
            data_var = ds[a]
            if np.iscomplexobj(data_var):
                logger.debug(f"Converting {a:} and _im to real and imag")
                ds[a + "_re" ] = data_var.real
                ds[a + "_im" ] = data_var.imag
                if drop : 
                    ds = ds.drop_vars( [a] )
        return ds
    
    
    @classmethod
    def read_hydrostar_v8(cls,filename):
        """Read old Hydrostar format

        Parameters
        ----------
        filename : str
            Path to hdf file

        Returns
        -------
        xarray
            Output
        """
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Can't find data file: {filename}")
        with xr.open_dataset(filename, lock = False) as f:
            ds = f.copy(deep = True)
        ds = ds.hydro.convert_hydrostar_v8()
        assert ds.hydro.check(kind = cls.KIND)
        return ds

    @classmethod
    def read(cls,filename):
        """Read standard format

        Parameters
        ----------
        filename : str
            Path to hdf file

        Returns
        -------
        xarray
            Output
        """        
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Can't find data file: {filename}")        
        with xr.open_dataset(filename, lock = False) as f:
            ds = f.copy(deep = True)
        ds = ds.hydro.convert_to_complex()
        ds = ds.hydro.get_transposed()
        assert ds.hydro.check(kind = cls.KIND)
        return ds



    def write(self,filename):
        output = self.convert_to_real()
        output.to_netcdf(filename)

    def convert_hydrostar_v8(self):
        from Snoopy.Mechanics.hydro_coef_io import hydro_coef_from_hstar_v8
        ds = hydro_coef_from_hstar_v8( self._data )
        ds = ds.hydro.convert_to_complex()
        ds = ds.hydro.get_transposed()
        return ds
    


    
    @classmethod
    def Build(cls, wave_length = None,**kwargs):
        """Construct the dataset with 'simple' inputs.
    
        Parameters
        ----------
        nb_body : int
            number of body

        cog : numpy.array or list or xarray.DataArray
            Center of gravity, dimension : [nbBody,3]

        cob : numpy.array or list or xarray.DataArray
            Center of gravity, dimension : [nbBody,3]
    
        ref_point : numpy.array or list or xarray.DataArray
            Reference point, dimension : [nbBody,3]
            Optional, default value: cog
    
        ref_wave : numpy.array or list or xarray.DataArray
            Origin of wave phase in surface, dimension : [2,],
            Optional, default = [0,(ref_point[0],ref_point[1])]
    
        heading    : numpy.array or list or xarray.DataArray
            ship heading, in degree, dimension [nb_head,]
    
        frequency  : numpy.array or list or xarray.DataArray
            frequency of problem, dimension [nb_freq,]

        speed   : float
            advancing speed [m/s]
    
        depth : float
            depth [m].
            Optional, default = 0.
            Attention, Depth = 0. mean Depth = infitity
    
        hydrostatic : numpy.array or list or xarray.DataArray
            hydrostatic stiffness total, dimension ["body","mode_i","mode_j"]
            hydrostatic = hydrostatic_hull + hydrostatic_grav
    
        base_flow_stiffness : numpy.array or list or xarray.DataArray
            stiffness caused by steady flow, dimension ["body","mode_i","mode_j"]
            Optional, default: numpy.zeros((nb_body,nb_mode,nb_mode))
    
        excitation_load : numpy.array or list or xarray.DataArray
            excitation force, dimension
            ["body","mode","heading","frequency"]
    
        added_mass : numpy.array or list or xarray.DataArray
            added mass in radiation problem, dimension
            ["body_i","body_j","mode_i","mode_j","heading","frequency"]
    
        wave_damping : numpy.array or list or xarray.DataArray
            wave damping in radiation problem, dimension
            ["body_i","body_j","mode_i","mode_j","heading","frequency"]
    
        Returns
        -------
        xr.Dataset
            The data organised in a xarray.Dataset with the coordinates set.
        """
        if "nb_body" not in kwargs:
            raise ValueError("Number of body 'nb_body' must be present")
        for key, val in cls.coordinate_helpers(  kwargs["nb_body"] ).items():
            kwargs.setdefault(key,val)



        coords = {}
        attrs = {}
        da_list = {}
        content = HydroCoef.content_df
        
        for row_name,row in content.iterrows():

            data_type = row["TYPE"]

            data_value = kwargs.pop(row_name,None)

            if data_value is not None:
                if data_type == "coordinate":    
                    coords[row_name] = data_value
                elif data_type == "attribute":
                    attrs[row_name] = data_value
                elif data_type == "variable":
                    dims = row["DEFAULT_DIMS"].split()
                    coords_data = [  (d,  coords[d] ) for d in dims ]
                    da_list[row_name] = xr.DataArray(  data = data_value , 
                                                        coords =  coords_data)

        for var, data in kwargs.items() :
            logger.info(f"{var:} is not handled but stored as an attribute")
            attrs[var] = data


        output_xa = xr.Dataset( da_list, attrs = attrs )
        assert output_xa.hydro.check(kind = cls.KIND)
        return output_xa



class RdfCoef(HydroCoef):
    """Specialization of HydroCoef for what is specific to the geometry only.
    
    No mass data. Only hydrodynamic and hydrostatic.
    """
    
    KIND = "RDF_COEF"

        


class McnCoef(HydroCoef):
    """Specialization of HydroCoef that contains RdfCoef + motion solver results
    
    """
    
    KIND = "MCN_COEF"
    
    


@xr.register_dataset_accessor("mcn")
class McnInput(HydroCoef):
    """Specialization of HydroCoef that contains only mechanical properties.

    """
    
    KIND = "MCN_INPUT"
    
    @property
    def mass(self):
        return self._data.mass_matrix.sel( mode_i = 1 , mode_j = 1).values
    

    @classmethod
    def read_mcn(cls,inputFile):
        """Read a input mcn file and produce a xr.Dataset

        Parameters
        ----------
        inputFile : str
            Path to input.mcn
        Returns
        -------
        Dataset
            THe mechanical properties stored in xr.Dataset.
        """
        return cls.Build( **parse_input_mcn(inputFile) )



    @classmethod
    def read_json(cls, inputdata):
        """Extract informations that needed to create mcn_input from HydroStarV format. 
        
        Parameters
        ----------
            inputFile : str
                path to .json file
                
        Returns
        -------
        Dataset
            THe mechanical properties stored in xr.Dataset.
        """
        raise(NotImplementedError)


    @classmethod
    def Build(cls, **kwargs):
        gyration_radius = kwargs.pop( "gyration_radius", None )

        mass = kwargs.pop("mass", None)
        mass_matrix = kwargs.get("mass_matrix" , None)
        
        if mass_matrix is  None :
            assert mass is not None , 'If mass_matrix is not present, mass must be given'
            assert gyration_radius is not None ,  'If mass_matrix is not present, mass must be given'
            nb_body = len(mass)

            mass_matrix = np.zeros((nb_body,6,6),dtype='float64')
            
            for ibody in range(nb_body):
                gyration_radius = np.asarray(gyration_radius)
                mass_matrix[ibody,:3,:3] = mass[ibody] * np.eye(3)
                mass_matrix[ibody,3:,3:] = mass[ibody] * np.diag(gyration_radius[ibody,:3]**2)
                mass_matrix[ibody,3,4:]  = mass[ibody] * gyration_radius[ibody,3:5] \
                                            * np.abs(gyration_radius[ibody,3:5])
                mass_matrix[ibody,4,5]   = mass[ibody] * gyration_radius[ibody,5]  \
                                            * np.abs(gyration_radius[ibody,5])
                # symmetrise
                mass_matrix[ibody,4:,3]  = mass_matrix[ibody,3,4:]
                mass_matrix[ibody,5,4]   = mass_matrix[ibody,4,5]
            kwargs["mass_matrix"] = mass_matrix
            
        if "ref_point" not in kwargs :
            kwargs["ref_point"] = kwargs["cog"]
            
        user_k =  kwargs.pop("user_stiffness_matrix", None)
        if user_k is None : 
            kwargs["user_stiffness_matrix"] = np.zeros( ( nb_body, nb_body, 6, 6 ), dtype = float)
        ds = super().Build( **kwargs )
        return ds
    
    

class TransDims():
    """Handle dimension ordering to be compatible with matrans routines.
    """
    
    default_order = [ ["body_i", "body_j" , "heading", "frequency", "mode_i", "mode_j" ], 
                      ["body", "mode_i", "mode_j" ], 
                      ["body", "heading", "frequency","mode" ], 
                      ["body_i", "body_j" , "mode_i", "mode_j" ],
                      ["body", "xyz" ], 
                      [ "xy" ],
                     ]

    matrans_order = [ ["mode"] ,
                      ["mode_i" ,"mode_j"] ,
                    ]
    
    @staticmethod
    def _order( dims, dims_order, check_all ):
        ordered_dims = [a for a in dims]
        for i, last in enumerate(dims_order) : 
            if np.all( [a in dims for a in last])  : 
                for a in last :
                    ordered_dims.remove(a)
                ordered_dims.extend( last )    
                return  ordered_dims, len(last)
        else:
            if check_all :
                raise(Exception(f"Do not know how to order {dims:}"))
            else :
                return ordered_dims, 0

    def __init__(self, dimension):
        self.original_dims = dimension
        self.matrans_dims, n_last = self._order( dimension, self.matrans_order, check_all=False )
        self.other_dims = self.matrans_dims[:-n_last]

    @property
    def ordered_dims(self):
        a, _ = self._order( self.original_dims, self.default_order, check_all = True )
        return a    


if __name__ == "__main__" :
    from Snoopy.Mechanics import TEST_DATA
    logger.setLevel(10)

    rdf_hdf = os.path.join(TEST_DATA,"Hydrostar","hdf","hsrdf_Wigley4.rd1.h5")
    
    mcn_hdf = os.path.join(TEST_DATA,"Hydrostar","hdf","hsmcn_Wigley4.h5")
    
    mcn_input = os.path.join(TEST_DATA,"Hydrostar", "Wigley4.mcn")
    mcn = McnInput.read_mcn( mcn_input )
    
    rdf_coef = RdfCoef.read_hydrostar_v8( rdf_hdf )  

    fig, ax = plt.subplots()
    np.abs(rdf_coef["excitation_load"]).loc[ 1, :, 150. , 5 ].plot(ax=ax, label = "original")
    moved = rdf_coef.hydro.get_at_ref_point( ref_point = [0. , 0. , 10.]  )
    
    np.abs(rdf_coef["excitation_load"]).loc[ 1, :, 150. , 5 ].plot(ax=ax , marker = "*", label = "orginal, unmodified", linestyle  = "")
    np.abs(moved["excitation_load"]).loc[ 1, :, 150. , 5 ].plot(ax=ax, marker = "+", label = "Moved")
    ax.legend()
