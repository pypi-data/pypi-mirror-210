from math import floor, log10, ceil
DOF   = ["surge","sway","heave","roll","pitch","yaw"]


def get_full_dataname(data_name,data_type,frequency,heading):
    index_mode  =  floor(data_type/2)
    is_real     = data_type%2

    if data_name.endswith("RAD") :
        name = f"{data_name}_{DOF[index_mode]}_HEAD_{heading:.1f}_FREQ_{frequency:.4f}"
    elif data_name[-3:] in ["EXC","DIF","INC"]:
        name = f"{data_name}_HEAD_{heading:.1f}_FREQ_{frequency:.4f}"
    elif data_name[-3:] in ["DBD","STD"]:
        name = f"{data_name}_{DOF[index_mode]}"
    else:
        return data_name
    if is_real:
        name += "_RE"
    else:
        name += "_IM"
    return name


def get_full_dataname_metadata(metadata):
    nbdata = len(metadata)
    nbspace = ceil(log10(nbdata))
    list_name = []
    for irow, row in metadata.iterrows():
        id = str(irow).zfill(nbspace)
        list_name.append(id +"_" +
            get_full_dataname(row.data_name,row.data_type,row.frequency,row.heading) )
    return list_name
    
        


def full_dataname_to_parameters(full_data_name):
    groups = full_data_name.split("_")
    data_name = groups[0]
    if groups[1] == "RAD":
        dof_name = groups[2]
        speed_val       = float(groups[4])
        frequency_val   = float(groups[6])
        heading_val     = 0
    elif groups[1] == "diffraction":
        index_rigid_mode = 6
        speed_val       = float(groups[3])
        heading_val     = float(groups[5])
        frequency_val   = float(groups[7])
    else:
        raise ValueError(f"Invalid name: {full_data_name}")



