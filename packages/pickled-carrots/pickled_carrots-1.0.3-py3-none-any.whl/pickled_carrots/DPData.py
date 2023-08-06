# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 08:59:35 2019

@author: sara.brazille
"""

import glob
import pandas as pd
import numpy as np
from . import database
from . import DPUtil
from . import mathutil
import configparser
import csv
import os


def ensureUniqueTRGIDs(dfCluster):
    """
    Making sure the trgids are unique in the cluster
    :param dfCluster: the cluster to examine
    :return:
    """
    print('Ensuring Unique TRG IDs')
    
    dfCluster = dfCluster.sort_values('TRGIDOfCentralEvent')
    
    progress = 0
    for index, row in dfCluster.iterrows():
        if progress % 20 == 0:
            DPUtil.printProgressBar(progress, len(dfCluster) - 1, 
                                    prefix='Progress:', suffix='Complete',
                                    length=50)
        valid = False
        while valid is False:
            if len(dfCluster[dfCluster['TRGIDOfCentralEvent'] == row['TRGIDOfCentralEvent']]) > 1:
                dfCluster.loc[index, 'TRGIDOfCentralEvent'] = row['TRGIDOfCentralEvent'] + 1
            else:
                valid = True
        progress += 1
    
    DPUtil.printProgressBar(1, 1, prefix='Progress:', suffix='Complete',
                            length=50)
    dfCluster = dfCluster.sort_index()
    
    return dfCluster


def hdfToDatabaseFormat(dfCluster, dfStage):
    """
    Translating hdf data to database format
    :param dfCluster:
    :param dfStage:
    :return:
    """
    if 'Log Diffusion Index (ft^2/s)' in dfCluster.columns:
        unit = 'ft'
    else:
        unit = 'm'

    # Prep this column to be a seconds column
    # dfCluster['First Event Time (min.)'] = dfCluster['First Event Time (min.)']*60
    
    hdftranslationtable = {
        '10 Percent Lateral Distance from Perf': 'LateralDistanceParallelToFracAzimuthOfPerf10thPercentile',
        '90 Percent Lateral Distance from Perf': 'LateralDistanceParallelToFracAzimuthOfPerf90thPercentile',
        'Acc. of Diffusion Index (ft/s^2)': 'Acc. of Diffusion Index (ft/s^2)',
        'Acc. of Diffusion Index (m/s^2)': 'Acc. of Diffusion Index (m/s^2)',
        'ClusterType': 'ClusterType',
        'Depth': 'Depth',
        'Diffusion Index (' + unit + '^2/s)': 'DiffusionIndex',
        'Distance Along Well from Perf (' + unit + ')': 'DistanceAlongWellFromPerf',
        'Easting': 'Easting',
        'Elasticity Index': 'Elasticity Index',
        'Energy Index': 'EnergyIndex',
        'FRAC_STAGE_ID': 'FRAC_STAGE_ID',
        'First Event Time (min.)': 'First Event Time (min.)',
        'Fracability Index': 'Fracability Index',
        'Geo Mean of Distance btw Events (' + unit + ')': 'Geo Mean of Distance btw Events (' + unit + ')',
        'Geo Mean of Distance btw Events (' + unit + '), no sr': 'Geo Mean of Distance btw Events '
                                                                 '(' + unit + '), no sr',
        'Geo Mean of Time btw Events (s)': 'Geo Mean of Time btw Events (s)',
        'Inverse of Fracability Index': 'Inverse of Fracability Index',
        'Inverse of Stress Index': 'Inverse of Stress Index',
        'Last Event Time (min.)': 'Last Event Time (min.)',
        'Lateral Distance East of Perf Mid (' + unit + ')': 'LateralDistanceParallelToFracAzimuthOfPerf',
        'Log Diffusion Index (' + unit + '^2/s)': 'LogOfDiffusionIndex',
        'Log Energy Index': 'LogOfEnergyIndex',
        'Log of Elasticity Index': 'Log of Elasticity Index',
        'Log of Fracability Index': 'Log of Fracability Index',
        'Log of Plasticity Index': 'LogOfPlasticityIndex',
        'Log of Stress Index': 'LogOfStressIndex',
        'Max Ellipsoid Length (' + unit + ')': 'MaxEllipsoidLength',
        'Max Ellipsoid Vector D': 'MaxEllipsoidVectorD',
        'Max Ellipsoid Vector E': 'MaxEllipsoidVectorE',
        'Max Ellipsoid Vector N': 'MaxEllipsoidVectorN',
        'Mean Apparent Stress': 'ArithmeticMeanApparentStress?',
        'Mean Seismic Efficiency': 'ArithmeticMeanSeismicEfficiency?',
        'Mean Seismic Moment': 'ArithmeticMeanSeismicMoment?',
        'Mean Stress Drop': 'ArithmeticMeanStressDrop?',
        'Median Distance btw Events (' + unit + ')': 'MedianDistanceBetweenEvents',
        'Median Distance btw Events (' + unit + '), no sr': 'Median Distance btw Events (' + unit + '), no sr',
        'Median Fracture Length (' + unit + ')': 'MedianFractureLength',
        'Median Time btw Events (s)': 'MedianTimeBetweenEvents',
        'Mid Ellipsoid Length (' + unit + ')': 'MidEllipsoidLength',
        'Mid Ellipsoid Vector D': 'MidEllipsoidVectorD',
        'Mid Ellipsoid Vector E': 'MidEllipsoidVectorE',
        'Mid Ellipsoid Vector N': 'MidEllipsoidVectorN',
        'Min Ellipsoid Length (' + unit + ')': 'MinEllipsoidLength',
        'Min Ellipsoid Vector D': 'MinEllipsoidVectorD',
        'Min Ellipsoid Vector E': 'MinEllipsoidVectorE',
        'Min Ellipsoid Vector N': 'MinEllipsoidVectorN',
        'N_events': 'NumberOfEvents',
        'Northing': 'Northing',
        'Plasticity Index': 'PlasticityIndex',
        'Proxy Index': 'Proxy Index',
        'Stress Index': 'StressIndex',
        'Sum of all Fracture Lengths (' + unit + ')': 'Sum of all Fracture Lengths (' + unit + ')',
        'Sum of all Moments (Nm)': 'SumOfAllMoments',
        'Sum of all Seismic energy': 'SumOfAllSeismicEnergy',
        'Time of first Event (s)': 'TimeOfFirstEvent',
        'Time of last Event (s)': 'TimeOfLastEvent',
        'Timespan of Events (s)': 'TimespanOfEvents',
        'Vel. of Diffusion Index (ft/s)': 'Vel. of Diffusion Index (ft/s)',
        'Vel. of Diffusion Index (m/s)': 'Vel. of Diffusion Index (m/s)',
        'Vertical Distance Above Perf Mid (' + unit + ')': 'VerticalDistanceAbovePerf',
        'Volume (' + unit + '^3)': 'Volume'
    }
    columnstemp = dfCluster.columns.values
    for key, value in hdftranslationtable.items():
        if key in columnstemp:
            columnstemp[columnstemp.tolist().index(key)] = value
    dfCluster.columns = columnstemp
    
    # Pandas timestamps are in nanoseconds, because... reasons
    for stage in dfCluster['FRAC_STAGE_ID'].unique():
        starttime = dfStage.loc[stage, 'Start']
        dfCluster.loc[dfCluster['FRAC_STAGE_ID'] == stage, 'TimeOfFirstEvent'] = \
            dfCluster.loc[dfCluster['FRAC_STAGE_ID'] == stage, 'TimeOfFirstEvent'].apply(
                lambda seconds: starttime.value +
                seconds*1000000000)
        
        dfCluster.loc[dfCluster['FRAC_STAGE_ID'] == stage, 'TimeOfLastEvent'] = \
            dfCluster.loc[dfCluster['FRAC_STAGE_ID'] == stage, 'TimeOfLastEvent'].apply(
                lambda seconds: starttime.value +
                seconds*1000000000)
    
    dfCluster['TimeOfFirstEvent'] = pd.to_datetime(dfCluster['TimeOfFirstEvent'], unit='ns')
    dfCluster['TimeOfLastEvent'] = pd.to_datetime(dfCluster['TimeOfLastEvent'], unit='ns')
    
    dfCluster['TRGIDOfCentralEvent'] = (dfCluster['TimeOfFirstEvent'] +
                                        (dfCluster['TimeOfLastEvent'] -
                                         dfCluster['TimeOfFirstEvent']) / 2).apply(MathUtil.dt2trgidint)
    
    dfCluster['TRGIDOfFirstEvent'] = (dfCluster['TimeOfFirstEvent']).apply(MathUtil.dt2trgidint)
    dfCluster['TRGIDOfLastEvent'] = (dfCluster['TimeOfLastEvent']).apply(MathUtil.dt2trgidint)

    dfCluster = ensureUniqueTRGIDs(dfCluster)
    
    return dfCluster
    

def readPumpClusterAndLithoData(dfStage, dfEvents, dataOptions, unit, skipPumpData=False,
                                new_fm=False, use_fracfm=True, nscale=0):
    # Load in Pump Data from vfdb
    
    # skip loading of pump data is enabled. a blank dataframe will be returned for pump data
    if os.name == 'posix':
        # Even if it's a lunux path still run this
        dataOptions.inPath = Database.makeLinuxPath(dataOptions.inPath)
        dataOptions.svc = Database.makeLinuxPath(dataOptions.svc)
        dataOptions.vfdb = Database.makeLinuxPath(dataOptions.vfdb)
    
    if '/' not in dataOptions.inPath and '\\' not in dataOptions.inPath:
        readfromdatabase = True
    else:
        readfromdatabase = False
    
    if skipPumpData:
        dfpump = pd.DataFrame({})
    else:
        print('Loading in pumping with stages')
        dfpump = Database.loadPumpingWStages(dataOptions.vfdb, dfStage)
    
    stagenames = dfEvents['FRAC_STAGE_ID'].unique()
    
    # Read in cluster data from CSV or HDF
    if readfromdatabase:
        print('Reading Cluster data from database')
        dfcluster = Database.readClusterDataFromDatabase(dataOptions.DSN,
                                                         stageNames=stagenames,
                                                         table=dataOptions.inPath,
                                                         debug=True)
        dfcluster['Time in stage (min.)'] = dfcluster['ElapsedTimeInStage']
        for name, group in dfcluster.groupby('FRAC_STAGE_ID'):

            dfcluster.loc[group.index, 'Time in stage (min)'] = \
                        (dfcluster.loc[group.index, 'TimeOfFirstEvent'] -
                         dfStage.loc[name]['Start']).astype('timedelta64[s]')/60.0
    else:
        print('Reading cluster data from file')
        dfcluster = readClusterData(dataOptions.inPath, stagenames,
                                    dfStage=dfStage)
        dfcluster = hdfToDatabaseFormat(dfcluster, dfStage)
    
    # Read in litho data
    print('Reading in Lithological data')
    dflitho = readLithoData(dataOptions.svc, new_fm=new_fm, use_fracfm=use_fracfm, nscale=nscale)
    
    return dfpump, dfcluster, dflitho


def readDataByStages(dataOptions, stageNames=None, unit='ft', skipPumpData=False):
    
    """
    Read stage well cluster etc data where the stage names correspond to the
    stageNames list given.
    
    Inputs
    ======
    dataOptions : DataClass.DataOptions
        Data options for the source etc.
    stageNames : list of strings
        Stage names to load data for
    unit: string
        Is the data in m or ft
    
    Dependencies
    ============
    Database.loadEventAndStageData
    """
    
    # Read raw event and stage data
    dfevents, dfstage = Database.loadEventAndStageData(dataOptions.DSN,
                                                       stageDSN=dataOptions.stageDSN,
                                                       types=dataOptions.types,
                                                       sqlsrv=dataOptions.sqlsrv,
                                                       stageNames=stageNames)
    
    # Load in Pump Data from vfdb
    dfpump, dfcluster, dflitho = readPumpClusterAndLithoData(dfstage,
                                                             dfevents,
                                                             dataOptions, 
                                                             unit,
                                                             skipPumpData)

    if stageNames is not None:
        dfcluster = dfcluster[dfcluster['FRAC_STAGE_ID'].isin(stageNames)]

    return dfevents, dfstage, dfpump, dfcluster, dflitho


def readDataBetweenStages(dataOptions, startStage, endStage, 
                          dropPartialStages=False, unit='ft',
                          skipPumpData=False):
    """
    Read stage well cluster etc data where the stage names are
    alphanumerically between the startStage and endStage
    
    Inputs
    ======
    dataOptions : DataClass.DataOptions
        Data options for the source etc.
    stageNames : list of strings
        Stage names to load data for
    unit: string
        Is the data in m or ft
    dropPartialStages: bool
        if True, dropping partial stages
    skipPumpData: bool
        if True, don't bother extracting pump data
    
    Dependencies
    ============
    Database.loadEventAndStageData
    """

    # Read raw event and stage data
    print('Loading event and stage data')
    dfevents, dfstages = Database.loadEventAndStageData(dataOptions.DSN,
                                                        stageDSN=dataOptions.stageDSN,
                                                        types=dataOptions.types,
                                                        sqlsrv=dataOptions.sqlsrv,
                                                        betweenStages=True,
                                                        dropPartialStages=dropPartialStages,
                                                        startStage=startStage,
                                                        endStage=endStage)

    print('reading pump cluster and litho data')
    dfpump, dfcluster, dflitho = readPumpClusterAndLithoData(dfstages,
                                                             dfevents,
                                                             dataOptions, 
                                                             unit,
                                                             skipPumpData)

    return dfevents, dfstages, dfpump, dfcluster, dflitho


def addDistRelPerfZone(data, dfStage, deslockeys=None, elev=False, wellAngle=50.0):
    """
    Add keys ['Distance Along Well','Distance East','Distance Above'] to input location data
    
    Inputs
    ======
    data : pandas.DataFrame
        input dataframe containing deslockeys
    dfStages : pandas.DataFrame
        stage information, from sf.combineStageInfo()
    deslockeys : list of 3 strings, optional
        keys of `data` giving the location coordinates, default ['Northing','Easting','Depth']
    elev : bool, optional
        if elev=True, Distance Above is distance between the perf zone to the 
        events (positive towards the surface), default False (Z = positive down)
    wellAngle : float, optional
        rotation angle in degrees of from North to the principle stress direction 
        (or angle perpendicular to strike of well), default 50.0 degrees
    
    Dependencies
    ============
    getDist_alongPerf()
    """
    if deslockeys is None:
        deslockeys = ['Northing', 'Easting', 'Depth']
    if dfStage is None:
        print('WARNING: `addDistRelPerfZone` only works for frac projects with valid stage info!')
        return
    
    # Gets the distance of clusters relative to the well perferation zones (center of stages)
    data['Distance Above'] = 0
    data['Distance East'] = 0
    for name, group in data.groupby('FRAC_STAGE_ID'):
        h1, h2 = getDist_alongPerf(group, name, dfStage, wellAngle)
        data.loc[group.index, 'Distance Along Well'] = h1
        data.loc[group.index, 'Distance East'] = h2
        if elev is False:
            data.loc[group.index, 'Distance Above'] = group['Depth'] -\
                                                      0.5*(dfStage.loc[name]['Z1']+dfStage.loc[name]['Z2'])
        else:
            data.loc[group.index, 'Distance Above'] = -1*(group['Depth'] -
                                                          0.5*(dfStage.loc[name]['Z1']+dfStage.loc[name]['Z2']))
    return


def getDist_alongPerf(df, name, dfZones, wellAngle=50.0):
    """
    Rotate coordinates by `wellAngle` relative to perf zone.
    
    Inputs
    ======
    df : pandas.DataFrame
        input dataFrame with ['Northing','Easting','Depth'] keys
    name : string
        name of stage, assumes it is in the index of dfZones
    dfZones : pandas.DataFrame
        output from sf.Zones() or sf.combineStageInfo(dsn), contains keys ['N1','E1','Z1','N2','E2','Z2']
    wellAngle : float, optional
        rotation angle in degrees of from North to the principle stress direction 
        (or angle perpendicular to strike of well), default 50.0 degrees
    
    Returns
    =======
    h1,h2 : numpy.ndarray
        array of distances along the strike of the treatment well and perpendicular 
        to the treatment well, from perf midpoint to event location
    """
    deskeys = ['Northing', 'Easting', 'Depth']
    frackeysst = ['N1', 'E1', 'Z1']
    frackeysen = ['N2', 'E2', 'Z2']
    
    fraczmid = 0.5*(dfZones.loc[name][frackeysst].values+dfZones.loc[name][frackeysen].values)
    
    # Code from Adam Baig
    well_prp = wellAngle*np.pi/180.
    r = np.mat([[np.cos(well_prp), -np.sin(well_prp)], [np.sin(well_prp), np.cos(well_prp)]])
    rn = df[deskeys[0]].values - fraczmid[0]
    re = df[deskeys[1]].values - fraczmid[1]
    xy = r*np.mat(np.vstack([re, rn]))
    h1 = np.array(xy[0].T)
    h2 = np.array(xy[1].T)
    
    return h1, h2


def readClusterData(path, stageNames=None,  clusterType=None, dfStage=None):
    
    """
    Reads cluster data from hdf file or rateVis csv file
    
    Inputs
    ======
    path : string
        Where you want to pull the HDF data from (this is your Mneg2p1 folder)
    stageNames : list, optional
        List of stage names to pull from hdf data
    multipleFiles : bool, optional
        Is the data stored in more than one hdf file? (if true, path is a directory)
    clusterType : string, optional
        Set this as the cluster type if there's only one HDF file
        
    Returns
    =======
    allData : pandas.DataFrame
        Cluster data with DateTime as index
    
    Dependencies
    ============
    glob
    pandas
    """
    readfromratevis = False
    multiplefiles = True
    
    try:
        if path.split('.')[-1] == 'csv':
            readfromratevis = True
        if path.split('.')[-1] == 'hdf':
            multiplefiles = False
    except:
        multiplefiles = True
    
    # Read all stage data from every HDF file in folder
    alldata = None
    if multiplefiles is True and readfromratevis is False and stageNames is None:
        list1 = []
        files1 = glob.glob(path+'*.hdf')
        for fname in files1:
            data = pd.read_hdf(fname, 'pcaDF')
            # Check if we're in a static or dynamic directory
            clust = None
            if os.name == 'nt':
                clust = fname.split('\\')[-2]
            if os.name == 'posix':
                clust = fname.split('/')[-2]
            if clust in ['dynamic', 'static']:
                # noinspection PyUnresolvedReferences
                data['ClusterType'] = [clust]*len(data.index)
            else:
                # noinspection PyUnresolvedReferences
                data['ClusterType'] = 'dynamic'
            list1.append(data)
        alldata = pd.concat(list1, sort=True)
    
    # Read all stage data from HDF files that correspond to the stageNames given
    if multiplefiles is True and readfromratevis is False and stageNames is not None:
        list1 = []
        for stage in stageNames:
            files1 = glob.glob(path + '*' + stage + '_.hdf')
            for fname in files1:
                data = pd.read_hdf(fname, 'pcaDF')
                # Check if we're in a static or dynamic directory
                clust = None
                if os.name == 'nt':
                    clust = fname.split('\\')[-2]
                if os.name == 'posix':
                    clust = fname.split('/')[-2]
                if clust in ['dynamic', 'static']:
                    # noinspection PyUnresolvedReferences
                    data['ClusterType'] = [clust]*len(data.index)
                else:
                    # noinspection PyUnresolvedReferences
                    data['ClusterType'] = 'dynamic'
                list1.append(data)
        alldata = pd.concat(list1, sort=True)
        
    # Read all stage data from one HDF file in folder
    if multiplefiles is False and readfromratevis is False:
        data = pd.read_hdf(path, 'pcaDF')
        # noinspection PyUnresolvedReferences
        data['ClusterType'] = clusterType
        alldata = data
        if stageNames is not None:
            # noinspection PyUnresolvedReferences
            alldata = data[data['FRAC_STAGE_ID'].isin(stageNames)]
            
    if readfromratevis:
        if dfStage is None:
            print("ERROR, Rate vis requires stage data")
        alldata = readClusterDataFromRateVis(dfStage, path, stageNames)
    
    return alldata


def readClusterDataFromRateVis(dfStage, csvFile, stageNames=None, raiseexception=True):
    
    """
    Reads cluster data from a rateVis csv file
    
    Inputs
    ======
    dfStages : pandas.DataFrame
        Stage data
    csvFile : string
        Path to csv file where the rateVis data is
        
    Returns
    =======
    dfOut : pandas.DataFrame
        Cluster data with DateTime as index
    
    Dependencies
    ============
    pandas
    """
    if raiseexception is True:
        raise Exception('''Reading from RateVis csv is disabled in this version
                        Please read from a database''')
    
    dfin = pd.read_csv(csvFile, skiprows=15, index_col=False)
    mycsv = csv.reader(open(csvFile))
    rowindex = 0
    unit = None
    eventspercluster = None
    timewindow = None
    for row in mycsv:
        if rowindex == 0:
            if row[1] == 'Metric':
                unit = 'm'
            else:
                unit = 'ft'
        
        if rowindex == 4:
            eventspercluster = row[1]
            
        if rowindex == 6:
            timewindow = row[1]
       
        rowindex = rowindex + 1
       
        if rowindex == 15:
            break
    
    # Put each csv column into it's appropriate dataframe column
    dfout = pd.DataFrame(columns=['N_events', 'Northing', 'Easting',
                                  'Depth', 'Mean Seismic Efficiency', 
                                  'Mean Apparent Stress', 
                                  'Mean Stress Drop', 
                                  'Mean Seismic Moment',
                                  'Sum of all Moments (Nm)', 
                                  'Sum of all Seismic energy', 
                                  'Median Fracture Length (ft)',
                                  'Time of first Event (s)',
                                  'Time of last Event (s)', 
                                  'First Event Time (min.)',
                                  'Last Event Time (min.)', 
                                  'Max Ellipsoid Length (ft)',
                                  'Mid Ellipsoid Length (ft)', 
                                  'Min Ellipsoid Length (ft)',
                                  'Max Ellipsoid Vector N', 
                                  'Max Ellipsoid Vector E',
                                  'Max Ellipsoid Vector D', 
                                  'Mid Ellipsoid Vector N',
                                  'Mid Ellipsoid Vector E', 
                                  'Mid Ellipsoid Vector D',
                                  'Min Ellipsoid Vector N', 
                                  'Min Ellipsoid Vector E',
                                  'Min Ellipsoid Vector D', 
                                  'FRAC_STAGE_ID',
                                  'Lateral Distance East of Perf Mid (' + unit + ')',
                                  'Vertical Distance Above Perf Mid (' + unit + ')',
                                  'Distance Along Well from Perf (' + unit + ')',
                                  'Energy Index',
                                  'Log Energy Index', 
                                  'Median Time btw Events (s)', 
                                  'Median Distance btw Events (ft)',
                                  'Timespan of Events (s)', 'Volume (ft^3)', 
                                  'ClusterType', 'Stress Index', 
                                  'Plasticity Index', 'Elasticity Index',
                                  'Log of Stress Index',
                                  'Log of Plasticity Index',
                                  'Log of Elasticity Index',
                                  'Diffusion Index (ft^2/s)',
                                  'Acc. of Diffusion Index (ft/s^2)', 
                                  'Vel. of Diffusion Index (ft/s)',
                                  'Inverse of Stress Index', 
                                  'Log Diffusion Index (ft^2/s)',
                                  'Diffusion Index (m^2/s)', 
                                  'Acc. of Diffusion Index (m/s^2)',
                                  'Vel. of Diffusion Index (m/s)',
                                  'Log Diffusion Index (ft^2/s)'])
    
    # ScalingV=35.147  # to convert cubic ft to cubic meters
    scalinga = 10.7639  # to convert square ft to square meters
    scalingl = 3.28084  # to convert ft to meters

    dfout['N_events'] = eventspercluster
    dfout['Northing'] = dfin['Northing']
    dfout['Easting'] = dfin['Easting']
    dfout['Depth'] = dfin['Depth']
    dfout['Mean Seismic Efficiency'] = dfin['Mean Seismic Efficiency']
    dfout['Mean Apparent Stress'] = dfin['Mean Apparent Stress']
    dfout['Mean Stress Drop'] = dfin['Mean Stress Drop']
    dfout['Mean Seismic Moment'] = dfin['Mean Seismic Moment']
    dfout['Sum of all Moments (Nm)'] = dfin['Sum of all Moments(Nm)']
    dfout['Sum of all Seismic energy'] = dfin['Sum of all Seismic energy']
    dfout['Median Fracture Length (' + unit + ')'] = dfin['Median Fracture Length (' + unit + ')']
    dfout['Time of first Event (s)'] = dfin['Time of first Event(s)']
    dfout['Time of last Event (s)'] = dfin['Time of last Event(s)']
    dfout['First Event Time (min.)'] = dfout['Time of first Event (s)']/60
    dfout['Last Event Time (min.)'] = dfout['Time of last Event (s)']/60
    
    ellipsoidvectorstring = dfin['Vectors (MaxXYZ MidXYZ MinXYZ )']
    # no args splits by space character
    ellipsoidvectorlist = ellipsoidvectorstring.str.split(" ", expand=True)
    
    dfout['Max Ellipsoid Length (' + unit + ')'] = dfin['Max Ellipsoid Length']
    dfout['Mid Ellipsoid Length (' + unit + ')'] = dfin['Mid Ellipsoid Length']
    dfout['Min Ellipsoid Length (' + unit + ')'] = dfin['Min Ellipsoid Length']
    
    # Depth = z, Northing = y, Easting = x
    dfout['Max Ellipsoid Vector N'] = ellipsoidvectorlist[1]
    dfout['Max Ellipsoid Vector E'] = ellipsoidvectorlist[0]
    dfout['Max Ellipsoid Vector D'] = ellipsoidvectorlist[2]
    dfout['Mid Ellipsoid Vector N'] = ellipsoidvectorlist[4]
    dfout['Mid Ellipsoid Vector E'] = ellipsoidvectorlist[3]
    dfout['Mid Ellipsoid Vector D'] = ellipsoidvectorlist[5]
    dfout['Min Ellipsoid Vector N'] = ellipsoidvectorlist[7]
    dfout['Min Ellipsoid Vector E'] = ellipsoidvectorlist[6]
    dfout['Min Ellipsoid Vector D'] = ellipsoidvectorlist[8]
    
    dfout['FRAC_STAGE_ID'] = dfin['FRAC_STAGE_ID']
    
    if dfStage is None:
        print('WARNING: `addDistRelPerfZone` only works for frac projects with valid stage info!')
    
    wellangle = dfStage['Angle Perpendicular to Well, CW'].mean()
    
    for name, group in dfout.groupby('FRAC_STAGE_ID'):
        h1, h2 = getDist_alongPerf(group, name, dfStage, wellangle)
        dfout.loc[group.index, 'Distance Along Well from Perf (' + unit + ')'] = h1
        dfout.loc[group.index, 'Lateral Distance East of Perf Mid (' + unit + ')'] = h2
        dfout.loc[group.index, 'Vertical Distance Above Perf Mid (' + unit + ')'] = \
            group['Depth']-0.5*(dfStage.loc[name]['Z1']+dfStage.loc[name]['Z2'])

    dfout['Median Time btw Events (s)'] = dfin['Median Time btw Events(s)']
    dfout['Median Distance btw Events (' + unit + ')'] = dfin['Median Distance btw Events']
    dfout['Timespan of Events (s)'] = dfin['Timespan of Events(s)']
    # HOW DO VOLUME
    if int(timewindow) < 0:
        dfout['ClusterType'] = 'static'
    else:
        dfout['ClusterType'] = 'dynamic'
    dfout['Stress Index'] = dfin['Stress Index']
    dfout['Plasticity Index'] = dfin['Plasticity Index']
    dfout['Elasticity Index'] = 1/dfin['Plasticity Index']
    # TODO: this is wrong
    dfout['Energy Index'] = 1
    dfout['Log of Stress Index'] = dfin['Stress Index'].apply(np.log10)
    dfout['Log of Plasticity Index'] = dfin['Plasticity Index'].apply(np.log10)
    dfout['Log of Elasticity Index'] = dfout['Elasticity Index'].apply(np.log10)
    dfout['Log Energy Index'] = dfout['Energy Index'].apply(np.log10)
    
    print('unit', unit)
    
    if unit == 'ft':
        dfout['Diffusion Index (ft^2/s)'] = dfin['Diffusion Index(ft^2/s)']
        dfout['Vel. of Diffusion Index (ft/s)'] = dfout['Diffusion Index (ft^2/s)'] /\
            dfout['Median Distance btw Events (' + unit + ')']
        dfout['Acc. of Diffusion Index (ft/s^2)'] = dfout['Vel. of Diffusion Index (ft/s)'] /\
            dfout['Median Time btw Events (s)']
        dfout['Log Diffusion Index (ft^2/s)'] = dfin['Diffusion Index(ft^2/s)'].apply(np.log10)
        
        dfout['Diffusion Index (m^2/s)'] = (1.0/scalinga)*dfin['Diffusion Index(ft^2/s)']
        # TODO Change these
        dfout['Vel. of Diffusion Index (m/s)'] = dfout['Diffusion Index (m^2/s)'] /\
            (dfout['Median Distance btw Events (' + unit + ')']/scalingl)
        dfout['Acc. of Diffusion Index (m/s^2)'] = dfout['Vel. of Diffusion Index (m/s)'] /\
            dfout['Median Time btw Events (s)']
        dfout['Log Diffusion Index (m^2/s)'] = dfout['Diffusion Index (m^2/s)'].apply(np.log10)
    
    else:  # Metric inputs
        dfout['Diffusion Index (m^2/s)'] = dfin['Diffusion Index(m^2/s)']
        dfout['Vel. of Diffusion Index (m/s)'] = dfout['Diffusion Index (m^2/s)'] /\
            dfout['Median Distance btw Events (' + unit + ')']
        dfout['Acc. of Diffusion Index (m/s^2)'] = dfout['Vel. of Diffusion Index (m/s)'] /\
            dfout['Median Time btw Events (s)']
    
    dfout['Inverse of Stress Index'] = 1/dfin['Stress Index']
    dfout['Inverse of Diffusion Index (' + unit + '^2/s)'] = 1/dfout['Diffusion Index (' + unit + '^2/s)']
    
    dfout.index = pd.to_datetime(dfin['DateTime'])
    
    if stageNames is not None:
        return dfout[dfout['FRAC_STAGE_ID'].isin(stageNames)]
    else:
        return dfout


def readLithoData(svc, new_fm=False, use_fracfm=True, nscale=0, addAboveBelowTops=False, buffer=10000.0):
    """
    Load litho information from SVC file. If no information is available, will 
    create default formation boundaries from [0,20000] and [20000,40000]
    
    Returns LithoDF, a pandas.DataFrame
    
    Dependencies
    ============
    configparser
    pandas
    numpy
    """
    
    config = configparser.ConfigParser()
    config.read_file(open(svc))

    svcvalid = True
    strike = None
    dip = None
    fmlog_n = None
    fmlog_e = None
    try:
        strike = config.getfloat('FractureField', 'FormationStrike')
        dip = config.getfloat('FractureField', 'FormationDip')
        fmlog_n = config.getfloat('FractureField', 'FormationLogNorthing')
        fmlog_e = config.getfloat('FractureField', 'FormationLogEasting')
    except:
        svcvalid = False
    
    if svcvalid:
        litho = Database.lithotops(svc, new_fm=new_fm, use_fracfm=use_fracfm, nscale=nscale, getstrdip=True)
        
        lithodf = pd.DataFrame(index=litho[0])
        lithodf['Top'] = litho[2]
        lithodf['Bottom'] = litho[3]
        lithocolours = np.array([(val[0]/255.0, val[1]/255.0, val[2]/255.0) for val in litho[1]])
        lithodf['Colour_R'] = lithocolours[:, 0]
        lithodf['Colour_G'] = lithocolours[:, 1]
        lithodf['Colour_B'] = lithocolours[:, 2]

        # Save formation strike and dip information
        lithodf.strike = strike
        lithodf.dip = dip
        lithodf.fmlog_n = fmlog_n
        lithodf.fmlog_e = fmlog_e

    else:
        lithodf = pd.DataFrame(index=['Formation', 'Formation_1'])
        lithodf['Top'] = [0, 20000]
        lithodf['Bottom'] = [20000, 40000]
        lithodf['Colour_R'] = np.ones(len(lithodf.index))
        lithodf['Colour_G'] = np.ones(len(lithodf.index))
        lithodf['Colour_B'] = np.ones(len(lithodf.index))
        lithodf.strike = 0.0
        lithodf.dip = 0.0
        lithodf.fmlog_n = 0.0
        lithodf.fmlog_e = 0.0

    if addAboveBelowTops:
        top_row = pd.DataFrame({'Top': lithodf.iloc[0].Top-buffer,
                                'Bottom': lithodf.iloc[0].Top,
                                'Colour_R': 127.0/255.0,
                                'Colour_G': 127.0/255.0,
                                'Colour_B': 127.0/255.0},
                               index=['Above Top Layer'])
        bottom_row = pd.DataFrame({'Top': lithodf.iloc[-1].Bottom,
                                   'Bottom': lithodf.iloc[-1].Bottom+buffer,
                                   'Colour_R': 180.0 / 255.0,
                                   'Colour_G': 180.0 / 255.0,
                                   'Colour_B': 180.0 / 255.0},
                                  index=['Below Bottom Layer'])

        lithodf = pd.concat([top_row, lithodf, bottom_row])

    # TODO : use strike and dip to add formation top for each stage to dfStages

    return lithodf


def SMT2kt(dfSMTIEvent, qualify=False):
    """ Calculate MT parameters, k and T

        Either pass the mdbfile path or send the database dictionary         
        
        Usage:  SMT2kt(mdbpath) # pass the mdb file path
                SMT2kt(smtdb=smtdb) # pass a database table container the momenttensor table
        
        Adams code. Modified by Mike Nov 2013 to take database dictionaries
    """
    t, k = [], []
    
    if qualify:
        dfSMTIEvent = dfSMTIEvent[dfSMTIEvent['T'] == 'x']

    evcs = np.vstack([dfSMTIEvent['e1x'], dfSMTIEvent['e1y'], dfSMTIEvent['e1z'],
                      dfSMTIEvent['e2x'], dfSMTIEvent['e2y'], dfSMTIEvent['e2z'],
                      dfSMTIEvent['e3x'], dfSMTIEvent['e3y'], dfSMTIEvent['e3z']]).T
    evls = np.vstack([dfSMTIEvent['Ev1'], dfSMTIEvent['Ev2'], dfSMTIEvent['Ev3']]).T
    for evl, evc in zip(evls, evcs):
        ev = np.mat(evc).reshape(3, 3)
        smt = ev.T*np.mat(np.diag(evl))*ev
        trc = np.trace(smt)
        dmt = smt - trc*np.eye(3)/3
        ev_dmt = np.linalg.eig(dmt)[0]
        if abs(ev_dmt[0]) < min(abs(ev_dmt[1]), abs(ev_dmt[2])):
            m1 = ev_dmt[0]
        elif abs(ev_dmt[1]) < abs(ev_dmt[2]):
            m1 = ev_dmt[1]
        else:
            m1 = ev_dmt[2]
        if abs(ev_dmt[0]) > max(abs(ev_dmt[1]), abs(ev_dmt[2])):
            m3 = ev_dmt[0]
        elif abs(ev_dmt[1]) > abs(ev_dmt[2]):
            m3 = ev_dmt[1]
        else:
            m3 = ev_dmt[2]
        t.append(2*m1/abs(m3))
        k.append(trc/(abs(trc) + 3*abs(m3)))
        
    return np.array(k), np.array(t)


def writeSRC(outFileName, dfIn, siteID):
    """
    Write V2.1 SRC file from DataFrame.
    
    Can optionally specify outfile=None to only return dfsFrame of SRC information.
    
    Inputs
    ======
    outfile : string
        file name for output
    dfs : dictionary-like
        will turn into a DataFrame if not already
    units : units to write the data from
    
    Returns
    =======
    Nothing, it only writes
    
    SRC columns (all separated by single spaces)
    ============================================
        Date - mm-dd-yyyy (10 characters)
        Time - hh:mm:ss.000 (12 characters)
        ID - 2-letter site stamp
        Event - integer number (5 characters)
        T - event type (1 lower case letter)
        Conf - confidence (4 characters)
        Northing - 9 characters, up to 2 decimal places
        Easting - 9 characters, up to 2 decimal places
        Depth - 8 characters, up to 2 decimal places
        Velocity - site P-wave velocity? (8 characters)
        NN_Err,EE_Err,DD_Err,NE_Err,ND_Err,ED_Err - error ellipsoid parameters (7 characters each, 2 decimal places)
        Ns,Nu - number of sensors (total and uniaxial) (2 characters each)
        uSt - ?? 3 characters, usually "num"
        uMag - uniaxial magnitude (8 characters, 2 decimal places)
        Nt - number of triaxial sensors (2 characters)
        tSt - ?? 3 characters, usually "ntm"
        tMag - triaxial magnitude? (8 characters, 2 decimal places)
        MomMag - moment magnitude (7 characters, 2 decimal places)
        SeiMoment - seismic moment (9 characters, X.XXe+XXX)
        Energy - energy released (9 characters, X.XXe+XXX)
        Es/Ep - energy ratio (8 characters, up to 2 decimal places) -> aligned left!
        SourceRo - source radius (9 characters, X.XXe+XXX)
        AspRadius - asperity radius (9 characters, X.XXe+XXX)
        StaticSD - static stress drop (9 characters, X.XXe+XXX)
        AppStress - apparent stress (9 characters, X.XXe+XXX)
        DyStressD - dynamic stress drop (9 characters, X.XXe+XXX)
        MaxDispla - maximum displacement (9 characters, X.XXe+XXX)
        PeakVelPa - peak velocity parameter (9 characters, X.XXe+XXX)
        PeakAccPa - peak acceleration parameter (9 characters, X.XXe+XXX)
        PSt - ?? integer number (3 characters)
        ML - local magnitude (8 characters, 2 decimal places)
        SrcPQ - ?? (5 characters)
        SrcSnDst - source-sensor distance (8 characters, 1 decimal place)
        
    Dependencies
    ============
    datetime
    """
    # from __future__ import division

    # Default information
#    dftdt = datetime(1970,1,1,0,0,0)
#    allparams = ['Date','Time','ID','Event','T','Conf','Northing','Easting','Depth','Velocity',
#                 'NN_Err','EE_Err','DD_Err','NE_Err','ND_Err','ED_Err','Ns','Nu','uSt','uMag',
#                 'Nt','tSt','tMag','MomMag','SeiMoment','Energy','Es/Ep','SourceRo','AspRadius',
#                 'StaticSD','AppStress','DyStressD','MaxDispla','PeakVelPa','PeakAccPa','PSt',
#                 'ML','SrcPQ','SrcSnDst']
#    fmt = ['DT','DT','s','d','s','f','f','f','f','d','f','f','f','f','f','f','d','d','s','f','d',
#           's','f','f','e','e','f','e','e','e','e','e','e','e','e','d','f','d','f']
#    dftval = [dftdt,dftdt,'HY',0,'u',0,dftloc[0],dftloc[1],dftloc[2],6000.,0.,0.,0.,0.,0.,0.,0,0,
#              'num',-9.9,0,'ntm',-9.9,-9.9,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,1,-9.9,0,0.]
#    nch = [10,12,2,5,1,4,9,9,8,8,7,7,7,7,7,7,2,2,3,8,2,3,8,7,9,9,8,9,9,9,9,9,9,9,9,3,8,5,8]
    
    df = dfIn.copy(deep=True)
    
    if len(siteID) != 2:
        print("site ID must be exactly 2 characters, no more, no less")
        return
    
    units = df['Units'].unique()[0]
    
    ellipkeys = ['PCA_NN', 'PCA_EE', 'PCA_DD', 'PCA_NE', 'PCA_ND', 'PCA_ED']
    pcakeys = ['Max Ellipsoid Length ('+units+')', 'Mid Ellipsoid Length ('+units+')',
               'Min Ellipsoid Length ('+units+')',
               'Max Ellipsoid Vector N', 'Max Ellipsoid Vector E', 'Max Ellipsoid Vector D',
               'Mid Ellipsoid Vector N', 'Mid Ellipsoid Vector E', 'Mid Ellipsoid Vector D',
               'Min Ellipsoid Vector N', 'Min Ellipsoid Vector E', 'Min Ellipsoid Vector D']
    
    # Calculate elipses
    df[ellipkeys] = df.apply(DPUtil.calcEllipsoidESG, axis=1, ekeys=pcakeys)
    
    # So, src files are really funky, they have to be exactly 305 characters per
    # line, and each cell has to line up character-wise with it's column
    headerline = r'SRC V2.1.. ........Time Id Event T Conf .Northing ..Easting ...Depth Velocity .NN_Err .' \
                 r'EE_Err .DD_Err .NE_Err .ND_Err .ED_Err Ns Nu uSt ....uMag Nt tSt ....tMag .MomMag SeiMoment ' \
                 r'...Energy ...Es/Ep .SourceRo AspRadius .StaticSD AppStress DyStressD MaxDispla PeakVelPa ' \
                 r'PeakAccPa PSt ......ML SrcPQ SrcSnDst'
    
    outfile = open(outFileName, "w")
    outfile.write(headerline + '\n')
    
    # Write each column properly formatted, and delimited by spaces
    # This is a very, very silly file format
    for index, row in df.iterrows():
        rowout = ''
        rowout += index.to_pydatetime().strftime('%m-%d-%Y')  # Date
        rowout += ' '
        rowout += index.to_pydatetime().strftime('%H:%M:%S.%f')[:-3]  # Time
        rowout += ' '
        rowout += siteID  # ID
        rowout += ' '
        rowout += '    0'  # Event
        rowout += ' '
        rowout += row['EventTypes']  # Event Type
        rowout += ' '
        rowout += '1.00'  # Confidence
        rowout += ' '
        rowout += ' '*(9-(len(str(int(row['Northing']))))) + str(int(row['Northing']))  # Northing
        rowout += ' '
        rowout += ' '*(9-(len(str(int(row['Easting']))))) + str(int(row['Easting']))  # Easting
        rowout += ' '
        rowout += ' '*(8-(len(str(int(row['Depth']))))) + str(int(row['Depth']))  # Depth
        rowout += ' '
        rowout += '   10000'  # Velocity
        rowout += ' '
        rowout += ' '*(7-(len("{:.2f}".format(row['PCA_NN'])))) + "{:.2f}".format(row['PCA_NN'])  # NN_Err
        rowout += ' '
        rowout += ' '*(7-(len("{:.2f}".format(row['PCA_EE'])))) + "{:.2f}".format(row['PCA_EE'])  # EE_Err
        rowout += ' '
        rowout += ' '*(7-(len("{:.2f}".format(row['PCA_DD'])))) + "{:.2f}".format(row['PCA_DD'])  # DD_Err
        rowout += ' '
        rowout += ' '*(7-(len("{:.2f}".format(row['PCA_NE'])))) + "{:.2f}".format(row['PCA_NE'])  # NE_Err
        rowout += ' '
        rowout += ' '*(7-(len("{:.2f}".format(row['PCA_ND'])))) + "{:.2f}".format(row['PCA_ND'])  # ND_Err
        rowout += ' '
        rowout += ' '*(7-(len("{:.2f}".format(row['PCA_ED'])))) + "{:.2f}".format(row['PCA_ED'])  # ED_Err
        rowout += ' '
        rowout += ' 0'  # Ns
        rowout += ' '
        rowout += ' 0'  # Nu
        rowout += ' '
        rowout += 'num'  # uSt
        rowout += ' '
        rowout += '   -9.90'  # uMag
        rowout += ' '
        rowout += ' 0'  # Nt
        rowout += ' '
        rowout += 'ntm'  # tSt
        rowout += ' '
        rowout += '   -9.90'  # tMag
        rowout += ' '
        rowout += '  -1.00'  # MomMag
        rowout += ' '
        rowout += ' ' + "{:.2e}".format(row['Mean Seismic Moment'])  # SeiMoment
        rowout += ' '
        rowout += ' ' + "{:.2e}".format(row['Sum of all Seismic energy'])  # Energy
        rowout += ' '
        rowout += '   10.01'  # Es/Ep
        rowout += ' '
        rowout += ' ' + "{:.2e}".format(row['Median Fracture Length ('+units+')'])  # SourceRo
        rowout += ' '
        rowout += ' ' + "{:.2e}".format(row['Inverse of Diffusion Index ('+units+'^2/s)'])  # AspRadius
        rowout += ' '
        rowout += ' ' + "{:.2e}".format(row['Mean Stress Drop'])  # StaticSD
        rowout += ' '
        rowout += ' ' + "{:.2e}".format(row['Mean Apparent Stress'])  # AppStress
        rowout += ' '
        rowout += ' ' + "{:.2e}".format(row['Plasticity Index'])  # DyStressD
        rowout += ' '
        rowout += ' ' + "{:.2e}".format(row['Inverse of Stress Index'])  # MaxDispla
        rowout += ' '
        rowout += ' ' + "{:.2e}".format(row['Stress Index'])  # PeakVelPa
        rowout += ' '
        rowout += ' ' + "{:.2e}".format(row['TI'])  # PeakAccPa
        rowout += ' '
        rowout += '  3'  # PSt
        rowout += ' '
        rowout += '   -9.90'  # ML
        rowout += ' '
        rowout += '    0'  # SrcPQ
        rowout += ' '
        rowout += ' '*(8-(len("{:.1f}".format(row['Median Distance btw Events ('+units+')'])))) + "{:.1f}".format(
            row['Median Distance btw Events ('+units+')'])  # SrcSnDst
        
        outfile.write(rowout + '\n')
    outfile.close()
