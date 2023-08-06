# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 10:15:37 2019

@author: sara.brazille
"""

import numpy as np
import pandas as pd
import struct
from sqlalchemy import create_engine
from . import DPUtil
from . import mathutil
import warnings
import os
import urllib
import datetime as dt
import pyodbc
# import datetime


def makeLinuxPath(path):
    """
    Convert path depending on the operating system that the program is running on
    :param path: the path that you want to convert
    :return:
    """
    # Convert path depending on the operating system that the program is running on

    if os.name == 'nt':  # WINDOWS
        if path.startswith(r'/mnt/esg_utils'):
            caps_path = path.replace('datashare', 'DataShare')
            mnt_path = caps_path.replace('/mnt/esg_utils', r'\\esg_utils.net')
            return mnt_path.replace('/', '\\')
    elif os.name == 'posix':  # LINUX
        if path.startswith(r'\\esg_utils.net'):
            caps_path = path.replace('datashare', 'DataShare')
            mnt_path = caps_path.replace(r'\\esg_utils.net', '/mnt/esg_utils')
            path = mnt_path.replace('\\', '/')
            # Linux is case sensitive - make sure the mount paths are correct
            path = path.replace('/Frac3', '/frac3')
            path = path.replace('/Frac4', '/frac4')
            path = path.replace('/ism', '/ISM')
            path = path.replace('/mgcs', '/MGCS')
            path = path.replace('/mgs2', '/MGS2')
            path = path.replace(r"/mosaic", '/Mosaic')
            path = path.replace('/resmap', '/RESMAP')
            path = path.replace('/rockmap', '/RockMap')
            path = path.replace('/Rockmap', '/RockMap')
            path = path.replace('/frac_reprocess', '/Frac_Reprocess')
            return path
    else:  # other OS?
        Exception('makeLinuxPath does not accept your operating system')

    return path


def connectToDB(sqlstr, dsn, print_warning=True):
    """
    Connecting to an SQL database
    :param sqlstr: server address to connect to
    :param dsn: the name of the database
    :param print_warning: if True, print the logging out warning
    :return:
    """
    # Database connection string
    # getting appropriate port to use
    if 'mgs' in sqlstr.lower():
        port = ',59281'
    elif 'resmap' in sqlstr.lower():
        port = ',1433'
    elif 'frac' in sqlstr.lower():
        port = ',59867'
    elif 'localhost' in sqlstr.lower():
        port = ''
    else:
        raise ValueError('Do not know the port for the sqlstr provided!')

    # Platform check
    cnxnstr = None
    if os.name == 'nt':  # WINDOWS
        cnxnstr = (r'DRIVER={SQL Server}; SERVER=' + sqlstr + port + ';DATABASE=' + dsn)
        cnxnstr += '; Trusted_Connection=yes'
        # cnxnstr = ( r'DRIVER={SQL Server}; SERVER=' + sqlstr+';DATABASE=' + dsn + '; UID=user; PWD=L4KAAB!') #;
        # Trusted_Connection=yes'   )
    elif os.name == 'posix':
        # LINUX
        # Normal driver using Kerberos

        cnxnstr = (r'DRIVER=ODBC Driver 17 for SQL Server; SERVER=' + sqlstr + port + '; DATABASE=' + dsn +
                   '; TDS_VERSION=8.0; Trusted_Connection=yes')
    else:  # other OS.... mac?
        Exception('connectToDB does not accept your operating system')

    try:
        return pyodbc.connect(cnxnstr)  # Connect to db
    except Exception as e:
        if print_warning:
            print('If the following is a Kerberos error, try logging out and logging ' +
                  'back in again')
        raise e
    

def connectToDBPandas(sqlstr, dsn):
    """
    Connect to SQL database through pandas?
    :param sqlstr: sql server address
    :param dsn: name of the database
    :return:
    """
    # Database connection string
    # Platform check  
    if os.name == 'nt':  # WINDOZE
        cnxnstr = (r'DRIVER={SQL Server}; SERVER=' + sqlstr + ';DATABASE=' + dsn)
        cnxnstr += '; Trusted_Connection=yes'
        # cnxnstr = ( r'DRIVER={SQL Server}; SERVER=' + sqlstr+';DATABASE=' + dsn + '; UID=user; PWD=L4KAAB!') #;
        # Trusted_Connection=yes'   )
    elif os.name == 'posix':  # LINUX
        cnxnstr = (r'DRIVER=ODBC Driver 17 for SQL Server; SERVER='+sqlstr+'; DATABASE='+dsn+'; TDS_VERSION=8.0; '
                                                                                             'Trusted_Connection=yes')
    else:  # other OS.... mac?
        Exception('connectToDBPandas does not accept your operating system')
        
    return create_engine("mssql+pyodbc:///?odbc_connect=%s" % urllib.parse.quote_plus(cnxnstr))


def readClusterDataFromDatabase(DSN, sqlsrv='FRAC\\FRAC', stageNames=None, table='Clusters_DPA_RV', debug=False):
    """
    Reading cluster data from a database
    :param DSN: the name of database
    :param sqlsrv: the sql server address
    :param stageNames: names of the stages to extract
    :param table: table of the database to examine
    :param debug: debug option
    :return:
    """
    # TODO: cluster database collisions from multiple runs
    if stageNames is not None:
        sql = 'SELECT * FROM ' + table + ' WHERE FRAC_STAGE_ID IN (\'' + '\', \''.join(stageNames) + '\')'
    else:
        sql = 'SELECT * FROM ' + table
    
    if debug:
        print(sql)
    
    cnxn = connectToDB(sqlsrv, DSN)
    
    df = pd.read_sql(sql, cnxn)
    
    df = df.apply(lambda x: x.str.strip() if isinstance(x.iloc[0], str) else x)
    
    return df


def loadEventAndStageData(DSN, types=None, stageNames=None, sqlsrv=None, stgindx='Name',
                          frac=True, stageDSN=None, angperpwell=None, mdb=False,
                          CustomFields=None, betweenStages=False, dropPartialStages=False,
                          startStage=None, endStage=None):
    """
    Loads event and stage data for stageNames given
    If no stage names are given, load all
    """
    if types is None:
        types = ['e']
    
    if frac:
        # If it is a frac (multiple stages present)
        print('Loading stages')
        if sqlsrv is not None:
            df_stages = loadStageDF(stageDSN, colours=True, index=stgindx, sqlstr=sqlsrv)
        else:
            df_stages = loadStageDF(stageDSN, colours=True, index=stgindx)
            
        # Drop duplicate stages
        df_stages.drop_duplicates('Name', inplace=True)

        if stageNames is None:
            stageNames = df_stages.index.values

        if betweenStages:
            print('Sorting stages and dropping partial stages if selected')
            stage_names_sorted = DPUtil.sorted_nicely(df_stages.index.values)
            start = stage_names_sorted.index(startStage)
            stop = stage_names_sorted.index(endStage)
            stageNames = stage_names_sorted[start:(stop + 1)]
            
            if dropPartialStages:
                stage_names_new = []
                for stage in stageNames:
                    if stage[-1].isdigit():
                        stage_names_new.append(stage)
                stageNames = stage_names_new
        if angperpwell is None:
            angperpwell = df_stages['Angle Perpendicular to Well, CW'].mean()

        print('Loading events')
        if sqlsrv is not None:
            df_event = loadEventDF(DSN, stageNames=stageNames, types=types, altDSN=stageDSN,
                                   CustomFields=CustomFields, sqlstr=sqlsrv)
        else:
            df_event = loadEventDF(DSN, stageNames=stageNames, types=types, altDSN=stageDSN, CustomFields=CustomFields)
    else:
        # It is not a frac, only one big glob of info
        df_stages = None
        if mdb:
            df_event = readsqlpd(DSN, mdb=True, typefilter=types)
        else:
            if sqlsrv is not None:
                df_event = readsqlpd(DSN, sqlstr=sqlsrv, typefilter=types)
            else:
                df_event = readsqlpd(DSN, typefilter=types)
        df_event['DateTime'] = [df_event['DateTime'].loc[i].replace(
            microsecond=int(float(df_event['DecSecond'].loc[i])*1e6)) for i in df_event.index]

    print('Processing events')
    df_event = df_event[(df_event['MomentMagnitude'] > -9.9) & (df_event['Energy'] > 0)]
    df_event['SeisEff'] = df_event['ApparentStress'] / df_event['StaticStressDrop']
    df_event = df_event.loc[df_event['SeisEff'].dropna().index]
    df_event.reset_index(inplace=True, drop=True)
    df_event = df_event.loc[df_event.TrgID.drop_duplicates().index]
    df_event.set_index('DateTime', drop=False, inplace=True)
    df_event = df_event.loc[~df_event.index.duplicated(keep='first')]
    if frac:
        addDistRelPerfZone(df_event, df_stages, deslockeys=['Northing', 'Easting', 'Depth'], wellAngle=angperpwell)
    df_event['Energy Index'] = DPUtil.energyindex(df_event, qcplot=False, plteqn=False)
    df_event['Log Energy Index'] = df_event['Energy Index'].apply(np.log10)

    if 'Time_in_stage(s)' not in df_event.keys():
        print('Making time in group column')
        is_64bit = struct.calcsize('P') * 8 == 64
        startt = df_event['DateTime'].min()
        if df_event.index.is_all_dates:
            df_event['Time_in_group(s)'] = [float((df_event['DateTime'].loc[k]-startt).seconds) for k in df_event.index]
        elif isinstance(startt, (pd.datetime, np.datetime64)):
            for k in df_event.index:
                if isinstance(df_event.loc[k, 'DateTime'], pd.datetime) | is_64bit:
                    tmp = -99999
                    try:
                        tmp = (df_event.loc[k, 'DateTime']-startt).total_seconds()
                    except:
                        tmp = -99999
                    else:
                        tmp = -99999
                    df_event.loc[k, 'Time_in_group(s)'] = tmp
                else:
                    df_event.loc[k, 'Time_in_group(s)'] = -99999
        else:
            df_event['Time_in_group(s)'] = -99999

    return df_event, df_stages


def loadStageDF(dsn, index='Name', colours=False, sqlstr='FRAC\\FRAC'):
    """combine information from stages and zones tables from the sqltable corresponding to dsn
    output is a dataframe with the stage name as the index
    can provide key inside Stages table and zones table for index
    e.g. default index='Name' or 'ZoneID'
    if you use index='ZoneID' then each entry in df_stages corresponds to a separate fracture zone within a stage

    Columns added for RGB color codes if colours=True
    dfStage[['Colour_R','Colour_G','Colour_B']]
    stgColor=(dfStage['Colour_R'].ix[j]/255.0, dfStage['Colour_G'].ix[j]/255.0, dfStage['Colour_B'].ix[j]/255.0)

    Modifications 9/20/16 to update stage zones
    """
    from . import dataclass

    df_stages = DataClass.Stages(dsn, sqlstr=sqlstr).stagesdf

    df_zones = DataClass.Fraczones(dsn, sqlstr=sqlstr).zonesdf

    if index == 'Name':
        df_stages.set_index(index, drop=False, inplace=True)
        zonestarts = \
            df_zones[df_zones['ZoneID'].isin(df_zones.groupby('StageName')['ZoneID'].min().values)][['StageName',
                                                                                                     'StartN',
                                                                                                     'StartE',
                                                                                                     'StartD',
                                                                                                     'StartMD']]
        zoneends = df_zones[df_zones['ZoneID'].isin(df_zones.groupby('StageName')['ZoneID'].max().values)][['StageName',
                                                                                                            'EndN',
                                                                                                            'EndE',
                                                                                                            'EndD',
                                                                                                            'EndMD']]

        df_zones = df_zones.rename(columns={'StartD': 'Z1', 'EndD': 'Z2', 'StartN': 'N1', 'EndN': 'N2',
                                            'StartE': 'E1', 'EndE': 'E2'})

        df_zones.set_index(index, drop=False, inplace=True)
        # df_stages=df_stages.merge(df_zones, left_index=True, right_index=True, suffixes={'','_z'})
        df_stages = df_stages.join(df_zones, how='inner', rsuffix='_z')
        df_stages.reset_index(drop=True, inplace=True)
        df_stages = df_stages.loc[df_stages['Name'].drop_duplicates().index]
        df_stages.set_index('Name', inplace=True, drop=False)

        zoneends.set_index('StageName', inplace=True)
        zonestarts.set_index('StageName', inplace=True)
        df_stages['N1'] = zonestarts['StartN']
        df_stages['E1'] = zonestarts['StartE']
        df_stages['Z1'] = zonestarts['StartD']
        df_stages['N2'] = zoneends['EndN']
        df_stages['E2'] = zoneends['EndE']
        df_stages['Z2'] = zoneends['EndD']
        df_stages['StartMD'] = zonestarts['StartMD']
        df_stages['EndMD'] = zoneends['EndMD']

    else:  # assume ZoneID
        zonestarts = \
            df_zones[df_zones['ZoneID'].isin(df_zones.groupby('StageName')['ZoneID'].min().values)][['StageName',
                                                                                                     'StartN',
                                                                                                     'StartE',
                                                                                                     'StartD',
                                                                                                     'StartMD']]
        zoneends = df_zones[df_zones['ZoneID'].isin(df_zones.groupby('StageName')['ZoneID'].max().values)][['StageName',
                                                                                                            'EndN',
                                                                                                            'EndE',
                                                                                                            'EndD',
                                                                                                            'EndMD']]

        # df_zones=df_zones.rename(columns={'StageName':'Name'})

        # df_zones.set_index(index, drop=False, inplace=True)
        df_out = df_stages.merge(df_zones, how='outer', on='Name', suffixes={'', '_z'}, copy=True)
        df_out = df_out.rename(columns={'StartD': 'Z1', 'EndD': 'Z2', 'StartN': 'N1', 'EndN': 'N2',
                                        'StartE': 'E1', 'EndE': 'E2'})

        # zoneends.set_index(index, inplace=True)
        # zonestarts.set_index(index, inplace=True)
        df_out['StartN'] = zonestarts['StartN']
        df_out['StartE'] = zonestarts['StartE']
        df_out['StartD'] = zonestarts['StartD']
        df_out['EndN'] = zoneends['EndN']
        df_out['EndE'] = zoneends['EndE']
        df_out['EndD'] = zoneends['EndD']
        df_out['StartMD'] = zonestarts['StartMD']
        df_out['EndMD'] = zoneends['EndMD']
        df_out.set_index(index, drop=False, inplace=True)
        df_stages = df_out

    if colours is True:
        df_stages['Colour_R'] = [(stgColour >> 0) & 0xFF for stgColour in df_stages['Colour'].apply(int)]
        df_stages['Colour_G'] = [(stgColour >> 8) & 0xFF for stgColour in df_stages['Colour'].apply(int)]
        df_stages['Colour_B'] = [(stgColour >> 16) for stgColour in df_stages['Colour'].apply(int)]
        df_stages['Colour'] = [(df_stages['Colour_R'].iloc[j]/255.0, df_stages['Colour_G'].iloc[j]/255.0,
                               df_stages['Colour_B'].iloc[j]/255.0) for j in range(len(df_stages.index))]

    df_stages['N_mid'] = 0.5*(df_stages['N1']+df_stages['N2'])
    df_stages['E_mid'] = 0.5*(df_stages['E1']+df_stages['E2'])
    df_stages['Z_mid'] = 0.5*(df_stages['Z1']+df_stages['Z2'])
    # add angle of well position
    vals = df_stages[['N1', 'E1']].values-df_stages[['N2', 'E2']].values
    welldirn = np.round(np.rad2deg(np.arctan2(vals[:, 1], vals[:, 0])))
    perpwell = np.round(np.rad2deg(np.arctan2(vals[:, 0], vals[:, 1])))
    df_stages['Angle Perpendicular to Well, CW'] = abs(perpwell)
    df_stages['Angle Parallel to Well, CW'] = abs(welldirn)

    return df_stages


def loadEventDF(sql, smti=False, stageNames=None, how='inner', removeDup=False, cthresh=50, Rthresh=0.5, FP=None,
                types=None, CustomFields=False, sqlstr='FRAC\\FRAC', dictout=False, domainauth=True, altDSN=None):
    """
    loads and joins source table and SMT table from SQL database, loaded by stage
    Inputs:
    sql - dsn name
    smti - False, default, set to True to load SMTI and source table
    stageNames - list of desired Stage names, must match sf.Stages(sql).stagesdf['Name']
    how - 'inner' option for loading SMTI table, can use 'outer' to get All of Source and SMT tables
    removeDup - default is true, remove duplicate TrgIDs when loading SMTI table WILL TAKE FOREVER!!
    Cthresh - Remove duplicates- choose GN sols with CondNum<= Cthresh
    Rthresh - Remove duplicates- choose GN sols with Rsq>= Rthresh
    FP- deault None assign FracPlanes options are ('old'= Perpendicular GN, 'new'= tensile angle)
    types- filter by types, default is ['e']
    CustomFields=False, under development
    dictout- return a dictionary instead of a dataframe
    domainauth- if true use your windows domain credentials to access the database
    altDSN - use this if the Stages are stored in a different database

    Outputs:
    outDF - dataframe of source and SMT tables from sql, indexed by time

    Code by L. Smith

    """
    if types is None:
        types = ['e']

    # from SQL database, load all events and fill 'FRAC_STAGE_ID ' and 'Time_in_stage sec'
    from . import dataclass

    is_64bit = struct.calcsize('P') * 8 == 64
    # Read in stages dataframe

    if isinstance(altDSN, pd.DataFrame):
        df_stages = altDSN
    elif isinstance(altDSN, dict):
        df_stages = pd.DataFrame(altDSN)

    elif altDSN is None:
        stg = DataClass.Stages(sql, domainauth=domainauth, sqlstr=sqlstr)
        df_stages = stg.stagesdf

    else:
        stg = DataClass.Stages(altDSN, domainauth=domainauth, sqlstr=sqlstr)
        df_stages = stg.stagesdf

    df_stages.set_index('Name', inplace=True, drop=False)
    dtk_key = 'DateTime'
    list1 = []

    if stageNames is None:  # If all stages selected, read all data
        # Load source table into a dataframe
        events = readsqlpd(sql, sqlstr=sqlstr, domainauth=domainauth)
        # Filter only for types we want
        events = events[events['T'].isin(types)]
        # Replace DateTimes with new DateTime from TrgID which includes microseconds
        events['DateTime'] = events.TrgID.apply(DPUtil.trgid2dt)
        # Set index
        events.set_index(events['DateTime'], inplace=True)

        for index, stage in df_stages.iterrows():
            # Add stage attributes to dataframe
            indices = np.logical_and(events.DateTime > stage.Start, events.DateTime < stage.End)
            events.loc[indices, 'Stage'] = index
            events.loc[indices, 'FRAC_STAGE_ID'] = index
            events.loc[indices, 'TreatWell'] = stage.TreatmentWell
            events.loc[indices, 'StgColour'] = stage.Colour
            events.loc[indices, 'ObsWells'] = stage.ObservationWells
            events.loc[indices, 'StgStart'] = stage.Start
            events.loc[indices, 'StgEnd'] = stage.End

        events['ElapsedTime'] = (events.index-events.StgStart).dt.seconds
        # Rename to outDF...
        out_df = events

        if smti is True:
            # Combine with SMTI Data
            # todo... make more efficient
            # select all stages
            Exception('TO DO!')
    else:  # If only certain stages wanted, read in stage by stage
        if len(stageNames) == 0:  # stop in the case where the stages are in a different database
            Exception('No stages found in the DSN provided.')

        for name in stageNames:
            # stg.findstg(name)
            startt = df_stages['Start'].loc[name]
            endt = df_stages['End'].loc[name]
            if smti is False:
                # events_SMTI = sf.readsql(sql, start=startt, end=endt, customfilter=customfilter)
                events = readsqlpd(sql, start=startt, end=endt, sqlstr=sqlstr)
                # events['DateTime'] = events.index
                # trgIDs=events['TrgID']
                # events=events[events['T'].isin(types)]
                # events['DateTime']=[events['DateTime'].loc[i].replace(microsecond=int(str(int(trgIDs[i]))[-3:])*1000)
                #                for i in events.index]
                # events['DateTime']=[events['DateTime'].ix[i].
                #                replace(microsecond=int(str(int(events['TrgID'].ix[i]))[-3:])*1000)
                #                for i in events.index]
                # events.set_index(pd.to_datetime(events['DateTime']), inplace=True)
                events_smti = events
            else:
                # events_SMTI = sf.readsql(sql, start=startt, end=endt, join='SMT')
                events = readsqlpd(sql, start=startt, end=endt, table='SOURCE', sqlstr=sqlstr)
                # trgIDs=events['TrgID']
                # events['DateTime']=events.index
                # events['DateTime']=[events['DateTime'].ix[i].
                #                replace(microsecond=int(str(int(events['TrgID'].loc[i]))[-3:])*1000)
                #                for i in events.index]
                # events=events[events['T'].isin(types)]
                # events.set_index(events['DateTime'], inplace=True, drop=False)
                events_smti_only = readsqlpd(sql, start=startt, end=endt, table='SeismicMomentTensor', sqlstr=sqlstr)
                stk = None
                dip = None
                if FP == 'old':
                    # events_SMTI_only=correct_fp(events_SMTI_only)
                    stk, dip = DPUtil.fpstrikedip(events_smti_only, oldversion=True)
                elif FP == 'new':
                    events_smti_only = DPUtil.correct_fp(events_smti_only)
                    stk, dip = DPUtil.fpstrikedip(events_smti_only, oldversion=False)

                events_smti_only = pd.DataFrame(events_smti_only)
                if FP == 'old' or FP == 'new':
                    events_smti_only['Strike'] = stk
                    events_smti_only['Dip'] = dip
                # events_SMTI_only['Date_Time']=pd.to_datetime(events_SMTI_only['Date_Time'])
                # events_SMTI_only['Date_Time']=[events_SMTI_only['Date_Time'].loc[i].
                #                replace(microsecond=int(str(int(events_SMTI_only['TrgID'].loc[i]))[-3:])*1000)
                #                for i in events_SMTI_only.index]

                # events_SMTI_only.set_index(events_SMTI_only['Date_Time'], inplace=True, drop=False)
                # events_SMTI_only.sort(inplace=True) # deprecated
                events_smti_only.sort_index(inplace=True)
                events_smti = events.join(events_smti_only, how=how, rsuffix='_SMTI')
                # events_SMTI = sf.readsql(sql, start=startt, end=endt, customfilter=customfilter, join='SMT')
            df = events_smti
            df['FRAC_STAGE_ID'] = name
            # df['TrgID']=df['TrgID'].apply(int)
            # df.set_index(df['TrgID'], inplace=True, drop=False)
            if removeDup is True:
                if df['TrgID'].unique().shape[0] < df.shape[0]:
                    df = MathUtil.pickBestSOL(df, cthresh, Rthresh)

            if df.index.inferred_type == "datetime64":
                df['Time_in_stage(s)'] = (df[dtk_key]-startt).dt.total_seconds()  # tmp
                # #(df[dtkKey].ix[k]-startt).total_seconds() if isinstance(df[dtkKey].ix[k]-startt, pd.datetime)
                # else -99999
            elif isinstance(startt, (dt.datetime, np.datetime64)):

                for k in df.index:
                    if isinstance(df[dtk_key].loc[k], pd.datetime)| is_64bit:
                        tmp = -9999
                        try:
                            tmp = (df[dtk_key].loc[k]-startt).total_seconds()
                        except:
                            tmp = -99999
                        else:
                            tmp = -99999
                        df.loc[k, 'Time_in_stage(s)'] = tmp  # (df[dtkKey].ix[k]-startt).total_seconds()
                        # if isinstance(df[dtkKey].ix[k]-startt, pd.datetime) else -99999
                    else:
                        df.loc[k, 'Time_in_stage(s)'] = -99999

            else:
                df['Time_in_stage(s)'] = -99999

            # df['Time_in_stage(s)']=[(df[dtkKey].iloc[k]-startt).total_seconds() for k in range(df.shape[0])]

            list1.append(df)
        out_df = pd.concat(list1, sort=True)

    if CustomFields is True:
        # If selected, merge custom field data into dataframe (typically SNR values, etc..)
        custom_f = readsqlpd(sql, table='CustomFields', sqlstr=sqlstr)
        # strTrgs=customF['TrgID'].astype(np.str)
        #  # Look for invalid TrgID values
        #  validTrgs=strTrgs.apply(lambda x: len(x)>16)
        #  customF=customF[validTrgs]
        #  # Convert datetimes from trgids and set to index
        #  customF['Date_Time']=strTrgs.apply(DPUtil.trgid2dt)
        #  customF.set_index(customF['Date_Time'], inplace=True)
        custom_f.sort_index(inplace=True)
        # join customfields dataframe to events dataframe
        out_df = out_df.join(custom_f, how='outer', rsuffix='_CF')
        out_df = out_df.loc[out_df['T'].dropna().index]

    # outDF.drop_duplicates('TrgID', inplace=True)
    # outDF['Stage Number']=[int(outDF['FRAC_STAGE_ID'].ix[k].split('Stage ')[-1].split('stage ')[-1].
    # split('-')[0]) for k in outDF.index]

    # Special function for dictionaries
    if dictout:
        return out_df.reset_index().to_dict()
    # Return dataframe
    return out_df


def getpickedarrays(dsn, df, sqlstr='FRAC\\FRAC', debug=False):
    """
        Function to read the arrays that were picked to calculated
        the number of arrays used in the location. This is quite useful in the
        Phase II for multi-array projects.

        Note for this to work:
        1. The arrayID column needs to be applied in the sensorfile
        2. The arrayID needs to be configured in configedit
        3. The processor GetPickedArrays needs to be run across the dataset

        Mike Preiksaitis, May, 2018

        returns input dataframe with array names and the list of arraynames
    """

    # load in sensor arrays table which is written by configedit
    senarrays = readsqlpd(dsn, table='SensorArray', sqlstr=sqlstr, debug=debug)

    if len(senarrays) < 1:
        print('Sensor Arrays data not set')
        return

    # assuming there are no legitimate double spaces, for some reason python seems to be loading the full
    # 100 characters from the SQL database
    senarrays.loc[:, 'ArrayName'] = senarrays.ArrayName.str.split('  ').str[0]
    # figure out the maximum number of arraysIDs configured
    maxarrays = len(senarrays)
    # convert to int, to binary, take the index numbers and fill in case some events don't have all arrays
    df.loc[:, 'SensorArray_binary'] = df['SensorArrays'].apply(int).apply(
        bin).str.split('b').str[-1].str.zfill(maxarrays)
    # note that binary is backwards from the array ID indexing
    df.loc[:, 'SensorArray_binary'] = df['SensorArray_binary'].apply(lambda x: x[::-1])
    # For each array, set to false
    for index, row in senarrays.iterrows():
        df.loc[:, row.ArrayName] = False
        df.loc[df['SensorArray_binary'].str[index].apply(int) == 1, row.ArrayName] = True

    # tally up the total number of arrays used for each event
    df.loc[:, 'Number of arrays'] = sum([df[array].apply(int) for array in senarrays.ArrayName])

    return df, senarrays['ArrayName'].unique()


def getCustomEventTypes(dsn, sqlstr='FRAC\\FRAC', table='CustomEventTypes', debug=False, addbasictypes=True):
    """ Access a db and get the custom event types

    Needs to be different than readsql since readsql looks to order by datetimes, etc....

    Mike Preiksaitis.
    """
    cnxn = connectToDB(sqlstr, dsn)
    sql = 'SELECT * FROM ' + table
    if debug:
        print(sql)  # for debug uncomment to print out SQL query

    df = pd.io.sql.read_sql(sql, cnxn)
    cnxn.close()

    df.set_index('TypeLetter', inplace=True)

    fractypes = {'e': 'Event',
                 'r': 'HighPriority',
                 'b': 'Perf',
                 's': 'NeedsQC',
                 'c': 'CasingFailure',
                 'a': 'Background',
                 'n': 'Noise',
                 'u': 'Unknown'}
    if addbasictypes:
        for key, value in fractypes.items():
            df.loc[key] = value

    return df


def readsqlpd(dsn, table='SOURCE', start=None, end=None, sqlstr=r'FRAC\FRAC', customfilter=None, typefilter=None,
              debug=False, join=None, leftjoin=None, joinstages=False, sort=None, print_warning=True):
    """
        Load an esg database and return a Pandas DataFrame.
        If you need milliseconds precision. Use the dt column.

    :param dsn: database name
    :param table: database table
    :param start: optional in datetime format
    :param end: optional in datetime format
    :param sqlstr: connection string defaults to frac
    :param customfilter: optional custom sql filter to append
    :param typefilter: optional dictionary of event types
    :param debug: if True will output the entire SQL commmand
    :param join: inner join record needs to exist in both tables
    :param leftjoin: left join, combine with primary table where the records exist
    :param joinstages: add the stages to the dataframe
    :param sort: optional parameter to sort dataframe by
    :param print_warning: if True, print the logging out warning
    :return:
    """
    from . import dataclass
    cnxn = connectToDB(sqlstr, dsn, print_warning=print_warning)

    table = table.upper()
    nj = None
    if join is not None:
        if isinstance(join, list):
            nj = len(join)
        else:
            nj = 1
            join = [join]
        for ij in range(nj):
            join[ij] = join[ij].upper()
            if join[ij] == 'SMT':
                join[ij] = 'SEISMICMOMENTTENSOR'
    elif leftjoin is not None:
        if isinstance(leftjoin, list):
            nj = len(leftjoin)
        else:
            nj = 1
            leftjoin = [leftjoin]
        for ij in range(nj):
            leftjoin[ij] = leftjoin[ij].upper()
            if leftjoin[ij] == 'SMT':
                leftjoin[ij] = 'SEISMICMOMENTTENSOR'

    # table of primary key for sorting for common databases
    if table == 'SMT':
        table = 'SEISMICMOMENTTENSOR'
    if table == 'SOURCE':
        dtime = 'DateTime'
    elif table == 'SEISMICMOMENTTENSOR':
        dtime = 'Date_Time'
    elif table == 'TYPE':
        dtime = 'DateTimeStamp'
    elif table == 'ALLTRGS':
        dtime = 'TrgID'
    elif table == 'ZONES':
        dtime = 'ZoneID'
    elif table == 'CUSTOMFIELDS':
        dtime = 'TrgID'
    elif table == 'TYPESTRING':
        dtime = 'ModTime'
    elif table == 'SENQC':
        dtime = 'TrgID'
    elif table == 'CHANDATA':
        dtime = 'RecTime'
    elif table == 'DATAMODTIME':
        dtime = 'ModTime'
    elif table == 'PICKS':
        dtime = 'TrgID'
    elif table == "SENSTATUS":
        dtime = "TrgID"
    elif table == "SENDATA":
        dtime = "TrgID"
    elif table == "KNOWNLOCATIONS":
        dtime = "TrgID"
    else:
        dtime = None
        sort = None

    # start building a query
    sql = 'SELECT * FROM '+table  # select all keys

    if join is not None:  # Allow joining a second table together based on TrgID
        for ij in range(nj):
            sql += ' INNER JOIN ' + join[ij] + ' ON '+table+'.TrgID='+join[ij]+'.TrgID'
    elif leftjoin is not None:  # Allow joining a second table together based on TrgID
        for ij in range(nj):
            sql += ' LEFT JOIN ' + leftjoin[ij] + ' ON '+table+'.TrgID='+leftjoin[ij]+'.TrgID '

    if start is not None and end is not None:
        if dtime == "TrgID":
            sql += ' WHERE ' + dtime + ' Between \'' + start.strftime("%Y%m%d%H%M%S") + '000\' And \'' + end.strftime(
                "%Y%m%d%H%M%S") + '999\''
        else:
            sql += ' WHERE ' + dtime + ' Between \'' + start.strftime("%Y-%m-%d %H:%M:%S") + '\' And \'' + end.strftime(
                "%Y-%m-%d %H:%M:%S") + '\''

    if customfilter is not None:  # Add a custom filter to the query
        if 'WHERE' not in sql and 'WHERE' not in customfilter:
            sql += ' WHERE ' + customfilter
        elif 'WHERE' in sql and 'WHERE' not in customfilter:
            sql += ' AND ' + customfilter
        else:  # should be case with WHERE in customfilter only
            sql += ' ' + customfilter

    if typefilter is not None:  # Add a filter based on types
        if table == "ALLTRGS":
            evttypelabel = "EvtType"
        elif table == "SOURCE":
            evttypelabel = "T"
        else:
            raise Exception("Event type filter can only be used on the Source and AllTrgs tables")

        if 'WHERE' not in sql:
            sql += ' WHERE ('
        else:
            sql += ' AND ('
        for t in typefilter:
            if '['+evttypelabel+']=' in sql:
                sql += ' OR ['+evttypelabel+']=\''+t+'\''
            else:
                sql += '['+evttypelabel+']=\''+t+'\''
        sql += ')'

    # database sorting
    if sort is not None:
        sql += ' ORDER BY ' + sort
    elif dtime is None:
        pass
    else:
        sql += ' ORDER BY ['+dtime+'];'

    if debug:
        print(sql)  # debug statement

    # use pandas to send the query to the connection and receive a df
    df = pd.io.sql.read_sql(sql, cnxn)

    # efficiently combine stages with the source table
    # won't work on tables other than the source table
    if joinstages and table == 'SOURCE':
        # Load Stages
        stagesdf = DataClass.Stages(dsn).stagesdf

        df.reset_index(inplace=True)
        # merge stages into dataframe
        df = df.sort_values(by=dtime)
        df = pd.merge_asof(df, stagesdf, left_on='DateTime', right_on='Start', direction='backward')
        # remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]

        df['Stage'] = df.Name  # put stage name into stage column
        df['FRAC_STAGE_ID'] = df.Name  # other stage name column sometimes used

    cnxn.close()

    if dtime is not None:
        df.set_index(dtime, drop=False, inplace=True)
    # remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]

    return df


def sqlquery(db, SQL, sqlstr=r"frac\frac", debug=False):
    """
    Function to run a custom SQL query.

    This was made as a contrast to readsqlpd if you don't need a function to compile a SQL SELECT query
    :param db: database name
    :param sqlstr: sqlstr generally frac\frac or mgs\\mgs
    :param debug: print out SQL query before running
    :return: dataframe
    """
    # make a connection
    cnxn = connectToDB(sqlstr, db)

    if debug:
        print(SQL)
    # get results
    df = pd.io.sql.read_sql(SQL, cnxn)
    # close connection
    cnxn.close()

    # return results
    return df


def readsql_distinct(db, table, col, sqlstr=r"frac\frac", debug=False):
    """
    Function to return the unique/distinct values in a particular column

    For example- figure out the unique sensor names in the SensorStatus table

    :param db:
    :param table:
    :param col:
    :param sqlstr
    :param debug
    :return:
    """
    # make a connection
    cnxn = connectToDB(sqlstr, db)
    # build a distinct query
    sql = r"SELECT DISTINCT ["+col+"] FROM ["+db+"].[dbo].["+table+"]"

    if debug:
        print(sql)
    # get results
    df = pd.io.sql.read_sql(sql, cnxn)
    # close connection
    cnxn.close()

    # return results
    return df


def load_mdb(mdb, table, query=None, debug=False):
    """
    Function to load a mdb (Microsoft Access) table

    On windows this will use the Microsoft Access driver.
    On linux this will use the mdb_tables CentOS package

    :param mdb: file path
    :param table: table name
    :param query: default load entire table, or use this custom SQL query instead
    :param debug: boolean if true print out the query
    :return:
    """
    # convert to windows/linux path format as required
    mdb = makeLinuxPath(mdb)

    if (os.name == 'posix') or debug:  # LINUX
        from meza import io

        # load records generator from mdb file
        # io.read uses mdb_tables under the hood and parses using pd.read_csv
        records = io.read(mdb, table=table)

        data = []

        try:
            for i in records:
                data.append(i)
        except RuntimeError:
            # Not sure why- looks like a py37 change, but a runtime error occurs at the end of the data loading
            pass

        # conver to a pandas dataframe
        out = pd.DataFrame(data)

    else:
        # cnxn_str = "Microsoft Access Driver (*.mdb)"
        cnxn_str = "Microsoft Access Driver (*.mdb, *.accdb)"
        cnxn = pyodbc.connect('Driver={' + cnxn_str + '};DBQ=' + mdb)
        cursor = cnxn.cursor()

        if query is None:
            sql = 'SELECT * FROM ' + table
        else:
            sql = query

        # result = {}
        result = cursor.execute(sql).fetchall()

        out = {}
        i = 0
        for col in cursor.columns(table=table):
            exec('out[\'' + col.column_name + '\'] = []')
            out[col.column_name] = np.array([r[i] for r in result])
            i += 1

        cursor.close()
        cnxn.close()

        out = pd.DataFrame(out)

    return out


def loadTreatmentData(db, start=None, end=None, sqlstr='FRAC\\FRAC', debug=False):
    """
    Function to loading in treatment data from SQL database.

    This function was designed to account for the change in configuration
    of channels performed in verifrac.

    The output will be a pandas dataframe.

    Mike Preiksaitis, June 2018
    """

    # channels=pd.DataFrame(readsql(db, table='InputChannels', debug=debug))
    # modtimes=pd.DataFrame(readsql(db, table='DataModTime', debug=debug))
    #
    data = readsqlpd(db, table='CHANDATA', sqlstr=sqlstr, start=start, end=end, debug=debug)

    return data


def readsqlblocks(dsn, sqlstr='MGS\\MGS', domainauth=True):
    """
    Helper function to read any stored blocks inside the SQL table

    Inputs
    ======
    dsn : string
        name of desired SQL database
    sqlstr : string, optional
        SQL server where database is located, default 'MGS\\MGS'
    domainauth : bool, optional
        True (default) is required to use windows domain authentication

    Returns
    =======
    df : pandas.DataFrame
        dataframe of block extents from SQL table

    Dependencies
    ============
    pandas
    """

    table = 'Mine Blocks'
    cnxn = connectToDB(sqlstr, dsn)
    sql = 'SELECT * FROM [' + table + ']'  # select all keys
    df1 = pd.io.sql.read_sql(sql, cnxn)
    cnxn.close()

    table = 'RotatedBlocks'
    cnxn = connectToDB(sqlstr, dsn)
    sql = 'SELECT * FROM [' + table + ']'  # select all keys
    df2 = pd.io.sql.read_sql(sql, cnxn)
    df2.rename(columns={'BlockID': 'Block ID'}, inplace=True)
    cnxn.close()

    table = 'VolumeBlocks'
    cnxn = connectToDB(sqlstr, dsn)
    sql = 'SELECT * FROM [' + table + ']'  # select all keys
    df3 = pd.io.sql.read_sql(sql, cnxn)
    df3.rename(columns={'BlockID': 'Block ID'}, inplace=True)
    cnxn.close()

    df1['BlockType'] = "Mine Blocks"
    df2['BlockType'] = "RotatedBlocks"
    df3['BlockType'] = "VolumeBlocks"

    # Combine different block tables together
    df = pd.concat([df1, df2, df3])
    df.reset_index(inplace=True, drop=True)

    return df


def lithotops(svcfile, nscale=0, new_fm=False, getstrdip=False, use_fracfm=False):
    """A function to read in the lithotop boundaries from a Seisvis file
    the array can then be plotted in a graph

    There are a few places that formations can be read in from.
    -> Seisvis Frac Formations (from Options->Formations)
        -use option use_fracfm=True
    -> Seisvis Primary Frac Formation
        -this is the formation called FORMATIONS in Tools->Vertical Scale which should be a copy of the frac formations
        unless it has been shifted based on a strike/dip
        -use option new_fm=True
    -> Seisvis Vertical Scales (from Tools->Vertical Scales)
        -use option nscale=5 where 5 is the number within the scales list

    Consider also using Sara's code in DPData.readLithoData to put directly into a dataframe
    """

    if os.name == 'posix':
        svcfile = makeLinuxPath(svcfile)

    import configparser

    config = configparser.ConfigParser()
    config.read_file(open(svcfile))

    # Load information about strike and dip
    try:
        strike = config.getfloat('FractureField', 'FormationStrike')
        dip = config.getfloat('FractureField', 'FormationDip')
        fmlog_n = config.getfloat('FractureField', 'FormationLogNorthing')
        fmlog_e = config.getfloat('FractureField', 'FormationLogEasting')
    except configparser.NoSectionError:
        strike, dip = 0, 0
        fmlog_n, fmlog_e = 0, 0

    if (dip != '0.00') and (getstrdip is False):
        warnings.warn('Lithotop dip is not zero. You should use the dip.')

    fms = None
    vertscale = None
    if use_fracfm:
        fms = config.get('FractureField', 'Formations')
    elif new_fm:
        vertscale = 'FORMATION_VERT_SCALE'
    else:
        vertscale = 'VERT_SCALE_'+str(nscale)

    layername, layercolour, layerstart, layerend = [], [], [], []

    if use_fracfm:
        fms_list = fms.split(";")
        for fm in fms_list:
            if len(fm.split(",")) == 4:
                layername.append(fm.split(",")[0])
                layerstart.append(float(fm.split(",")[1]))
                colorref = int(fm.split(",")[3])
                layercolour.append([(colorref >> 0) & 0xFF,
                                    (colorref >> 8) & 0xFF,
                                    (colorref >> 16)])
        # since frac formations does not have layerbottoms
        # layer bottoms are the layer tops shifted over by one
        layerend = layerstart[1:]
        # the bottom layer is hard coded to be 100 m or ft below the last layer top
        layerend.append(layerstart[-1]+100)

    else:
        # Loop over each layer identified in NUM_LAYERS
        for i in range(0, config.getint(vertscale, 'NUM_LAYERS')):
            layername.append(config.get(vertscale+'_LAYER_'+str(i), 'LAYER_NAME'))

            # ini files are stored as colorref color types... need to convert to rgb by bit-shifting
            colorref = config.getint(vertscale+'_LAYER_'+str(i), 'LAYER_COLOR')
            layercolour.append([(colorref >> 0) & 0xFF,
                                (colorref >> 8) & 0xFF,
                                (colorref >> 16)])

            layerstart.append(config.getfloat(vertscale+'_LAYER_'+str(i), 'LAYER_START'))
            layerend.append(config.getfloat(vertscale+'_LAYER_'+str(i), 'LAYER_END'))

    if getstrdip:
        return np.array(layername), np.array(layercolour), np.array(layerstart), np.array(layerend), \
               np.array([strike, dip, fmlog_n, fmlog_e])
    else:
        return np.array(layername), np.array(layercolour), np.array(layerstart), np.array(layerend)


def getDist_alongPerf(dfEvent, name, dfZones, wellAngle=50.0):
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
    h1, h2 : numpy.ndarray
        array of distances along the strike of the treatment well and perpendicular
        to the treatment well, from perf midpoint to event location
    """
    deskeys = ['Northing', 'Easting', 'Depth']
    frac_keys_st = ['N1', 'E1', 'Z1']
    frac_keys_en = ['N2', 'E2', 'Z2']

    frac_zmid = 0.5*(dfZones.loc[name][frac_keys_st].values+dfZones.loc[name][frac_keys_en].values)

    # Code from Adam Baig
    well_prp = wellAngle*np.pi/180.
    r_val = np.mat([[np.cos(well_prp), -np.sin(well_prp)], [np.sin(well_prp), np.cos(well_prp)]])
    rn = dfEvent[deskeys[0]].values - frac_zmid[0]
    re = dfEvent[deskeys[1]].values - frac_zmid[1]
    xy = r_val*np.mat(np.vstack([re, rn]))
    h1 = np.array(xy[0].T)
    h2 = np.array(xy[1].T)

    return h1, h2


def addDistRelPerfZone(dfEvent, dfStages, deslockeys=None, elev=False, wellAngle=50.0):
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

    if dfStages is None:
        print('WARNING: `addDistRelPerfZone` only works for frac projects with valid stage info!')
        return

    dfEvent['Distance Above'] = 0
    dfEvent['Distance East'] = 0
    for name, group in dfEvent.groupby('FRAC_STAGE_ID'):
        h1, h2 = getDist_alongPerf(group, name, dfStages, wellAngle)
        dfEvent.loc[group.index, 'Distance Along Well'] = h1
        dfEvent.loc[group.index, 'Distance East'] = h2
        if elev is False:
            dfEvent.loc[group.index, 'Distance Above'] = group['Depth']-0.5*(dfStages.loc[name]['Z1'] +
                                                                             dfStages.loc[name]['Z2'])
        else:
            dfEvent.loc[group.index, 'Distance Above'] = -1*(group['Depth']-0.5*(dfStages.loc[name]['Z1'] +
                                                                                 dfStages.loc[name]['Z2']))
    return


def loadPumpingWStages(vdb, dfStages, usedb=None, sqlsrv=None):
    """
    From Verifrac database, load all treatment data and fill 'FRAC_STAGE_ID ',
    'Time_in_stage sec', and 'Time_in_stage (min)'.

    Inputs
    ======
    vdb : string filepath
        full path to Verifrac database
    dfStages : pandas.DataFrame
        info for all stages to be included in output

    Returns
    =======
    dfPump : pandas.DataFrame
        all treatment data read from `vdb` for stages in `dfStages`

    Dependencies
    ============
    seis_func
    pandas
    """

    # try to guess if the vfdb is a database or access file
    if usedb is None:
        # guess if it belongs to a database or vfdb file
        if os.path.isfile(vdb):
            usedb = False
            if os.name == 'posix':
                raise Exception('use of database files not supported ' +
                                'in linux, please use verifrac to export ' +
                                'the vfdb file to an sql database')
        else:
            usedb = True

    if dfStages is None:
        print('WARNING: Fun.ction `loadPumpingWStages` only works for frac projects with valid stage info!')
        df_pump = None
    else:
        df_pump = pd.DataFrame()
        for name in dfStages.index:
            if usedb:  # new treatment data is on SQL
                if sqlsrv is not None:
                    pumpdat = loadTreatmentData(vdb, start=dfStages.loc[name]['Start'],
                                                end=dfStages.loc[name]['End'], sqlstr=sqlsrv)
                else:
                    pumpdat = loadTreatmentData(vdb, start=dfStages.loc[name]['Start'], end=dfStages.loc[name]['End'])

            else:  # old school, treatment data is in a vfdb file
                pumpdat = readvfdb(vdb, start=dfStages.loc[name]['Start'], end=dfStages.loc[name]['End'])
                pumpdat = pd.DataFrame(pumpdat)
            pumpdat['FRAC_STAGE_ID'] = name
            # df['Time_in_stage sec']=[(df['RecTime'].iloc[k]-dfStages.loc[name]['Start']).total_seconds()
            # for k in range(df.shape[0])]
            pumpdat['Time_in_stage sec'] = (pumpdat['RecTime']-dfStages.loc[name]['Start']).apply(
                lambda d: d.total_seconds()).iloc[:pumpdat.shape[0]]
            pumpdat['Time in stage (min)'] = pumpdat['Time_in_stage sec'].apply(lambda u: u/60.0)
            df_pump = df_pump.append(pumpdat)

    return df_pump


def readvfdb(verifracdb, start=None, end=None, debug=False):
    """
    # read a verifrac database.  Adam Baig Aug 29, 2013, Mostly wholesale stolen
    # from readmdb
    :param verifracdb: the database to access
    :param start: start time (datetime object)
    :param end: end time (datetime object)
    :param debug: NOT IMPLEMENTED
    :return:
    """
    # read a verifrac database.  Adam Baig Aug 29, 2013, Mostly wholesale stolen
    # from readmdb

    if os.name == 'posix':  # LINUX

        raise Exception('You can\'t read vfdb files on linux, please consider ' +
                        'uploading your data to the database in verifrac and ' +
                        'retrieving it from there')
    else:
        # cnxn_str = "Microsoft Access Driver (*.mdb)"
        cnxn_str = "Microsoft Access Driver (*.mdb, *.accdb)"
        cnxn = pyodbc.connect('Driver={'+cnxn_str+'};DBQ='+verifracdb)
    cursor = cnxn.cursor()

    sql = 'SELECT * FROM CHANDATA'
    if start is not None and end is not None:
        sql = sql+' WHERE RecTime Between #' + start.strftime("%Y-%m-%d %H:%M:%S") + '# And #' + \
            end.strftime("%Y-%m-%d %H:%M:%S") + '#'

    sql += ' ORDER BY [RecTime];'

    # result = {}
    result = cursor.execute(sql).fetchall()

    out = {}
    i = 0
    for col in cursor.columns(table='CHANDATA'):
        exec('out[\''+col.column_name+'\'] = []')
        out[col.column_name] = np.array([r[i] for r in result])
        i += 1

    cursor.close()
    cnxn.close()

    return out


def removeDPAtable(dsn, sqlstr='FRAC\\FRAC', debug=False, domainauth=True):
    """
    Dropping the DPA table
    :param dsn: the dsn to select
    :param sqlstr: the sql server connection string
    :param debug: if True, debugging mode so more print outs
    :param domainauth: NOT IMPLEMENTED
    :return:
    """

    sql = "DROP TABLE Clusters_DPA"

    cnxn = connectToDB(sqlstr, dsn)

    db_cursor = cnxn.cursor()

    if debug is True:
        print(sql)  # for debug uncomment to print out SQL query

    db_cursor.execute(sql)

    db_cursor.close()
    cnxn.commit()
    cnxn.close()


def createDPAtable(dsn, sqlstr='FRAC\\FRAC', debug=False, domainauth=True):
    """
    Creating table in database to store the Dynamic Parameters Analysis results
    :param dsn: the database name
    :param sqlstr: string for the SQL server
    :param debug: debug option
    :param domainauth: unused
    :return:
    """

    sql = """CREATE TABLE Clusters_DPA (
            ClusterLabel CHAR(63),
            ClusterType CHAR(15),
            TRGIDOfCentralEvent BIGINT,
            NumberOfEvents INT,
            TimespanOfEvents INT,
            Density FLOAT,
            ShearModulus FLOAT,
            Northing REAL,
            Easting REAL,
            Depth REAL,
            ArithmeticMeanSeismicEfficiency FLOAT,
            GeometricMeanSeismicEfficiency FLOAT,
            StandardDeviationOfSeismicEfficiency FLOAT,
            ArithmeticMeanApparentStress FLOAT,
            GeometricMeanApparentStress FLOAT,
            StandardDeviationOfApparentStress FLOAT,
            ArithmeticMeanStressDrop FLOAT,
            GeometricMeanStressDrop FLOAT,
            StandardDeviationOfStressDrop FLOAT,
            ArithmeticMeanSeismicMoment FLOAT,
            GeometricMeanSeismicMoment FLOAT,
            StandardDeviationOfSeismicMoment FLOAT,
            SumOfAllMoments FLOAT,
            SumOfAllSeismicEnergy FLOAT,
            MedianFractureLength FLOAT,
            TRGIDOfFirstEvent BIGINT,
            TRGIDOfLastEvent BIGINT,
            TimeOfFirstEvent DATETIME,
            TimeOfCentralEvent DATETIME,
            TimeOfLastEvent DATETIME,
            MaxEllipsoidLength FLOAT,
            MidEllipsoidLength FLOAT,
            MinEllipsoidLength FLOAT,
            MaxEllipsoidVectorN FLOAT,
            MaxEllipsoidVectorE FLOAT,
            MaxEllipsoidVectorD FLOAT,
            MidEllipsoidVectorN FLOAT,
            MidEllipsoidVectorE FLOAT,
            MidEllipsoidVectorD FLOAT,
            MinEllipsoidVectorN FLOAT,
            MinEllipsoidVectorE FLOAT,
            MinEllipsoidVectorD FLOAT,
            FRAC_STAGE_ID CHAR(63),
            LateralDistanceParallelToFracAzimuthOfPerf FLOAT,
            LateralDistanceParallelToFracAzimuthOfPerf10thPercentile FLOAT,
            LateralDistanceParallelToFracAzimuthOfPerf90thPercentile FLOAT,
            VerticalDistanceAbovePerf FLOAT,
            VerticalDistanceAbovePerf10thPercentile FLOAT,
            VerticalDistanceAbovePerf90thPercentile FLOAT,
            DistanceAlongWellFromPerf FLOAT,
            DistanceAlongWellFromPerf10thPercentile FLOAT,
            DistanceAlongWellFromPerf90thPercentile FLOAT,
            MedianTimeBetweenEvents FLOAT,
            MedianDistanceBetweenEvents FLOAT,
            Volume FLOAT,
            StressIndex FLOAT,
            PlasticityIndex FLOAT,
            DiffusionIndex FLOAT,
            EnergyIndex FLOAT,
            TernaryIndex FLOAT,
            LogOfStressIndex FLOAT,
            LogOfPlasticityIndex FLOAT,
            LogOfDiffusionIndex FLOAT,
            LogOfEnergyIndex FLOAT,
            ElapsedTimeInStage INT,
            primary key (ClusterLabel, ClusterType, TRGIDOfCentralEvent)
            ); """

    cnxn = connectToDB(sqlstr, dsn)

    db_cursor = cnxn.cursor()

    if debug is True:
        print(sql)  # for debug uncomment to print out SQL query

    db_cursor.execute(sql)

    db_cursor.close()
    cnxn.commit()
    cnxn.close()


def writeDPAtoDB(dfCluster, dsn, sqlstr='FRAC\\FRAC'):
    """
        Method to write Dynamic Parameters results to the database
    """
    if 'ClusterLabel' not in dfCluster.columns:
        raise Exception('You must set a ClusterLabel to save to the database')
    if 'ClusterType' not in dfCluster.columns:
        raise Exception('You must set a ClusterType to save to the database')
    if 'TRGIDOfCentralEvent' not in dfCluster.columns:
        raise Exception('You must set a TRGIDOfCentralEvent ' +
                        'to save to the database')
    if dfCluster['ClusterLabel'].isnull().values.any():
        raise Exception('You must set a ClusterLabel to save to the database')
    if dfCluster['ClusterType'].isnull().values.any():
        raise Exception('You must set a ClusterType to save to the database')
    if dfCluster['TRGIDOfCentralEvent'].isnull().values.any():
        raise Exception('You must set a TRGIDOfCentralEvent ' +
                        'to save to the database')

    # Dropping rows where trgid is incorrect length
    dfCluster = dfCluster[dfCluster['TRGIDOfCentralEvent'].apply(lambda x: len(x) == 17)]

    cluster_label = dfCluster['ClusterLabel'].unique()[0]
    cluster_type = dfCluster['ClusterType'].unique()[0]

    print('You are about to delete every single cluster in the database with ' +
          'label \'' + cluster_label + '\' and type \'' + cluster_type + '\'')
    print('Are you absolutely sure you want to do this? (type \'I am sure\'):')
    sure = input()

    if sure != 'I am sure':
        print('aborting')
        return 1

    sql = ("DELETE FROM Clusters_DPA WHERE ClusterType = \'" + cluster_type +
           "\' AND ClusterLabel = \'" + cluster_label + "\'")

    print(sql)

    cnxn = connectToDB(sqlstr, dsn)

    print('Executing sql')

    db_cursor = cnxn.cursor()
    db_cursor.execute(sql)

    sql = 'SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = \'Clusters_DPA\''
    valid_columns = []
    columns = db_cursor.execute(sql)
    for row in columns:
        valid_columns.append(row[3])

    df_cluster_sql = dfCluster.copy(deep=True)

    for dfColumn in df_cluster_sql.columns:
        if dfColumn not in valid_columns:
            df_cluster_sql = df_cluster_sql.drop(dfColumn, axis=1)

    print('Done deleting')
    print('Connecting to server again but with SQLAlchemy this time')

    cnxn = connectToDBPandas(sqlstr, dsn)

    print('Writing Dataframe')

    df_cluster_sql.to_sql('Clusters_DPA', con=cnxn, if_exists='append', index=False)

    return 0


def writesql(TrgID, column, value, dsn, mdbtable='Source', sqlstr='FRAC\\FRAC', debug=True,
             domainauth=True, insertonfail=False, key='TrgID'):
    """ Access a seismic sql express database and update a TrgID with a certain value

    If TrgID is not key the use key='StageName' or whatever else it is
    For example for fieldperfs, key=['StageName','DateTime']

    Usage: writesql('','Error',5,'DSN')
           writesql(['',''],['Error','T'],[5,'b'])
           writesql('20130801051201332','Error',5,'DSN')
           writesql(events['DateTime'][0].strftime('%Y%m%d%H%M%S%f')[:-3],'Error',5,'DSN')

    Mike Preiksaitis. Oct 26, 2012
    Kirill modified to use TrgID to update events
    Install from: http://code.google.com/p/pyodbc/
    """

    cnxn = connectToDB(sqlstr, dsn)

    db_cursor = cnxn.cursor()
    mdbtable = mdbtable.upper()

    if mdbtable == 'SMT':
        mdbtable = 'SEISMICMOMENTTENSOR'

    sql = 'UPDATE ' + mdbtable + ' SET '

    # If a group of things to update
    if isinstance(column, list) or isinstance(value, list):
        for c, v in zip(column, value):
            if isinstance(v, dt.datetime):
                # convert to sql friendly time
                v = dt.datetime.strftime(v, '%Y-%m-%d %H:%M:%S')
            sql += '[' + c + ']=\'' + str(v) + '\','

        if mdbtable == 'CLUSTERS' or mdbtable == 'FIELDPERFS':
            sql += '[ModTime]=GETDATE(),'

        # remove comma from last item
        sql = sql[:-1]

    else:  # if a single thing to update
        if isinstance(value, dt.datetime):
            # convert to sql friendly time
            value = dt.datetime.strftime(value, '%Y-%m-%d %H:%M:%S')
            sql += '[' + column + ']=\'' + str(value) + '\''
        else:
            sql += '[' + column + ']=' + str(value)

    sql += ' WHERE '

    if isinstance(key, list):
        for k, t in zip(key, TrgID):
            if isinstance(t, dt.datetime):
                # convert to sql friendly time
                t = dt.datetime.strftime(t, '%Y-%m-%d %H:%M:%S')
            sql += '[' + k + ']=\'' + str(t) + '\' AND '
        sql = sql[:-4]
    else:
        sql += '['+key+']=\'' + str(TrgID)+'\''

    if debug is True:
        print(sql)  # for debug uncomment to print out SQL query

    execupdate = db_cursor.execute(sql)
    if debug is True:
        print(' Rows updated: ' + str(execupdate.rowcount))

    # if cannot update or a list of things to update
    if execupdate.rowcount < 1 & insertonfail:
        if debug:
            print('No rows updated therefore trying to insert')
        sql = 'INSERT INTO ' + mdbtable + ' ('

        if isinstance(key, list):
            for k in key:
                sql += k+','
        else:
            sql += key+','

        if isinstance(column, list) or isinstance(value, list):
            for c in column:
                sql += '' + c + ','

            # remove comma from last item
            sql = sql[:-1]
        else:
            sql += '['+column+']'

        if mdbtable == 'CLUSTERS' or mdbtable == 'FIELDPERFS':
            sql += ',ModTime'

        sql += ')'
        sql += ' VALUES ('

        if isinstance(column, list):
            for t in TrgID:
                if isinstance(t, dt.datetime):
                    # convert to sql friendly time
                    t = dt.datetime.strftime(t, '%Y-%m-%d %H:%M:%S')
                sql += '\''+str(t)+'\','
        else:
            sql += '\''+str(TrgID) + '\','

        if isinstance(column, list) or isinstance(value, list):
            for v in value:
                if isinstance(v, dt.datetime):
                    # convert to sql friendly time
                    v = dt.datetime.strftime(v, '%Y-%m-%d %H:%M:%S')
                sql += '\''+str(v) + '\','
            sql = sql[:-1]
        else:
            sql += '\''+str(value)+'\''

        if mdbtable == 'CLUSTERS' or mdbtable == 'FIELDPERFS':
            sql += ',GETDATE()'
        sql += ')'

        if debug:
            print(sql)
        execupdate = db_cursor.execute(sql)

        if debug:
            print(' Rows updated: ' + str(execupdate.rowcount))

    db_cursor.close()
    cnxn.commit()
    cnxn.close()

    return


def writecolumnsql(df, label, tableKey, dsn, sqlstr='FRAC\FRAC', trgIDKey='TrgID', debug=False, isChar=False):
    """write array of values from dataframe or dictionary into CustomFields table
    Assumes TrgID is an integer data type (will not work for floats)
    Assumes tableKey exists in the CustomFields table for the dsn
    Assumes rows exist for all TrgIDs in the CustomFields table for the given events
    (rows can be added easily in SeisVis using CustomFields menu)

    Input:
    df- dictonary or dataframe containing TrgID column and a label column
    label- name of column of df to output
    tableKey- name of column in CustomFields table to output data
    dsn - string of desired SQL table
    sqlstr- default is 'FRAC\\FRAC
    trgIDKey - name of TrgID key, assumes 'TrgID'
    debug - if True, print out SQL strings and check rows updated, default is False
    isChar false by default, set to True if the data written is a string or char
    Useage:
    sf.writecolumnsql(smtdb,'ClusterID','ClusterID','Nexen_D37H_2013')
    sf.writecolumnsql(smtdb,'Softening','SofteningIndex','Nexen_D37H_2013').
    """
    if isChar is False:
        trgs = [str(trg) for trg in df[trgIDKey]]
        val = [str(val) for val in df[label]]
        [writesql(trgs[j], tableKey, val[j], mdbtable='CustomFields', dsn=dsn, sqlstr=sqlstr, debug=debug)
         for j in range(len(trgs))]
    else:
        trgs = [str(trg) for trg in df[trgIDKey]]
        val = ['\''+str(val)+'\'' for val in df[label]]
        [writesql(trgs[j], tableKey, val[j], mdbtable='CustomFields', dsn=dsn, sqlstr=sqlstr, debug=debug)
         for j in range(len(trgs))]

    return


def writepickssql(trgid, newpicks, dsn, sqlstr='FRAC\\FRAC', debug=False):
    """
        Function to update the travel time picks in the database.

        The newpicks should be a dictionary with the sensor name and the P and
        S arrivals from the start of the trace.

        {'W2_002': array([0.344, 0.423, np.nan]),
         'W2_003': array([0.3425, 0.4205, np.nan]),
         'W2_004': array([0.3425, 0.419, np.nan]),
         'W2_005': array([0.342, 0.417, np.nan]),
         'W2_006': array([0.342, 0.415, np.nan]),
         'W2_007': array([0.3405, 0.415, np.nan]),
         'W2_008': array([0.339, 0.413, np.nan]),
         'W2_009': array([0.337 , 0.4095, np.nan]),
         'W2_010': array([0.335, 0.41, np.nan])}
    """

    cnxn = connectToDB(sqlstr, dsn)

    db_cursor = cnxn.cursor()

    for sen in newpicks.keys():
        sql = "UPDATE PICKS SET "

        # convert to string, if nan replace with NULL
        parr = str(newpicks[sen][0]).replace('nan', 'NULL')
        sharr = str(newpicks[sen][1]).replace('nan', 'NULL')
        svarr = str(newpicks[sen][2]).replace('nan', 'NULL')

        sql += "PArr="+parr+", "
        sql += "SvArr="+svarr+", "
        sql += "ShArr="+sharr+" "
        sql += "WHERE TRGID="+str(trgid)+" AND SenID=\'"+str(sen)+"\'"

        if debug is True:
            print(sql)  # for debug uncomment to print out SQL query

        db_cursor.execute(sql)

    db_cursor.close()
    cnxn.commit()
    cnxn.close()

    return


def addcustomfield(dsn, customfield, data_type='float', debug=True, sqlstr='FRAC\\FRAC'):
    """
        Add column to a CustomFields table in SQL
        dsn - SQL database name
        customfield - name of the new column
        data_type - int, float or text - must be float to be used by SeisVis

        Usage: addcustomfield('Frac_Test','VelocityModel', data_type = 'text', debug = False, sqlstr = 'FRAC\\FRAC')
               addcustomfield('Frac_Test','EventCategory', data_type = 'int', debug = False, sqlstr = 'FRAC\\FRAC')
               addcustomfield('Frac_Test','SomeFloat', data_type = 'float', debug = False, sqlstr = 'FRAC\\FRAC')
    """
    cnxn = connectToDB(sqlstr, dsn)

    db_cursor = cnxn.cursor()

    sql = 'ALTER TABLE CustomFields ADD ' + str(customfield) + ' ' + str(data_type)  # generate a query

    if debug:
        print(sql)  # print query if debug is True

    execupdate = db_cursor.execute(sql)

    db_cursor.close()
    cnxn.commit()
    cnxn.close()

    return


def tag_procstat_sourcetable(df):
    """
    Map the source table proc stat definitions into the dataframe

    :param df:
    :return:
    """
    procstat_definitions = {0: "Unprocessed",
                            1: "ManualGood",
                            2: "ManualBad",
                            3: "AutoGood",
                            4: "AutoBad",
                            5: "Rejected",
                            6: "Remote",
                            7: "ExternalMag",
                            8: "ManualRemote",
                            9: "Associated",
                            10: "ManualAssoc",
                            11: "UnknownStat"}

    df["ProcStat_Source"] = df.ProcStat.map(procstat_definitions)

    return df


def tag_procstat_alltrgs(df):
    """
    Map the alltrgs table proc stat definitions into the dataframe

    :param df:
    :return:
    """
    procstat_alltrgs_def = {0: "Unprocessed Trigger",
                            1: "Autoprocessed Trigger",
                            2: "Manually Processed Trigger"}

    df["ProcStat_AllTrgs"] = df.ProcStat.map(procstat_alltrgs_def)

    return df


def updateSQLKnownLocationsTable(df, outputDSN, outputdsn_db_string, outputDSN_sitestamp, sqlstr=r"MGS\MGS",
                                 dbtable='KnownLocations'):
    """
    Update the Known Locations Table with the TrgIDs N,E,D.
    Accurate Serial Time required for known location to work in SeisVis.
    :param df:
    :param outputDSN: dsn
    :param outputdsn_db_string: database name
    :param outputDSN_sitestamp:
    :param sqlstr:
    :param dbtable:
    :return:
    """
    # reset Serial Time to long.
    df['Serial Time'] = df['Serial Time'].astype('str')

    cnxn = connectToDB(sqlstr, outputdsn_db_string)
    db_cursor = cnxn.cursor()

    for i, v, in df.iterrows():
        sql = "INSERT INTO [" + str(
            outputdsn_db_string) + "].[dbo].[KnownLocations] " \
                                   "([Serial Time],[ID], [N],[E],[D],[T0],[TrgID],[MD]) VALUES (" + \
              str(v['Serial Time']) + ",'" + str(outputDSN_sitestamp) + "'," + str(v['known_northing']) + "," + str(
            v['known_easting']) + "," + \
              str(v['known_depth']) + ",0," + str(v['TrgID']) + ",-1);"
        print(sql)
        try:
            execupdate = db_cursor.execute(sql)
            if execupdate.rowcount < 1:
                print('No rows updated therefore trying to insert')
            else:
                print('Row successfully updated :' + v['TrgID'])
        except pyodbc.Error as ex:
            print(ex)
            print("failed for " + v['TrgID'])

    db_cursor.close()
    cnxn.commit()
    cnxn.close()


def check_new_mgs_sensors(days, todrop=None, print_todrop=False):
    """
    Checking for new sensors for mining sites that have been added within the last days
    :param days: the number of days to go back to detect new sensors
    :param todrop: list of databases not to consider, this will be combined with the default list
    :param print_todrop: if True, print the databases that were dropped
    :return:
    """
    from tqdm.auto import tqdm
    from datetime import datetime, timedelta
    from IPython.display import display

    # defaulting the todrop list
    default_todrop = ['master', 'tempdb', 'model', 'msdb', 'Seismic_TestBogus', '_BatchQueue', 'Nickel_Rim_RML',
                      'Vivein_SQL', 'Vivien_Opt_SQL', 'Bogus_Verifrac', 'North_SGM_artifact', 'North_SGMOpt_SQL',
                      'Seismic_YoungDavidson_SGM_Orig', 'Seismic_ACG', 'Seismic_AcqGroupTest',
                      'Seismic_AcqGroupTestOrig', 'Seismic_AFTON_SGM', 'SeisWebService',
                      '153Coleman_AD_SQL', '153Coleman_MSOpt_SQL', '153OB_AA_SQL', '170OB_AA_SQL', '170OB_Opt_SQL',
                      'AA_GrasbergRegCONTROL', 'ACG_Re2', 'AdvAnalysis_Coleman17', 'AdvAnalysis_CreightonSGMPMA18',
                      'AdvAnalysis_CreightonTest', 'AdvAnalysis_FarEast17', 'AdvAnalysis_GBC_AnthroNoise',
                      'AdvAnalysis_GBC_DumpNoise', 'AdvAnalysis_GBC_MSopt', 'AdvAnalysis_GoldHunter_Mech',
                      'AdvAnalysis_GrasbergSGM', 'AdvAnalysis_IslandGold_SWC',
                      'AdvAnalysis_KLGold_RML', 'AdvAnalysis_LacDesIles_Mech', 'AdvAnalysis_LacDesIles_Opt',
                      'AdvAnalysis_Laronde_Mech', 'AdvAnalysis_Laronde_MSOPT', 'AdvAnalysis_LeevilleCalib17',
                      'AdvAnalysis_Macassa', 'AdvAnalysis_MGS_SMTI_training', 'AdvAnalysis_MorrisonMech',
                      'AdvAnalysis_NorthPMA17', 'AdvAnalysis_Redlake2_MS_Opt', 'AdvAnalysis_Redlake2_Processing_Issu',
                      'AdvAnalysis_Redlake_AD', 'AdvAnalysis_Redlake_Fine_opt', 'AdvAnalysis_TottenCalib',
                      'AdvAnalysis_TottenSGM17', 'AdvAnalysis_YDPMA17', 'Adv_Analysis_153SMTI', 'Adv_Analysis_DMLZHF',
                      'Afton_Test', 'Alpayana_AD', 'AMECarlsLoc', 'AMECarlsMT',
                      'AMEC_FilterDev_SQL', 'AMEC_Opt_3DVM_SQL', 'AMEC_SMTI_SQL', 'Antamina_AD', 'BigGossan_OPTest',
                      'Campbell_NAD83_SQL', 'Carlsbad_AD_SQL', 'Carlsbad_SysOpt_SQL', 'Cayuga_AD', 'Cayuga_reproc',
                      'CC880_AD_SQL', 'Cedro_SQL', 'changcun_sql', 'ChinaTest', 'CNRL', 'Cochenour_MSOpt_DSN',
                      'Cochenour_NAD83_SQL', 'Cochenour_SQL', 'Coleman_SMTI_SQL', 'CopperCliff_3DVM_Control_SQL',
                      'CopperCliff_3DVM_Dev_SQL', 'Coppercliff_AD_SQL', 'DMLZ_Local', 'Dongshengmiao', 'DOZ_MGCS',
                      'CopperCliff_SMTIFeas_SQL', 'CreighTest', 'CreightonSPTest_SitePRC', 'CreightonSPTest_SQL',
                      'CreightonTest', 'Creighton_AD', 'Creighton_AD_new_SQL', 'Creighton_MS_Opt_SQL',
                      'Creighton_Opt_Control_SQL', 'Creighton_SMTI', 'CrippleCreek', 'Diavik_Opt',
                      'Creighton_SMTI_Feas_SQL', 'Creighton_SMTI_SQL', 'CreiSGMSPTest_Comp_SQL', 'CreiSGMSPTest_SQL',
                      'CrippleCrk_BlastOpt', 'Cyuga_AD_2020_SQL', 'DaveTest', 'Diavik', 'Diavik_ArrayAssessment_SQL',
                      'DMLZ_20200212_MW3', 'DMLZ_3DVMUpdates_SQL', 'DMLZ_AA', 'DMLZ_CASE_STDY', 'DMLZ_FRAC_Verifrac',
                      'DMLZ_Opt_SQL', 'DMLZ_PRC_Test_SQL', 'DMLZ_Stress', 'DMLZ_UnderEst', 'DMLZ_YA_SQL',
                      'DSK2018Test_SQL', 'EatonGold_SysAn_SQL', 'EatonGold_SystemAnalysis',
                      'EatonGold_SystemAnalysis_SQL', 'ESG_Versions', 'Garson_MSOpt_SQL', 'Goldex_SrcParamOpt_SQL',
                      'Eleonore_RBS', 'Eleonore_Test', 'ESGCertification', 'ESGLicence', 'ESGLicenceOld', 'ESG_OT',
                      'Estrella_MSOpt', 'Estrella_MSOpt_SQL', 'FarEast_SQL', 'Fletcher_MSOpt_SQL', 'ForVlad_SQL',
                      'FraserMorgan_PRCOpt_SQL', 'FraserM_3DVMUpdate_SQL', 'Galena_PMA2017Opt', 'GarsonSGM_Opt_SQL',
                      'Garson_3DVM_Update', 'Garson_3DVM_Update_SQL', 'Garson_AD_2_SQL', 'Garson_AD_SQL',
                      'GBC_EB_Comp_SQL', 'GBC_EB_SQL', 'GBC_MultiPRC', 'GoldcorpSGM', 'Goldex_Noise_Issue_SQL',
                      'GoldHntr_Reproc', 'HudBay_AD_SQL', 'IG_SeisWatch_SQL', 'Immel_AD_SQL', 'IslandGold_SWatch_SQL',
                      'JansenTauP', 'Jansen_Local_SQL', 'Jinneng_SQL', 'Jinzhou', 'Karari_MSOpt_SQL', 'Kidd_Pal_MSOpt',
                      'KLGold_AD_SQL', 'KLGold_SQL', 'Lamaque_AA_SQL', 'Lamaque_ControlDSN_SQL_SQL',
                      'Lamaque_MSOpt_SQL', 'Laronde_HNAS1_SQL', 'Laronde_Optimization', 'MorrisonSrcMech',
                      'Lamaque_SGMOpt_SQL', 'larondeoptim_10events', 'LarondeTest', 'Laronde_AD_SQL',
                      'Laronde_HNAS2_SQL', 'Laronde_Mech2_SQL', 'LaRonde_Mech_Loc_SQL', 'Laronde_MSOpt_SQL',
                      'laronde_ProcTest_SQL', 'Laronde_Reproc_SQL', 'LuoHe', 'Macassa_MSOpt_SQL', 'Marlin',
                      'MGSAdvAnalysis_Eleonore_SrcParaOpt', 'MGSAnalysis_Cayuga_Reproc', 'Mittersill_MSOpt_SQL',
                      'Mittersill_SysCalib_SQL', 'Monthly_DMLZ_Mech', 'MorrisMSCal', 'MorrisonSGMCalib',
                      'NewSQLCreateTest', 'NickelRim_AutoSMTI', 'NickelRim_Mech', 'NickelRim_PeerReview_BackProcessing',
                      'NickelRim_PRCtests_SQL', 'NickelRim_Reproc', 'NickelRim_SGM', 'NickelRim_SMTI', 'Nickel_Mech',
                      'Nickel_Rim_BackProc_SQL', 'Nickel_Rim_Control_Set_SQL', 'Nickel_RIM_DPA', 'Nickel_Rim_Mech_Loc',
                      'Nickel_Rim_Mech_Loc_Auto_SQL', 'Nickel_Rim_Mech_SQL', 'Nickel_Rim_Opt', 'Nickel_Rim_Opt_SQL',
                      'Nickel_Rim_PRC_Comp', 'Niobec_3DVMUpdate_SQL', 'Niobec_AD_SQL', 'Niosh_3DVM', 'Niosh_3DVM_SQL',
                      'NorthMine_SourceParamOpt_SQL', 'NorthMine_SourceP_SGM_SQL', 'NorthTest', 'North_artfifact8',
                      'North_artifact', 'North_artifact1', 'North_artifact2', 'North_artifact3', 'North_artifact4',
                      'North_artifact5', 'North_artifact6', 'North_artifact7', 'North_BackProcessing_SQL',
                      'North_SPOpt_SGM_SQL', 'Osborne_Asses_SQL', 'Redlake2_Comparison_SQL',
                      'North_SP_Opt', 'NRDReproc', 'NRDVictor_AD_SQL', 'NRTest', 'NR_1D_VM', 'NR_AutoSMTI_ref',
                      'NR_AutoSMTI_test1', 'NR_SGM1_SGMOpt_SQL', 'OD_Part2_SQL', 'OD_SenAnalysis2_SQL',
                      'OD_SenAnalysis_SQL', 'OnapingDepth_PRCOpt_SQL', 'OnapingDepth_SNOpt_SQL', 'onapingdsyscal',
                      'Onaping_MSOpt_SQL', 'Onaping_SourceParam_SQL', 'Osborne_3DVM_SQL', 'Osborne_Asses',
                      'Osborne_MsOpt_SQL', 'Oyu_Tolgoi', 'PaladinFlash', 'PalLicence', 'PalTraceability',
                      'Penkas_MSOpt_SQL', 'PleasantGap_3DVM', 'Raura_MSOpt_SQL', 'RdLakeMergedLocation',
                      'Redlake2_Opt_2020_SQL', 'RedLakeMerg', 'RedlakeOrig_Comparison_SQL', 'RedLake_DNOpt_SQL',
                      'Redlake_Fine_Opt_SCB_SQL', 'Redlake_Orig_SQL', 'Redlake_SQL', 'ReportServer$MGS',
                      'ReportServer$MGSTempDB', 'SanMartin_AD_SQL', 'Seismic_BogusOrig', 'Seismic_Cayuga_RBF',
                      'Resolution_AD_SQL', 'Resolution_ArrayDesign_SQL', 'RMLNickelRim', 'RML_Eleonore',
                      'SanMartin_SQL', 'SanRafaelPDTest', 'SanRafael_MSOpt_SQL', 'SanRafOpt', 'SantaMaria_AD_SQL',
                      'SantaMaria_MSOpt_SQL', 'SanVincente_MSOpt_SQL', 'Seismic_Barriefield', 'Seismic_BDA1',
                      'Seismic_Cameco', 'Seismic_CamecoOrig', 'Seismic_Cantung', 'Seismic_CantungOrig',
                      'Seismic_CFPH', 'Seismic_CFPH_Orig', 'Seismic_Cleveland', 'Seismic_ClevelandOrig',
                      'Seismic_CreightonADV', 'Seismic_Diavik_Orig', 'Seismic_EastBoulderOrig', 'Seismic_EleonoreSGM',
                      'Seismic_CreightonSA', 'Seismic_CZone', 'Seismic_Diavik', 'Seismic_DiavikOrig',
                      'Seismic_Dicun', 'Seismic_DicunOrig', 'Seismic_DMLZ_Advanced', 'Seismic_EastBoulder',
                      'Seismic_EatonGold', 'Seismic_Eleonore', 'Seismic_EleonoreOrig', 'Seismic_EleonoreRBF',
                      'Seismic_EPS1', 'Seismic_Estrella', 'Seismic_FonrocheVH', 'Seismic_FraserCopper_TEST',
                      'Seismic_FraserCopSGMOrig', 'Seismic_FraserCU', 'Seismic_FraserCUOrig',
                      'Seismic_FraserMorgan_SGMOrig', 'Seismic_HyperionSGM', 'testdnss', 'Totten_AD',
                      'Seismic_FraserNiPal', 'Seismic_FraserNiPalOrig', 'Seismic_Galena2', 'Seismic_GalenaOld',
                      'Seismic_GalenaOrig', 'Seismic_GalenaSGM', 'Seismic_GBC_Advanced', 'Seismic_GBC_FalseAlerts',
                      'Seismic_Goldcorp', 'Seismic_GoldHuntrLE', 'Seismic_HSFHeader', 'Seismic_Hyperion',
                      'Seismic_KiddCreek', 'Sesimic_TeckPOMOrig', '_EmptyDBforJosh', '_Metrics', 'Seismic_LeeVille',
                      'Seismic_LeeVilleOrig', 'Seismic_Leeville_SGM', 'Seismic_Lockerby', 'Seismic_LockerbyOrig',
                      'Seismic_LockerbySGM', 'Seismic_LockerbySGMOrig', 'Seismic_LuckyFriday', 'Seismic_LuoHeOrig',
                      'Seismic_MajubaUCG', 'Seismic_Majuba_UCGOrig', 'SFTest', 'SGM_SGMOpt_SQL', 'Shizhuyuan',
                      'Shuangyashan_AD_SQL', 'Siphon2019_SQL', 'Siphon2020_SQL', 'SiteAcqConfigChanges', 'SiteB-2_SQL',
                      'SiteB-_SQL', 'software_test', 'SouthC_SQL', 'sqltestdb', 'SQL_AMEC_CarlsbadAD', 'SteveBigGoss',
                      'Stillwater_MSOpt.sql', 'Stillwater_Opt_SQL', 'SudburyBasin_SQL', 'SuperTestBologna', 'SVTestSel',
                      'SwSStest', 'Tantalum_AD', 'Tantalum_MSOpt_SQL', 'Tayahua_SGM_Opt_SQL', 'Tayahua_SGM_SQL',
                      'testDSNs', 'TestHNAS_SQL', 'testMojy', 'TestMP', 'TestMP_Orig', 'TestNewSystem', 'TestOT',
                      'TestPalLicence', 'TestSWSSqlUpdate', 'Test_CreighTest', 'Test_PaladinGroup', 'Tier1Test',
                      'Totten_GMPEOpt_SQL', 'Totten_MSOpt_SQL', 'Totten_OptBlastOnly', 'Totten_PPV_SQL',
                      'Totten_SesWatchOpt_SQL', 'UCHU_AD_SQL', 'YoungDavidson_AD_SQL', 'Westwood_HNAS1_SQL',
                      'Totten_SGMSrcParam_SQL', 'Totten_SMTIFeas', 'Totten_SrcParmOpt_SQL',  'UchuSysCal_SQL',
                      'UpperRedLake_SQL', 'Vale_Analysis', 'Wanhua_AD_SQL', 'Wanhua_SQL', 'Westwood_AD_SQL',
                      'Westwood_AutoMech', 'Yauliyacu_MSOpt_SQL', 'YoungDavidson_3DVMUpdate_SQL',
                      'Zhanjiang', 'Seismic_MGS', 'Seismic_MGSORG', 'Seismic_MGS_2016TEST', 'Seismic_Morrison',
                      'Seismic_MorrisonSA', 'Seismic_MorrisonSGM', 'Seismic_MorrisonSGMOrig', 'Seismic_Mouska',
                      'Seismic_Mouskaorig', 'Seismic_MusselWhite_SGM', 'Seismic_NewOx', 'Westwood2_SQL',
                      'Westwood_HNAS2', 'Westwood_HNAS3_SQL', 'Westwood_Mech', 'Westwood_MSOpt_SQL',
                      'Westwood_Reproc_SQL', 'Westwood_SMTI_Mech_SQL', 'Willem_Test', 'WW_Mech_SQL',
                      'Yauliyacu_AD_Short_SQL', 'Seismic_Penkas', 'Seismic_Sinecuanon', 'seismic_thompson',
                      'Seismic_Osborne', 'Seismic_OsborneOrig', 'Seismic_Paddington', 'Seismic_Paladin',
                      'Seismic_PleasantGap', 'Seismic_PyongOrig', 'Seismic_RedLake', 'Seismic_RedLakeSA',
                      'Seismic_RedLake_test', 'Seismic_Sabinas', 'Seismic_SabinasOrig', 'Seismic_SantaMaria',
                      'Seismic_SantaMaria2', 'Seismic_SantaMaria2_Orig', 'Seismic_SantaMaria_Orig',
                      'Seismic_SoftTest', 'Seismic_StillwaterRProc', 'Seismic_Stobie', 'Seismic_StobieOrig',
                      'Seismic_StobieSGM', 'Seismic_SuperHSFHeader', 'Seismic_TayahuaMSOpt', 'Seismic_TeckPOM',
                      'Seismic_TeckPOMOrig', 'Seismic_TeckPOM_Orig', 'Seismic_TestAcq1', 'Seismic_TestAcq2',
                      'Seismic_TestAGHNAS', 'Seismic_TestAGHNASOrig', 'Seismic_Test_DSN', 'Seismic_TF',
                      'seismic_thompson_orig', 'Seismic_Tongxin', 'Seismic_TroyMine', 'Seismic_TroyMineOrig',
                      'Seismic_UCHU', 'Seismic_WestvacoOrig', 'Seismic_Wuhanu', 'Garson_DataNormAnalysis',
                      'Seismic_UCHU_Original', 'Seismic_Utah', 'Seismic_Victor_SQL', 'Seismic_Westvaco',
                      'Seismic_WestVero', 'SeismicMorrisonOrig', 'SeismicTest_Bogusoid', 'Seismic_Wolfram',
                      'Seismic_Yauliyacu', 'Seismic_Yichang', 'Seismic_Yichang_Orig', 'Garson_MSOptimization_SQL',
                      'Sesimic_TottenTest2', 'Seismic_TottenTest2', 'Sesimic_Totten_LocalMag',
                      'Seismic_Laronde_copy', 'Seismic_Resolution1', 'Seismic_TestSite', 'XGBC_Art_Orig',
                      'Test_SWS_Nick', 'Totten_Control_SQL', 'CC865_MS_Test', 'LaRonde_AutoPRCOpt_SQL',
                      'GBC_Art_Orig2', 'IG_ArrayAssess_SQL', 'CC&V_Opt_SQL', 'Seismic_HyperionOrig',
                      'Totten_PRCModel_SQL', 'Redlake2_Multiple_Triggers', 'Redlake2_Copy', 'Redlake2_Test_SQL',
                      'CC865_MS_Test_SQL', 'CC865_SGM_Test_SQL', 'GBC_Cave', 'Resolution_MSOpt_SQL',
                      'LaRonde_AutoPRC2_SQL', 'Laronde_Auto_Cur_Online_SQL', 'NickleRim_3DVM_SQL', 'Test27Acq1',
                      'Seismic_Test27AGHNAS', 'Creighton_StressInv_SQL', 'Westwood_SQL', 'OnapingDepth_CC',
                      'Tantalum_ArrayDesign_SQL', 'SantaMaria_Tomo', 'Redlake2_Truth_SQL', 'Redlake2_Model_SQL',
                      'Fraser_SourceParam_Opt', 'Fraser_Copper_SourceParam_Opt', 'RedLake2_CurrentAuto_SQL',
                      'YoungDavidson3DVMUpdate_SQL', 'Nickel_Rim_SF', 'Nickel_Rim_SF_SQL', 'NickelRim_3DVM_2_SQL',
                      'Seismic_BogusDave', 'NickelRim_3DVM_3_SQL', 'YDavidsonMerge_SQL', 'Xinli_MSOpt_SQL', 'Xinli_SQL',
                      'DeepSouth_Opt_SQL', 'Seismic_BogusDave32', 'DeepSouth_CurrentOnline', 'Alpayana_Opt_SQL',
                      'CC810_Test_SQL', 'Creighton_MultiProcRePro_SQL', 'Creighton_BackProc_SGM_SQL',
                      'Goldex_AutoPRCOpt_SQL', 'Laronde_Send_SQL', 'Seismic_GoldhunterTest', 'RedLake_Art',
                      'Goldcorp_SGM_retrigger', 'Gualcamayo_3DVM_SQL', 'Creighton_3DVM_Dev_SQL', 'Laronde_MSOpt2_SQL',
                      'DM_BECK', 'Century_AD', 'Test_JRW', 'cc865_sourceparam', 'Afton_B3_Opt_SQL', 'Creighton_RPS_All',
                      'Bogus_test', 'KBTraining', 'Seismic_LeeVille_', 'Simsa_MSOpt_SQL',
                      'Seismic_RedLake2_SMTI', 'Seismic_Goldcorp_SGM_SMTI', 'Cozamin_AD_SQL', 'Grosvenor_AD_SQL',
                      'Creighton_BackProc_SQL', 'Seismic_GBC_BlastsOnly', 'Creighton_BackPro_SGM',
                      'RedLake_SM_SQL', 'DMLZ_Online', 'Gualcamayo_AD_SQL', 'Seismic_GBC_BENNY', 'SantaMaria_SMTI_SQL',
                      'Totten_BENNY', 'North_BENNY', 'YoungDavidson_BENNY', 'LacDesiles_HISARD_SQL',
                      'Seismic_DMLZ_BENNY', 'Seismic_Garson_BlastsOnly', 'Catalina_AD_SQL', 'LasBambas_AD_SQL',
                      'CNL_AnnualAnalysis_SQL2', 'Seismic_Totten_BlastsOnly', 'Seismic_YD_BlastsOnly',
                      'Lalor_Opt_SQL', 'Analytics_Karari_Testing', 'Seismic_MGSALTER_DBO', 'dbo.aTest', 'AAABCtEST',
                      'RedLake_SM_Test_SQL', 'Goldcorp_SGM', 'Seismic_RedLake2_SMTI_m', 'SE_AD_SQL', 'ST_AD_SQL',
                      'CC880_VelOpt_SQL', 'Seismic_BogusAdvan', 'Leeville_Calib_SQL', 'Uchuchacua_AD_SQL',
                      'Macassa_SGMOpt_SQL', 'YoungDavidson_MSOptimization_SQL', 'Redlake2_SiteChampion_SQL',
                      'Penkas_Reproc_SQL', 'NickelRim_SMTI_SQL', 'Westwood_SGM_OPT', 'Cayuga_MGCS_Testing',
                      'Seismic_Dagangshan', 'Macassa_MS_SGMAtest2_SQL', 'Cozamin_MSOpt_SQL_v2',
                      'KLGold_PPV_Analysis', 'Macassa_SGMtesting_SQL', 'Macassa_MS_SGMAtest_SQL',
                      'Macassa_SGMAtesting2_SQL', 'Lalor_AD_SQL', 'Macassa_MS_SGMAtest3', 'Macassa_SGMAtesting3_SQL',
                      'Cozamin_MSOpt_SQL', 'Analytics_KarariSourceParam', 'Tantalum_3DVM_SQL', 'Seismic_Bogus22',
                      'SMTI_Aug_Backup', 'BG_3DVM_SQL', 'Redlake2_MSOpt_SQL', 'MOBColeman_MSOpt_SQL',
                      'Kidd_Pal_SQL', 'zzzCreightcopy', 'Jwaneng_AD_SQL', 'Alpayana_AD_SQL', 'SanRafael_3DVM_SQL',
                      'Seismic_Baikuang', 'Jansen_MSOpt_SQL', 'Westwood_SGM_Opt_SQL', 'Alpayana_SMTI_SQL',
                      'Goldex_Assessment_SQL', 'Niobec_NoiseTagging_SQL', 'Seismic_Optisol',
                      'Vivien_IL', 'Galena', 'Simsa_AD_SQL', 'Penkas_SeisWOpt_SQL', 'Alpayana_SMTI2_SQL',
                      'Lamaque_MS_Opt_SQL', 'Fletcher_AD_SQL', 'GarsonMSOpt_SQL', 'Niobec_NoiseTagging_Test_SQL',
                      'SanRafael_AD_SQL', 'SanRafael_AD_SQL2', 'GBC_SR', 'SeisAlertDB', 'NickelRimSMTI_Extnd',
                      'Seismic_GrasbergReg_AdvAn', 'Totten_SrcParamOpt_Feb22', 'Totten_SrcParamOpt_SGM',
                      'SantaMaria_ArrayDesign_SQL', 'Simsa_Mech_SQL', 'Redlake2_SMTI_Analysis_SQL', 'ODP_retrigger',
                      'DeepSouth_Sandbox', 'Gran_Colombia_Gold', 'LaCorada', 'LaCorada_AD', 'KucingLiar',
                      'KucingLiar_AD_SQL', 'DMLZ_SMTI_Extnd', 'DMLZ_Review2022', 'Dervish_Sandbox', 'LongNorth_Opt_SQL',
                      'LacDesIsles_Demo', 'Platinum_UF', 'Lamaque_Demo', 'Pal_Test', 'distribution',
                      '153Coleman_Analysis', 'CC810_MSOpt', 'Benny_FraserCopper', 'Benny_Stillwater',
                      'ODP_Seismicity_Analysis_SQL', 'Laronde_AD_2022_SQL', 'Cayuga_MGCS_OrigRPS', 'DMLZ_AW_CS_SQL',
                      'CC865_MSOpt', 'AuraMinerals_AD', 'Katanga', 'sgmkidd_sql', 'kidd_pal_SPOpt_SQL', 'KiddSGM_SPOpt',
                      'KiddSGM_SPOPT_SQL', 'Grafana_Dashboard', 'Benny_DMLZ', 'Benny_GBC', 'Benny_FraserMorgan',
                      'Benny_CC865', 'Benny_Garson', 'Benny_170Coleman', 'Benny_153Coleman', 'Benny_CC810',
                      'Benny_Laronde', 'Benny_Goldhunter', 'Benny_IslandGold', 'Benny_Karari', 'Benny_KLGold',
                      'Benny_LacDesIles', 'Benny_McCreedy', 'Benny_North', 'Benny_Redlake2', 'Benny_Simsa',
                      'Benny_Totten', 'Benny_Vivien', 'Benny_YoungDavidson', 'Benny_OnapingDepth']
    if todrop is None:
        todrop = default_todrop
    elif type(todrop) != list:
        raise ValueError('todrop must be a Python list')
    else:
        # combining the provided list with the existing one if required
        todrop = todrop + default_todrop
        todrop = np.unique(todrop)

    if print_todrop:
        print(todrop)

    # Take today's date and subtract
    starttime = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)

    # Show the start time (new sensors added after this date/time)
    print(starttime)

    # build the query to find all databases
    query = r"SELECT name, database_id, create_date FROM sys.databases"
    sqlstr = "mgs\\mgs"

    # getting all the databases
    dbs = sqlquery("master", query, sqlstr, debug=True)

    # Remove the databases to skip
    dbs = dbs[~dbs['name'].isin(todrop)]

    # Start with a blank dictionary
    allnewsensors = {}

    # Loop over each databases
    # load the ChanDiagnostics table
    # and figure out which sensors have been added since the start date
    # errors might pop up if the db is really old and doesn't have the ChanDiagnostics table
    # (that should be okay since it is an old site)
    queried_dbs = []
    bad_dbs = []
    pbar = tqdm(total=len(dbs), desc='Checking databases for new sensors')
    for idx, db in dbs.iterrows():
        dbname = db['name']
        queried_dbs.append(dbname)

        try:
            # reads in data from the channel diagnostics table of the dsn
            df = readsqlpd(dbname, table="ChanDiagnostics", sqlstr=sqlstr, print_warning=False)

            # groups sensor data by date?
            sen_statdategrp = df.groupby("SenID").StatDate.min().sort_values(ascending=False)

            # grabs sensors that are newer than the user defined start time
            newsensors = sen_statdategrp[sen_statdategrp > starttime]
            newsensors.rename("FirstOnline", inplace=True)

            # making a dictionary of all of them
            if len(newsensors) > 0:
                # allnewsensors[db['name']] = newsensors
                allnewsensors[dbname] = newsensors

        # catching errors where databases don't exist etc.
        except Exception as exp:
            bad_dbs.append(dbname)
            print("DB error with " + dbname)
            print(exp)

        pbar.update(1)

    # Summarize the results into a format that can be copied to an email
    print('=======================================================')
    for site in allnewsensors:
        print(site)
        # noinspection PyTypeChecker
        display(pd.DataFrame(allnewsensors[site]))
        print('=======================================================')
