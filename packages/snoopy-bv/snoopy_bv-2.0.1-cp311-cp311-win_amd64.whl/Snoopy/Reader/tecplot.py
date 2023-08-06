"""

   Reader for tecplot files

"""

from Snoopy import logger
import pandas as pd
import numpy as np

def tecplot_HOS(file):
    """
       Read the 3d.dat from HOS (might be made more general)
    """

    import re
    from io import StringIO

    with open(file, 'r') as a:
        data = a.read()

    blockList = [StringIO(str_) for str_ in data.split("\nZONE")]
    data_list = []
    time_list = []
    if len( blockList ) > 1 :   # Several "ZONE" block
        logger.info("Reading surface time series")
        for ibloc in range(1, len(blockList)) :
            # Parse zone information
            blocHeader = blockList[ibloc].readline()
            time = float( re.findall(r"[\S]+", blocHeader.replace(",", " ")  )[2] )
            time_list.append( time )
            if ibloc == 1 :
                a = pd.read_csv(  blockList[ibloc] , skiprows = 0, header = None , names = [ "x" , "y" , time ] , usecols = [0,1,2] , delim_whitespace = True, engine = "c" , dtype = float)
                x = a.x.values
                data_list.append( a.loc[:,time].values )
            else :
                data_list.append( pd.read_csv(  blockList[ibloc] , skiprows = 0, header = None , names = [ time ] , usecols = [0]  , delim_whitespace = True, engine = "c", dtype = float ).values[:,0])
        return pd.DataFrame( index = pd.Index(time_list, name = "time"), columns = pd.Index(x, name = "x") , data = np.stack( data_list, axis = 0 ))

    else :   # Only one block
        # Parse variables :
        title = blockList[0].readline()
        while title.startswith("#") :
            title = blockList[0].readline()
        var = blockList[0].readline().split("=")[1].split()
        var = [ s[1:-1] for s in var]
        return pd.read_csv(  blockList[0] , skiprows = 0, header = None , names = var, delim_whitespace = True, engine = "c", index_col = 0, dtype = float )



if __name__ == "__main__" :

    print ("Plot tecplot files")

    import argparse
    from Snoopy.PyplotTools import dfSlider
    parser = argparse.ArgumentParser(description='Visualize HOS 2D results', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument( '-nShaddow', help='For animation', type = int, default=0)
    parser.add_argument( "inputFile" )
    args = parser.parse_args()

    if args.inputFile[:-4] == ".wif" :
        from Spectral import Wif
        df = Wif( args.inputFile ).Wave2DC( tmin = 0.0 , tmax = 200. , dt = 0.4 , xmin = 0. , xmax = 400. , dx = 4. ,  speed = 0. )
    else :
        df = tecplot_HOS( args.inputFile )
    dfSlider( df )
