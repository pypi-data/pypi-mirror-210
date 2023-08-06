# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 10:31:54 2019

@author: sara.brazille
"""
import datetime as dt
import matplotlib.pyplot as plt
from . import mathutil
from . import database
from os import name
import time
from .database import connectToDB
import os
import glob
import numpy as np
from datetime import timedelta
from obspy.core.util.misc import BAND_CODE
from obspy.clients.filesystem.sds import Client


class Gridspec:
    """
    Set extents of a grid, with grid points spaced at gridspc.
        Units are set here as well
    """
    # TODO: is this ever used?
    def __init__(self, n1, n2, e1, e2, d1, d2, gridspc, nanval=-1e+45, units='m'):
        """
        Set extents of a grid, with grid points spaced at gridspc.
        Units are set here as well
        """
        self.gridspc = gridspc  # spacing of grid
        self.n1 = n1  # minimum northing of grid
        self.n2 = n2  # maximum northing of grid
        self.e1 = e1
        self.e2 = e2
        self.d1 = d1
        self.d2 = d2
        self.nanval = nanval  # to use as nanval when reading/writing files
        self.nvs = np.arange(n1, n2+1., gridspc)  # coordinates for grid
        self.evs = np.arange(e1, e2+1., gridspc)
        self.dvs = np.arange(d1, d2+1., gridspc)
        self.units = units


class Limits:
    """
    Simple data class to store limits for graphs
    """
    def __init__(self, xMin=None, xMax=None,
                       yMin=None, yMax=None,
                       zMin=None, zMax=None):
        if (xMin is None) != (xMax is None):
            raise Exception('You can\'t set one x limit and not the other')
        if (yMin is None) != (yMax is None):
            raise Exception('You can\'t set one y limit and not the other')
        if (zMin is None) != (zMax is None):
            raise Exception('You can\'t set one z limit and not the other')
        self.xMin = xMin
        self.xMax = xMax
        self.yMin = yMin
        self.yMax = yMax
        self.zMin = zMin
        self.zMax = zMax


class DataOptions:
    """
    Simple data class to store data options for loading data
    """
    def __init__(self, DSN, stageDSN, types, sqlsrv, vfdb, svc, inPath):
        self.DSN = DSN
        self.stageDSN = stageDSN
        self.types = types
        self.sqlsrv = sqlsrv
        self.vfdb = vfdb
        self.svc = svc
        self.inPath = inPath


class PumpKeyNames:
    """
    Simple data class to store pump key names for extracting data from dfPump
    """
    def __init__(self, presKey, propconKey, flowKey):
        self.presKey = presKey
        self.propconKey = propconKey
        self.flowKey = flowKey


class Stages:
    """Template of a class to iterate over frac stages
    Example usage:
    for stage in sf.Stages(svcfilepath):
        events=sf.readsql('EOGNunnely','source',stage.starttime(),stage.endtime())
        print stage.name()+str(mean(events['MomentMagnitude']))
    
    Mike Preiksaitis. October 12, 2011
    re-written April 11, 2014 to account for move of stages and zones to db    
    """
    
    def __init__(self, dsn, sqlstr='FRAC\\FRAC', debug=False, domainauth=True):               

        if dsn is None:
            raise Exception("DSN is none and did not get passed to the Stages class.")

        if debug:
            print('Importing pandas')

        import pandas.io.sql as pd

        # connecting to the database
        cnxn = connectToDB(sqlstr, dsn)

        stgquery = "SELECT * FROM [Stages] ORDER BY [Start]"  # select all keys
        if debug: 
            print('Querying DB')
            
        self.stagesdf = pd.read_sql(stgquery, cnxn)

        if debug: 
            print('Done query. Closing connection')
            
        cnxn.close()
        if debug: 
            print('Connection closed')
        
        # Sort based on Start Time
        self.stagesdf.sort_values('Start')
        # Set index to first stage, or last stage read-in    
        self.nostages = len(self.stagesdf)
        self.index = -1
        
    def __iter__(self):
        return self
        
    def next(self):
        """
        Get next value
        :return:
        """
        self.index += 1
        if self.index > self.nostages-1:
            raise StopIteration 
        return self
    
    def prev(self):
        """
        Get previous value
        :return:
        """
        if self.index == 0:
            raise StopIteration
        self.index -= 1
        return self
        
    def name(self):
        """
        Get name of stage
        :return:
        """
        return self.stagesdf['Name'][self.index]
        
    def findstg(self, search):
        """
        Find specific stage
        :param search: condition to search by
        :return:
        """
        # if isinstance(search,unicode):
        #    search=np.str(search)
        # #above commented out because all strings are unicode in python3
        if isinstance(search, str):  # searching by stage name
            for i in range(0, self.nostages):
                if self.stagesdf['Name'].iloc[i] == search:
                    self.index = i
                    return self.name()
            raise LookupError('Stage not found: ' + search)                
        elif isinstance(search, dt.datetime):  # searching by datetime
            for i in range(0, self.nostages):
                if (search >= self.stagesdf['Start'][i]) and (search < self.stagesdf['End'][i]):
                    self.index = i
                    return self.name()
            raise LookupError('Stage not found at ' + str(search))
        else:
            Exception('Not a valid way to find a stage. Use a stage name or a DateTime')
        return

    def starttime(self):
        """
        Return start time
        :return:
        """
        return self.stagesdf['Start'][self.index]
        
    def endtime(self):
        """
        Return end time
        :return:
        """
        return self.stagesdf['End'][self.index]
        
    def endpumptime(self):
        """
        Return end of pump time
        :return:
        """
        return self.stagesdf['EndPump'][self.index]
        
    def colour(self):
        """
        Return colour
        :return:
        """
        return self.stagesdf['Colour'][self.index]
    
    def stageshift(self):
        """
        Return stage location shift
        :return:
        """
        return [self.stagesdf['ShiftN'][self.index],
                self.stagesdf['ShiftE'][self.index],
                self.stagesdf['ShiftD'][self.index]]


class Fraczones:
    """
    Class to iterate over and work with frac zones
    """
    def __init__(self, dsn, domainauth=True, sqlstr='FRAC\\FRAC'):

        import pandas.io.sql as pd

        # connecting to the database
        cnxn = connectToDB(sqlstr, dsn)

        # making the zone query
        zonequery = "SELECT * FROM [Stages] INNER JOIN [Zones] ON [Stages].[Name]=[Zones].[StageName]"
        # self.zonesdf = pd.read_frame(zonequery,cnxn) # deprecated in pandas 0.18
        self.zonesdf = pd.read_sql(zonequery, cnxn)
        cnxn.close()

        self.add_allmidpoints()

    def allzones(self):    
        """
        Return frac zone and stage info in Pandas format
        """
        return self.zonesdf
    
    def legacy(self):
        """
        Return frac zones in the old style way similar to when we used SVC files 
        
        This might be useful for scripts before April 2014        
        """
        return [self.zonesdf['StartN'],
                self.zonesdf['StartE'],
                self.zonesdf['StartD']],\
               [self.zonesdf['EndN'],
                self.zonesdf['EndE'],
                self.zonesdf['EndD']], self.zonesdf['ZoneID'], self.zonesdf['StartMD'], self.zonesdf['EndMD']
        
    def midpoint(self, stagename):
        """
        Find the N,E,D midpoint for selected stage
        """
        zones = self.zonesdf.loc[self.zonesdf['Name'] == stagename]
                
        start = list(zip(zones['StartN'], zones['StartE'], zones['StartD']))
        end = list(zip(zones['EndN'], zones['EndE'], zones['EndD']))
        
        north, east, depth = 0.0, 0.0, 0.0
        for i in range(0, len(zones)):
            north += (float(start[i][0]) + float(end[i][0]))/2
            east += (float(start[i][1]) + float(end[i][1]))/2
            depth += (float(start[i][2]) + float(end[i][2]))/2
            
        if len(start) > 0:
            north /= len(start)
            east /= len(start)
            depth /= len(start)         
        return (north, east, depth)

    def add_allmidpoints(self):
        """
        Add midpoints for all zones
        """

        # mid point for each zone
        self.zonesdf['N'] = 0.5 * (self.zonesdf.StartN + self.zonesdf.EndN)
        self.zonesdf['E'] = 0.5 * (self.zonesdf.StartE + self.zonesdf.EndE)
        self.zonesdf['D'] = 0.5 * (self.zonesdf.StartD + self.zonesdf.EndD)

        # mid point for each stage
        for stg in self.zonesdf['Name'].unique():
            i = self.zonesdf['Name'] == stg
            n, e, d = self.midpoint(stg)
            self.zonesdf.loc[i, 'stgN'] = n
            self.zonesdf.loc[i, 'stgE'] = e
            self.zonesdf.loc[i, 'stgD'] = d

    def zone(self, stagename):
        """
        Find the N,E,Ds for selected stage zone
        """
        zones = self.zonesdf.ix[self.zonesdf['Name'] == stagename]
        start = zip(zones['StartN'], zones['StartE'], zones['StartD'])
        end = zip(zones['EndN'], zones['EndE'], zones['EndD'])
        if len(start) > 0:
            if len(end) > 0:
                return (start[0], end[0])
        return ()


class Seisvis:
    """
    Template of class to read in any settings from Seisvis file
    
    Can read information about wells, etc...
    
    Historically (before April 11, 2014) this was part of the Stages class
    since the svcfile contained all information about stages and frac zones.
    """    

    def __init__(self, svcfile):
        import configparser

        self.config = configparser.ConfigParser()
        
        from os import name
        
        if name == 'posix':
            svcfile = Database.makeLinuxPath(svcfile)
        
        # error handling to try up to ten times to open svc file
        # network issues/multithreading issues can cause 
        nattempts = 10
        sleep = 0.5
        for i in range(0, nattempts):
            try:
                self.config.readfp(open(svcfile))      
            except Exception as exp:
                print("Attempt "+str(i+1)+"/"+str(nattempts)+" to load SVC file - "+str(exp))
                if i+1 == nattempts:
                    Exception("Cannot open SVC file. Tried "+str(i+1)+" times.")
                
                time.sleep(sleep)
                sleep *= 2
            else:
                # loaded successfully
                break
        
        # Read in Frac setup info (anything not stage specific)
        self.refwell = self.config.get('FRAC', 'FracCoordRefWellName')
        self.refprojection = self.config.get('FRAC', 'ProjectionSystem')
        self.refe = self.config.getfloat('FRAC', 'RefOrigenE')
        self.refn = self.config.getfloat('FRAC', 'RefOrigenN')
        self.refkb = self.config.getfloat('FRAC', 'KBElevation')
        self.refelev = self.config.getfloat('FRAC', 'KBHeight')
        self.fracloc = self.config.get('FRAC', 'FracInfoLocation')
        self.dsn = self.config.get('DATA_SOURCE', 'SITE DSNS')
        # self.zaxisdown=self.config.get('SITE_'+self.dsn[:-1],'SiteZAxisDown')

    def wellpaths(self):
        """ Function to return the paths of all treatment and observation wells.
            In addition, the indices for each column is returned.
        """
        wellinfo = {}
        
        ntreatmentwells = self.config.getint('FRAC', 'NumTreatmentWells')
        nobswells = self.config.getint('FRAC', 'NumObsWells')
        
        # Generate lists of treatment wells and obs wells
        twells = ['TreatmentWell' + str(i) for i in range(1, ntreatmentwells+1)]
        owells = ['ObsWell' + str(i) for i in range(1, nobswells+1)]
        
        for welli in twells+owells:  # Loop over obs wells
            wellid = self.config.get('FRAC', welli+'ID')
            wellfilename = self.config.get('FRAC', welli+'File')
            wellncol = self.config.getint('FRAC', welli+'NorthingCol')-1
            wellecol = self.config.getint('FRAC', welli+'EastingCol')-1
            welldcol = self.config.getint('FRAC', welli+'DepthCol')-1
            wellmdcol = self.config.getint('FRAC', welli+'MDCol')-1
            welldeviated = self.config.getboolean('FRAC', welli+'IsDeviated')
            welln = self.config.getfloat('FRAC', welli+'North')
            welle = self.config.getfloat('FRAC', welli+'East')
            welltop = self.config.getfloat('FRAC', welli+'Top')
            wellbottom = self.config.getfloat('FRAC', welli+'Bottom')
            wellskiplines = self.config.getint('FRAC', welli+'NumHeader')
            wellusecustomcolor = self.config.getint('FRAC', welli+'UseCustomColor')
            wellcustomcolor = self.config.getint('FRAC', welli+'CustomColor')
            # Put into dictionary            
            wellinfo[wellid] = welli, wellfilename, wellncol, wellecol, welldcol, wellmdcol, welldeviated,\
                welln, welle, welltop, wellbottom, wellskiplines, wellusecustomcolor, wellcustomcolor

        return wellinfo
 
    def ms2rbg(self, colorref):
        """
        Convert color ref to proper color
        :param colorref:
        :return:
        """
        return [((colorref >> 0) & 0xFF)/255, ((colorref >> 8) & 0xFF)/255, (colorref >> 16)/255]
    
    def wellinfo(self):
        """
            Return a pandas dataframe of well info.
            Essentially designed to return everything except deviations.
        """
        
        import pandas as pd
        df = pd.DataFrame(self.wellpaths())
        # flip dataframe, index is well name
        df = df.T
        # rename columns
        df.columns = ['welli', 'wellfilename', 'wellncol', 'wellecol', 'welldcol', 'wellmdcol', 'welldeviated',
                      'welln', 'welle', 'welltop', 'wellbottom', 'wellskiplines', 'wellusecustomcolor',
                      'wellcustomcolor']

        df['wellrgb'] = df.wellcustomcolor.apply(self.ms2rbg).apply(tuple)
        
        return df
    
    def wells(self, returnmd=False, debug=False):
        """
        The full deviation surveys are loaded in and returned in a dictionary.
        """
        deviations = {}
        wellpaths = self.wellpaths()
        for i in wellpaths:  # for each well read in the txt files
            welltype, wellfilename, wellncol, wellecol, welldcol, wellmdcol, welldeviated,\
                welln, welle, welltop, wellbottom, wellskiplines, wellusecustomcolor, wellcustomcolor = wellpaths[i]
            n, e, d, md = [], [], [], []
            if welldeviated:  # If a deviated well
                try:
                    if name == 'posix':
                        wellpathtoload = Database.makeLinuxPath(wellpaths[i][1])
                    else:
                        wellpathtoload = wellpaths[i][1]
                    f = open(wellpathtoload)
                    for j in range(0, wellskiplines):
                        f.readline()  # skip header lines
                    lines = f.readlines()
                    f.close()
                except:
                    print(wellpaths[i][1] + 'Fails')
                    lines = []
                if debug: 
                    print(wellfilename)
                for line in lines:
                    try:
                        if ',' in line:  # apparent you can use commas!
                            n.append(float(line.split(',')[wellncol]))
                            e.append(float(line.split(',')[wellecol]))
                            d.append(float(line.split(',')[welldcol]))
                            md.append(float(line.split(',')[wellmdcol]))
                        else:
                            n.append(float(line.split()[wellncol]))
                            e.append(float(line.split()[wellecol]))
                            d.append(float(line.split()[welldcol]))
                            md.append(float(line.split()[wellmdcol]))
                    except IndexError:
                        # Debugging help for strange characters in deviation files
                        print('IndexError in ' + str(i))
                        print('Path' + str(wellfilename))
                        print('line: + ' + str(line))
            else:  # If a vertical well
                for j in range(0, 2):
                    n.append(welln)
                    e.append(welle)
                d.append(welltop)
                d.append(wellbottom)    
            wellname = wellfilename.split('\\')[-1]
            
            if returnmd:
                deviations[wellname] = np.array(n), np.array(e), np.array(d), np.array(md)
            else:
                deviations[wellname] = np.array(n), np.array(e), np.array(d)
                    
        return deviations

    def plotwells(self, view='Plan', c='r', rot=0, plotwells=True, plotzones=True, ax=None):
        """
         Plot wells on an axes.

         Choose a view of:
             -Plan
             -Lateral, or
             -Transverse

         Use rot to rotate the well paths counter-clockwise
        """
        if ax is None:
            ax = plt.subplot(111)

        if plotwells:
            wells = self.wells()
            for well in wells:
                n, e, d = wells[well]
                newe, newn = MathUtil.rotatecoord(e, n, rot)
                if view == 'Plan' or view == 'p':
                    ax.plot(newe, newn, c=c)
                elif view == 'Lateral' or view == 'l':
                    ax.plot(newe, d, c=c)
                    plt.gca().invert_yaxis()
                elif view == 'Transverse' or view == 't':
                    ax.plot(newn, d, c=c)
                    plt.gca().invert_yaxis()
                else:
                    Exception('Please choose Plan, Lateral, or Transverse for the view')

        return ax


class LocalClient(Client):
    """
    Version of obspy client for IRIS file ISM data
    """
    def __init__(self, root, fmt, **kwargs):
        """
        Parameters:
        -----------
        root: str
            Path where is located the Local structure
        fmt: str
            The parameter should name the corresponding keys of the stats object, e.g.
            "{year}-{month:02d}/{year}-{month:02d}-{day:02d}/{network}.{station}.{location}.{channel}.{year}.{julday:03d}"

        **kwargs SDS client additional args
        """
        self.root = root
        self.fmt = fmt
        super().__init__(root, **kwargs)

    def _get_filenames(self, network, station, location, channel, starttime,
                       endtime, sds_type=None):
        """
        Get list of filenames for certain waveform and time span.
        :type network: str
        :param network: Network code of requested data (e.g. "IU").
        :type station: str
        :param station: Station code of requested data (e.g. "ANMO").
        :type location: str
        :param location: Location code of requested data (e.g. "").
        :type channel: str
        :param channel: Channel code of requested data (e.g. "HHZ").
        :type sds_type: str
        :param starttime: start time of window
        :param endtime: end time of window
        :param sds_type: None
        :rtype: str
        """
        sds_type = sds_type or self.sds_type
        # SDS has data sometimes in adjacent days, so also try to read the
        # requested data from those files. Usually this is only a few seconds
        # of data after midnight, but for now we play safe here to catch all
        # requested data (and with MiniSEED - the usual SDS file format - we
        # can use starttime/endtime kwargs anyway to read only desired parts).
        year_doy = set()
        # determine how far before starttime/after endtime we should check
        # other dayfiles for the data
        t_buffer = self.fileborder_samples / BAND_CODE.get(channel[:1], 20.0)
        t_buffer = max(t_buffer, self.fileborder_seconds)
        t = starttime - t_buffer
        t_max = endtime + t_buffer
        # make a list of year/doy combinations that covers the whole requested
        # time window (plus day before and day after)
        while t < t_max:
            year_doy.add((t.year, t.month, t.day, t.julday))
            t += timedelta(days=1)
        year_doy.add((t_max.year, t_max.month, t_max.day, t_max.julday))

        full_paths = set()
        for year, month, day, doy in year_doy:
            filename = self.fmt.format(
                network=network, station=station, location=location,
                channel=channel, year=year, month=month,
                day=day, julday=doy, sds_type=sds_type)
            full_path = os.path.join(self.sds_root, filename)
            full_paths = full_paths.union(glob.glob(full_path))

        return full_paths

    def _get_filename(self, network, station, location, channel, ttime, sds_type=None):
        """
        Get filename for certain waveform.
        :type network: str
        :param network: Network code of requested data (e.g. "IU").
        :type station: str
        :param station: Station code of requested data (e.g. "ANMO").
        :type location: str
        :param location: Location code of requested data (e.g. "").
        :type channel: str
        :param channel: Channel code of requested data (e.g. "HHZ").
        :type ttime: :class:`~obspy.core.utcdatetime.UTCDateTime`
        :param ttime: Time of interest.
        """
        sds_type = sds_type or self.sds_type
        filename = self.fmt.format(
            network=network, station=station, location=location,
            channel=channel, year=ttime.year, month=ttime.month,
            day=ttime.day, doy=ttime.julday, sds_type=sds_type)
        return os.path.join(self.sds_root, filename)
