"""
   Contain readers for HydroStar HDF5 files
"""
import numpy as np
import xarray

from Snoopy import Spectral as sp
from Snoopy import logger
import os
def read_hsmcn_h5(file_path, kind = "Motion"):
    """Read HSmcn HDF5 output file and return list of RAOs  (list length = number of bodies)


    Parameters
    ----------
    file_path : str
        HDF file to read
    kind : str, optional
        RAO to be read, "Motion" or "Excitation". The default is "Motion".

    Returns
    -------
    raoList : list
        list of sp.Rao (one RAO with 6ddl for each body)

    """

    data = xarray.open_dataset(file_path)

    raoList = []
    for ibody in range(data.attrs["NBBODY"]) :

        if kind in ["Excitation" , "Motion"] :
            rao_data = np.transpose(data[f"{kind:}_Re"].values[:,ibody,:,:] + 1j*data[f"{kind}_Im"].values[:,ibody,:,:], axes = [1, 0, 2])

        elif kind in [ "Radiation", "Radiation_wo_inf"] :
            motion_data = np.transpose(data[f"Motion_Re"].values[:,ibody,:,:] + 1j*data[f"Motion_Im"].values[:,ibody,:,:], axes = [1, 0, 2])
            amss = data["AddedMass"].transpose(  "Heading" , "Frequency" , "Body_i" , "Body_j", "Mode_i", "Mode_j" )[ :,:,0,0,:,: ]

            if kind == "Radiation_wo_inf" :
                amssInf = data["AddedMassInf"].transpose(  "Body_i" , "Body_j", "Mode_i", "Mode_j" )[ 0,0,:,: ]


            damp = data["WaveDamping"].transpose(  "Heading" , "Frequency" , "Body_i" , "Body_j", "Mode_i", "Mode_j" )[ :,:,0,0,:,: ]
            rao_data = np.empty( motion_data.shape , dtype = "complex" )

            for ifreq in range(len( data["Frequency"] )) :
                w = data["Frequency"][ifreq]
                for ihead in range(len( data["Heading"] )) :
                    we = sp.w2we( w ,  data["Heading"][ihead] , speed = data.attrs["SPEED"] )

                    if kind == "Radiation" :
                        amss_ = amss[ ihead, ifreq, : , : ].values
                    else :
                        amss_ = amss[ ihead, ifreq, : , : ].values - amssInf.values

                    rad = -we**2 * amss_ + 1j * we * damp[ ihead, ifreq, : , : ].values
                    rao_data[ihead, ifreq] = -np.matmul(  rad , motion_data[ihead, ifreq, :]  )



        raoList.append( sp.Rao(
                  b = np.deg2rad( data.Heading.values) ,
                  w = data.Frequency.values,
                  cvalue = rao_data,
                  modes = [1,2,3,4,5,6],
                  refPoint = data.RefPoint.values[ibody],
                  waveRefPoint = data.RefWave.values,
                  depth = data.attrs["WATERDEPTH"],
                  forwardSpeed = data.attrs["SPEED"]
                  ) )

    return raoList


def read_hsprs_h5(file_path, component = "total", motionsRao = None) :
    """Read HSprs HDF5 output file and return RAOs

    Parameters
    ----------
    file_path : str
        HDF file to load.

    component : str, optional
        Type of pressure field, among ["total, "diffraction", "total_from_given_motion", "surge", "sway", "heave", "roll", "pitch", "yaw"]. The default is "total".

    motionsRao : sp.Rao, optional
        Motions Rao, necessary for total_from_given_motion. The default is None.

    Returns
    -------
    sp.Rao
        Pressure Rao.

    """

    data = xarray.open_dataset(file_path)
    if component == "total":
        rao_data = np.transpose(data["Pressure_Re"].values + 1j*data["Pressure_Im"].values, axes = [1,0,2])

    elif component == "incident+diffraction" :
        rao_data = np.transpose(data["Pressure_Dif_Re"].values + 1j*data["Pressure_Dif_Im"].values, axes = [1,0,2])
        rao_data += np.transpose(data["Pressure_Inc_Re"].values + 1j*data["Pressure_Inc_Im"].values, axes = [1,0,2])

    elif component == "total_from_given_motion":
        rao_data = np.transpose(data["Pressure_Dif_Re"].values + 1j*data["Pressure_Dif_Im"].values, axes = [1,0,2])
        rao_data += np.transpose(data["Pressure_Inc_Re"].values + 1j*data["Pressure_Inc_Im"].values, axes = [1,0,2])
        #Add radiation

        logger.warning("Radiation not yet included")
    elif component == "surge":
        rao_data = np.transpose(data["Pressure_Rad_Re"].values[:,:,0,:] +1j*data["Pressure_Rad_Im"].values[:,:,0,:], axes = [1,0,2])
        if motionsRao is not None:
            complexData = motionsRao.getComplexData()[:,:,0]
            rao_data[:,:,:] = rao_data *complexData[:,:,None]
    elif component == "sway":
        rao_data = np.transpose(data["Pressure_Rad_Re"].values[:,:,1,:] +1j*data["Pressure_Rad_Im"].values[:,:,1,:], axes = [1,0,2])
        if motionsRao is not None:
            complexData = motionsRao.getComplexData()[:,:,1]
            rao_data[:,:,:] = rao_data *complexData[:,:,None]
    elif component == "heave":
        rao_data = np.transpose(data["Pressure_Rad_Re"].values[:,:,2,:] +1j*data["Pressure_Rad_Im"].values[:,:,2,:], axes = [1,0,2])
        if motionsRao is not None:
            complexData = motionsRao.getComplexData()[:,:,2]
            rao_data[:,:,:] = rao_data *complexData[:,:,None]
    elif component == "roll":
        rao_data = np.transpose(data["Pressure_Rad_Re"].values[:,:,3,:] +1j*data["Pressure_Rad_Im"].values[:,:,3,:], axes = [1,0,2])
        if motionsRao is not None:
            complexData = motionsRao.getComplexData()[:,:,3]
            rao_data[:,:,:] = rao_data *complexData[:,:,None]
    elif component == "pitch":
        rao_data = np.transpose(data["Pressure_Rad_Re"].values[:,:,4,:] +1j*data["Pressure_Rad_Im"].values[:,:,4,:], axes = [1,0,2])
        if motionsRao is not None:
            complexData = motionsRao.getComplexData()[:,:,4]
            rao_data[:,:,:] = rao_data *complexData[:,:,None]
    elif component == "yaw":
        rao_data = np.transpose(data["Pressure_Rad_Re"].values[:,:,5,:] +1j*data["Pressure_Rad_Im"].values[:,:,5,:], axes = [1,0,2])
        if motionsRao is not None:
            complexData = motionsRao.getComplexData()[:,:,5]
            rao_data[:,:,:] = rao_data *complexData[:,:,None]
    elif component == "raw_data":
        return data

    else :
        raise(NotImplementedError)



    print(rao_data.shape)
    return sp.Rao(w = data.Frequency.values,
                      b = np.deg2rad(data.Heading.values),  # h5 output from HydroStar in degree
                      cvalue = rao_data,
                      refPoint = data.RefPoint.values[0],
                      waveRefPoint = data.RefWave.values,
                      depth = data.attrs["WATERDEPTH"],
                      forwardSpeed = data.attrs["SPEED"]
                      )
