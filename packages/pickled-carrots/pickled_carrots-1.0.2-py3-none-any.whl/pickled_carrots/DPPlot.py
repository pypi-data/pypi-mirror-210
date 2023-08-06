# -*- coding: utf-8 -*-
"""
Created on Tue Jul  9 09:22:28 2019

@author: sara.brazille
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import pandas as pd
from . import DPUtil
from . import database
from . import dataclass
from . import mathutil
import ternary
import matplotlib.tri as tri
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches


# <codecell> Simplified Plotting Functions

# https://sashat.me/2017/01/11/list-of-20-simple-distinct-colors/
# removed white
distinctColours = ['#e6194b', '#3cb44b', '#4363d8', '#f58231', 
                   '#911eb4', '#f032e6', '#bcf60c', '#fabebe', 
                   '#008080', '#9a6324', '#800000', '#808000', 
                   '#000075', '#808080', '#000000']
    
                   
def drawDeviation(ax, df, column, SDVar, SD, text=True):
    
    """
    Takes the number of standard deviations from the mean and 
    plots it as a rectangle
    
    Inputs
    ======
    ax : matplotlib.pyplot.axes
        The axes to draw the SD rectangle on
    df : pandas.DataFrame
        The data to extract the variable to be analyzed
    column : string
        Which variable will be analyzed
    SDVar : string (x, y)
        Which axis on the resulting plot is the variable on
    SD : scalar between 0 and 1
        How many standard deviations from the mean to include
        
    Outputs
    ============
    None, outputs data to ax by reference
    
    Dependencies
    ============
    None
    """
    
    # Shape the rectangle based on which axes we're limiting it by
    if SDVar == 'x':
        top = ax.get_ylim()[1]
        bottom = ax.get_ylim()[0]
        
        left = df[column].mean() - df[column].std()*SD
        right = df[column].mean() + df[column].std()*SD
    else:  # it's y
        top = df[column].mean() + df[column].std()*SD
        bottom = df[column].mean() - df[column].std()*SD
        
        left = ax.get_xlim()[0]
        right = ax.get_xlim()[1]
    
    # Draw the rectangle
    highlightSection(ax, top, bottom, left, right, [1, 1, 1], alpha=.5)
    
    if SDVar == 'y':
        # Add an s to deviation if there is not 1 SD
        if SD != 1:
            if text:
                ax.text(left - (right - left)*0.01, (top + bottom)/2.0, str(SD) +
                        " standard deviations from the mean---------->", horizontalalignment='right')
        else:
            if text:
                ax.text(left - (right - left)*0.01, (top + bottom)/2.0, str(SD) +
                        " standard deviation from the mean---------->", horizontalalignment='right')
    else:
        # Add an s to deviation if there is not 1 SD
        if SD != 1:
            if text:
                ax.text((left + right)/2.0, bottom - (top - bottom)*0.06, str(SD) +
                        " standard deviations from the mean---------->", verticalalignment='top',
                        horizontalalignment='right', rotation=45, rotation_mode='anchor')
        else:
            if text:
                ax.text((left + right)/2.0, bottom - (top - bottom)*0.06, str(SD) +
                        " standard deviation from the mean---------->", verticalalignment='top',
                        horizontalalignment='right', rotation=45, rotation_mode='anchor')

    if SDVar == 'x':
        return left, right
    else:
        return top, bottom


def highlightSection(ax, top, bottom, left, right, colour=None, alpha=0.25):
    """
    Draw a rectangle on the graph under the data
    
    Inputs
    ======
    ax : matplotlib.pyplot.axes
        The axes to draw the rectangle on
    top, bottom, left, right : scalars
        Limits of the rectangle in plotted variable space
    colour : list (len = 3)
        List of 3 scalars between 0 and 1 representing rgb components
    alpha : scalar between 0 and 1
        Alpha value of the rectance
        
    Outputs
    ============
    None, outputs data to ax by reference
    
    Dependencies
    ============
    matplotlib.path.Path
    matplotlib.patches.PathPatch
    """
    from matplotlib.path import Path
    from matplotlib.patches import PathPatch

    if colour is None:
        colour = [0.4, 0.4, 0.4]
    
    # Draw a line around the rectangle, then fill it
    codes = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
    vertices = [(left, top),
                (right, top),
                (right, bottom),
                (left, bottom),
                (left, top)]
    vertices = np.array(vertices, float)
    path = Path(vertices, codes)
    
    # Draw the plot highlight (in grey)
    facecolour = colour
    pathpatch = PathPatch(path, facecolor=facecolour,
                          edgecolor='black', alpha=alpha, zorder=-10)
    
    ax.add_patch(pathpatch)


def plotWells(ax, dfStages, xVar, yVar, stageLabels=False, activeStages=None,
              relativeCoordinates=False, svcfile=None, angle=0,
              relStage=None, debug=False):
    
    """
    Plots the well stages given by activeStages
    
    Inputs
    ======
    ax : matplotlib.pyplot.axes
        The axes to draw the well stages on
    dfStages : pandas.DataFrame
        Stage data
    xVar : string (Northing, Easting, Depth, Distance Along Well, Distance Right Perpendicular to Well)
        Which positional variable is plotted on the X axis
    yVar : string (Northing, Easting, Depth, Distance Along Well, Distance Right Perpendicular to Well)
        Which positional variable is plotted on the Y axis
    stageLabels : bool, optional
        Whether to plot the stage labels along with the stages
    activeStages : list, optional
        list of 'FRAC_STAGE_ID' values
        
    Outputs
    ============
    None, outputs data to ax by reference
    
    Dependencies
    ============
    numpy
    """
    if activeStages is None:
        activeStages = []

    if debug:
        print("Relative Stage: "+str(relStage))
        print("Angle: "+str(angle))
    
    # The keys in the stage data are the first letter of Northing/Easting/Depth
    # Except for Depth, it's Z for Depth, which in my personally opinion is silly
    
    if xVar in ['Distance Right Perpendicular To Well', 'Distance Along Well']:
        relativeCoordinates = True
    
    if relativeCoordinates is True:
        x_key = xVar
        y_key = yVar
    else:
        x_key = xVar[0]
        y_key = yVar[0]
    
    if xVar == "Depth":
        x_key = 'Z'
    if yVar == "Depth":
        y_key = 'Z'
    
    if svcfile is not None:    
        wells = DataClass.Seisvis(svcfile).wells()
        
        for well in wells:
            n, e, d = wells[well]
            
            df_ned = pd.DataFrame(wells[well]).T
            df_ned.columns = ['Northing', 'Easting', 'Depth']
            
            if relStage is None:
                relStage = dfStages.index[-1]
            # need to rotate the wells
            df_ned_rot, _ = MathUtil.addRelativeCoordinates(df_ned,
                                                            dfStages,
                                                            relStage,
                                                            angle=angle)
            
            wellx, welly = None, None
            if xVar == "Easting":
                wellx = df_ned.Easting
            elif xVar == "Northing":
                wellx = df_ned.Northing
            elif xVar == "Depth":
                wellx = df_ned.Depth
            elif xVar == "Distance Right Perpendicular To Well":
                wellx = df_ned_rot['Distance Right Perpendicular To Well']
            elif xVar == "Distance Along Well":
                wellx = df_ned_rot['Distance Along Well']
            else:
                Exception("Need an acceptable xVar for plotting")
            
            if yVar == "Easting":
                welly = df_ned.Easting
            elif yVar == "Northing":
                welly = df_ned.Northing
            elif yVar == "Depth":
                welly = df_ned.Depth
            elif yVar == "Distance Right Perpendicular To Well":
                welly = df_ned_rot['Distance Right Perpendicular To Well']
            elif yVar == "Distance Along Well":
                welly = df_ned_rot['Distance Along Well']
            else:
                Exception("Need an acceptable yVar for plotting")
            
            if (wellx is not None) and (welly is not None):
                ax.plot(wellx, welly, 'r')
            else:
                print("Issue figuring out axis to plot well. xVar="+str(xVar)+" yVar="+str(yVar))
    
    # Text x value is the midpoint of the enpoints of the stages
    dfStages['textX'] = (dfStages[x_key+'1'] + dfStages[x_key+'2'])/2.0
    
    # Spacing for expanding the graph to the right so that the text doesn't
    # go out of the bound of the graph
    textspacing = (dfStages['textX'].max() - dfStages['textX'].min()) * 0.4
    
    if dfStages['textX'].max() + textspacing > ax.get_xlim()[1]:
        ax.set_xlim(ax.get_xlim()[0], dfStages['textX'].max() + textspacing)
    
    for index, row in dfStages.iterrows():
        # Either plot all if activeStages is empty or just plot the active Stages
        if (len(activeStages) == 0) or (row['Name'] in activeStages):
            
            # Make line points for the stages
            xl = np.linspace(row[x_key+'1'], row[x_key+'2'], 10)
            yl = np.linspace(row[y_key+'1'], row[y_key+'2'], 10)
            
            # Get midpoints
            xkeymid = (row[x_key+'1'] + row[x_key+'2'])/2.0
            ykeymid = (row[y_key+'1'] + row[y_key+'2'])/2.0
            
            if len(activeStages) == 1:
                # If there's only one active stage, plot a white hexagon with a
                # black plus sign
                ax.plot(xkeymid, ykeymid, 'wh', markersize=10)
                ax.plot(xkeymid, ykeymid, 'k+', markersize=10)
            else:
                # Plot from stage colour data
                stgcolor = (row['Colour_R']/255.0, row['Colour_G']/255.0, row['Colour_B']/255.0)
                ax.plot(xl, yl, linewidth=3, color=stgcolor, zorder=10)
                
            offset = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.05
            
            ymin = np.amin(ax.get_ylim())
            ymax = np.amax(ax.get_ylim())
            
            yinbox = ((ykeymid > ymin) & (ykeymid < ymax))
            if stageLabels:
                if yinbox:
                    # If the text will be in the box, plot it
                    ax.text(xkeymid + offset, ykeymid, row['Name'], zorder=11)


def plotClustersOnAx(ax, dfCluster, dfStages, xVar, yVar, dependantVariable, 
                     cmap='cool', alpha=1.0, markerSize=5,
                     c=None, colourBar=True, onlyShowActiveStages=False,
                     stageLabels=False, limitToData=False, limits=None,
                     hideTicks=False, relativeCoordinates=False,
                     aspect='equal', svcfile=None, angle=0,
                     relStage=None, showArrow=False):
    
    """
    Plots all cluster centroids on a graph
    
    Inputs
    ======
    ax : matplotlib.pyplot.axes
        Axes to plot on
    dfCluster : pandas.DataFrame
        Cluster data to be used for plotting
    dfStages : pandas.DataFrame
        Stage data so that the stages can be plotted
    xVar : string
        Variable to plot on the X axis (Northing, Easting, Depth)
    xVar : string
        Variable to plot on the Y axis (Northing, Easting, Depth)
    dependantVariable : string
        What to colour the clusters by
    cmap : string, optional
        What colour map to use
    alpha : scalar between 0 and 1, optional
        Transparency value of the centroids
    onlyShowActiveStages : bool, optional
        Should we only show stages for which there are entries in dfCluster
    stageLabels : Bool, optional
        Whether to include stage labels or not
    limitToData : Bool, optional
        Sets the plot limits to automatically fit around the contour data
    limits : DataClass.Limits
        Limits the range of the plot
        X limits are the X axis of the plot
        Y limits are the Y axis of the plot
        Z limits are the limits of the dependant variable
        Overrides limitToData
    hideTicks : bool, optional
        Used to hide the x and y tick labels
        
    Outputs
    ============
    None, just the plot
    
    Dependencies
    ============
    numpy
    matplotlib.pyplot
    DPUtil
    """

    # plot wells and also add all stages for which there is data to activeStages
    activestages = []
    if onlyShowActiveStages:
        for name in dfCluster['FRAC_STAGE_ID'].unique():
            activestages.append(name)
    x = None
    y = None
    if dfCluster is not None:
        x = dfCluster[xVar].values
        y = dfCluster[yVar].values
        if c is None:
            c = dfCluster[dependantVariable].values
    
    vmin = None
    vmax = None
    
    if limits is not None:
        if limits.zMin is not None:
            vmin = limits.zMin
            vmax = limits.zMax

    scatterplot = None
    if dfCluster is not None:
        scatterplot = ax.scatter(x, y, c=c, s=markerSize, cmap=cmap,
                                 vmin=vmin, vmax=vmax, alpha=alpha)

    cb = None
    if colourBar is True:
        # Draw a colour bar
        cb = plt.colorbar(scatterplot)
        cb.set_label(dependantVariable)
    
    # Set the plot labels
    ax.set_xlabel(xVar)
    ax.set_ylabel(yVar)
    
    plotWells(ax, dfStages, xVar, yVar, stageLabels, activestages,
              relativeCoordinates=relativeCoordinates, svcfile=svcfile,
              angle=angle, relStage=relStage)
    
    if hideTicks is True:
        # Hide tick labels
        ax.tick_params(labelbottom=False)
        ax.tick_params(labelleft=False)   
        ax.tick_params(labelright=False)
        ax.tick_params(labeltop=False)
    
    if colourBar is True:
        # if the colour variable is Depth, flip the colourbar
        if dependantVariable == 'Depth':
            if len(cmap.split('_')) > 1:
                rcmap = cmap.split('_')[0]
            else:
                rcmap = cmap+'_r'
            
            cb.set_cmap(plt.get_cmap(rcmap))
            if dfCluster[dependantVariable].max() - dfCluster[dependantVariable].min() > 10:
                cb.set_ticks(np.flip(cb.get_ticks()).astype(int))
                cb.set_ticklabels(np.flip(cb.get_ticks()).astype(int))
            else:
                cb.set_ticks(np.flip(cb.get_ticks()))
                cb.set_ticklabels(np.flip(cb.get_ticks()))
        
        # Make the colour bar not transparent
        cb.set_alpha(1)
        cb.draw_all()
        
    ax.set_aspect(aspect)
        
    # Set limits if provided
    if limits is not None:
        if limits.xMin is not None:
            ax.set_xlim(limits.xMin, limits.xMax)
        if limits.yMin is not None:
            ax.set_ylim(limits.yMin, limits.yMax) 

    if showArrow:
        plotArrow(ax, angle)


def plotClusters(dfCluster, dfStages, xVar, yVar, dependantVariable, 
                 cmap='cool', sizeOfDots=5, alpha=1.0,
                 onlyShowActiveStages=False, stageLabels=False,
                 limitToData=False, limits=None, svcfile=None,
                 figPath=None):
    
    """
    Plots all cluster centroids on a graph
    
    Inputs
    ======
    dfCluster : pandas.DataFrame
        Cluster data to be used for plotting
    dfStages : pandas.DataFrame
        Stage data so that the stages can be plotted
    xVar : string
        Variable to plot on the X axis (Northing, Easting, Depth)
    xVar : string
        Variable to plot on the Y axis (Northing, Easting, Depth)
    dependantVariable : string
        What to colour the clusters by
    cmap : string, optional
        What colour map to use
    alpha : scalar between 0 and 1, optional
        Transparency value of the centroids
    onlyShowActiveStages : bool, optional
        Should we only show stages for which there are entries in dfCluster
    stageLabels : Bool, optional
        Whether to include stage labels or not
    limitToData : Bool, optional
        Sets the plot limits to automatically fit around the contour data
    limits : DataClass.Limits
        Limits the range of the plot
        X limits are the X axis of the plot
        Y limits are the Y axis of the plot
        Z limits are the limits of the dependant variable
        Overrides limitToData
    figPath : str, optional
        Path where to save the figures

    Outputs
    ============
    None, just the plot
    
    Dependencies
    ============
    numpy
    matplotlib.pyplot
    DPUtil
    """
    
    if xVar not in ['Northing', 'Easting', 'Depth', 'Distance Right Perpendicular To Well', 'Distance Along Well']:
        raise Exception(xVar + ' is not one of Northing Easting or Depth, or relative coordinates')
    if yVar not in ['Northing', 'Easting', 'Depth', 'Distance Right Perpendicular To Well', 'Distance Along Well']:
        raise Exception(xVar + ' is not one of Northing Easting or Depth, or relative coordinates')
    if dependantVariable not in dfCluster.columns:
        raise Exception(dependantVariable + 'is not a DPA cluster attribute\n' +
                        'Type dfCluster.columns in a blank cell to see the available attributes')
    
    plotClustersOnAx(plt.gca(), dfCluster, dfStages, xVar, yVar, 
                     dependantVariable, cmap=cmap, markerSize=sizeOfDots,
                     alpha=alpha, onlyShowActiveStages=onlyShowActiveStages,
                     stageLabels=stageLabels, limitToData=limitToData,
                     limits=limits, svcfile=svcfile)
    
    plt.gcf().set_size_inches(15, 15)

    if figPath is not None:
        plt.savefig(figPath+"Plot_"+xVar+"_"+yVar+"_"+dependantVariable+".png", dpi=200)

    plt.show()


def contourPlotWithWells(dfCluster, dfStages, xVar, yVar, dependantVariable,
                         cmap='cool', levels=14,
                         onlyShowActiveStages=False, stageLabels=False,
                         colourBar=True, limitToData=False, limits=None,
                         axIn=None, hideTicks=False, clusterOverlay=True,
                         relativeCoordinates=False, maskLength=100,
                         aspect='equal', svcfile=None, figPath=None):
    
    """
    Plots a contour plot showing interpolated dependantVariable values
    Also plots stages on the plot
    
    Inputs
    ======
    dfCluster : pandas.DataFrame
        Cluster data to be used for plotting
    dfStages : pandas.DataFrame
        Stage data so that the stages can be plotted
    xVar : string
        Variable to plot on the X axis (Northing, Easting, Depth)
    yVar : string
        Variable to plot on the Y axis (Northing, Easting, Depth)
    independantVariable : string
        Variable to plot contours based on
    cmap : string, optional
        What colour map to use
    levels : int, optional
        How many levels to divide the contour map into
    onlyShowActiveStages : bool, optional
        Should we only show stages for which there are entries in dfCluster
    stageLabels : Bool, optional
        Whether to include stage labels or not
    colourBar : Bool, optional
        Whether to include a colour bar
    limitToData : Bool, optional
        Sets the plot limits to automatically fit around the contour data
    limits : DataClass.Limits
        Limits the range of the plot
        X limits are the X axis of the plot
        Y limits are the Y axis of the plot
        Z limits are the limits of the dependant variable
        Overrides limitToData
    svcfile : string, optional
        
        
    Outputs
    ============
    None, just the plot
    
    Dependencies
    ============
    numpy
    matplotlib.pyplot
    DPUtil
    """
    
    if xVar not in ['Northing', 'Easting', 'Depth', 'Distance Right Perpendicular To Well', 'Distance Along Well']:
        raise Exception(xVar + ' is not one of Northing Easting or Depth, or relative coordinates')
    if yVar not in ['Northing', 'Easting', 'Depth', 'Distance Right Perpendicular To Well', 'Distance Along Well']:
        raise Exception(xVar + ' is not one of Northing Easting or Depth, or relative coordinates')

    #    #Number of grid points is equal to the range of spacial data
    #    ngridx = int(dfCluster[xVar].max()) - int(dfCluster[xVar].min())
    #    ngridy = int(dfCluster[yVar].max()) - int(dfCluster[yVar].min())
    
    x = np.array(dfCluster[xVar].values)
    y = np.array(dfCluster[yVar].values)
    z = np.array(dfCluster[dependantVariable].values)

    #    #Create grid values first.
    #    xi = np.linspace(dfCluster[xVar].min(), dfCluster[xVar].max(), ngridx)
    #    yi = np.linspace(dfCluster[yVar].min(), dfCluster[yVar].max(), ngridy)

    # Perform linear interpolation of the data (x,y)
    # on a grid defined by (xi,yi)
    triang = tri.Triangulation(x, y)
    #    interpolator = tri.LinearTriInterpolator(triang, z)
    #    Xi, Yi = np.meshgrid(xi, yi)
    #    zi = interpolator(Xi, Yi)
    
    def apply_mask(triang1, alpha=0.4):
        """
        Applying masking to trianges with sidelengths bigger than some alpha
        :param triang1: the trianlges object
        :param alpha: the alpha threshold
        :return:
        """
        # Mask triangles with sidelength bigger some alpha
        triangles = triang1.triangles
        # Mask off unwanted triangles.
        xtri = x[triangles] - np.roll(x[triangles], 1, axis=1)
        ytri = y[triangles] - np.roll(y[triangles], 1, axis=1)
        maxi = np.max(np.sqrt(xtri**2 + ytri**2), axis=1)
        # apply masking
        triang1.set_mask(maxi > alpha)
        return triang1
    
    apply_mask(triang, alpha=maskLength)
    
    vmin = None
    vmax = None
    
    # Set limits if provided
    if limits is not None:
        if limits.zMin is not None:
            vmin = limits.zMin
            vmax = limits.zMax
    
    # Plot the countour plot
    if axIn is None:
        contourplot = plt.tricontourf(triang, z, levels=levels, cmap=cmap, vmin=vmin, vmax=vmax, zorder=-10)
        ax = plt.gca()
    else:
        ax = axIn
        contourplot = ax.tricontourf(triang, z, levels=levels, cmap=cmap, vmin=vmin, vmax=vmax, zorder=-10)
    # Draw a colour bar
    if colourBar:
        cb = plt.colorbar(contourplot)
        cb.set_label(dependantVariable)
    if clusterOverlay is True:
        ax.scatter(x, y, c='k', s=1, cmap=cmap, vmin=vmin, vmax=vmax)
    
    # Set the plot labels
    ax.set_xlabel(xVar)
    ax.set_ylabel(yVar)
    
    if limitToData:
        # Limit the plot to the existing data
        ax.set_ylim(dfCluster[yVar].min(), dfCluster[yVar].max())
    
    # plot wells and also add all stages for which there is data to activeStages
    activestages = []
    if onlyShowActiveStages:
        for name in dfCluster['FRAC_STAGE_ID'].unique():
            activestages.append(name)
    
    plotWells(ax, dfStages, xVar, yVar, stageLabels, activestages,
              relativeCoordinates=relativeCoordinates, svcfile=svcfile)
    
    if limitToData:
        ax.set_xlim(dfCluster[xVar].min(), dfCluster[xVar].max())
        
    ax.set_aspect(aspect)
    if axIn is None:
        ax.figure.set_size_inches(12, 15)
    
    # Set limits if provided
    if limits is not None:
        if limits.xMin is not None:
            ax.set_xlim(limits.xMin, limits.xMax)
        if limits.yMin is not None:
            ax.set_ylim(limits.yMin, limits.yMax)
    
    # Flip y axis if the yVar is depth, looks better
    if yVar == 'Depth':
        ax.invert_yaxis()
        
    if hideTicks is True:
        # Hide tick labels
        ax.tick_params(labelbottom=False)
        ax.tick_params(labelleft=False)   
        ax.tick_params(labelright=False)
        ax.tick_params(labeltop=False)
    
    if axIn is None:
        if figPath is not None:
            plt.savefig(figPath + "ContourPlot with Wells_"+xVar+"_"+yVar+".png", dpi=200)
        plt.show()
    else:
        return ax


def plotEventsClusterVariableAndPumpData(dfCluster, dfPump, dfEvent, 
                                         dependantVariable, pumpKeyNames,
                                         intervalWidth=0, intervals=0,
                                         smoothPoints=30, limits=None,
                                         figPath=None):
    
    """
    Makes 2 plots with the same time scaling
    
    Plots number of events vs time and dependantVariable vs time on the top plot
    Plots the pump data on the bottom plot
    
    Inputs
    ======
    dfCluster : pandas.DataFrame
        ClusterData to be used for plotting the dependant variable on the top plot
    dfPump : pandas.DataFrame
        Pump data, must include the stages you are plotting
    dfEvent : pandas.DataFrame
        EventData to be used for plotting number of events vs time
    dependantVariable : string
        The variable from dfCluster that is being displayed
    pumpKeyNames : DataClass.PumpKeyNames
        The names of the pump keys so data can be extracted from the dataframe
    intervalWidth : scalar, optional (don't define if intervals is defined)
        The width of each interval grouping
    intervals : int, optional (don't define if intervalWidth is defined)
        The number of grouping intervals
    smoothPoints : int
        Number of points to smoth the dependant variable data over
    limits : DataClass.Limits
        Limits the range of the plot
        X limits are the limits to the Time in stage (min)
        Y limits are the limits to the specified dependant variable
    figPath : string, optional
        Path to output figures
        
    Outputs
    ============
    None, just the plot
    
    Dependencies
    ============
    numpy
    matplotlib.pyplot
    DPUtil
    """
    
    if dependantVariable not in dfCluster.columns:
        raise Exception(dependantVariable + 'is not a DPA cluster attribute\n' +
                        'Type dfCluster.columns in a blank cell to see the available attributes')
    
    for name in dfCluster['FRAC_STAGE_ID'].unique():
        
        # Get data for the current plot
        df_cluster_cur = dfCluster[dfCluster['FRAC_STAGE_ID'] == name].copy()
        df_event_cur = dfEvent[dfEvent['FRAC_STAGE_ID'] == name].copy()
        df_pump_cur = dfPump[dfPump['FRAC_STAGE_ID'] == name].copy()
        
        if df_event_cur.shape[0] > 0:

            # Calculate the time in the stage by averaging the first and last event times
            if 'Time in stage (min)' not in df_cluster_cur.columns:
                df_cluster_cur['Time in stage (min)'] = (0.5*(df_cluster_cur['First Event Time (min.)']
                                                         + df_cluster_cur['Last Event Time (min.)']))
            
            # convert to minutes and make the max time a multiple of 10 minutes
            df_event_cur.loc[:, 'Time in stage (min)'] = df_event_cur['Time_in_stage(s)']/60.0
            maxtime = int(np.ceil(df_event_cur['Time in stage (min)'].max()/10) * 10)
            
            # set up 2 axes, one on top of the other
            fig, axes = plt.subplots(nrows=2, ncols=1, figsize=[10, 8])
            
            # Set up dependant variable plot and event frequency chart
            eventax = axes[0]
            
            # Make them have the same X axis
            dependantvariableax = eventax.twinx()
            
            if dependantVariable == 'Depth':
                dependantvariableax.invert_yaxis()
            
            pumpax = axes[1]
            
            # This is generally the independant variable, set it in the function
            independantvariable = 'Time in stage (min)'
            
            # Setup intervalWidth and intervals based on the values given or not given
            intervalWidth, intervals = DPUtil.intervalSetup(intervalWidth, intervals,
                                                            df_event_cur, independantvariable)
            
            # Plot the pumping data
            pumpax2, pumpax3 = plotPump(df_pump_cur, pumpax,
                                        presKey=pumpKeyNames.presKey,
                                        propconKey=pumpKeyNames.propconKey,
                                        flowKey=pumpKeyNames.flowKey)

            x = []
            y = []
            
            # Split up the number of Events by independant variable interval
            for i in range(intervals):
                x.append(df_event_cur[independantvariable].min() + intervalWidth*(i + 0.5))
                
                minvalforinterval = (df_event_cur[independantvariable].min()
                                     + intervalWidth*i)
                maxvalforinterval = (df_event_cur[independantvariable].min()
                                     + intervalWidth*(i + 1))
                y.append(DPUtil.dfBetweenTwoValues(df_event_cur,
                                                   independantvariable,
                                                   minvalforinterval,
                                                   maxvalforinterval).shape[0])
        
            # Plot the event bar chart
            eventax.bar(x, y, width=(intervalWidth * 0.8), color='cornflowerblue')
            eventax.set_ylabel('Number Events', color='cornflowerblue')
            
            # Smooth and Plot the dependant variable from cluster data
            df_cluster_cur = df_cluster_cur.sort_values(independantvariable)
            df_cluster_cur = df_cluster_cur.set_index(independantvariable)
            yclean = df_cluster_cur[dependantVariable].rolling(smoothPoints, min_periods=1).mean()
            
            dependantvariableax.plot(df_cluster_cur.index.values, yclean, c='red')
            dependantvariableax.set_ylabel(dependantVariable, color='r')
            
            eventax.set_title(name)
            
            eventax.set_xlim(0, maxtime)
            dependantvariableax.set_xlim(0, maxtime)
            pumpax.set_xlim(0, maxtime)
            pumpax2.set_xlim(0, maxtime)
            pumpax3.set_xlim(0, maxtime)
            
            # Set limits if provided
            if limits is not None:
                eventax.set_xlim(limits.xMin, limits.xMax)
            
            if figPath is not None:
                plt.savefig(figPath+"DPAClusterwithPumpData_"+name+".png", dpi=200)
            
            plt.show()
    # return plt.gcf()


def plotNormalizedTernaryMulti(dfCluster, dfStage, plotTitle=False, **kwargs):
    
    """
    Just an itterated implementation of plotNormalizedTernary
    """
    
    if kwargs['colourBy'] == 'Stage Database Colour':
        print('WARNING: colourBy Stage Index is meaningless if you\'re only plotting ' +
              'one stage per animation')
    
    kwargs_orig = kwargs.copy()
        
    for stageName in dfCluster['FRAC_STAGE_ID'].unique():
        dfclustercur = dfCluster[dfCluster['FRAC_STAGE_ID'] == stageName]
        try:
            print("Plotting normalized ternary for: "+stageName)
            
            # Method to save ternary figures
            if 'figPath' in kwargs.keys():
                kwargs['figPath'] = kwargs_orig['figPath']+"Ternary_"+stageName+"_"+kwargs['colourBy']+".png"

            if plotTitle:
                kwargs['plotTitle'] = stageName

            plotNormalizedTernary(dfclustercur, dfStage, **kwargs)
        except Exception as e:
            print(e)


def plotNormalizedTernary(dfCluster, dfStage, hideTicks=False, colourBy='Depth',
                          cmap='cool', sizeOfDots=3, trendLine=True,
                          downsample=False, sampleInterval=1,
                          downsampleStyle='Select first from (buckets by scalar interval)',
                          downsampleVariable='Time in stage (min)', limits=None,
                          figPath=None, plotTitle=None):

    """
    Makes a ternary plot, outputs to notebook/console
    
    Inputs
    ======
    dfCluster : pandas.DataFrame
        ClusterData to be used for plotting
    colourBy : string, optional
        The variable which the data points will be coloured by 
    unit : string, optional (m or ft)
        What units the data is in
    cmap : string, optional
        Name of an internal colourmap to be used
    sizeOfDots : int, optional
        How large the dots should be
    trendLine : bool, optional
        Should a trend line be drawn on top of the data
    downsample : bool, optional
        Whether or not to downsample the data
    sampleInterval : int, optional
        Sample spacing to use for downsampling
    downsampleStyle : string, optional
        Style to use for downsampling
    downsampleVariable : string, optional
        Variable to downsample over
    limits : DataClass.Limits
        Limits the range of the plot
        Z limits are the limits to the colourBy key
    saveFig : string, optional
        Path of folder to save figure
    
    Outputs
    ============
    None, just the plot
    
    Dependencies
    ============
    os
    numpy
    matplotlib.pyplot
    ternary
    DPUtil
    """
    
    if len(dfCluster) < 50:
        raise Exception('ERROR: too few clusters to interpolate from for potential trend line. ' +
                        'Dataset must contain more than 50 points')
    
    if colourBy not in dfCluster.columns and colourBy != 'Stage Database Colour':
        raise Exception(colourBy + 'is not a DPA cluster attribute\n' +
                        'Type dfCluster.columns in a blank cell to see the available attributes')
    
    if colourBy == 'Stage Database Colour' and downsample == True:
        print('ERROR: Colouring by Database colour with downsampling not supported yet')
    if colourBy == 'Stage Database Colour' and trendLine == True:
        print('ERROR: Colouring by Database colour with trendLine not supported yet')
    
    downsample_styles = []
    downsample_styles.append('Average over variable (buckets by data points)')
    downsample_styles.append('Average over variable (buckets by scalar interval)')
    downsample_styles.append('Select first from (buckets by data points)')
    downsample_styles.append('Select first from (buckets by scalar interval)')
    
    # If downsample is true, apply the appropriate downsampling methodd
    points = None
    colour_scalars = None
    if downsample:
        if downsampleVariable is None:
            downsampleVariable = colourBy
        
        dfCluster = dfCluster.sort_values(downsampleVariable)
        
        # If the downsample style they chose doesn't exist, tell them instead
        # of performing some unexpected behaviour
        if downsampleStyle not in downsample_styles:
            warning_string = ("Selected downsampleStyle is not supported, "
                              + "please use one of the following: \n")
            for style in downsample_styles:
                warning_string += ('\n'+style)
                
            print(warning_string)
            return
        
        # Function switch statement basically, but Python doesn't have switch
        # case for some reason
        
        # We've already checked that the downsampleStyle is one of these styles
        # so we don't need an elif or an else statment, makes the code look
        # cleaner
        if downsampleStyle == 'Average over variable (buckets by data points)':
            downsampled_di, downsampled_si, downsampled_pi, colour_scalars = \
                DPUtil.smoothTernaryByDataInterval(dfCluster, colourBy, sampleInterval)
            points = DPUtil.listsToListOfTuples(downsampled_di, downsampled_si, downsampled_pi)
            
        if downsampleStyle == 'Average over variable (buckets by scalar interval)':
            downsampled_di, downsampled_si, downsampled_pi, colour_scalars = \
                DPUtil.smoothTernaryByScalarInterval(dfCluster, colourBy, sampleInterval, downsampleVariable)
            points = DPUtil.listsToListOfTuples(downsampled_di, downsampled_si, downsampled_pi)
            
        if downsampleStyle == 'Select first from (buckets by data points)':
            downsampled_di, downsampled_si, downsampled_pi, colour_scalars = \
                DPUtil.selectFirstFromTernaryByDataInterval(dfCluster, colourBy, sampleInterval)
            points = DPUtil.listsToListOfTuples(downsampled_di, downsampled_si, downsampled_pi)
            
        if downsampleStyle == 'Select first from (buckets by scalar interval)':
            downsampled_di, downsampled_si, downsampled_pi, colour_scalars = \
                DPUtil.selectFirstFromTernaryByScalarInterval(dfCluster, colourBy, sampleInterval, downsampleVariable)
            points = DPUtil.listsToListOfTuples(downsampled_di, downsampled_si, downsampled_pi)
    else:
        points = DPUtil.dfColumnsToListOfTuples(dfCluster, 
                                                'norm_logDI', 
                                                'norm_logSI', 
                                                'norm_logPI')
        # Get colors for the data
        # This function doesn't actually do much, but for code clarity sake this is a function
        colour_scalars = DPUtil.generateColourScalars(dfCluster, colourBy, dfStage)
        
    scale = 1
    figure, tax = ternary.figure(scale=scale)
    
    # Draw Boundary and Gridlines
    tax.boundary(linewidth=2.0)
    tax.gridlines(color='black', multiple=0.1)
    figure.set_size_inches(6, 6)
    
    # Set Axis labels and Title
    fontsize = 19
    offset = 0.14
    fontsize_label = 14

    if hideTicks is False:
        tax.left_axis_label('Normalized Log of PI value', 
                            fontsize=fontsize_label, offset=offset)
        tax.right_axis_label('Normalized Log of SI value', 
                             fontsize=fontsize_label, offset=offset)
        tax.bottom_axis_label('Normalized Log of DI value', 
                              fontsize=fontsize_label, offset=offset)
    else:
        tax.right_corner_label('DI', fontsize=fontsize, fontweight='bold')
        tax.top_corner_label('SI', fontsize=fontsize, fontweight='bold')
        tax.left_corner_label('PI', fontsize=fontsize, fontweight='bold')

    if plotTitle is not None:
        tax.set_title(plotTitle, fontsize=fontsize, y=-0.1)

    if hideTicks is False:
        # Draw the ternary plot ticks
        tax.ticks(axis='lbr', multiple=0.1, linewidth=1, 
                  offset=0.025, tick_formats="%.1f")
        
    tax.get_axes().axis('off')
    tax.clear_matplotlib_ticks()
    
    if colourBy == 'Stage Database Colour':
        cmap = None
        vmin = None
        vmax = None

    else:
        vmin = dfCluster[colourBy].min()
        vmax = dfCluster[colourBy].max()
        
        # Set limits if provided
        if limits is not None:
            vmin = limits.zMin
            vmax = limits.zMax
        
    # Plot the points
    tax.scatter(points, s=sizeOfDots, c=colour_scalars, cmap=cmap,
                vmin=vmin, vmax=vmax)
    
    if trendLine:
        DPUtil.addTrendLineToTernaryPlot(tax, dfCluster, colourBy)
    
    if colourBy != 'Stage Database Colour':
        # Make colour bar bounds
        norm = mpl.colors.Normalize(vmin=dfCluster[colourBy].min(), 
                                    vmax=dfCluster[colourBy].max())
        
        # Set limits if provided
        if limits is not None:
            norm = mpl.colors.Normalize(limits.zMin, 
                                        limits.zMax)
        
        # Initialize the color bar axes
        ax2 = figure.add_axes([0.97, 0.25, 0.05, 0.65])
        
        # r_cmap is the reverse maping of cmap
        # This is so that the color bar can go from low at the top to high at the bottom
        # Most maps have a reverse in the from of map_r
        if len(cmap.split('_')) > 1:
            r_cmap = cmap.split('_')[0]
        else:
            r_cmap = cmap+'_r'
        
        # Draw the colour bar
        
        cb1 = mpl.colorbar.ColorbarBase(ax2, cmap=plt.get_cmap(r_cmap),
                                        norm=norm,
                                        orientation='vertical')
        cb1.set_label(colourBy)
        
        # If colourBy is a spatial corrdinate, show where the first stage is on the
        # colour bar
        if colourBy in ['Depth', 'Easting', 'Northing']:
            
            first_stage_name = dfCluster['FRAC_STAGE_ID'].unique()[0]
        
            y_key = colourBy[0]
            
            # The key for Depth is Z in the stage data
            if colourBy == "Depth":
                y_key = 'Z'
            
            y_key_mid = (dfStage.loc[first_stage_name, y_key+'1'] + dfStage.loc[first_stage_name, y_key+'2'])/2.0
            
            # Flip position of stage hex on colourbar
            y_key_mid = ax2.get_ylim()[1] - (y_key_mid - ax2.get_ylim()[0])
            
            # Plot it, the x corrdinate of the hexagon is surprisingly not 0
            ax2.plot(ax2.get_xlim()[0], y_key_mid, 'wh', markersize=20)
            ax2.plot(ax2.get_xlim()[0], y_key_mid, 'k+', markersize=20)
        
        # If the range of data is greater than 10, change to int so it looks cleaner
        if dfCluster[colourBy].max() - dfCluster[colourBy].min() > 10:
            cb1.set_ticks(np.flip(cb1.get_ticks()).astype(int))
            cb1.set_ticklabels(np.flip(cb1.get_ticks()).astype(int))
        else:
            cb1.set_ticks(np.flip(cb1.get_ticks()))
            cb1.set_ticklabels(np.flip(cb1.get_ticks()))

    if figPath is not None:
        if ".png" not in figPath:
            # if no filename provided then by default name using the color parameter and number of stages included
            nstgs = len(dfStage)
            if nstgs > 1:
                stgs_str = "MultipleStages_nstgs-"+str(nstgs)
            elif nstgs == 1:
                stgs_str = dfStage.index[0]
            else:
                stgs_str = "NoStgs"
            figPath += "TernaryPlot_"+colourBy+"_"+stgs_str+".png"
        plt.savefig(figPath, dpi=200, bbox_inches="tight")
        
    plt.show()
    

def clustersByString(dfCluster, independantVariable, rot=45, limits=None,
                     axIn=None, figPath=None):

    """
    Output a plot that shows how many clusters exists in each unique 
    string of the independant variable provided
    
    Inputs
    ======
    dfCluster : pandas.DataFrame
        Cluster data to analyze
    independantVariable : string
        Variable with which to analyze how may clusters are each unique string
    rot : scalar
        How much to rotate the labels by 
        (this is so that the labels don't collide)
    limits : DataClass.Limits
        Limits the range of the plot
        X limits are the limits to the independantVariable
        Y limits are the limits to the Number of Clusters
    
    Returns
    =======
    None, just outputs plots
    
    Dependencies
    ============
    numpy
    matplotlib.pyplot
    """
    
    if independantVariable not in dfCluster.columns:
        raise Exception(independantVariable + 'is not a DPA cluster attribute\n' +
                        'Type dfCluster.columns in a blank cell to see the available attributes')
    
    # Fill a list with all the numbers from 1 to how many unique strings there are
    # This will be used to map the labels onto the graph
    x = []
    for i in range(1, len(dfCluster[independantVariable].unique()) + 1):
        x.append(i)
    
    labels = []
    y = []
    
    # Count how many clusters are in each unique string
    for name in dfCluster[independantVariable].unique():
        y.append(dfCluster[dfCluster[independantVariable] == name].shape[0])
        # Put unique string into the labels list
        labels.append(name)
    
    # Plot the bar graph
    if axIn is None:
        ax = plt.gca()
        ax.bar(x, y, align='center')
    else:
        ax = axIn
        ax.bar(x, y, align='center')
    # Label the x ticks with the labels extracted earliers
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    # Rotate the text around an anchor that looks nice
    plt.setp(ax.xaxis.get_majorticklabels(), 
             rotation=(rot*-1), ha="left", rotation_mode="anchor") 
    ax.figure.set_size_inches(12, 12)
    ax.set_xlabel(independantVariable)
    ax.set_ylabel('Number of Clusters')
    
    if axIn is None:
        if figPath is not None:
            plt.savefig(figPath + "ClusterBy"+independantVariable+".png", dpi=200)
        plt.show()
    else:
        return ax


def plotFractureDimensions(dfCluster, dfStage, dataOptions, axis='Width', legend=True,
                           customlim=None, inverty=True, flipx=False,
                           savecatalog=False, figPath=None):
    # Plot regular (Phase II) and DPA fracture dimensions

    # To save a final copy of the combinedDF dataframe pass savecatalog="path.xlsx"

    def intersection(lst1, lst2):
        """
        Find values in both lists
        :param lst1: first list
        :param lst2: second list
        :return:
        """
        lst3 = [value for value in lst1 if value in lst2] 
        return lst3
    
    axises = ['Width', 'Length', 'Height']
    
    if axis not in axises:
        warningstring = ("Selected axis is not supported, "
                         + "please use one of the following: \n")
        for option in axises:
            warningstring += ('\n'+option)
            
        print(warningstring)
        return
    
    left = ''
    right = ''
    
    if axis == 'Width':
        left = 'Width1'
        right = 'Width2'
        
    if axis == 'Length':
        left = 'Length1'
        right = 'Length2'
        
    if axis == 'Height':
        left = 'HeightBot'
        right = 'HeightTop'

    # Load Fracture dimensions table
    combined_df = Database.readsqlpd(dataOptions.DSN, table='FracDimensionTable', sqlstr=dataOptions.sqlsrv)

    for well in combined_df['Name'].str.split(' Stage', expand=True)[0].unique():
        
        gs1 = mpl.gridspec.GridSpec(1, 2)
        gs1.update(wspace=0.0, hspace=0.0)  # set the spacing between axes.
        
        ax1 = plt.subplot(gs1[0])
        ax2 = plt.subplot(gs1[1])
        plt.subplots_adjust(wspace=None, hspace=None)
        
        df_frac = combined_df[(combined_df['Type'] == 'FinalType') & combined_df['Name'].str.startswith(well)]
        df_dpa_frac = combined_df[(combined_df['Type'] == 'DPAType') & combined_df['Name'].str.startswith(well)]
        df_frac = df_frac.set_index('Name')
        df_dpa_frac = df_dpa_frac.set_index('Name')
        
        stages1 = df_dpa_frac.index.unique()
        stages2 = df_frac.index.unique()
        stages = intersection(stages1, stages2)

        # stop loop if no stages for this well in phase ii dimensions nor DPA dimensions
        if (len(stages2) == 0) & (len(stages1) == 0):
            break

        # only plot regular Phase II frac dimensions if there are any to plot
        avg_height = None
        y_pos = None
        if (len(stages2) > 0) and (len(stages1) > 0):

            if axis == 'Height':
                heights = []

                for stage in stages:
                    cur_height = (dfStage.loc[stage, 'Z1'] + dfStage.loc[stage, 'Z2'])/2
                    heights.append(cur_height)

                avg_height = sum(heights)/len(heights)

            y_pos = np.arange(len(stages))
            west_frac_length = []
            east_frac_length = []

            for stage in stages:
                try:
                    west_frac_length.append(df_frac.loc[stage, left])
                except:
                    if axis == 'Height':
                        west_frac_length.append(avg_height)
                    else:
                        west_frac_length.append(0)
                try:
                    east_frac_length.append(df_frac.loc[stage, right])
                except:
                    if axis == 'Height':
                        east_frac_length.append(avg_height)
                    else:
                        east_frac_length.append(0)

            if flipx:
                temp = east_frac_length
                east_frac_length = west_frac_length
                west_frac_length = temp

            if len(west_frac_length) == 0:
                print("Well: " + well + " is blank for west half length. Skipping plot for this well.")
                pass
            else:
                ax1.barh(y_pos, west_frac_length, align='center')
                ax1.set_yticks(y_pos)
                ax1.set_yticklabels(stages)
                ax1.set_ylim(min(y_pos) - 0.5, max(y_pos) + 0.5)
                if inverty:
                    ax1.invert_yaxis()
                if flipx:
                    # ax1.invert_xaxis()
                    pass

            if axis != 'Height':
                if len(east_frac_length) == 0:
                    print("Well: " + well + " is blank for east half length. Skipping plot for this well.")
                    pass
                else:
                    ax2.barh(y_pos, east_frac_length, align='center')
            if len(y_pos) > 0:
                ax2.set_ylim(min(y_pos) - 0.5, max(y_pos) + 0.5)
            if inverty:
                ax2.invert_yaxis()
            if flipx:
                # ax2.invert_xaxis()
                pass

            if (len(west_frac_length) > 0) and (len(east_frac_length) > 0):
                ax2.get_yaxis().set_visible(False)

                if axis == 'Height':
                    west_lim = max(west_frac_length)
                    east_lim = min(east_frac_length)
                    lim = abs(max([abs(west_lim), abs(east_lim)]) - avg_height)
                else:
                    west_lim = min(west_frac_length)
                    east_lim = max(east_frac_length)
                    lim = max([abs(west_lim), abs(east_lim)])*1.1

                if customlim is not None:
                    lim = customlim

                if axis == 'Height':
                    ax1.set_xlim(avg_height + lim, avg_height)
                    ax2.set_xlim(avg_height, avg_height - lim)
                else:
                    ax1.set_xlim(lim*-1, 0)
                    ax2.set_xlim(0, lim)

                if axis == 'Height':
                    ax2_height = ax2.twiny()
                    ax2_height.axis('off')
                    ax2_height.set_xlim([min(ax2.get_xlim()), max(ax2.get_xlim())])
                    east_frac_length_inv = []
                    for fraclen in east_frac_length:
                        east_frac_length_inv.append(min(ax2_height.get_xlim()) + (max(ax2_height.get_xlim()) - fraclen))
                    ax2_height.barh(y_pos, east_frac_length_inv, align='center')

        if len(stages1) > 0:
            ax1_dpa = ax1.twinx()
            ax2_dpa = ax2.twinx()

            west_frac_length_dpa = []
            east_frac_length_dpa = []
            for stage in stages:
                try:
                    west_frac_length_dpa.append(df_dpa_frac.loc[stage, left])
                except:
                    if axis == 'Height':
                        west_frac_length_dpa.append(avg_height)
                    else:
                        west_frac_length_dpa.append(0)
                try:
                    east_frac_length_dpa.append(df_dpa_frac.loc[stage, right])
                except:
                    if axis == 'Height':
                        east_frac_length_dpa.append(avg_height)
                    else:
                        east_frac_length_dpa.append(0)
            if flipx:
                temp = east_frac_length_dpa
                east_frac_length_dpa = west_frac_length_dpa
                west_frac_length_dpa = temp

            ax1_dpa.barh(y_pos, west_frac_length_dpa, align='center', color=(1, 0, 0, 0.5))
            ax1_dpa.set_yticks(y_pos)
            ax1_dpa.get_yaxis().set_visible(False)
            ax1_dpa.set_ylim(min(y_pos) - 0.5, max(y_pos) + 0.5)
            if inverty:
                ax1_dpa.invert_yaxis()
            if flipx:
                # ax1DPA.invert_xaxis()
                pass

            if axis != 'Height':
                ax2_dpa.barh(y_pos, east_frac_length_dpa, align='center', color=(1, 0, 0, 0.5))
            ax2_dpa.set_yticks(y_pos)
            ax2_dpa.get_yaxis().set_visible(False)
            ax2_dpa.set_ylim(min(y_pos) - 0.5, max(y_pos) + 0.5)
            if inverty:
                ax2_dpa.invert_yaxis()
            if flipx:
                # ax2DPA.invert_xaxis()
                pass

            if axis == 'Height':
                ax2_height_dpa = ax2_dpa.twiny()
                ax2_height_dpa.axis('off')
                ax2_height_dpa.set_xlim([min(ax2_dpa.get_xlim()), max(ax2_dpa.get_xlim())])
                east_frac_length_inv = []
                for fraclen in east_frac_length_dpa:
                    east_frac_length_inv.append(min(ax2_height_dpa.get_xlim()) +
                                                (max(ax2_height_dpa.get_xlim()) - fraclen))
                ax2_height_dpa.barh(y_pos, east_frac_length_inv, align='center', color=(1, 0, 0, 0.5))

        if axis == 'Width':
            ax1.set_xlabel('Fracture Behind Well from Stage Mid')
            ax2.set_xlabel('Fracture Along Well from Stage Mid')
            
        if axis == 'Length':
            ax1.set_xlabel('Fracture Left of Stage')
            ax2.set_xlabel('Fracture Right of Stage')            
            
        if axis == 'Height':
            ax1.set_xlabel('Fracture Depth Below Well')
            ax2.set_xlabel('Fracture Depth Above Well')
        
        if legend:
            blue_patch = mpatches.Patch(color='blue', label='Total '+axis)
            red_patch = mpatches.Patch(color=(1, 0, 0, 0.5), label='Effective '+axis)
            plt.legend(handles=[blue_patch, red_patch])
        
        ysize = 0.3*len(stages)
        
        plt.gcf().set_size_inches(8, ysize)

        if figPath is not None:
            plt.savefig(figPath + "DimensionPlot_"+well+"_"+axis+".png", dpi=200)

        plt.show()

    if savecatalog is not False:
        if isinstance(savecatalog, str):
            savecatalog = Database.makeLinuxPath(savecatalog)
            combined_df.to_excel(savecatalog)
            print("Wrote catalog to: "+str(savecatalog))


def clustersByInterval(dfCluster, independantVariable, 
                       intervalWidth=0, intervals=0, limits=None, axIn=None, figPath=None):
    
    """
    Output a plot that shows how many clusters exists in each interval of the 
    independant variable provided
    
    Inputs
    ======
    dfCluster : pandas.DataFrame
        Cluster data to analyze
    independantVariable : string
        Variable with which to analyze how may clusters are each interval
    intervalWidth : scalar, optional (don't define if intervals is defined)
        The width of each interval grouping
    intervals : int, optional (don't define if intervalWidth is defined)
        The number of grouping intervals
    limits : DataClass.Limits
        Limits the range of the plot
        X limits are the limits to the independantVariable
        Y limits are the limits to the Number of Clusters
    
    Returns
    =======
    None, just outputs plots
    
    Dependencies
    ============
    numpy
    matplotlib.pyplot
    """
    
    if independantVariable not in dfCluster.columns:
        raise Exception(independantVariable + 'is not a DPA cluster attribute\n' +
                        'Type dfCluster.columns in a blank cell to see the available attributes')
    
    # Setup intervalWidth and intervals based on the values given or not given
    intervalWidth, intervals = DPUtil.intervalSetup(intervalWidth, intervals,
                                                    dfCluster, independantVariable)

    x = []
    y = []
    
    # Split up the number of Events by independant variable interval
    for i in range(intervals):
        minvalforinterval = (dfCluster[independantVariable].min()
                             + intervalWidth*i)
        maxvalforinterval = (dfCluster[independantVariable].min()
                             + intervalWidth*(i + 1))
        x.append(dfCluster[independantVariable].min()
                 + intervalWidth*(i + 0.5))
        y.append(DPUtil.dfBetweenTwoValues(dfCluster, 
                                           independantVariable, 
                                           minvalforinterval,
                                           maxvalforinterval).shape[0])

    # Plot the chart
    if axIn is None:
        plt.bar(x, y, width=(intervalWidth * 0.8))
        ax = plt.gca()
    else:
        ax = axIn
        ax.bar(x, y, width=(intervalWidth * 0.8))
    
    ax.set_xlabel(independantVariable)
    ax.set_ylabel('Number of Clusters')
    
    # Set limits if provided
    if limits is not None:
        ax.set_xlim(limits.xMin, limits.xMax)
        ax.set_ylim(limits.yMin, limits.yMax)
    
    ax.figure.set_size_inches(12, 12)
    
    if axIn is None:
        if figPath is not None:
            plt.savefig(figPath + "ClustersBy"+independantVariable+"_Intervals"+str(intervals)+".png", dpi=200)
        plt.show()
    else:
        return ax


def linePlotAx(ax, dfClusterCur, xVar, yVar, orderBy, 
               smoothByInterval, smoothPoints, color=None):
    
    """
    Plots a line on a matplotlib.axes, option to smooth the data
    
    Inputs
    ======
    ax : matplotlib.pyplot.axes
        Axes to plot the line on
    xVar : string
        Variable to go on the X Axis
    yVar : string
        Variable to go on the Y axis
    orderBy : string, optional (defaults to xVar)
        Which variable should the data be ordered by (the independant variable)
    smoothPoints : int
        Number of points near each data point to be used for smoothing the data
    smoothByInterval : bool, optional
        Whether to smooth by intervals and output only one datapoint per interval
    color: tuple, optional
        The color to plot the lines with.

    Returns
    =======
    line : matplotlib.pyplot.line
        The line object that was plotted
    
    Dependencies
    ============
    DPUtil.smoothPointsByInterval
    """
    
    # If no orderBy string is provided, it defaults to xVar
    if orderBy is None:
        orderBy = xVar
        
    # Sort the data by the independant variable and set that variable as the
    # index for rolling average processing
    dfClusterCur = dfClusterCur.sort_values(orderBy)
    dfClusterCur = dfClusterCur.set_index(orderBy)
    
    # keep data for drawDeviation
    dfClusterCur[orderBy] = dfClusterCur.index.values
    
    # perform the rolling average on the dependant variable and plot the data
    line = None
    if orderBy == xVar:
        if smoothByInterval:
            x, yclean = DPUtil.smoothPointsByInterval(dfClusterCur.index.values,
                                                      dfClusterCur[yVar].values, smoothPoints)
            line = ax.plot(x, yclean, color=color)
        else:
            yclean = dfClusterCur[yVar].rolling(smoothPoints,
                                                min_periods=1).mean()
            line = ax.plot(dfClusterCur.index.values, yclean, color=color)
        
    if orderBy == yVar:
        if smoothByInterval:
            y, xclean = DPUtil.smoothPointsByInterval(dfClusterCur.index.values,
                                                      dfClusterCur[xVar].values, smoothPoints)
            line = ax.plot(xclean, y, color=color)
        else:
            xclean = dfClusterCur[xVar].rolling(smoothPoints,
                                                min_periods=1).mean()
            line = ax.plot(xclean, dfClusterCur.index.values, color=color)

    if line is None:
        raise ValueError('None of the above conditions were fulfilled! Ask a Python person.')

    return line


def linePlotMulti(dfCluster, dfLitho, dfStage, xVar, yVar, orderBy=None,
                  smoothPoints=30, smoothByInterval=False,
                  SD=None, limits=None, set_dpi=100, figsize=(6, 6), ms=10,
                  figPath=None):
    """
    Output a plot that shows how many clusters exists in each interval of the 
    independant variable provided
    
    Inputs
    ======
    dfCluster : pandas.DataFrame
        Cluster data to plot
    dfLitho : pandas.DataFrame
        Litho data
    dfStage : pandas.DataFrame
        Stage data
    xVar : string
        Variable to go on the X Axis
    yVar : string
        Variable to go on the Y axis
    orderBy : string, optional (defaults to xVar)
        Which variable should the data be ordered by (the independant variable)
    smoothPoints : int
        Number of points near each data point to be used for smoothing the data
    smoothByInterval : bool, optional
        Whether to smooth by intervals and output only one datapoint per interval
    SD : scalar, optional
        If set, plots a highlight box that covers x standard deviations from the mean
    limits : DataClass.Limits
        Limits the range of the plot
        X limits are the limits to the xVar
        Y limits are the limits to the yVar
    figPath : str, optional
        path where to save figures

    Returns
    =======
    None, just outputs plots
    
    Dependencies
    ============
    matplotlib.pyplot
    """
    
    if xVar not in dfCluster.columns:
        raise Exception(xVar + ' is not a DPA cluster attribute\n' +
                        'Type dfCluster.columns in a blank cell to see the available attributes')
    if yVar not in dfCluster.columns:
        raise Exception(xVar + ' is not a DPA cluster attribute\n' +
                        'Type dfCluster.columns in a blank cell to see the available attributes')
    if orderBy not in [xVar, yVar]:
        raise Exception(orderBy + ' is not either ' + xVar + ' or ' + yVar)
    
    if len(dfCluster['FRAC_STAGE_ID'].unique()) > len(distinctColours):
        print("There aren't enough distinct colours to colour your graph meaningfully. Plotting anyway.")
    
    colour_index = 0
    
    stage_depth = []
    
    # Set limits if provided
    if limits is not None:
        if limits.xMin is not None:
            plt.gca().set_xlim(limits.xMin, limits.xMax)
        if limits.yMin is not None:
            plt.gca().set_ylim(limits.yMin, limits.yMax)

    name = None
    for name in dfCluster['FRAC_STAGE_ID'].unique():
        # set the color of the stage from the database
        temp_color = dfStage.loc[name, 'Colour']

        df_cluster_cur = dfCluster[dfCluster['FRAC_STAGE_ID'] == name]
        line = linePlotAx(plt.gca(), df_cluster_cur, xVar, yVar,
                          orderBy, smoothByInterval, smoothPoints, color=temp_color)
        line[0].set_label(name)
        
        colour_index = colour_index + 1
        
        stage_depth.append((dfStage.loc[name, 'Z1'] + dfStage.loc[name, 'Z2'])/2)
    
    plt.legend(loc='upper left', bbox_to_anchor=(1.3, 1))
    
    # If the yVar is Depth, invert the y axis and plot litho data
    if yVar == 'Depth':
        plt.gca().invert_yaxis()
        addLitho(plt.gca(), dfLitho)
        
        stage_depth = (dfStage.loc[name, 'Z1'] + dfStage.loc[name, 'Z2'])/2
        xlim_before = plt.gca().get_xlim()
        plt.gca().plot(xlim_before[0], stage_depth, 'kh', markersize=ms)
        plt.gca().plot(xlim_before[0], stage_depth, 'w+', markersize=ms)
        plt.gca().set_xlim(xlim_before)
    
    plt.gca().set_xlabel(xVar)
    plt.gca().set_ylabel(yVar)
    
    # If standard deviations is given, draw that
    if SD is not None:
        sd_var = None
        if orderBy == xVar:
            sd_var = 'x'
        if orderBy == yVar:
            sd_var = 'y'
        
        drawDeviation(plt.gca(), dfCluster, orderBy, sd_var, SD)
    
    plt.gca().set_title('All Data')
        
    plt.gcf().set_size_inches(figsize[0], figsize[1])
    
    plt.gcf().set_dpi(set_dpi)

    if figPath is not None:
        plt.savefig(figPath + "Plot_"+xVar+"_"+yVar+".png", dpi=200)

    plt.show()
    
    
def linePlot(dfCluster, dfLitho, dfStage, xVar, yVar, orderBy=None,
             smoothPoints=30, smoothByInterval=False,
             SD=None, limits=None, figsize=(4, 4), ms=10,
             set_dpi=100, text=True, grid=False, forReport=False,
             titlefont=13, figPath=None, usedip=False, debug=False):
    
    """
    Output a plot that shows how many clusters exists in each interval of the 
    independant variable provided
    
    Inputs
    ======
    dfCluster : pandas.DataFrame
        Cluster data to plot
    dfLitho : pandas.DataFrame
        Litho data
    dfStage : pandas.DataFrame
        Stage data
    xVar : string
        Variable to go on the X Axis
    yVar : string
        Variable to go on the Y axis
    orderBy : string, optional (defaults to xVar)
        Which variable should the data be ordered by (the independant variable)
    smoothPoints : int, optional
        Number of points near each data point to be used for smoothing the data
    smoothByInterval : bool, optional
        Whether to smooth by intervals and output only one datapoint per interval
    SD : scalar, optional
        If set, plots a highlight box on that covers x standard deviations from the mean
    limits : DataClass.Limits, optional
        Limits the range of the plot
        X limits are the limits to the xVar
        Y limits are the limits to the yVar
    ms : int, optional
        marker size in plot
    set_dpi : int, optional
        customize dpi of plot
    forReport : boolean, optional
        option to hide number of clusters for final report if desired
    title_font : int, optional
        font size of title for plot
    figPath : str, optional
        optional path to save figure to if desired
    usedip : boolean, optional
        use formation strike and dip to adjust lithological unit tops

    Returns
    =======
    None, just outputs plots
    
    Dependencies
    ============
    matplotlib.pyplot
    """
    
    if xVar not in dfCluster.columns:
        raise Exception(xVar + 'is not a DPA cluster attribute\n' +
                        'Type dfCluster.columns in a blank cell to see the available attributes')
    if yVar not in dfCluster.columns:
        raise Exception(xVar + 'is not a DPA cluster attribute\n' +
                        'Type dfCluster.columns in a blank cell to see the available attributes')
    if orderBy not in [xVar, yVar]:
        raise Exception(orderBy + 'is not either ' + xVar + ' or ' + yVar)
    
    for name in DPUtil.alphanumericsort(dfCluster['FRAC_STAGE_ID'].unique()):
        
        df_cluster_cur = dfCluster[dfCluster['FRAC_STAGE_ID'] == name]
        
        # Plot smoothed line of data to plot
        linePlotAx(plt.gca(), df_cluster_cur, xVar, yVar,
                   orderBy, smoothByInterval, smoothPoints)
        
        # Set limits if provided
        if limits is not None:
            if limits.xMin is not None:
                plt.gca().set_xlim(limits.xMin, limits.xMax)
            if limits.yMin is not None:
                plt.gca().set_ylim(limits.yMin, limits.yMax)
        
        # If the yVar is Depth, invert the y Axis and plot the litho data
        if yVar == 'Depth':
            plt.gca().invert_yaxis()

            stagenorth = dfStage.loc[name, 'stgN']
            stageeast = dfStage.loc[name, 'stgE']
            stagedepth = dfStage.loc[name, 'stgD']

            if usedip:
                # Calculate depth offset to apply to lithotops due to 2d dip
                strike = dfLitho.strike
                dip = dfLitho.dip
                refn = dfLitho.fmlog_n
                refe = dfLitho.fmlog_e
                offset = MathUtil.calc_depth_offset(stagenorth, stageeast, refn, refe, strike, dip)

                if debug:
                    print("Use dip enabled for stage: "+name)
                    print("Strike: "+str(strike)+" - Dip: "+str(dip)+" refN: "+str(refn)+" refE: "+str(refe))
                    print("Current stage zone - stgN: "+str(stagenorth) +
                          " stgE: "+str(stageeast)+" stgD: "+str(stagedepth))
                    print("Calculated lithotop depth offset: "+str(offset))
            else:
                # Do not apply an offset
                offset = 0.0

            # Add lithotop boxes
            addLitho(plt.gca(), dfLitho, offset=offset)

            xlimbefore = plt.gca().get_xlim()
            plt.gca().plot(xlimbefore[0], stagedepth, 'kh', markersize=ms)
            plt.gca().plot(xlimbefore[0], stagedepth, 'w+', markersize=ms)
            plt.gca().set_xlim(xlimbefore)

        # If standard deviations is given, draw a rectangle that covers
        # x Standard deviations from the mean
        if SD is not None:
            sdvar = None
            if orderBy == xVar:
                sdvar = 'x'
            if orderBy == yVar:
                sdvar = 'y'
            
            drawDeviation(plt.gca(), df_cluster_cur, orderBy, sdvar, SD, text=text)

        plt.gca().set_xlabel(xVar, color='blue', fontsize=12)
        plt.gca().set_ylabel(yVar, color='blue', fontsize=12)

        # it is useful to know the number of clusters being shown
        # forReport boolean disables number of clusters from title for reports
        if forReport:
            plt.gca().set_title(name, fontsize=titlefont)
        else:
            plt.gca().set_title(name+" - "+str(len(df_cluster_cur)) + " clusters", fontsize=titlefont)

        plt.gcf().set_size_inches(figsize[0], figsize[1])
        
        plt.gcf().set_dpi(set_dpi)

        if grid:
            plt.grid(which='major', color='black')
            plt.minorticks_on()
            plt.grid(True, which='minor', color='r', linestyle='--', alpha=0.2)

        if figPath is not None:
            # Save figure if desired
            plt.savefig(figPath + "DPAlineplot_" + name + "_"+xVar+"_"+yVar+".png", dpi=set_dpi)

        plt.show()


def calcFracDim(dfCluster, dfStage, dataOptions,
                smoothPoints=30, smoothByInterval=False,
                SD=None, limits=None, figsize=(6, 6),
                set_dpi=150, text=True, legend=True, showClusters=False, figPath=None
                ):
    """
    Calculate fracture dimension
    """
    combineddf = Database.readsqlpd(dataOptions.DSN, table='FracDimensionTable', sqlstr=dataOptions.sqlsrv)
    combineddf = combineddf[combineddf.duplicated('Name', keep=False)]

    xvar = 'LateralDistanceParallelToFracAzimuthOfPerf'
    orderby = xvar
    yvar = 'LogOfPlasticityIndex'

    dffrac = combineddf[(combineddf['Type'] == 'FinalType')]
    dfdpafrac = combineddf[(combineddf['Type'] == 'DPAType')]
    dffrac = dffrac.set_index('Name')
    dfdpafrac = dfdpafrac.set_index('Name')

    for name in dfCluster['FRAC_STAGE_ID'].unique():
        fig, ax = plt.subplots(figsize=figsize)
        df_cluster_cur = dfCluster[dfCluster['FRAC_STAGE_ID'] == name]

        linePlotAx(ax, df_cluster_cur, xvar, yvar,
                   orderby, smoothByInterval, smoothPoints)

        # Set limits if provided
        if limits is not None:
            if limits.xMin is not None:
                ax.set_xlim(limits.xMin, limits.xMax)
            if limits.yMin is not None:
                ax.set_ylim(limits.yMin, limits.yMax)

        ymin, ymax = ax.get_ylim()[0], ax.get_ylim()[1]
        l1, l2 = dffrac.loc[name].Length1, dffrac.loc[name].Length2
        ax.plot([l1, l1], [ymin, ymax], color='blue')
        ax.plot([l2, l2], [ymin, ymax], color='blue')

        l1, l2 = dfdpafrac.loc[name].Length1, dfdpafrac.loc[name].Length2
        ax.plot([l1, l1], [ymin, ymax], color='red')
        ax.plot([l2, l2], [ymin, ymax], color='red')

        # If standard deviations is given, draw a rectangle that covers
        # x Standard deviations from the mean
        left = None
        right = None
        if SD is not None:
            sdvar = 'x'
            left_clusters = df_cluster_cur[df_cluster_cur['LateralDistanceParallelToFracAzimuthOfPerf'] < 0]
            if len(left_clusters) > 0:
                left, _ = drawDeviation(ax, left_clusters, orderby, sdvar, SD, text=text)
            else:
                left = 0

            right_clusters = df_cluster_cur[df_cluster_cur['LateralDistanceParallelToFracAzimuthOfPerf'] > 0]
            if len(right_clusters) > 0:
                _, right = drawDeviation(ax, right_clusters, orderby, sdvar, SD, text=text)
            else:
                right = 0

        l1, l2 = left, right
        ax.plot([l1, l1], [ymin, ymax], color='orange')
        ax.plot([l2, l2], [ymin, ymax], color='orange')
        # TODO Write mean/std frac dimensions to database

        # Show location of clusters
        if showClusters:
            ax2 = ax.twinx()
            ax2.scatter(df_cluster_cur['LateralDistanceParallelToFracAzimuthOfPerf'],
                        df_cluster_cur['Depth'], color='black', alpha=0.5)
            ax2.invert_yaxis()
            ax2.set_ylabel('Depth')

        if legend:
            p1 = mpatches.Patch(color='blue', label='Regular half lengths')
            p2 = mpatches.Patch(color='red', label='Effective half lengths from DB')
            p3 = mpatches.Patch(color='orange', label='Effective half length from stdev+mean')
            ax.legend(handles=[p1, p2, p3])
        ax.set_xlabel(xvar)
        ax.set_ylabel(yvar)
        ax.set_title(name+" - "+str(len(df_cluster_cur)) + " clusters")

        fig.set_size_inches(figsize[0], figsize[1])
        fig.set_dpi(set_dpi)

        if figPath is not None:
            fig.savefig(figPath + "FracDim_"+name+".png", dpi=200)

        plt.show()


def heatmapGun(dfCluster, dfLitho, dfStage, relStage, xlimit=None,
               figsize=(6, 6), ms=20, ylimits=None,
               set_dpi=150, dontRotate=False, angle=None,
               vmin=0, vmax=0.000009, dfEvent=None, plotLitho=True,
               svcfile=None, flipx=False, figPath=None):
    
    """
    Output a plot that shows how many clusters exists in each interval of the 
    independant variable provided
    
    Inputs
    ======
    dfCluster : pandas.DataFrame
        Cluster data to plot
    dfLitho : pandas.DataFrame
        Litho data
    dfStage : pandas.DataFrame
        Stage data
    smoothPoints : int, optional
        Number of points near each data point to be used for smoothing the data
    smoothByInterval : bool, optional
        Whether to smooth by intervals and output only one datapoint per interval
    SD : scalar, optional
        If set, plots a highlight box on that covers x standard deviations from the mean
    xlimit : xlim
    ms : int, optional
        marker size in plot
    set_dpi : int, optional
        customize dpi of plot
    
    Returns
    =======
    None, just outputs plots
    
    Dependencies
    ============
    matplotlib.pyplot
    """
    import seaborn as sns

    df_stage_rot = None
    df_cluster_rot = None
    df_event_rot = None
    if dfCluster is not None:
        df_cluster_rot, df_stage_rot = MathUtil.addRelativeCoordinates(dfCluster, dfStage, relStage,
                                                                       angle=angle, dontRotate=dontRotate)
        # Add treatment well names to dataframes
        df_cluster_rot['TreatmentWell'] = df_cluster_rot.FRAC_STAGE_ID.str.split().str[0]
   
    if dfEvent is not None:
        df_event_rot, df_stage_rot = MathUtil.addRelativeCoordinates(dfEvent, dfStage, relStage,
                                                                     angle=angle, dontRotate=dontRotate)
        df_event_rot['TreatmentWell'] = df_event_rot.FRAC_STAGE_ID.str.split().str[0]

    df_stage_rot['Depth'] = (df_stage_rot['Z1']+df_stage_rot['Z2'])/2.0

    for well, grp in df_cluster_rot.groupby('TreatmentWell'):
        fig = plt.figure(facecolor='w', figsize=figsize)
        ax = fig.add_subplot(111)
        zorder = 1
    
        # Grab stage zones for this well
        x_stg = df_stage_rot[df_stage_rot.TreatmentWell == well]['Distance Right Perpendicular To Well1']
        y_stg = df_stage_rot[df_stage_rot.TreatmentWell == well].Depth

        if 'LateralDistanceParallelToFracAzimuthOfPerf' not in dfCluster.columns:
            # plotting events and not cluster dataframe
            dfCluster = dfEvent
            dfEvent = None
        
        if dfEvent is not None:
            # grab event data to plot
            x_evt = df_event_rot['Distance Right Perpendicular To Well']
            y_evt = df_event_rot['Depth']
            # plot kde of event data
            ax = sns.kdeplot(x_evt, y_evt, n_levels=200, bw=(50), cmap='GnBu', alpha=0.8, vmin=vmin, vmax=vmax,
                             shade=True, gridsize=200, shade_lowest=False, zorder=zorder)
            zorder += 1
        
        # grab cluster data to plot
        if dfCluster is not None:
            x = grp['LateralDistanceParallelToFracAzimuthOfPerf']
            y = grp['Depth']
            # plot kde
            ax = sns.kdeplot(x, y, n_levels=200, bw=(50), cmap='PuRd', alpha=0.8, vmin=vmin, vmax=vmax,
                             shade=True, gridsize=200, shade_lowest=False, zorder=zorder)
            zorder += 1
    
        # Plot Stage Centers
        ax.scatter(x_stg, y_stg, s=200, c='white', marker='*', edgecolors='black', zorder=zorder)
        zorder += 1

        # TODO PLOT WELLS
        # plotWells(ax,dfStage,'Distance Right Perpendicular To Well','Depth',
        #          svcfile=svcfile,angle=angle)

        if xlimit is not None:
            if flipx:
                xlimit *= -1
            ax.set_xlim(-1*xlimit, xlimit)
        if ylimits is not None:
            ax.set_ylim(ylimits[0], ylimits[1])
        ax.set_title(well[0]+' Plan', fontsize=14)
        ax.set_xlabel('Relative Easting (ft)', fontsize=12)
        ax.set_ylabel('Relative Depth (ft)', fontsize=12)
        ax.ticklabel_format(axis='both', style='scientific', scilimits=(0, 4))
        ax.tick_params(labelsize=10)
        ax.grid(True)
        ax.invert_yaxis()
        ax.set_aspect('equal')

        if plotLitho:
            addLitho(ax, dfLitho, txt=True)
    
        ax.title.set_text(well)
        
        plt.gcf().set_size_inches(figsize[0], figsize[1])                 
        plt.tight_layout()

        if figPath is not None:
            plt.savefig(figPath + "GunbarrelHeatMap_"+well+".png", dpi=200)

        plt.show()


def addLitho(ax, dfLitho, txt=True, offset=0.0, txt_factor=1.0):
    
    """
    Plots the litho data as rectangles on a graph
    
    Inputs
    ======
    ax : matplotlib.pyplot.axes
        The axes to draw the litho data on
    dfLitho : pandas.DataFrame
        Litho data
    txt : bool, optional
        Whether to show the litho layer labels
    offset : float, optional
        Use an offset to plot the lithotops shallower or deeper (useful after a rotation for example)
    txt_factor: float, optional
        Use a ratio to move the x position of the text (ex. xlim=(0,100) if factor in 0.5 then text would be in middle)

    Outputs
    ============
    None, outputs data to ax by reference
    
    Dependencies
    ============
    numpy
    """
    _dfLitho = dfLitho.copy()

    # apply a depth offset if provided
    _dfLitho.loc[:, 'Top'] = _dfLitho.Top + offset
    _dfLitho.loc[:, 'Bottom'] = _dfLitho.Bottom + offset

    # Only draw litho data that would be on the plot
    relevant_litho_truth_table = ((_dfLitho['Bottom'] > ax.get_ylim()[1])
                                  & (_dfLitho['Top'] < ax.get_ylim()[0]))
    _dfLitho = _dfLitho[relevant_litho_truth_table]
    extents = ax.get_xlim()

    # Draw all litho data as coloured rectangles
    for index, row in _dfLitho.iterrows():
        top = row['Top']
        bottom = row['Bottom']
        
        left = extents[0]
        right = extents[1]
        
        highlightSection(ax, top, bottom, left, right, [row['Colour_R'], row['Colour_G'], row['Colour_B']])

        if txt:
            ypos_text = (top + bottom) / 2

            if ypos_text < ax.get_ylim()[0] and ypos_text > ax.get_ylim()[1]:
                ax.text(extents[1] * txt_factor + (extents[1] - extents[0]) * 0.03 * txt_factor,
                        ypos_text, index, ha='left', va='top')


def plotDepthContourVsTime(ax, depths=None, times=None,
                           numDataPoints=None, depthContourAx=None,
                           spacing=120, limits=None,
                           hideDepthTicks=False, dimensionLimits=None):

    # Register a new colourmap where the first half is just alpha
    ncolors = 256
    color_array = plt.get_cmap('cool')(range(ncolors))
    color_array[:int(ncolors/2), -1] = np.linspace(0.0, 1.0, len(color_array[:int(ncolors/2), -1]))
    map_object = LinearSegmentedColormap.from_list(name='cool_alpha', colors=color_array)
    plt.register_cmap(cmap=map_object)
    
    # If there was no ax given to plot on, make one
    if depthContourAx is None:
        depthContourAx = ax.twinx()
    
    # Plot the depth contour
    majorlocator = depthContourAx.xaxis.get_major_locator()
    majorlocator.MAXTICKS = 100000
    depthContourAx.xaxis.set_major_locator(majorlocator)
    
    majorlocator = depthContourAx.yaxis.get_major_locator()
    majorlocator.MAXTICKS = 100000
    depthContourAx.yaxis.set_major_locator(majorlocator)

    depthContourAx.contourf(times, depths, numDataPoints, levels=int(np.amax(numDataPoints) + 1),
                            cmap='cool_alpha', zorder=-100)
    depthContourAx.spines['right'].set_position(('outward', spacing))
    depthContourAx.set_ylabel('Depth', color='#ff00ff')

    # debug
    # from IPython.core.display import display
    # display("depths: " + str(depths))
    # display("times: " + str(times))
    # display("dimensionLimits: zMin:" + str(dimensionLimits.zMin)+ " zMax:"+str(dimensionLimits.zMax))
    # display("numDataPoints: " + str(numDataPoints))

    if limits is not None:
        if limits.yMin is not None:
            depthContourAx.set_ylim(limits.yMin, limits.yMax)
    if dimensionLimits is not None:
        if dimensionLimits.zMin is not None:
            # display("Setting ylim")
            depthContourAx.set_ylim(dimensionLimits.zMin, dimensionLimits.zMax)
        else:
            pass
            # display("Not setting ylim1")
    else:
        pass
        # display("Not setting ylim2")

    if hideDepthTicks is True:
        # Hide tick labels
        # depthContourAx.tick_params(labelbottom=False)
        depthContourAx.tick_params(labelleft=False)   
        depthContourAx.tick_params(labelright=False)
        # depthContourAx.tick_params(labeltop=False)
        
    return depthContourAx
    

# <codecell> Non-simplified Plotting Functions
def plotArrow(ax, angle, xpct=0.1, ypct=0.1, lengthpct=0.05, color='black'):
    """
    Plot an arrow at a particular angle to demonstrate the rotation
    
    The arrow is in the upper right based on 
    
    Dependencies
    ============
    matplotlib.pyplot
    """
    # plot a north arrow
    from math import pi, cos, sin
    # arrow length
    r = lengthpct*(ax.get_xlim()[1]-ax.get_xlim()[0])
    # where to draw arrow in x
    arrow_x = ax.get_xlim()[0] + xpct*(ax.get_xlim()[1]-ax.get_xlim()[0])
    # where to draw arrow in y
    arrow_y = ax.get_ylim()[1] - ypct*(ax.get_ylim()[1]-ax.get_ylim()[0])
    # angle arrow
    angle_arrow = (angle - 90)*pi/180.0 * -1
    # draw arrow
    ax.arrow(arrow_x, arrow_y, r*cos(angle_arrow), r*sin(angle_arrow),
             shape='full', width=r, color=color)
     

def plotPump(dfPump, ax, rightadj=0.78, presKey=None, propconKey=None, flowKey=None, timeKey='Time in stage (min)',
             lims=None, spacing=90):
    """
    Plot treatment data (pressure, rate, proppant concentration) on a single plot (3 Y-axes).

    lims to set each axis limits in the order propCon, pressure, rate

    Dependencies
    ============
    matplotlib.pyplot
    """
    
    if presKey is None:
        presKey = DPUtil.findKeys('Pressure', dfPump.keys())
        if len(presKey) > 1:
            presKey = DPUtil.findKeys('Treating', presKey)[0]
        else:
            presKey = presKey[0]
    if propconKey is None:
        propconKey = DPUtil.findKeys('Prop', dfPump.keys())[0]
        # if len(propconKey)>1:
        #    propconKey=sf.findKeys('Prop',propconKey)[0]
        # else:
        #    propconKey=propconKey[0]
    if flowKey is None:
        flowKey = DPUtil.findKeys('Rate', dfPump.keys())
        if len(flowKey) > 1:
            flowKey = DPUtil.findKeys('Clean', flowKey)[0]
        else:
            flowKey = flowKey[0]
    ax3 = ax.twinx()
    ax4 = ax.twinx()
    ax.plot(dfPump[timeKey].values, dfPump[propconKey].values, color='g', zorder=10)
    ax3.plot(dfPump[timeKey].values, dfPump[presKey].values, color='r', zorder=10)
    ax4.spines['right'].set_position(('outward', spacing))
    ax4.yaxis.tick_right()
    
    ax4.plot(dfPump[timeKey].values, dfPump[flowKey].values, color='b', zorder=10)
    
    ax4.set_ylabel(flowKey, color='b')
    ax4.yaxis.set_label_position('right')
    
    ax.set_ylabel(propconKey, color='g')
    ax.set_xlabel(timeKey)
    ax3.set_ylabel(presKey, color='r')
    
    if lims is not None:
        for a, l in zip([ax, ax3, ax4], lims):
            a.set_ylim(0, l)
    else:
        for a in [ax, ax3, ax4]:
            a.set_ylim(bottom=0)
    plt.gcf().subplots_adjust(right=rightadj)
    
    return ax3, ax4


def rotationQC(dfCluster, dfStage, svcfile, relStage=None, angle=0, dontRotate=False,
               figPath=None):
    """
    Plots the unrotated and rotated results for QC
    
    Inputs
    ======
    dfCluster : dataframe with clusters/events
    dfStage   : stages dataframe
    svcfile   : Seisvis file path
    relStage  : str, optional
        Stage with which the rotation is relative to. The last stage will be chosen by default
    angle     : int, optional
        rotation angle by default 0 (no rotation)
    dontRotate: boolean
        perform rotation if False (by default)
    figPath   : str, optional
        directory with which to save figures

        
    Outputs
    ============
    None, outputs data to ax by reference
    
    Dependencies
    ============
    numpy
    """
    
    if relStage is None:
        relStage = dfStage.index[-1]
    
    print("Rotation is relative to stage: "+relStage)
    
    fig, ax = plt.subplots(figsize=(5, 9))
    ax.scatter(dfCluster.Easting, dfCluster.Northing)
    plotWells(ax, dfStage, 'Easting', 'Northing', svcfile=svcfile, relStage=relStage)
    ax.axis('equal')
    if figPath is not None:
        fig.savefig(figPath + "RotationQC_DistEasting vs Northing.png", dpi=200)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(dfCluster.Northing, dfCluster.Depth)
    plotWells(ax, dfStage, 'Northing', 'Depth', svcfile=svcfile, relStage=relStage)
    ax.invert_yaxis()
    ax.axis('equal')
    if figPath is not None:
        fig.savefig(figPath + "RotationQC_DistNorthing vs Depth.png", dpi=200)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(dfCluster.Easting, dfCluster.Depth)
    plotWells(ax, dfStage, 'Easting', 'Depth', svcfile=svcfile, relStage=relStage)
    ax.invert_yaxis()
    ax.axis('equal')
    if figPath is not None:
        fig.savefig(figPath + "RotationQC_Easting vs Depth.png", dpi=200)

    dfCluster, dfStage = MathUtil.addRelativeCoordinates(dfCluster, dfStage, relStage, angle) 
    
    fig, ax = plt.subplots(figsize=(5, 9))
    ax.scatter(dfCluster['Distance Right Perpendicular To Well'], dfCluster['Distance Along Well'])
    plotWells(ax, dfStage, 'Distance Right Perpendicular To Well', 'Distance Along Well',
              svcfile=svcfile, angle=angle, relStage=relStage)
    ax.axis('equal')
    plotArrow(ax, angle)
    if figPath is not None:
        fig.savefig(figPath + "RotationQC_DistPerpendicular vs AlongWell.png", dpi=200)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(dfCluster['Distance Along Well'], dfCluster['Depth'])
    plotWells(ax, dfStage, 'Distance Along Well', 'Depth', svcfile=svcfile, angle=angle, relStage=relStage)
    ax.invert_yaxis()
    ax.axis('equal')
    if figPath is not None:
        fig.savefig(figPath + "RotationQC_DistAlongWell vs Depth.png", dpi=200)
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(dfCluster['Distance Right Perpendicular To Well'], dfCluster['Depth'])
    plotWells(ax, dfStage, 'Distance Right Perpendicular To Well', 'Depth', svcfile=svcfile,
              angle=angle, relStage=relStage)
    ax.invert_yaxis()
    ax.axis('equal')
    if figPath is not None:
        fig.savefig(figPath + "RotationQC_DistRight vs Depth.png", dpi=200)

    return
