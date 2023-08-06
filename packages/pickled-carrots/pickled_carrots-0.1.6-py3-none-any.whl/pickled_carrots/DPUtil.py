# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 14:12:37 2019

@author: sara.brazille
"""

import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib
import datetime as dt
import pylab as py
import pandas as pd
from . import mathutil
from . import database
# import scipy
import scipy.signal
from ternary.helpers import project_sequence
from ternary.helpers import simplex_iterator
import re
# import mplstereonet
import sys


def sorted_nicely(l): 
    """ Sort the given iterable in the way that humans expect.""" 
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def printAllStages(dataOptions):
    """
    Print a list of all stages so that it can be used to create an array
    in notebooks of the stages to be selected
    """
    dfevents, dfstages = Database.loadEventAndStageData(dataOptions.DSN,
                                                        stageDSN=dataOptions.stageDSN,
                                                        types=dataOptions.types,
                                                        sqlsrv=dataOptions.sqlsrv,
                                                        stageNames=None)
    print(dfevents['FRAC_STAGE_ID'].unique())


def intervalSetup(intervalWidth, intervals, df, column, minX=None, maxX=None):
    
    """
    Set up intervalWidth and number of intervals based on only one given
    
    Inputs
    ======
    intervalWidth : scalar
        Width of each interval
    intervals : int
        Number of intervals
    df : pandas.DataFrame
        Input dataframe to use for interval calculation
    column : string
        Column in dataframe to use for interval calculation
    
    Returns
    =======
    intervalWidth : scalar
        Calculated width of each interval
    intervals : int
        Calculated number of intervals
    
    Dependencies
    ============
    math.ceil
    """
    
    x_min = df[column].min()
    x_max = df[column].max()
    
    if minX is not None:
        x_min = minX
    if maxX is not None:
        x_max = maxX
    
    # Set up intervalWidth with intervals = 20 if no width or number given
    if intervalWidth == 0 and intervals == 0:
        intervals = 20
        intervalWidth = (x_max - x_min)/20
        intervalWidth = roundToOneSignificantFigure(intervalWidth)
        return intervalWidth, intervals
      
    # If intervals given, calculate width
    if intervals != 0:
        intervalWidth = (x_max - x_min)/intervals
        return intervalWidth, intervals
    
    # if width given, calculate intervals
    else:
        intervals = int(math.ceil((x_max - x_min) / intervalWidth))
        return intervalWidth, intervals

    
def normalizeDataBySpecifiedStages(df, stages=None):
    
    """
    Ternary normalize  DI, SI, and PI columns by a range of stages
    
    Inputs
    ======
    df : pandas.DataFrame
        Input dataframe to normalize
    stages : list
        List of strings that correspond to 'FRAC_STAGE_ID's
    
    Returns
    =======
    df : pandas.DataFrame
        Normalized dataframe
    
    Dependencies
    ============
    math.ceil
    """
    
    if len(stages) == 0 or stages is None:
        print('You must specify stage names to use for the normalization process')
        return
    
    # Take the log of each value
    # It might already exist, but for simplicity sake, assume it doesn't
    df['logPI'] = np.log10(df['PlasticityIndex'])
    df['logDI'] = np.log10(df['DiffusionIndex'])
    df['logSI'] = np.log10(df['StressIndex'])
    
    df['norm_logPI'] = 0
    df['norm_logSI'] = 0
    df['norm_logDI'] = 0
     
    dftemp = df[df['FRAC_STAGE_ID'].isin(stages)]
            
    # Put each between 1 and 0
    df['norm_logPI'] = (df['logPI'].values - min(dftemp['logPI'])) / (max(dftemp['logPI']) - min(dftemp['logPI']))
    df['norm_logDI'] = (df['logDI'].values - min(dftemp['logDI'])) / (max(dftemp['logDI']) - min(dftemp['logDI']))
    df['norm_logSI'] = (df['logSI'].values - min(dftemp['logSI'])) / (max(dftemp['logSI']) - min(dftemp['logSI']))
    
    # Ternary normalize so PI + DI + SI = 1.0
    df['TI'] = df['norm_logPI'] + df['norm_logDI'] + df['norm_logSI']
    df['norm_logPI'] /= df['TI']
    df['norm_logDI'] /= df['TI']
    df['norm_logSI'] /= df['TI']
    
    print()
    print("Complete!")
    
    return df
    

def normalizeData(df, byStage=False):
    
    """
    Ternary normalize  DI, SI, and PI columns
    
    Inputs
    ======
    df : pandas.DataFrame
        Input dataframe to normalize
    byStage : bool, optional
        Should the data be normalized by stage, or over the whole dataset
    
    Returns
    =======
    df : pandas.DataFrame
        Normalized dataframe
    
    Dependencies
    ============
    math.ceil
    """
    
    # Take the log of each value
    # It might already exist, but for simplicity sake, assume it doesn't
    df['logPI'] = np.log10(df['PlasticityIndex'])
    df['logDI'] = np.log10(df['DiffusionIndex'])
    df['logSI'] = np.log10(df['StressIndex'])
    
    df['norm_logPI'] = 0
    df['norm_logSI'] = 0
    df['norm_logDI'] = 0
     
    # Normalize
    if byStage is True:
        
        print('Normalizing by stage')
        printProgressBar(0, len(df['FRAC_STAGE_ID'].unique()) - 1, 
                         prefix='Progress:', suffix='Complete',
                         length=50)
        cur_stage_index = 0
        for name, group in df.groupby('FRAC_STAGE_ID'):
            tempdf = df.loc[group.index]
            # Put each between 1 and 0
            df.loc[group.index, 'norm_logPI'] = (tempdf['logPI'].values - min(tempdf['logPI'])) / \
                                                (max(tempdf['logPI']) - min(tempdf['logPI']))
            df.loc[group.index, 'norm_logDI'] = (tempdf['logDI'].values - min(tempdf['logDI'])) / \
                                                (max(tempdf['logDI']) - min(tempdf['logDI']))
            df.loc[group.index, 'norm_logSI'] = (tempdf['logSI'].values - min(tempdf['logSI'])) / \
                                                (max(tempdf['logSI']) - min(tempdf['logSI']))
            cur_stage_index = cur_stage_index + 1
            printProgressBar(cur_stage_index, len(df['FRAC_STAGE_ID'].unique()),
                             prefix='Progress:', suffix='Complete',
                             length=50)
            
    else:
        # Put each between 1 and 0
        df['norm_logPI'] = (df['logPI'].values-min(df['logPI']))/(max(df['logPI'])-min(df['logPI']))
        df['norm_logDI'] = (df['logDI'].values-min(df['logDI']))/(max(df['logDI'])-min(df['logDI']))
        df['norm_logSI'] = (df['logSI'].values-min(df['logSI']))/(max(df['logSI'])-min(df['logSI']))
    
    # Ternary normalize so PI + DI + SI = 1.0
    df['TI'] = df['norm_logPI']+df['norm_logDI']+df['norm_logSI']
    df['norm_logPI'] /= df['TI']
    df['norm_logDI'] /= df['TI']
    df['norm_logSI'] /= df['TI']
    
    print()
    print("Complete!")
    
    return df


def listsToListOfTuples(list1, list2, list3):
    
    """
    Literally just transpose these lists in a single 2D array
    """
    
    tuplelist = np.array([list1, list2, list3])
    return tuplelist.T


def dfColumnsToListOfTuples(df, column1, column2, column3, scale=1):
    
    """
    Literally just transpose these columns in a single 2D array
    """
    
    tuplelist = np.array([(df[column1]*scale).values, (df[column2]*scale).values, (df[column3]*scale).values])
    return tuplelist.T


def generateColourScalars(df, column, dfStage=None):
    
    """
    Literally just turn a dataframe column to a list 
    """
    
    if column == 'Stage Database Colour':
        colours = []
        for index, row in df.iterrows():
            r = dfStage.loc[row['FRAC_STAGE_ID'], 'Colour_R']/256.00
            g = dfStage.loc[row['FRAC_STAGE_ID'], 'Colour_G']/256.00
            b = dfStage.loc[row['FRAC_STAGE_ID'], 'Colour_B']/256.00
            colours.append([r, g, b])
        return colours
    else:
        if df.shape[0] == 0:
            return []    
        else:
            return df[column].tolist()


def printProgressBar (iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    
    """
    # TODO this progress bar should probably be replaced with tqdm functions
    https://gist.github.com/giantas/e2b3c7bc1229478b966394d10925130d
    
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    if total > 0:
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledlength = int(length * iteration // total)
        bar = fill * filledlength + '-' * (length - filledlength)
        # Spyder says this is invalid syntax. It's not, it runs just fine
        print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
        # Print New Line on Complete
        if iteration == total: 
            print()
            
    sys.stdout.flush()


def dfBetweenTwoValues(df, column, value1, value2):
    
    """
    Get dataframe rows where specified column values
    are between value1 and value2
    """
    
    truthtable = (df[column] > value1) & (df[column] < value2)
    return df[truthtable]


def roundToOneSignificantFigure(x):
    
    """
    Does what it says in the function name
    """
    # TODO there are better functions for this
    
    return round(x, -int(math.floor(math.log10(abs(x)))))


def removeSPchar(stringIn):
    
    """
    Remove special characters that can't be in file names
    
    Inputs
    ======
    stringIn : string
        String that might have special path characters in it
        
    Returns
    ======
    stringOut : string
        String that does not have special path characters in it
    """
    
    return stringIn.replace(' ', '').replace('/', '').replace('.', '').replace('^', '').replace('(', '').replace(')',
                                                                                                                 '')


def pointInBox(point, box):
    """
    Return True or False, depending on if the point given is in face, in the box
    
    point is a list like this -> [x, y]
    box is a list like this -> [x1, y1, x2, y2]
    """
    
    xinbox = ((point[0] > box[0]) & (point[0] < box[2]))
    yinbox = ((point[1] > box[1]) & (point[1] < box[3]))
    
    return (xinbox & yinbox)


def ternaryDensity(i, j, k, x, y, z, scale):
    # TODO: proper ternary space?
    
    """
    Take the euclidean distance between all points then adds them up so that
    every point 1/10 of the scale away is worth half as much density
    
    Treats ternary variable space as 3D space, even though it 100% isn't
    
    i, j, k : Point to analyze density around
    x, y, z : Lists of point values that are on the ternary plot
    scale : Limit of the ternary plot
    
    """
    if len(x) != len(y):
        raise Exception("in ternaryDensity x and y have different lengths")
    if len(y) != len(z):
        raise Exception("in ternaryDensity y and z have different lengths")

    distance = 0
    for index in range(len(x)):
        try:
            pointdistance = (x.iloc[index]-i)**2 + (y.iloc[index]-j)**2 + (z.iloc[index]-k)**2
            distance = distance + (1.0/math.pow(2.0, 10.0*(pointdistance/(scale**2))))
        except KeyError:
            print("Key Error with index: " + str(index))
            print("len of x " + str(len(x)))
            print("len of y " + str(len(y)))
            print("len of z " + str(len(z)))
            print("i " + str(i))
            print("j " + str(j))
            print("k " + str(k))
            print("dtype of x "+str(type(x)))
            print("dtype of y " + str(type(y)))
            print("dtype of z " + str(type(z)))
            print("dtype of i " + str(type(i)))
            print("dtype of j " + str(type(j)))
            print("dtype of k " + str(type(k)))

        return distance


def color_point(d, distances, colourMap):
    """
    Colour a point d in distances based on it's normalized value interpolated
    between red and blue
    """
    cmap = matplotlib.cm.get_cmap(colourMap)

    lendist = len([x for x in distances if x is not None])

    if distances is None:
        return (1.0, 1.0, 1.0, 1.0)

    if lendist > 1:
        mindist = min(x for x in distances if x is not None)
        maxdist = max(x for x in distances if x is not None)

        if (maxdist - mindist) != 0:
            colourscalar = (d - min(distances))/(max(distances) - min(distances))
            colour = list(cmap(colourscalar))
            colour[3] = 0.2
            return colour

    return (1.0, 1.0, 1.0, 1.0)


def generate_heatmap_data(x, y, z, scale, colourMap):
    
    """
    Ternary normalize  DI, SI, and PI columns
    
    Inputs
    ======
    x, y, z : lists
        Lists of point variables to use for density calculations
    scale : int
        Number of samples to use for heatmap calculation
    colourMap: string
        color map to use in plot
    
    
    Returns
    =======
    d : dict
        Dictionary of structure {(i, j, k): density}
    
    Dependencies
    ============
    ternary.helpers.simplex_iterator
    """

    d = dict()
    distances = []
    for (i, j, k) in simplex_iterator(scale):
        d[(i, j, k)] = ternaryDensity(i, j, k, x, y, z, scale)
        distances.append(d[(i, j, k)])

    # debug understand
    if any(distances) is None:
        print("# of distances: " + str(len(distances)))
        print(distances)
        print("type: "+str(type(distances)))

    for (i, j, k) in simplex_iterator(scale): 
        d[(i, j, k)] = color_point(d[(i, j, k)], distances, colourMap)

    return d


def smoothPointsByInterval(x, y, interval):
    
    """
    Smooths data by changing the y values to the average of the interval given
    
    Inputs
    ======
    x, y : lists
        List of points to smooth
    interval : int
        How many points to the left and right of the point being sampled to 
        ues for smoothing
    
    
    Returns
    =======
    xOut, yOut : lists
        Lists of smoothed points
    """
    
    xout = []
    yout = []
    
    xout.append(x[0])
    yout.append(y[0])
    
    point_to_smooth = interval
    while point_to_smooth < len(y):
        
        # Smooth points by taking a number of points to the left and right
        # defined by interval and averaging them
        if point_to_smooth + interval < len(y):
            points_to_average_x = x[point_to_smooth - interval:point_to_smooth + interval]
            points_to_average_y = y[point_to_smooth - interval:point_to_smooth + interval]
            
            averagex = sum(points_to_average_x)/len(points_to_average_x)
            averagey = sum(points_to_average_y)/len(points_to_average_y)
            
            xout.append(averagex)
            yout.append(averagey)
            
        # Clip sample to dataset when at the end
        else:
            points_to_average_x = x[point_to_smooth - interval:len(y)]
            points_to_average_y = y[point_to_smooth - interval:len(y)]
            
            averagex = sum(points_to_average_x)/len(points_to_average_x)
            averagey = sum(points_to_average_y)/len(points_to_average_y)
            
            xout.append(averagex)
            yout.append(averagey)
        
        point_to_smooth = point_to_smooth + interval
    
    # Add the last point
    xout.append(x[-1])
    yout.append(y[-1])
    
    return xout, yout


def addTrendLineToTernaryPlot(tax, df, independantVariable, numPoints=40):
    
    """
    Adds a trend line to a ternary plot
    
    'Someone needs to give Sara Brazille a medal for this'
                                            -Sara Brazille 2019
    
    Inputs
    ======
    tax : ternary.TernaryAxesSubplot
        Ternary plot to put the trend line on
    df : pandas.DataFrame
        Dataframe to take DI, SI, and PI values from
    independantVariable : string
        Dataframe column to take the data from that will be used to make the
        trend line
    
    Returns
    =======
    None, just plots the trend line
    """
    
    # Sort the data by the variable we're going to be
    # using to plot the trend line
    df_clusters_sorted_by_colour = df.sort_values(independantVariable)
    
    # Get the data interval width to make 100ish ponits on a line
    line_interval = (df_clusters_sorted_by_colour[independantVariable].max()
                     - df_clusters_sorted_by_colour[independantVariable].min())/numPoints
    
    # Smooth the ternary plot data by scalar interval buckets to see the trend
    # in the specified variable
    line_di, line_si, line_pi, colourscalars = \
        smoothTernaryByScalarInterval(df_clusters_sorted_by_colour, independantVariable, line_interval)
    
    windowlength = numPoints - 12
    
    if windowlength % 2 == 0:
        windowlength += 1
        
    print(len(line_di))
    print(windowlength)
    
    # Smooth the data further, this time using Savitzky-Golay smoothing
    line_di_smooth, line_si_smooth, line_pi_smooth = \
        smoothTernaryPoints(line_di, line_si, line_pi, window=windowlength)
    
    # Convert the data to a list of tuples to be plotted as the line
    linepoints = listsToListOfTuples(line_di_smooth, line_si_smooth, line_pi_smooth)
    # '#b3cfdd'
    # Plot the line
    tax.plot(linepoints, color='k', linewidth=4, aa=True)  # line edge
    tax.plot(linepoints, color='k', linewidth=3, aa=True)  # line body
    xs, ys = project_sequence(linepoints)
    tax.get_axes().arrow(xs[-1], ys[-1], xs[-1] - xs[-2], ys[-1] - ys[-2], width=0.008, edgecolor='k', facecolor='k',
                         zorder=10)


def smoothTernaryPoints(x, y, z, window=35, polyOrder=4):
    # TODO: maybe apply it to all 3 then renormalize them?
    """
    Applies a Savitzky-Golay filter to the data in x and y and z, then
    renormalizes all 3
    """
    
    print(len(x))
    
    xout = scipy.signal.savgol_filter(x, window, polyOrder)
    yout = scipy.signal.savgol_filter(y, window, polyOrder)
    zout = scipy.signal.savgol_filter(z, window, polyOrder)
    
    ternaryvalues = xout + yout + zout
    
    xout /= ternaryvalues
    yout /= ternaryvalues
    zout /= ternaryvalues
    
    return xout, yout, zout
        

def findKeys(keyWord, inKeys):
    
    """
    Search a list of strings for keywords, case insensitive
    """
    
    import re

    # inKeys=df.keys()
    foundkeys = []
    for val in inKeys:
        if re.search(keyWord, val, re.IGNORECASE):
        
            # if val==keyWord:
            foundkeys.append(val)
    return foundkeys


def alphanumericsort(l):
    """ Sort the given iterable in the way that humans expect.""" 
    import re
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def dateTimeToString(dateTime):
    return dateTime.strftime('%Y/%m/%d, %I:%M:%S %p')


def trgid2hsf(dsn, trgid):
    """
    Convert a DateTime into a hsf filename
    """
    filename = dsn+str(trgid)[2:]+'.hsf'
    return filename


def trgid2hsfpath(dsn, trgid, rootpath='\\\\esg_utils.net\\datashare\\frac'):
    """
    Convert a DateTime into a full hsf path
    """
    if rootpath[-1] not in ['\\', '/']:
        rootpath += '\\'
    yr, mn, day = trgid[0:4], trgid[4:6], trgid[6:8]
    filepath = rootpath + dsn + '\\' + yr + '\\' + mn + '\\' + day + '\\' + trgid2hsf(dsn, trgid)
    return filepath


# <codecell> Ternary downsampling methods
def smoothTernaryByDataInterval(df, independantVariable, interval):
    
    """
    Smooths The ternary data by taking a window of points of interval length on
    each side of the point being sampled and averaging them
    
    Inputs
    ======
    df : pandas.DataFrame
        Dataframe to get the DI, SI, and PI values from
    independantVariable : string
        Extra variable to output the smoothing results of 
        The data is smoothed across which ever variable the dataframe is sorted
        by, this input has no effect on how it's smoothed
    interval : int
        How many points to the left and right of each point being
        sampled to use
    
    
    Returns
    =======
    DIOut, SIOut, PIOut, independantVariableOut : lists
        Lists of smoothed data
    """
    # Expects data to be sorted by independantVariable
    
    di = df['norm_logDI'].values
    si = df['norm_logSI'].values
    pi = df['norm_logPI'].values
    independant_variable_list = df[independantVariable].values
    
    independant_variable_out = []
    di_out = []
    si_out = []
    pi_out = []
    
    # Add the first point without averaging it as an "anchor" point
    independant_variable_out.append(independant_variable_list[0])
    di_out.append(di[0])
    si_out.append(si[0])
    pi_out.append(pi[0])
    
    # Average the points within the current interval, add the result as a point
    # in the resulting array, move to the next interval
    point_to_smooth = interval
    while point_to_smooth < len(independant_variable_list):
        
        if point_to_smooth + interval < len(independant_variable_list):
            points_to_average_di = di[point_to_smooth - interval:point_to_smooth + interval]
            points_to_average_si = si[point_to_smooth - interval:point_to_smooth + interval]
            points_to_average_pi = pi[point_to_smooth - interval:point_to_smooth + interval]
            points_to_average_iv = independant_variable_list[point_to_smooth - interval:point_to_smooth + interval]
            
        else:
            points_to_average_di = di[point_to_smooth - interval:len(independant_variable_list)]
            points_to_average_si = si[point_to_smooth - interval:len(independant_variable_list)]
            points_to_average_pi = pi[point_to_smooth - interval:len(independant_variable_list)]
            
            # Note, ternary values do not need to be renormalized, taking an
            # average of ternary values necesarily makes the output normalized
            points_to_average_iv = independant_variable_list[point_to_smooth - interval:len(independant_variable_list)]
            
        average_di = sum(points_to_average_di)/len(points_to_average_di)
        average_si = sum(points_to_average_si)/len(points_to_average_si)
        average_pi = sum(points_to_average_pi)/len(points_to_average_pi)
        average_iv = sum(points_to_average_iv)/len(points_to_average_iv)
        
        di_out.append(average_di)
        si_out.append(average_si)
        pi_out.append(average_pi)
        independant_variable_out.append(average_iv)
        
        point_to_smooth = point_to_smooth + interval
    
    # Add the end point without averaging it as an "anchor" point
    independant_variable_out.append(independant_variable_out[-1])
    di_out.append(di[-1])
    si_out.append(si[-1])
    pi_out.append(pi[-1])
    
    return di_out, si_out, pi_out, independant_variable_out


def selectFirstFromTernaryByDataInterval(df, independantVariable, interval):
    
    """
    Samples The ternary data by taking a window of points of interval length on
    each side of the point being sampled and selecting the first datapoint
    
    Inputs
    ======
    df : pandas.DataFrame
        Dataframe to get the DI, SI, and PI values from
    independantVariable : string
        Extra variable to output the smoothing results of 
        The data is smoothed across which ever variable the dataframe is sorted
        by, this input has no effect on how it's sampled
    interval : int
        How many points to the left and right of each point being
        sampled to use
    
    
    Returns
    =======
    DIOut, SIOut, PIOut, independantVariableOut : lists
        Lists of sampled data
    """
    
    di = df['norm_logDI'].values
    si = df['norm_logSI'].values
    pi = df['norm_logPI'].values
    independant_variable_list = df[independantVariable].values
    
    independant_variable_out = []
    di_out = []
    si_out = []
    pi_out = []
    
    # Keep taking buckets of values going up by a certain interval and selecting
    # the first value from that bucket
    point_to_select = 0
    while point_to_select < len(independant_variable_list):
        first_di = di[point_to_select]
        first_si = si[point_to_select]
        first_pi = pi[point_to_select]
        first_iv = independant_variable_list[point_to_select]
        
        di_out.append(first_di)
        si_out.append(first_si)
        pi_out.append(first_pi)
        independant_variable_out.append(first_iv)
        
        point_to_select = point_to_select + interval
    
    # Add the end point without averaging it as an "anchor" point
    independant_variable_out.append(independant_variable_out[-1])
    di_out.append(di[-1])
    si_out.append(si[-1])
    pi_out.append(pi[-1])
    
    return di_out, si_out, pi_out, independant_variable_out


def smoothTernaryByScalarInterval(df, independantVariable, interval, downsampleVariable=None):
    """
    Smooths the ternary data by taking ponits inside of each scalar interval
    and averaging them
    
    Inputs
    ======
    df : pandas.DataFrame
        Dataframe to get the DI, SI, and PI values from
    independantVariable : string
        Extra variable to output the smoothing results of
    interval : int
        How many points to the left and right of each point being
        sampled to use
    downsampleVariable : string, optional
        The variable to average across
    
    Returns
    =======
    DIOut, SIOut, PIOut, independantVariableOut : lists
        Lists of smoothed data
    """
    
    if downsampleVariable is None:
        downsampleVariable = independantVariable
        
    independant_variable_out = []
    di_out = []
    si_out = []
    pi_out = []
    
    # Add the first point without averaging it as an "anchor" point
    independant_variable_out.append(df[independantVariable].values[0])
    di_out.append(df['norm_logDI'].values[0])
    si_out.append(df['norm_logSI'].values[0])
    pi_out.append(df['norm_logPI'].values[0])
    
    # Average the points within the current interval, add the result as a point
    # in the resulting array, move to the next interval
    point_to_smooth = interval
    while point_to_smooth < df[downsampleVariable].max():
        
        minvalue = point_to_smooth - interval
        maxvalue = point_to_smooth + interval
        dfcur = dfBetweenTwoValues(df, downsampleVariable, minvalue, maxvalue)
        
        if dfcur.shape[0] > 0:
            points_to_average_di = dfcur['norm_logDI'].values
            points_to_average_si = dfcur['norm_logSI'].values
            points_to_average_pi = dfcur['norm_logPI'].values
            points_to_average_iv = dfcur[independantVariable].values
                
            average_di = sum(points_to_average_di)/len(points_to_average_di)
            average_si = sum(points_to_average_si)/len(points_to_average_si)
            average_pi = sum(points_to_average_pi)/len(points_to_average_pi)
            
            # Note, ternary values do not need to be renormalized, taking an
            # average of ternary values necesarily makes the output normalized
            average_iv = sum(points_to_average_iv)/len(points_to_average_iv)
            
            di_out.append(average_di)
            si_out.append(average_si)
            pi_out.append(average_pi)
            independant_variable_out.append(average_iv)
        
        point_to_smooth = point_to_smooth + interval
    
    # Add the end point without averaging it as an "anchor" point
    independant_variable_out.append(df[independantVariable].values[-1])
    di_out.append(df['norm_logDI'].values[-1])
    si_out.append(df['norm_logSI'].values[-1])
    pi_out.append(df['norm_logPI'].values[-1])
    
    return di_out, si_out, pi_out, independant_variable_out


def selectFirstFromTernaryByScalarInterval(df, independantVariable, interval, downsampleVariable=None):
    """
    Samples the ternary data by taking ponits inside of each scalar interval
    and selecting the first
    
    Inputs
    ======
    df : pandas.DataFrame
        Dataframe to get the DI, SI, and PI values from
    independantVariable : string
        Extra variable to output the sampling results of
    interval : int
        How many points to the left and right of each point being
        sampled to use
    downsampleVariable : string, optional
        The variable to downsample across
    
    Returns
    =======
    DIOut, SIOut, PIOut, independantVariableOut : lists
        Lists of sampled data
    """
    
    # If no downsample variable specified, take the independant variable as it
    if downsampleVariable is None:
        downsampleVariable = independantVariable
        
    independant_variable_out = []
    di_out = []
    si_out = []
    pi_out = []
    
    # Set up the initial sample mid-point
    point_to_select_around = interval
    
    # Keep taking buckets of values going up by a certain interval and selecting
    # the first value from that bucket
    while point_to_select_around < df[downsampleVariable].max():
        
        minvalue = point_to_select_around - interval
        maxvalue = point_to_select_around + interval
        dfcur = dfBetweenTwoValues(df, downsampleVariable, minvalue, maxvalue)
        
        if dfcur.shape[0] > 0:
            points_to_select_from_di = dfcur['norm_logDI'].values
            points_to_select_from_si = dfcur['norm_logSI'].values
            points_to_select_from_pi = dfcur['norm_logPI'].values
            points_to_select_from_iv = dfcur[independantVariable].values
                
            first_di = points_to_select_from_di[0]
            first_si = points_to_select_from_si[0]
            first_pi = points_to_select_from_pi[0]
            first_iv = points_to_select_from_iv[0]
            
            di_out.append(first_di)
            si_out.append(first_si)
            pi_out.append(first_pi)
            independant_variable_out.append(first_iv)
        
        point_to_select_around = point_to_select_around + interval
    
    # Add the end point without averaging it as an "anchor" point
    independant_variable_out.append(df[independantVariable].values[-1])
    di_out.append(df['norm_logDI'].values[-1])
    si_out.append(df['norm_logSI'].values[-1])
    pi_out.append(df['norm_logPI'].values[-1])
    
    return di_out, si_out, pi_out, independant_variable_out


def downsampleDataFrame(df, interval):
    
    """
    # TODO documentation needed
    """
    
    return df.iloc[::interval, :]

# <codecell> Math functions


def calcEllipsoidESG(row, ekeys, flipud=False):
    """
    Calculate components of esg format error ellipsoid. Keys must be in order:
        - lengths of principal vectors
        - N,E,D components of principal unit vectors, in same order as lengths
    
    For example:
    
    keys = ['Max length','Mid length','Min length','Max Vector N','Max Vector E','Max Vector D',
            'Mid Vector N','Mid Vector E','Mid Vector D','Min Vector N','Min Vector E','Min Vector D']
    
    Vectors are assumed to be orthonormal! For example, the eigenvalues returned
    from PCA decomposition.
    
    Outputs are in order [NN,EE,DD,NE,ND,ED].
    """
    p = np.mat([[row[ekeys[3]], row[ekeys[6]], row[ekeys[9]]],
                [row[ekeys[4]], row[ekeys[7]], row[ekeys[10]]],
                [row[ekeys[5]], row[ekeys[8]], row[ekeys[11]]]])
    d = np.mat([[row[ekeys[0]]**2, 0, 0], [0, row[ekeys[1]]**2, 0], [0, 0, row[ekeys[2]]**2]])
    
    cov = p * d * p.T
    nn = np.sqrt(cov[0, 0])
    ee = np.sqrt(cov[1, 1])
    dd = np.sqrt(cov[2, 2])
    ne = cov[0, 1] / nn / ee
    nd = cov[0, 2] / nn / dd
    ed = cov[1, 2] / ee / dd
    
    return pd.Series({'1-NN': nn, '2-EE': ee, '3-DD': dd, '4-NE': ne, '5-ND': nd, '6-ED': ed})


def energyindex(data, qcplot=False, plteqn=False):
    """ Calculate energy index for db
    
    Give this function the output from sf.readsql or sf.readsqlpd    
    It will return the energyindex
    
    qcplot=True produces a crossplot"""
    # import scipy
    import scipy.stats
    l_en = np.log10(data['Energy'])
    l_mo = np.log10(data['SeiMoment'])
    igood = (np.isfinite(l_mo) & np.isfinite(l_en))
    a, b, rsq, pval, std = scipy.stats.linregress(l_mo[igood], l_en[igood])
    l_mo_min = np.floor(min(l_mo[igood]))
    l_mo_max = np.ceil(max(l_mo[igood]))
    l_en_min = np.floor(min(l_en[igood]))
    l_en_max = np.ceil(max(l_en[igood]))
    
    # make a crossplot if told to do so
    if qcplot:
        plt.figure(facecolor='w')
        plt.scatter(l_mo, l_en, s=50)
        plt.plot(l_mo, l_mo*a+b, 'r-')
        plt.xlim(l_mo_min, l_mo_max)
        plt.ylim(l_en_min, l_en_max)
        plt.text(l_mo_min+0.05*(l_mo_max-l_mo_min), l_en_min+0.9*(l_en_max-l_en_min),
                 'E = 10^(a*Mo+b), with a = ' + str(a) + ', b = ' + str(b))
        plt.xlabel('log_10(Mo)')
        plt.ylabel('log_10(E)')
    # calculated energy function
    y = lambda x: 10**(a*x+b)
    # EI is radiated energy/calculated energy
    ei = []
    for en, mo in zip(data['Energy'], data['SeiMoment']):
        if np.isfinite(en):
            en_th = y(np.log10(mo))
            ei_ind = en/en_th
        else:
            ei_ind = -9999.9
        ei.append(ei_ind)
    return ei


def trgid2dt(trgid):
    """ Convert a trgid into a datetime """
    # import datetime as dt
    if not isinstance(trgid, np.str):
        trgid = np.str(trgid)
    yr, mn, day = trgid[0:4], trgid[4:6], trgid[6:8]
    hr, minute, sc = trgid[8:10], trgid[10:12], trgid[12:14]
    yr = int(yr)
    mn = int(mn)
    day = int(day)
    hr = int(hr)
    minute = int(minute)
    sc = int(sc)
    ms = int(trgid[14:17]+'000')

    # weird case where seconds = 60
    if sc == 60:
        sc = 0
        minute = int(minute) + 1
    return dt.datetime(yr, mn, day, hr, minute, sc, ms)


def fpstrikedip(dfSMTIEvent, oldversion=False):
    """ Calculate fracture plane strike dip from database
        uses fracture plane corrected by tensile angle by default
        or older version if correction not done.
        The old version can be forced by setting oldversion=True
        Note: FMSI must have been run on the dataset
        Note: Uses CorrStrA, CorrDipA, CorrStrB, CorrDipB
        and only considers Fault Plane Index 1 or 2
        SMFI must have been ran with minDC=0
        import pandas as pd
        Gisela 23 March 2015
        added the dataframe index part as it was crashing for DF
        an alternative option it will be to turn the df into a dic
        """
    # pd.set_option('display.max_colwidth', -1)
    # pd.set_option('display.max_columns', -1)
    # pd.set_option('display.max_rows', -1)

    nevents = len(dfSMTIEvent['TrgID'])
    strike, dip = np.zeros(nevents), np.zeros(nevents)
    
    # if (('CorrDipA' in smtdb.keys()) & oldversion==False):
    if oldversion is False:
        if isinstance(dfSMTIEvent, pd.DataFrame):
            # if it is a dataframe index may not be 0...nevents
            dfSMTIEvent = dfSMTIEvent.loc[~dfSMTIEvent.index.duplicated(keep='first')]
            j = 0
            for i in dfSMTIEvent.index:
                if dfSMTIEvent.loc[i, 'FaultPlaneIndex'] == 1:
                    strike[j] = dfSMTIEvent.loc[i, 'CorrStrA']
                    dip[j] = dfSMTIEvent.loc[i, 'CorrDipA']
                elif dfSMTIEvent.loc[i, 'FaultPlaneIndex'] == 2:
                    strike[j] = dfSMTIEvent.loc[i, 'CorrStrB']
                    dip[j] = dfSMTIEvent.loc[i, 'CorrDipB']
                else: # No fault plane solution
                    strike[j] = py.nan
                    dip[j] = py.nan
                j += 1
            return strike, dip
        else:
            for i in range(nevents):
                if dfSMTIEvent['FaultPlaneIndex'][i] == 1:
                    strike[i] = dfSMTIEvent['CorrStrA'][i]
                    dip[i] = dfSMTIEvent['CorrDipA'][i]
                elif dfSMTIEvent['FaultPlaneIndex'][i] == 2:
                    strike[i] = dfSMTIEvent['CorrStrB'][i]
                    dip[i] = dfSMTIEvent['CorrDipB'][i]
                else:  # No fault plane solution
                    strike[i] = py.nan
                    dip[i] = py.nan
            return strike, dip
    # elif (('CorrDipA' not in smtdb.keys()) | oldversion==True):
    elif oldversion is True:
        for i in range(nevents):
            if dfSMTIEvent['FaultPlaneIndex'][i] == 1:
                strike[i] = dfSMTIEvent['StrikeA'][i]
                dip[i] = dfSMTIEvent['DipA'][i]
            elif dfSMTIEvent['FaultPlaneIndex'][i] == 2:
                strike[i] = dfSMTIEvent['StrikeB'][i]
                dip[i] = dfSMTIEvent['DipB'][i]
            elif dfSMTIEvent['FaultPlaneIndex'][i] == 3:
                strike[i] = dfSMTIEvent['Paz'][i]+90
                if strike[i] > 360:
                    strike[i] = strike[i]-360
                dip[i] = 90 - dfSMTIEvent['Pdip'][i]
            elif dfSMTIEvent['FaultPlaneIndex'][i] == 4:
                strike[i] = dfSMTIEvent['Taz'][i]+90
                if strike[i] > 360:
                    strike[i] = strike[i]-360
                dip[i] = 90 - dfSMTIEvent['Tdip'][i]
            else:  # No fault plane solution
                strike[i] = py.nan
                dip[i] = py.nan
        return strike, dip


def correct_fp(smtdb, slip='No'):
    """ correct Fault Planes A and B in database for tensile angles.  Outputs
    new columns in the dictionary variable for the database
    Written by Adam Baig"""
    
    pd.options.mode.chained_assignment = None
    
    nevents = len(smtdb['TrgID'])
    smtdb['CorrStrA'] = np.zeros(nevents)
    smtdb['CorrDipA'] = np.zeros(nevents)    
    smtdb['CorrStrB'] = np.zeros(nevents)
    smtdb['CorrDipB'] = np.zeros(nevents)
    if slip != 'No':
        smtdb['CorrSlpA'] = np.zeros([3, nevents])
        smtdb['CorrSlpB'] = np.zeros([3, nevents])
    d2r = np.pi/180.    
    for i in range(nevents):
        pax = MathUtil.unit_vector(smtdb['Paz'][i], smtdb['Pdip'][i])
        bax = MathUtil.unit_vector(smtdb['Baz'][i], smtdb['Bdip'][i])
        tax = MathUtil.unit_vector(smtdb['Taz'][i], smtdb['Tdip'][i])
        fpa = MathUtil.normal_vector(smtdb['StrikeA'][i], smtdb['DipA'][i])
        fpb = MathUtil.normal_vector(smtdb['StrikeB'][i], smtdb['DipB'][i])
        tna = d2r*smtdb['TnAng'][i]

        # rotate  by tensile angle
        na1 = np.dot(MathUtil.rotation_matrix(bax, tna/2.), fpa)
        na2 = np.dot(MathUtil.rotation_matrix(bax, -tna/2.), fpa)
        nb1 = np.dot(MathUtil.rotation_matrix(bax, tna/2.), fpb)
        nb2 = np.dot(MathUtil.rotation_matrix(bax, -tna/2.), fpb)
        if (1+np.sign(tna))/2:    # opening events, normal closer to t
            ta1 = np.dot(tax, na1)
            ta2 = np.dot(tax, na2)
            tb1 = np.dot(tax, nb1)
            tb2 = np.dot(tax, nb2)
            if abs(ta1) > abs(ta2):
                na = na1
            else:
                na = na2
            if abs(tb1) > abs(tb2):
                nb = nb1
            else:
                nb = nb2
        else:                   # closure events, normal closer to p
            pa1 = np.dot(pax, na1)
            pa2 = np.dot(pax, na2)
            pb1 = np.dot(pax, nb1)
            pb2 = np.dot(pax, nb2)
            if abs(pa1) > abs(pa2):
                na = na1
            else:
                na = na2
            if abs(pb1) > abs(pb2):
                nb = nb1
            else:
                nb = nb2
        csa, cda = MathUtil.strike_dip(na)
        csb, cdb = MathUtil.strike_dip(nb)
        corr_str_a_series = smtdb['CorrStrA']
        corr_dip_a_series = smtdb['CorrDipA']
        corr_str_b_series = smtdb['CorrStrB']
        corr_dip_b_series = smtdb['CorrDipB']
        corr_str_a_series[i] = csa
        corr_dip_a_series[i] = cda
        corr_str_b_series[i] = csb
        corr_dip_b_series[i] = cdb
        smtdb['CorrStrA'] = corr_str_a_series
        smtdb['CorrDipA'] = corr_dip_a_series
        smtdb['CorrStrB'] = corr_str_b_series
        smtdb['CorrDipB'] = corr_dip_b_series
    
        if slip == 'FaultAligned':
            # TODO this code doesn't seem to be doing anything? Values get overwritten after
            sla, slb = np.cross(na, bax), np.cross(nb, bax)
            if tax[2] > pax[2]:   # t ax more vert --> normal regime, slip down (+ve z)
                if sla[2] > 0:
                    sla = -sla
                if slb[2] > 0:
                    slb = -slb
            else:               # p ax more vert --> thrust regime, slip up (-ve z)
                if sla[2] < 0:
                    sla = -sla
                if slb[2] < 0:
                    slb = -slb

            sta, dpa, rka = smtdb['StrikeA'][i], smtdb['DipA'][i], smtdb['SlipA'][i]
            stb, dpb, rkb = smtdb['StrikeB'][i], smtdb['DipB'][i], smtdb['SlipB'][i]
            sla = MathUtil.slip_vector(sta, dpa, rka)
            slb = MathUtil.slip_vector(stb, dpb, rkb)
            smtdb['CorrSlpA'][:, i] = sla
            smtdb['CorrSlpB'][:, i] = slb
        if slip == 'General':
            sla, slb = nb, na
            if tax[2] > pax[2]:   # t ax more vert --> normal regime, slip down (+ve z)
                if sla[2] < 0:
                    sla = -sla
                if slb[2] < 0:
                    slb = -slb
            else:               # p ax more vert --> thrust regime, slip up (-ve z)
                if sla[2] > 0:
                    sla = -sla
                if slb[2] > 0:
                    slb = -slb
            smtdb['CorrSlpA'][:, i] = sla
            smtdb['CorrSlpB'][:, i] = slb
    return smtdb

# <codecell> DataFrame processing


def getHighPIClusters(dfCluster, PICutoff=0.5):
    """
    Get all rows in dataframe where PI > PICutoff
    """
    
    return dfCluster[dfCluster['norm_logPI'] > PICutoff]


def dimensionQuantile(dfCluster, quantile=.97):
    """
    get dfCluster rows where the cluster is in a box defined by
    each dimension's limits resulting in quantile*100% of the data is in that
    limit and that each dimension's data is the center-most sample of that data
    """
    
    quantity = (1 - quantile) / 2
    northinghigh = dfCluster['Northing'].quantile(1-quantity)
    northinglow = dfCluster['Northing'].quantile(quantity)
    
    eastinghigh = dfCluster['Easting'].quantile(1-quantity)
    eastinglow = dfCluster['Easting'].quantile(quantity)
    
    depthhigh = dfCluster['Depth'].quantile(1-quantity)
    depthlow = dfCluster['Depth'].quantile(quantity)
    
    betweennorthing = (dfCluster['Northing'] < northinghigh) & (dfCluster['Northing'] > northinglow)
    betweeneasting = (dfCluster['Easting'] < eastinghigh) & (dfCluster['Easting'] > eastinglow)
    betweendepth = (dfCluster['Depth'] < depthhigh) & (dfCluster['Depth'] > depthlow)
    
    truthtable = betweennorthing & betweeneasting & betweendepth
    return dfCluster[truthtable]

    
def varQuantile(df, var, quantile):
    """
    # TODO needs documentation
    :param df:
    :param var:
    :param quantile:
    :return:
    """
    quantity = (1 - quantile) / 2
    varhigh = df[var].quantile(1-quantity)
    varlow = df[var].quantile(quantity)
    
    betweenvar = (df[var] < varhigh) & (df[var] > varlow)
    return df[betweenvar]
