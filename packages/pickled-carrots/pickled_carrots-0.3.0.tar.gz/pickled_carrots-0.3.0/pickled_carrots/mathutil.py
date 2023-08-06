# -*- coding: utf-8 -*-
"""
Created on Thu Jul 18 11:38:21 2019

@author: sara.brazille
"""

import math
import numpy as np
import pylab as py
import datetime as dt
import re
import os
import pickle
import pandas as pd
from . import DPUtil
from . import database
from scipy.spatial import Delaunay


def intersection(lst1, lst2):
    """
    Finding which values in lst1 are in lst2
    # TODO this should be replaced by a numpy equivalent
    :param lst1: first list of variables
    :param lst2: second list of variables
    :return:
    """
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3


def addRelativeCoordinates(dfCluster, dfStage, stage, angle=None, dontRotate=False, cartesian=False):
    
    df_cluster_out = dfCluster.copy(deep=True)
    df_stage_out = dfStage.copy(deep=True)
    
    if angle is None:
        angle = 0
        print('No angle provided, assuming 0')
        
    if dontRotate:
        angle = 0
        
    if not cartesian:
        angle = angle*(-1)
    
    origin = ((dfStage.loc[stage, 'E1'] + dfStage.loc[stage, 'E2'])/2, 
              (dfStage.loc[stage, 'N1'] + dfStage.loc[stage, 'N2'])/2)
    
    df_cluster_out['Distance Right Perpendicular To Well'], \
        df_cluster_out['Distance Along Well'] = \
        rotatecoordRemoveOrigin(dfCluster['Easting'], dfCluster['Northing'], angle, origin=origin)
    
    df_stage_out['Distance Right Perpendicular To Well1'], \
        df_stage_out['Distance Along Well1'] = \
        rotatecoordRemoveOrigin(dfStage['E1'], dfStage['N1'], angle, origin=origin)
    
    df_stage_out['Distance Right Perpendicular To Well2'], \
        df_stage_out['Distance Along Well2'] = \
        rotatecoordRemoveOrigin(dfStage['E2'], dfStage['N2'], angle, origin=origin)
    
    if dontRotate:
        print("As per setting skip rotation of relative coordinates.")
    return df_cluster_out, df_stage_out


def zptile(z_score):
    return .5 * (math.erf(z_score / 2 ** .5) + 1)


def sigmaToPercentOfSample(sigma):
    return zptile(sigma) - zptile(sigma * -1)


def rotatecoord(x, y, rot, origin=(0, 0), inrad=False):
    """
    Definition to convert x,y to rotated coordinates    
    """
    if inrad:
        th = rot
    else:
        th = rot*np.pi/180.  # rotate
        
    r = np.mat([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])  # rotation matrix
    h1, h2 = np.array(r*[x-origin[0], y-origin[1]])
    
    return h1+origin[0], h2+origin[1]


def rotatecoordRemoveOrigin(x, y, rot, origin=(0, 0), inrad=False):
    """
    Definition to convert x,y to rotated coordinates    
    """
    if inrad:
        th = rot
    else:
        th = rot*np.pi/180.  # rotate
        
    r = np.mat([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]])  # rotation matrix
    h1, h2 = np.array(r*[x-origin[0], y-origin[1]])
    
    return h1, h2


def calc_depth_offset(stgN, stgE, refN, refE, strike, dip):
    """
    Function to calculate the depth offset with 2d dipping layers
    :param stgN:
    :param stgE:
    :param refN:
    :param refE:
    :param strike:
    :param dip:
    :return:
    """
    dn = stgN - refN
    de = stgE - refE

    if strike+90 > 360:
        strike = strike-360.0

    # angle to stage (cartesian coordinates) also known also apparent dip direction
    ang_to_stg = np.rad2deg(np.arctan(dn / de))
    ang_to_stg_map = np.rad2deg(np.pi / 2 - np.deg2rad(ang_to_stg))
    beta = np.deg2rad(strike - ang_to_stg_map)
    # true dip in radians
    dip_rad = np.deg2rad(dip)
    # total dist: c
    dist = np.sqrt(dn**2 + de**2)
    # apparent dip angle
    alpha = np.arctan(np.sin(beta) * np.tan(dip_rad))
    # depth shift to move lithotop
    depth_shift = dist * alpha

    return depth_shift


def rotate_depth(e, n, z, rot, orig_e=0.0, orig_n=0.0):
    """
    Depth rotation offset - useful for depth histograms

    This module returns revised depth values based on a dip relative to the origin. Note that this is simplistic
    and does not take into account strike/dip relative to the well log. Choose an appropriate origin for the

    :param e: easting
    :param n: northing
    :param z: depth
    :param rot: depth rotation angle in degrees
    :param orig_e: origin easting
    :param orig_n: origin northing
    :return:
    """
    th = rot*np.pi/180.  # rotate
    dist = np.sqrt((orig_e-e)**2+(orig_n-n)**2)
    delta_z = dist*np.sin(th)

    return z+delta_z


def pickBestSOL(df_in, Cthresh=50, Rthresh=0.5):
    """
    # Resolve duplicates SMTI entries by choosing first GN sols with
    # CondNum<= Cthresh and Rthresh>=0.5
    # Otherwise DC solution is chosen
    # assumes input index is Date_Time
    # L. Smith
    """
    if not(isinstance(df_in, pd.DataFrame)):
        df = pd.DataFrame(df_in)
    else:
        df = df_in

    grp_df = df.groupby("TrgID")
    # newDF=pd.DataFrame(index=grpDF.groups.keys(),columns=df.keys())
    duplicates = grp_df.filter(lambda x: len(x) > 1).reset_index(inplace=False, drop=True)
    single_values = grp_df.filter(lambda x: len(x) == 1)
    tmp_df = single_values
    if single_values.shape[0] < df.shape[0]:
        grp_df = duplicates.groupby('TrgID')
   
        new_df = pd.DataFrame()
        for name, group in grp_df:
            if group.shape[0] > 1:
                sol_found = 0
                grp_sols = group.groupby('Sol')
                grp_keys = grp_sols.groups.keys()
                
                if 'GN' in grp_keys:
                    if sol_found == 0:
                        subgroup = grp_sols.get_group('GN')
                        good_sols = subgroup[(subgroup['CondNum'] <= Cthresh) & (group['Rsq'] >= Rthresh)]
                        if good_sols.shape[0] > 1:
                            new_df = new_df.append(good_sols.ix[(good_sols['CondNum'].argmin())])
                        elif good_sols.shape[0] == 1:
                            new_df = new_df.append(good_sols)
                                
                elif 'DC' in grp_keys:
                    if sol_found == 0:
                        subgroup = grp_sols.get_group('DC')
                        
                        good_sols = subgroup[(subgroup['CondNum'] <= Cthresh) & (group['Rsq'] >= Rthresh)]
                        if good_sols.shape[0] > 1:
                            new_df = new_df.append(good_sols.ix[(good_sols['CondNum'].argmin())])
                        elif subgroup.shape[0] > 1:
                            new_df = new_df.append(subgroup.ix[(subgroup['CondNum'].argmin())])
                        else:
                            new_df = new_df.append(subgroup)
                        
            else:
                new_df = new_df.append(group)
        if new_df.shape[0] > 0:
            new_df['TrgID'] = new_df['TrgID'].apply(int)
            new_df['Date_Time'] = pd.to_datetime(new_df['Date_Time'])
            new_df['Date_Time'] = [new_df['Date_Time'].ix[i].replace(
                microsecond=int(str(int(new_df['TrgID'].ix[i]))[-3:])*1000) for i in new_df.index]
            new_df.set_index(new_df['Date_Time'], inplace=True, drop=False)
                     
        out_df = tmp_df.append(new_df)
        out_df = out_df.sort(ascending=True)
    else:
        out_df = df_in
    return out_df


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    """
    axis = np.asarray(axis)
    theta = np.asarray(theta)
    axis = axis/np.math.sqrt(np.dot(axis, axis))
    a = np.math.cos(theta/2.)
    b, c, d = -axis*np.math.sin(theta/2.)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])


def unit_vector(trend, plunge):
    """
    return unit vector from trend and plunge
        coordinate system NED
    """
    d2r = np.pi/180.
    tr, pl = d2r*trend, d2r*plunge
    v = np.array([np.cos(tr)*np.cos(pl), np.sin(tr)*np.cos(pl), np.sin(pl)])
    return v


def normal_vector(strike, dip):
    """
    return unit normal vector for a plane specified by strike and dip
    coordinate system NED.  Normal vector is up and outward from the footwall
    """
    d2r = np.pi/180.
    st, dp = d2r*strike, d2r*dip
    v = np.array([-np.sin(dp)*np.sin(st), np.sin(dp)*np.cos(st), -np.cos(dp)])
    return v


def slip_vector(strike, dip, rake):
    """
    return unit normal vector for a plane specified by strike and dip
    coordinate system NED.  rake is assumed to measured ccw from strike
    """
    d2r = np.pi/180.
    sr, dr, rr = d2r*np.array([strike, dip, rake])
    slip = np.array([np.cos(rr)*np.cos(sr) + np.cos(dr)*np.sin(rr)*np.sin(sr),
                    np.cos(rr)*np.sin(sr) - np.cos(dr)*np.sin(rr)*np.cos(sr),
                    -np.sin(rr)*np.sin(dr)])
    return slip


def trend_plunge(vectors):
    """
    return trend and plunge values in degrees for a vector
       coordinate system NED
    """
    r2d = 180./np.pi
    tr = None
    pl = None
    if vectors.ndim == 1:
        if vectors[2] < 0:
            vectors = -vectors
        tr = np.arctan2(vectors[1], vectors[0])*r2d
        pl = np.arctan(vectors[2]/py.norm([vectors[0], vectors[1]]))*r2d
        if tr < 0:
            tr += 360.
    elif vectors.ndim == 2:
        dum, nev = vectors.shape
        tr, pl = np.zeros(nev), np.zeros(nev)
        for iev in range(nev):
            vector = vectors[:, iev]
            if vector[2] < 0:
                vector = -vector
            tr[iev] = np.arctan2(vector[1], vector[0])*r2d
            pl[iev] = np.arctan(vector[2]/py.norm([vector[0], vector[1]]))*r2d
            if tr[iev] < 0:
                tr[iev] += 360.
    return tr, pl


def strike_dip(normals):
    """
    return plane in strike dip in degrees for a normal vector.
        coordinate system NED
    """
    r2d = 180./np.pi
    st = None
    dp = None
    if normals.ndim == 1:
        normal = normals
        if normal[2] > 0:
            normal = -normal
        st = np.arctan2(normal[1], normal[0])*r2d - 90.
        dp = -np.arctan(py.norm([normal[0], normal[1]])/normal[2])*r2d
        if st < 0.:
            st += 360.
    elif normals.ndim == 2:
        dum, nev = normals.shape
        st, dp = np.zeros(nev), np.zeros(nev)
        for iev in range(nev):
            normal = normals[:, iev]
            if normal[2] > 0:
                normal = -normal
            st[iev] = np.arctan2(normal[1], normal[0])*r2d - 90.
            dp[iev] = -np.arctan(py.norm([normal[0], normal[1]])/normal[2])*r2d
            if st[iev] < 0.:
                st[iev] += 360.

    return st, dp


def vect_to_trendplunge(v, deg=True):
    """
    Output in degrees by default, input must be a 3-D unit vector
    """
    pl = np.arcsin(v[2])
    if v[1] == 0:
        tr = 0
        if v[0] < 0:
            tr += np.pi
    else:
        tr = np.arctan(v[1] / v[0])
        if np.sign(v[0]) == -1:
            tr += np.pi
        if tr < 0:
            tr += 2 * np.pi

    if pl < 0:
        pl = np.abs(pl)
        tr += np.pi
    if tr > 2 * np.pi:
        tr -= 2 * np.pi

    if deg:
        return np.array((tr, pl)) * 180 / np.pi
    else:
        return np.array((tr, pl))


def finddensestpoint(strike, dip):
    """
    Find densest point on a stereonet grid
    :param strike:
    :param dip:
    :return:
    """
    import mplstereonet as mpl

    for i in range(len(strike)):
        if strike[i] > 360:
            strike[i] = strike[i] - 360

    # Estimate the point density on a regular grid.
    lon, lat, density = mpl.density_grid(strike, dip)

    # Find index of "densest" point
    i, j = np.unravel_index(density.argmax(), density.shape)

    # find strike/dip of the plane
    try:
        pstrike, pdip = mpl.geographic2pole(lon[i, j], lat[i, j])
    except IndexError:
        pstrike, pdip = mpl.geographic2pole(lon[j], lat[i])

    return pstrike, pdip


def ms2rgb(colorref, norm=True):
    """
        Helper function to convert microsoft colors to RBG values

        norm: default True normalize rgb values between 0 and 1

    """
    r = ((colorref >> 0) & 0xFF)
    g = ((colorref >> 8) & 0xFF)
    b = (colorref >> 16)

    if norm:
        r /= 255.0
        g /= 255.0
        b /= 255.0

    return tuple([r, g, b])


def alphanumericsort(l):
    """
    Sort the given iterable in the way that humans expect.
    """
    import re
    convert = lambda text: int(text) if text.isdigit() else text 
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def trgid2dt(trgid):
    """
    Convert a TrgID into a datetime 
    """
    # import datetime as dt
    if not isinstance(trgid, str):
        trgid = str(trgid)
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


def dt2trgid(dtm):
    """
    Converts a datetime to a TrgID
    """
    year = dtm.year
    month = dtm.month
    day = dtm.day
    hour = dtm.hour
    minute = dtm.minute
    sec = dtm.second
    mst = int(dtm.microsecond/1000)
    cbm = [year, month, day, hour, minute, sec, mst]
    deslen = [4, 2, 2, 2, 2, 2, 3]
    trgid = ''
    for k in range(7):
        if (deslen[k]-len(str(cbm[k]))) == 1:
            trgid = trgid+'0'+str(cbm[k])
        elif (deslen[k]-len(str(cbm[k]))) == 2:
            trgid = trgid+'00'+str(cbm[k])
        else:
            trgid = trgid+str(cbm[k])
    
    return trgid  


def dt2trgidint(dtm):
    """
    Converts datetime to a TrgID
    """
    return int(dt2trgid(dtm))


def serialtime2dt(st):
    """
    Converts esg serial time to datetime
    """
    st = float(st)
    st_dt = pd.to_datetime('1900-1-2') + pd.to_timedelta(st, 'D') + pd.to_timedelta(0.5, 'ms')
    return st_dt


def trgid2serialtime(trgid):
    """
    Convert TrgID to Serial Time
    :param trgid:
    :return:
    """
    x = trgid2dt(trgid) - pd.to_datetime('1900-1-1')
    st = x.total_seconds() / 60 / 60 / 24
    return st


def trgid2hsf(dsn, trgid):
    """
    Convert a DateTime into a hsf filename
    """
    if not isinstance(trgid, str):
        raise Exception("TrgID must be passed as a string to prevent rounding issues")

    filename = dsn+str(trgid)[2:]+'.hsf'
    return filename


def trgid2hsfpath(dsn, trgid, rootpath='\\\\esg_utils.net\\datashare\\frac'):
    """
    Convert a DateTime into a full hsf path
    """
    if not isinstance(trgid, str):
        raise Exception("TrgID must be passed as a string to prevent rounding issues")

    if rootpath[-1] not in ['\\', '/']:
        rootpath += '\\'
    yr, mn, day = trgid[0:4], trgid[4:6], trgid[6:8]
    filepath = rootpath + dsn + '\\' + yr + '\\' + mn + '\\' + day + '\\' + trgid2hsf(dsn, trgid)
    return filepath


def hsfpath2trgid(filepath):
    """
    Convert an hsf path to trgid
    """
    filename = filepath.replace(r"\\", "/").split('/')[-1]
    filename = filename.split(".hsf")[0]

    values = None
    for i in re.findall(r'\d+', filename):
        if len(i) > 5:
            values = i

    if values is not None:
        year = "20" + values[0:2]
        month = values[2:4]
        day = values[4:6]
        hour = values[6:8]
        minute = values[8:10]
        sec = values[10:12]
        mst = values[12:16]
        cbm = [year, month, day, hour, minute, sec, mst]
        deslen = [4, 2, 2, 2, 2, 2, 3]
        trgid = ''
        for k in range(7):
            if (deslen[k] - len(str(cbm[k]))) == 1:
                trgid = trgid + '0' + str(cbm[k])
            elif (deslen[k] - len(str(cbm[k]))) == 2:
                trgid = trgid + '00' + str(cbm[k])
            else:
                trgid = trgid + str(cbm[k])
    else:
        raise Exception("Could not parse hsfpath into a trgid.")

    return trgid


def rotate_triax(data, senrt):
    """
    Take in 3-channel data for 1 sensor and rotation matrix (orientation cosines, 3x3 array/matrix)
    Output rotated 3-channel data
    
    data.shape = (channels, points)
    
    Example Usage
    =============
    (Using `data` and `header` from readhsf())
    trace = data[i*3:(i+1)*3,:]
    rt = header['sen_rot'][i]
    art = header['eig_rot'][i].T
    mot_trc = rotate_triax(rotate_triax(trace,rt),art)
    """
    rot = np.mat(senrt)
    rd = np.array(rot.T*np.mat(data))
    return rd


def normed(x):
    """
    Normalising x by the square root of the sum of squares
    :param x: the variable to be normalised
    :return:
    """
    x = np.array(x)
    mx = np.sqrt(sum(x*x))
    return x/mx    


def rotray(pdir):
    """
    Rotate ray in p-dir
    """
    
    pvec = normed(pdir)
    hvec = normed(np.array([pvec[1], -pvec[0], 0.0]))
    vvec = -np.cross(pvec, hvec)
    if vvec[2] < 0:
        rt = np.mat([pvec, vvec, hvec])
    else:
        rt = np.mat([pvec, -vvec, -hvec])
    # TODO what is the point of this if statement if you force overwrite it?
    rt = np.mat([pvec, -vvec, -hvec])
    return rt


def rotate_raydir(data, raydir, senrt):
    """
       Rotation of traces to ray direction of the p-wave    
       
       MathUtil.rotate_raydir(data,head['raydir'],head['sen])
       
       Returns: rotate triaxial waveform data
    """
    rot_traces = []
    
    # if a single sensor rather than entire evt
    if len(data) == 3 and isinstance(raydir, tuple):
        raydir = [raydir]
        senrt = [senrt]
        returnsingle = True
    else:
        returnsingle = False
    
    for sen in range(0, len(raydir)):
        fch = sen*3
        lch = (sen*3)+2
    
        traces = data[fch:lch+1, :]
        rt = senrt[sen]
        pdir = raydir[sen]
        
        rot_traces.append(np.array(rotray(pdir)*rt.T*np.mat(traces)))
    
    if returnsingle:
        return rot_traces[0]        
    else:
        return rot_traces


def sta_lta_mask(x, sta_w=100, lta_w=500):
    """
    Simplistic classic STA LTA function
    """
    
    sta_lta_arr = []

    for i in range(0, len(x)):
        if i + sta_w < len(x):
            sta = np.average([abs(k) for k in x[i:i+sta_w]])
        else:
            sta = 0
        if i - lta_w > 0:
            lta = np.average([abs(k) for k in x[i-lta_w:i]])
        else:
            lta = 100
        sta_lta = sta/lta
        sta_lta_arr.append(sta_lta)

    return np.array(sta_lta_arr)


def energy_ratio(x, l=100):
    """
    Modified Energy Ratio method (MER)
        
    As defined: Automatic time-picking of first arrivals on large seismic datasets (Joe Wong)
                https://crewes.org/ForOurSponsors/ResearchReports/2014/CRR201476.pdf
    
    """
    mer_arr = []
    
    for i in range(0, len(x)):
        if (i + l < len(x)) and (i - 6*l > 0):
            er_a = np.power(np.sum([np.abs(k) for k in x[i:i+l]]), 2)
            er_b = np.power(np.sum([np.abs(k) for k in x[i-l:i]]), 2)
            er = er_a / er_b
            mer = np.power(np.abs(x[i]) * er, 3)
        else:
            mer = 0
        
        mer_arr.append(mer)                        
    
    return np.array(mer_arr)


def scientific_notation_fmt(x, pos):
    """
    Putting number into scientific notation (with 10 exponential)
    :param x: the number
    :param pos: not sure
    :return:
    """
    a, b = '{:.2e}'.format(x).split('e')
    b = int(b)
    return r'${} \times 10^{{{}}}$'.format(a, b)


def calc_residual(df_picks):
    """

    :param df_picks:
    :return:
    """
    for wave in ['P', 'Sv', 'Sh']:
        df_picks[wave + 'res'] = df_picks[wave + 'TTT'] - df_picks[wave + 'Arr']

    return df_picks


def applyDFFilter(inputdf, filterDict):
    """
    Filter the data in `inputdf` using the keys and ranges described in `filterDict`

    e.g. inputdf=pcaDfSpace
        filterDict={}
        filterDict['Depth']=[900,5000]

        filterDict['Easting']=[1900,4000]

    This example returns a dataframe that is limited to Depth values >900 and Depth values<=5000 and Easting>1900 and
    Easting<=4000

    Another example, is to send pass a "mining block"

    filterDict can have many keys
    """
    filter_gen = lambda u, key_val, key_range: (u[key_val] > key_range[0]) & (u[key_val] <= key_range[1])

    filtout = None
    for key in filterDict:
        filterpca = filter_gen(inputdf, key, filterDict[key])

        if filtout is None:
            filtout = filterpca
        else:
            filtout = filtout & filterpca

    return inputdf[filtout]


def filterEventsByBlock(df, sql, blockname, blocktype=None):
    """
    This function is used to decide which type of block filtering is required.
    :param df:
    :param sql:
    :param blockname:
    :param blocktype:
    :return:
    """
    block = Database.readsqlblocks(sql, sqlstr='MGS\\MGS')

    blocktofilter = block[block['Block ID'] == blockname]

    if blocktype is not None:
        blocktofilter = blocktofilter[blocktofilter['BlockType'] == blocktype]
    if len(blocktofilter) == 0:
        raise Exception("Block to filter was not found.")
    elif len(blocktofilter) > 1:
        raise Exception("Multiple blocks with this name are found.")

    blockrow = blocktofilter.iloc[0]
    blocktype = blockrow['BlockType']

    if blocktype == "Mine Blocks":
        df_filtered = filterEventsByBlockAligned(df, sql, blockname)
    elif blocktype == "RotatedBlocks":
        df_filtered = filterEventsByBlockRotated(df, sql, blockname)
    elif blocktype == "VolumeBlocks":
        df_filtered = filterEventsByBlockPolygon(df, sql, blockname)
    else:
        raise Exception("The block type "+blocktype+" is not yet in the code.")

    return df_filtered


def filterEventsByBlockAligned(df, sql, blockname='SMTI_VOL'):
    """
    This function is used to filter events based on a regular aligned block (without rotation)
    :param df:
    :param sql:
    :param blockname:
    :return:
    """
    block = Database.readsqlblocks(sql, sqlstr='MGS\\MGS')
    desblock = block[block['Block ID'].isin(DPUtil.findKeys(blockname, block['Block ID'].values))]

    filterdict = dict()
    filterdict['Depth'] = desblock[['Dmin', 'Dmax']].values[0]
    filterdict['Easting'] = desblock[['Emin', 'Emax']].values[0]
    filterdict['Northing'] = desblock[['Nmin', 'Nmax']].values[0]

    outputdata = applyDFFilter(df, filterdict)

    return outputdata


def filterEventsByBlockRotated(df, sql, blockname='SMTI_VOL', elev=True):
    """
    This function is used to filter events based on a regular aligned block (with rotation)
    :param df:
    :param sql:
    :param blockname:
    :param elev:
    :return:
    """
    block = Database.readsqlblocks(sql, sqlstr='MGS\\MGS')
    desblock = block[block['Block ID'].isin(DPUtil.findKeys(blockname, block['Block ID'].values))]

    strike = desblock.iloc[0].Strike  # azim from N
    dip = desblock.iloc[0].Dip

    if dip != 0.0:
        raise Exception("The block dip is not zero. "
                        "3D rotation has not been implemented in the python code. Block dip: " + str(dip))

    orn, ore, ordd = desblock.iloc[0].OrN, desblock.iloc[0].OrE, desblock.iloc[0].OrD
    lenn, lene, lend = desblock.iloc[0].LenN, desblock.iloc[0].LenE, desblock.iloc[0].LenD

    strike *= -1
    angle = strike * math.pi/180

    # 2d rotation without dip
    evts_x_rot, evts_y_rot = rotatecoord(df.Easting, df.Northing, -strike, origin=(ore, orn), inrad=False)
    df['Rot_E'] = evts_x_rot
    df['Rot_N'] = evts_y_rot

    # rotate corners of rectangle to be in placement as per seisvis rotated block
    x_coords = np.array([ore, ore+lene, ore+lene, ore, ore])
    y_coords = np.array([orn, orn, orn + lenn, orn + lenn, orn])
    # TODO any point to running this calculation? The values aren't used
    x_rot, y_rot = rotatecoord(x_coords, y_coords, strike, origin=(ore, orn), inrad=False)

    filterdict = dict()
    filterdict['Rot_E'] = np.array([x_coords[0], x_coords[1]])
    filterdict['Rot_N'] = np.array([y_coords[0], y_coords[2]])

    if elev:
        filterdict['Depth'] = np.array([ordd, ordd + lend])
    else:
        filterdict['Depth'] = np.array([ordd + lend, ordd])

    outputdata = applyDFFilter(df, filterdict)

    return outputdata


def filterEventsByBlockPolygon(df, sql, blockname='SMTI_VOL', elev=True):
    """
    Return dataframe of events within the polygon block
    :param df:
    :param sql:
    :param blockname:
    :param elev:
    :return:
    """
    block = Database.readsqlblocks(sql, sqlstr='MGS\\MGS')
    desblock = block[block['Block ID'].isin(DPUtil.findKeys(blockname, block['Block ID'].values))]
    blockrow = desblock.iloc[0]
    blockdata_list = blockrow.BlockData.split(",")

    # build depth filter
    zmin = float(blockdata_list[0])
    zmax = float(blockdata_list[1])

    filterdict = dict()
    if elev:
        filterdict['Depth'] = np.array([zmin, zmax])
    else:
        filterdict['Depth'] = np.array([zmax, zmin])

    # apply depth filter
    outputdata = applyDFFilter(df, filterdict)

    # remove depth filter
    blockdata = np.array(blockdata_list[2:])
    # re-arrange polygon points
    blockdata = blockdata.reshape(int(len(blockdata) / 2), 2)
    blockdata = blockdata.astype(float)

    y_coords = blockdata[:, 0]
    x_coords = blockdata[:, 1]

    # add first point in to close the polygon
    y_coords = np.append(y_coords, y_coords[0])
    x_coords = np.append(x_coords, x_coords[0])
    pts = np.transpose([x_coords, y_coords])
    outputdata2 = pnt_in_polygon(pts, outputdata.copy())

    return outputdata2


def pnt_in_cvex_hull_1(hull, pnt):
    """
    Checks if `pnt` is inside the convex hull.
    `hull` -- a QHull ConvexHull object
    `pnt` -- point array of shape (3,)
    :param hull:
    :param pnt:
    :return: boolean
    """
    from scipy.spatial import ConvexHull

    # add point to test to the hull vertices
    hullpts_withtestpnt = np.concatenate((hull.points, [pnt]))

    # build hull with pnt to test
    new_hull = ConvexHull(hullpts_withtestpnt)

    # if the hull vertices are the same, then the point is within the hull
    if np.array_equal(new_hull.vertices, hull.vertices):
        return True
    else:
        return False


def pnt_in_polygon(hull_vertices, dframe, filterdf=True, hull_3d=False):
    """
    Checks if a series of points provided in a dataframe are present in a given polygon. Polygon can be defined in
    2D or 3D coordinates
    https://stackoverflow.com/questions/16750618/
    whats-an-efficient-way-to-find-if-a-point-lies-in-the-convex-hull-of-a-point-cl
    :param hull_vertices: polygon vertices from the db or csv file
    :param dframe: dataframe to filter
    :param filterdf: return only the events within the polygon
    :param hull_3d: if True then the hull is 3D
    :return: dframe with new InVol column
    """

    # checking whether the hull is 3d or not
    if hull_3d is False:
        if 'Easting' not in dframe.columns:
            colnames = ['X', 'Y']
        else:
            colnames = ['Easting', 'Northing']
    else:
        if 'Easting' not in dframe.columns:
            colnames = ['X', 'Y', 'Z']
        else:
            colnames = ['Easting', 'Northing', 'Depth']

    # building the hull from the vertices
    hulldel = Delaunay(hull_vertices)

    # pulling out the data
    test_points = dframe[colnames].values

    # testing if the point is within the hull
    res = hulldel.find_simplex(test_points) >= 0

    # converting to integers
    in_hull_1 = res.astype(int)

    # and saving to the data frame
    dframe.loc[:, 'InVol'] = in_hull_1

    if filterdf:
        dframe = dframe[dframe.InVol == 1]

    return dframe


def set_proc_name(newname):
    """
    Setting process name for showing in top
    :param newname: the new name to assign to the process
    :return:
    """
    from ctypes import cdll, byref, create_string_buffer

    # cancelling setting proc name if on windows
    if os.name == 'nt':
        return

    # turning new name into bytes
    newname = newname.encode()

    # initializing the library and bugger to set the process name
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(len(newname)+1)

    # setting the process name to be shown in top
    buff.value = newname
    libc.prctl(15, byref(buff), 0, 0, 0)


def get_proc_name():
    """
    Getting the process name that would be displayed in top
    :return:
    """
    from ctypes import cdll, byref, create_string_buffer

    # cancelling getting name if on windows
    if os.name == 'nt':
        return None

    # initializing the library and buffer to load the process name
    libc = cdll.LoadLibrary('libc.so.6')
    buff = create_string_buffer(128)
    # 16 == PR_GET_NAME from <linux/prctl.h>
    # loading the process name
    libc.prctl(16, byref(buff), 0, 0, 0)
    return buff.value


def check_version_value(notebook_name, version_str):
    """
    Comparing
    :param notebook_name: name of the notebook to check the version of
    :param version_str: the string of the version that has been assigned to the notebook
    :return:
    """
    # dictionary of notebooks with corresponding versions
    notebook_dict = {
        'rubiales': '1.4',
        'castilla': '1.3',
        'chichimene': '1.3',
        'apiay': '1.3',
        'frontera': '1',
        'canosur': '1.3',
        'check_mgs_sensors': '1',
        'noise_analysis_automation': '1.1',
        'frontera_daily': '1.4',
        'frontera_weekly': '1.2',
        'download_s6': '1.1',
        'check_response': '1.1'
        }

    # raising error if notebook name not included
    if notebook_name not in list(notebook_dict.keys()):
        raise ValueError('Notebook name is not recognised. Your options are: ' + str(list(notebook_dict.keys())))

    # checking if the provided version matches with the current version
    if version_str != notebook_dict[notebook_name]:
        raise ValueError('This version of the notebook is out of date! Please upload and use the new version')
    else:
        print('Notebook is up to date!')


def setup_logging(log_folder, log_file_name, backupcount=10, maxbytes=102401000, debug=False):
    """
    Setting up logging for a process
    :param log_folder: where to save the logs
    :param log_file_name: the file name to save the log under
    :param backupcount: sets the number of back up log files to keep, defaults to 10
    :param maxbytes: Maximum size of the log file, defaults to 102401000
    :param debug: if True, then include DEBUG messages on log
    :return:
    """
    import logging
    from logging.handlers import RotatingFileHandler
    import time

    # making sure end_str has .log in it
    if log_file_name[-4:] != '.log':
        log_file_name += '.log'

    # setting up the logging
    # https://stackoverflow.com/a/28333560
    log_handler = RotatingFileHandler(filename=os.path.join(log_folder, log_file_name),
                                      mode='a', maxBytes=maxbytes, backupCount=backupcount, delay=False)

    # setting up the format for the logging messages
    formatter = logging.Formatter(
        '%(asctime)s %(message)s')
    formatter.converter = time.gmtime  # if you want UTC time
    log_handler.setFormatter(formatter)

    # setting up the logging
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)


def is_picklable(obj):
    """
    Utility function to test if an object is picklable
    This is crucial for multiprocessing because every object must be picklable to be passed into the processes
    :param obj: object to be tested to see if it is picklable
    """
    try:
        pickle.dumps(obj)
    except pickle.PicklingError:
        return False
    return True


def will_multiprocessing_work(obj_list):
    """
    Utility function to test if a list of objects are picklable
    :param obj_list: List of objects which will be tested.
    :return: raises Value Error if one of the objects is not picklable
    """
    for obj in obj_list:
        picklable = is_picklable(obj)

        if picklable is False:
            print(obj)
            raise ValueError('Object is not picklable, multiprocessing will silently crash and stop working!')
