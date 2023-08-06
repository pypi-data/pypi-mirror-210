# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 15:56:01 2019

@author: sara.brazille
"""
import numpy as np
import pandas as pd
from .DPData import SMT2kt
from .mathutil import trend_plunge, finddensestpoint, rotatecoord, normal_vector
from . import database
import mplstereonet
import matplotlib.pyplot as plt
from scipy import signal


def source_type_kde_old(ax, k, t):
    """
    produce source-type plot contoured by event density
    """
    from scipy import stats
    from matplotlib import patches
    # ax2 = axes([0.57,0.3,0.43,0.3225],frameon=False,xticks=[],yticks=[])
    # ax2 = subplot(241,frameon=False,xticks=[],yticks=[])
    # ax2=subplot2grid((3,4),(0,0),rowspan=2,colspan=2,frameon=False,xticks=[],yticks=[])
    u, v = [], []
    for ki, ti in np.array([k, t]).T:
        tau = ti*(1.-abs(ki))
        if ((ki < 0.) & (tau > 0.)) or ((ki > 0.) & (tau < 0.)):
            u.append(tau)
            v.append(ki)
        elif (ki > 0.) & (tau > 0.):
            if tau < 4*ki:
                u.append(tau/(1.-tau/2.))
                v.append(ki/(1.-tau/2.))
            else:
                u.append(tau/(1.-2.*ki))
                v.append(ki/(1.-2.*ki))
        else:
            if tau > 4*ki:
                u.append(tau/(1.+tau/2.))
                v.append(ki/(1.+tau/2.))
            else:
                u.append(tau/(1.+2.*ki))
                v.append(ki/(1.+2.*ki))
    values = np.c_[u, v]
    if len(u) >= 3:
        kernel = stats.kde.gaussian_kde(values.T)
        xval, yval = np.mgrid[-4./3.:4./3.:100j, -1.:1.:100j]
        positions = np.c_[xval.ravel(), yval.ravel()]
        zval = np.reshape(kernel(positions.T).T, xval.T.shape)
        im = ax.imshow(np.rot90(zval), extent=[-4./3., 4./3., -1., 1.])
    else:
        im = ax.imshow(np.zeros([100, 100]), extent=[-4./3., 4./3., -1., 1.])
    diamond = np.array([[0., 1.], [4./3., 1./3.], [0., -1.], [-4./3., -1./3.], [0., 1.]])
    patch = patches.Polygon(diamond, closed=True, transform=ax.transData)
    im.set_clip_path(patch)
    # for ii in range(2,10,2):
    # yi = float(ii)/30.
    # xi = yi*4.
    # plot([0,xi,0,-xi,0],[1,yi,-1,-yi,1],'0.75')
    # for ii in range(2,10,2):
    # tau = 1. - float(ii)/10
    # yr = float(ii)/10./(1. - tau/2.)
    # xr = tau/(1. - tau/2.)
    # yl = float(ii)/10.
    # xl = -1.+float(ii)/10
    # plot([xl,0,xr],[yl,yl,yr],'0.75')
    # plot([-xr,0,-xl],[-yr,-yl,-yl],'0.75')
    ax.plot([0., 0.], [-1., 1.], 'w', lw=1)
    ax.plot([-1., 1.], [0., 0.], 'w', lw=1)
    ax.plot([-4./3., 4./3.], [-1./3., 1./3], 'w', lw=1)
    frame_x = [0., 4./3., 0, -4./3., 0.]
    frame_y = [1., 1./3., -1., -1./3., 1.]
    ax.plot(frame_x, frame_y, 'k', lw=1)
    ax.axis('off')
    # text(0,1.03,'Explosive', ha='center', fontsize=fs2)
    # text(0,-1.03,'Implosive',ha='center',va='top',fontsize=fs2)
    # text(1.00,0,'$-$CLVD',                  ha='left', va='center',fontsize=fs2)
    # text(-1.03,0,'+CLVD',                   ha='right',va='center',fontsize=fs2)
    # text(0.68,-1./3.,'$-$Linear Dipole',    ha='left',             fontsize=fs2)
    # text(0.5,-5./9.,'Tensile Crack Close', ha='left',             fontsize=fs2)
    # text(-0.68,1./3.,'+Linear Dipole',       ha='right',            fontsize=fs2)
    # text(-0.47,5./9.,'Tensile Crack Opening',ha='right',            fontsize=fs2)
    # text(0,0,'DC',ha='center',va='center',fontsize=fs2,bbox=dict(facecolor='w',edgecolor='w'))
    ax.set_title('Source Mechanism')


def plotfp_old(ax, strike, dip):
    """
    Plot fracture planes on a stereonet
    """
    if len(strike) > 0 and len(dip) > 0:
        strike = strike[~np.isnan(strike)]
        dip = dip[~np.isnan(dip)]
    # ax = subplot(243,projection='stereonet')
    cax = ax.density_contourf(strike, dip, measurement='poles')
    cax.fontsize = 0
    ax.axis('off')
    # ax.grid()
    if len(strike) < 3:
        cax.set_clim([1e7, 1e8])
    ax.set_title('Fracture Plane Orientation', pad=40)
    if len(strike) >= 3:
        p_str, p_dip = finddensestpoint(strike, dip)
        ax.plane(p_str, p_dip, 'white', linewidth=2)


def plot_sensors(data_to_plot, head, detrend=False, showpicks=False, cleanplot=True):
    """
    Plot Waveforms Function
    
    data_to_plot: data array
    head: header
    detrend: remove the zero offset from waveform
    showpicks: show the theoretical and actual arrival picks
    cleanplot: hide borders around plot
    """
    if data_to_plot is None:
        raise Exception("No data to plot")

    sensornames = pd.Series(head['ch_descr'][::3])

    # noinspection PyTypeChecker
    fig, axs = plt.subplots(figsize=(16, 8), nrows=len(sensornames), ncols=1, sharex=True)

    for sen in range(0, len(sensornames)):
        # get sensor name
        sensorname = sensornames.iloc[sen]

        ch1 = data_to_plot[sen * 3, :]
        ch2 = data_to_plot[sen * 3 + 1, :]
        ch3 = data_to_plot[sen * 3 + 2, :]

        if detrend:
            ch1 = signal.detrend(ch1)
            ch2 = signal.detrend(ch2)
            ch3 = signal.detrend(ch3)

        if len(sensornames) == 1:  # if a single sensor, then axs will not be a tuple of axes but a single ax
            ax_currentsen = axs
        else:
            ax_currentsen = axs[sen]

        # plot signal
        ax_currentsen.plot(ch1, 'r')
        ax_currentsen.plot(ch2, 'g')
        ax_currentsen.plot(ch3, 'b')

        if cleanplot:
            ax_currentsen.axis('off')
        ax_currentsen.set_title(sensorname, loc="left", fontdict={'verticalalignment': 'top'})

        if showpicks:
            ax_yscaling = ax_currentsen.get_ylim()
            pttt = head['ttt'][sen][0]
            sttt = head['ttt'][sen][1]
            parr = head['parr'][sen][0]
            sarr = head['sarr'][sen][0]
            harr = head['harr'][sen][0]
            varr = head['varr'][sen][0]

            # Plot theoretical arrivals
            ax_currentsen.plot([pttt * head['fs'], pttt * head['fs']], [ax_yscaling[0], ax_yscaling[1]], 'red')
            ax_currentsen.plot([sttt * head['fs'], sttt * head['fs']], [ax_yscaling[0], ax_yscaling[1]], 'red')
            # Plot picked arrivals
            ax_currentsen.plot([parr * head['fs'], parr * head['fs']], [ax_yscaling[0], ax_yscaling[1]], 'black')
            ax_currentsen.plot([sarr * head['fs'], sarr * head['fs']], [ax_yscaling[0], ax_yscaling[1]], 'black')
            ax_currentsen.plot([harr * head['fs'], harr * head['fs']], [ax_yscaling[0], ax_yscaling[1]], 'black')
            ax_currentsen.plot([varr * head['fs'], varr * head['fs']], [ax_yscaling[0], ax_yscaling[1]], 'black')

    return fig, axs


def plotstrain(smtdb, dots=True, density=False, numberdots=True, ms=3,
               malpha=1, fnum=None, color="blue", fs=8):
    """
    Plot P,T axes
    :param smtdb:
    :param dots: show strain trend/plunge as a dot
    :param density: show heatmap of strain
    :param numberdots: for a small sample size, number the order of dots
    :param ms: marker size for dots
    :param malpha: marker alpha for dots
    :param fnum:
    :param color:
    :param fs:
    :return:
    """

    ppl = np.array(smtdb['Pdip'])
    ptr = np.array(smtdb['Paz'])
    tpl = np.array(smtdb['Tdip'])
    ttr = np.array(smtdb['Taz'])

    fig = plt.figure(fnum, facecolor='w', figsize=(9, 5), dpi=100)
    ax1 = fig.add_subplot(121, projection='stereonet')

    if density:
        _ = ax1.density_contourf(ppl, ptr, measurement='lines', zorder=1, alpha=0.3)

    if dots:
        if numberdots:
            num = 1
            lons, lats = mplstereonet.line(ppl, ptr)
            for x, y, c, a, b in zip(ppl, ptr, color, lons, lats):
                ax1.line(x, y, 'ko', markersize=ms, zorder=2, alpha=malpha, color=c)
                ax1.annotate("#"+str(num),
                             xy=(a, b),
                             fontsize=fs)
                num = num+1
        else:
            ax1.line(ppl, ptr, 'ko', markersize=ms, zorder=2, alpha=malpha, color=color)
    ax1.set_title('P-axis\n')
    ax1.grid(True)
    ax3 = fig.add_subplot(122, projection='stereonet')

    if density:
        _ = ax3.density_contourf(tpl, ttr, measurement='lines', zorder=1, alpha=0.3)
    if dots:
        if numberdots:
            lons, lats = mplstereonet.line(tpl, ttr)
            num = 1
            for x, y, c, a, b in zip(tpl, ttr, color, lons, lats):
                ax3.line(x, y, 'ko', markersize=ms, zorder=2, alpha=malpha, color=c)
                ax3.annotate("#"+str(num),
                             xy=(a, b),
                             fontsize=fs)
                num = num+1
        else:
            ax3.line(tpl, ttr, 'ko', markersize=ms, zorder=2, alpha=malpha, color=color)
    ax3.set_title('T-axis\n')
    ax3.grid(True)
    fig.subplots_adjust(left=0.05, hspace=0.3, top=0.9)

    return fig


def rotate_to_perf(df1, dfs):
    """
    Plot of perfs in rotated domain
    Legacy module - not sure if used
    :param df1:
    :param dfs:
    :return:
    """
    # print([val-dfs['E_mid'] for val in df1['Easting']])
    df1['Eperf'] = [val - float(dfs['E_mid'].values) for val in df1['Easting']]
    df1['Nperf'] = [val - float(dfs['N_mid'].values) for val in df1['Northing']]
    df1['Zperf'] = [val - float(dfs['Z_mid'].values) for val in df1['Depth']]

    # rotation angle - counterclockwise
    # teta=degrees(atan(-(dfs['E2']-dfs['E1'])/(dfs['N2']-dfs['N1'])))
    teta = np.arctan((dfs['E2'] - dfs['E1']) / (dfs['N2'] - dfs['N1']))
    # rotation matriz - positive angle counterclockwise
    rot_mat = [[np.cos(teta), -np.sin(teta)], [np.sin(teta), np.cos(teta)]]

    xy = np.array([np.dot(rot_mat, np.array([df1['Eperf'].ix[i], df1['Nperf'].ix[i]])) for i in df1.index])
    df1['E_perfA'] = np.squeeze(xy)[:, 0]
    df1['N_perfA'] = np.squeeze(xy)[:, 1]

    # plot to check
    fig = plt.figure(facecolor='w', figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(121)
    ax.scatter(df1['Eperf'], df1['Nperf'], s=50, c='r')
    ax.scatter(0, 0, s=150, c='k')
    ax.axis('equal')
    xf = ax.get_xbound()
    yf = ax.get_ybound()
    r = 50  # or whatever fits you
    ax.arrow(xf[1] * 0.7, yf[1] * 0.7, 0, r, head_width=50, head_length=50)
    ax1 = fig.add_subplot(122)
    ax1.scatter(df1['E_perfA'], df1['N_perfA'], s=50, c='r')
    ax1.scatter(0, 0, s=150, c='k')
    ax1.axis('equal')
    xf1 = ax1.get_xbound()
    yf1 = ax1.get_ybound()
    ax1.arrow(xf1[1] * 0.7, yf1[1] * 0.7, r * np.cos(np.pi / 2 + teta), r * np.sin(np.pi / 2 + teta),
              head_width=50, head_length=50)

    df1 = df1.drop(['Eperf', 'Nperf', 'Zperf'], 1)
    return df1


def plots_ev_loc(stage, df, dfs):
    """
    Plot event locations in plan and ED
    legacy from SMTI modules
    :param stage: stages dataframe
    :param df: events dataframe
    :param dfs: frac zones dataframe
    :return:
    """
    fig = plt.figure(facecolor='w', figsize=(9, 6), dpi=100)
    ax = fig.add_subplot(211)
    ax.scatter(df['Easting'], df['Northing'], s=50, c='r')
    ax.plot([dfs['E1'], dfs['E2']], [dfs['N1'], dfs['N2']], 'k', lw=3)
    ax.axis('equal')
    ax.set_xlabel('Easting (ft)')
    ax.set_ylabel('Northing (ft)')
    ax.set_title(stage)
    ax1 = fig.add_subplot(212)
    ax1.scatter(df['Easting'], df['Depth'], s=50, c='r')
    ax1.plot([dfs['E1'], dfs['E2']], [dfs['Z1'], dfs['Z2']], 'k', lw=3)
    ax1.invert_yaxis()
    ax1.axis('equal')
    ax1.set_xlabel('Easting (ft)')
    ax1.set_ylabel('Depth (ft)')
    return fig


def plotptb(smtdb, dots=False, only_dots=False, ms=3, malpha=1, fnum=1):
    """
    Plot P,T,B axes
    :param smtdb:
    :param dots: False to only plot density countours
    :param only_dots: plot dots
    :param ms: marker size for dots option
    :param malpha: marker alpha for dots option
    :param fnum:
    :return:
    """
    ppl = np.array(smtdb['Pdip'])
    ptr = np.array(smtdb['Paz'])
    tpl = np.array(smtdb['Tdip'])
    ttr = np.array(smtdb['Taz'])
    bpl = np.array(smtdb['Bdip'])
    btr = np.array(smtdb['Baz'])
    fig = plt.figure(fnum, facecolor='w', figsize=(15, 5), dpi=100)
    fig.clf()
    ax1 = fig.add_subplot(131, projection='stereonet')
    if dots:
        ax1.line(ppl, ptr, 'ko', markersize=ms, zorder=2, alpha=malpha)
        if not only_dots:
            _ = ax1.density_contourf(ppl, ptr, measurement='lines', zorder=1, alpha=0.3)
    else:
        _ = ax1.density_contourf(ppl, ptr, measurement='lines', zorder=2, alpha=1)
    ax1.set_title('P-axis\n')
    ax1.grid(True)
    ax2 = fig.add_subplot(132, projection='stereonet')
    if dots:
        ax2.line(bpl, btr, 'ko', markersize=ms, zorder=2, alpha=malpha)
        if not only_dots:
            _ = ax2.density_contourf(bpl, btr, measurement='lines', zorder=1, alpha=0.3)
    else:
        _ = ax2.density_contourf(bpl, btr, measurement='lines', zorder=2, alpha=1)
    ax2.grid(True)
    ax2.set_title('B-axis\n')
    ax3 = fig.add_subplot(133, projection='stereonet')
    if dots:
        ax3.line(tpl, ttr, 'ko', markersize=ms, zorder=2, alpha=malpha)
        if not only_dots:
            _ = ax3.density_contourf(tpl, ttr, measurement='lines', zorder=1, alpha=0.3)
    else:
        _ = ax3.density_contourf(tpl, ttr, measurement='lines', zorder=2, alpha=1)
    ax3.set_title('T-axis\n')
    ax3.grid(True)
    fig.subplots_adjust(left=0.05, hspace=0.3, top=0.85)
    # savefig(outdir+'Strain\\PT_'+name+'_'+well+'_'+str('%02d' % stagen)+'.png') #,transparent=True)
    return fig


def add_stress_axes(ax, strten):
    """
    Add p,t,b vector to a figure axis
    :param ax:
    :param strten:
    :return:
    """
    from ..StressInversion import principal_axes
    rval, s1, s2, s3 = principal_axes(strten)
    s1t, s1p = trend_plunge(s1)
    s2t, s2p = trend_plunge(s2)
    s3t, s3p = trend_plunge(s3)
    ax.line(s1p, s1t, 'r*', mec='w')
    ax.line(s2p, s2t, 'g*', mec='w')
    ax.line(s3p, s3t, 'b*', mec='w')


def plotptb_sigma(smtdb, strten, dots=False, fnum=1, cmap=None):
    """
    Plot P,T,B axes
    :param smtdb: database of values
    :param strten: stress tensor
    :param dots: plots for events? stations?
    :param fnum: figure number
    :param cmap: optional color map to select
    :return:
    """
    from ..StressInversion import principal_axes
    rval, s1, s2, s3 = principal_axes(strten)
    ppl = np.array(smtdb['Pdip'])
    ptr = np.array(smtdb['Paz'])
    tpl = np.array(smtdb['Tdip'])
    ttr = np.array(smtdb['Taz'])
    bpl = np.array(smtdb['Bdip'])
    btr = np.array(smtdb['Baz'])

    fig = plt.figure(fnum, facecolor='w', figsize=(15, 5), dpi=100)
    fig.clf()
    ax1 = fig.add_subplot(131, projection='stereonet')
    if dots:
        _ = ax1.density_contourf(ppl, ptr, measurement='lines', zorder=2, alpha=0.8, cmap=cmap)
        ax1.line(ppl, ptr, 'ko', markersize=5, zorder=1)
    else:
        _ = ax1.density_contourf(ppl, ptr, measurement='lines', zorder=1, alpha=1, cmap=cmap)
    ax1.set_title(r'P-axis, $\sigma_1$\n')
    ax1.grid(True)
    ax2 = fig.add_subplot(132, projection='stereonet')
    if dots:
        _ = ax2.density_contourf(bpl, btr, measurement='lines', zorder=2, alpha=0.8, cmap=cmap)
        ax2.line(bpl, btr, 'ko', markersize=5, zorder=1)
    else:
        _ = ax2.density_contourf(bpl, btr, measurement='lines', zorder=1, alpha=1, cmap=cmap)
    ax2.grid(True)
    ax2.set_title(r'B-axis, $\sigma_2$\n')
    ax3 = fig.add_subplot(133, projection='stereonet')
    if dots:
        _ = ax3.density_contourf(tpl, ttr, measurement='lines', zorder=2, alpha=0.8, cmap=cmap)
        ax3.line(tpl, ttr, 'ko', markersize=5, zorder=1)
    else:
        _ = ax3.density_contourf(tpl, ttr, measurement='lines', zorder=1, alpha=1, cmap=cmap)
    ax3.set_title(r'T-axis, $\sigma_3$\n')
    ax3.grid(True)
    s1t, s1p = trend_plunge(s1)
    s2t, s2p = trend_plunge(s2)
    s3t, s3p = trend_plunge(s3)
    ax1.line(s1p, s1t, 'w*', markersize=20, zorder=13)
    ax2.line(s2p, s2t, 'w*', markersize=20, zorder=13)
    ax3.line(s3p, s3t, 'w*', markersize=20, zorder=13)
    fig.add_axes([0.83, 0.1, 0.1, 0.75], frameon=False, xticks=[], yticks=[])

    fig.subplots_adjust(left=0.05, hspace=0.3, top=0.85)
    # savefig(outdir+'Strain\\PT_'+name+'_'+well+'_'+str('%02d' % stagen)+'.png') #,transparent=True)
    return fig


#
# def plotptb_sigma_scat(smtdb,strten):
#    ''' Plot P,T,B axes '''
#    R,s1,s2,s3 = principal_axes(strten)
#    smtdb['Pstr0'],smtdb['Pdip0'] = mplstereonet.plunge_bearing2pole(smtdb['Pdip'].values,smtdb['Paz'].values)
#    smtdb['Tstr0'],smtdb['Tdip0'] = mplstereonet.plunge_bearing2pole(smtdb['Tdip'].values,smtdb['Taz'].values)
#    smtdb['Bstr0'],smtdb['Bdip0'] = mplstereonet.plunge_bearing2pole(smtdb['Bdip'].values,smtdb['Baz'].values)
#
#    fig = figure(facecolor='w',figsize=(15,5),dpi=100)
#
#    ax = fig.add_subplot(131,projection='stereonet')
#    ax.pole(smtdb[smtdb['Sol']=='DC']['Pstr0'], smtdb[smtdb['Sol']=='DC']['Pdip0'], 'ro', markersize=7,
#    zorder=1,label='DC')
#    ax.pole(smtdb[smtdb['Sol']=='GN']['Pstr0'], smtdb[smtdb['Sol']=='GN']['Pdip0'], 'co', markersize=7,
#    zorder=2,label='GN')
#    ax.pole(smtdb[(smtdb['Sol']=='GN')&(smtdb['DC']>=0.5)]['Pstr0'], smtdb[(smtdb['Sol']=='GN')&
#    (smtdb['DC']>=0.5)]['Pdip0'], 'o', color='orange',markersize=7, zorder=3,label='GN In')
#
#    ax.set_title('P-axis,  $\sigma_1$\n')
#    ax.grid(True)
#
#    ax2 = fig.add_subplot(133,projection='stereonet')
#    ax2.pole(smtdb[smtdb['Sol']=='DC']['Tstr0'], smtdb[smtdb['Sol']=='DC']['Tdip0'], 'ro', markersize=7,
#    zorder=1,label='DC')
#    ax2.pole(smtdb[smtdb['Sol']=='GN']['Tstr0'], smtdb[smtdb['Sol']=='GN']['Tdip0'], 'co', markersize=7,
#    zorder=2,label='GN')
#    ax2.pole(smtdb[(smtdb['Sol']=='GN')&(smtdb['DC']>=0.5)]['Tstr0'], smtdb[(smtdb['Sol']=='GN')&
#    (smtdb['DC']>=0.5)]['Tdip0'], 'o', color='orange',markersize=7, zorder=3,label='GN In')
#    ax2.set_title('T-axis,  $\sigma_3$\n')
#    ax2.grid(True)
#    text(-0.70,-0.22,name+'  '+well,color='k',ha='center',va='bottom',
#         rotation=0, clip_on=False, fontsize=18, transform=ax2.transAxes)
#
#    ax3 = fig.add_subplot(132,projection='stereonet')
#    ax3.pole(smtdb[smtdb['Sol']=='DC']['Bstr0'], smtdb[smtdb['Sol']=='DC']['Bdip0'], 'ro', markersize=7,
#    zorder=1,label='DC')
#    ax3.pole(smtdb[smtdb['Sol']=='GN']['Bstr0'], smtdb[smtdb['Sol']=='GN']['Bdip0'], 'co', markersize=7,
#    zorder=2,label='GN')
#    ax3.pole(smtdb[(smtdb['Sol']=='GN')&(smtdb['DC']>=0.5)]['Bstr0'], smtdb[(smtdb['Sol']=='GN')&
#    (smtdb['DC']>=0.5)]['Bdip0'], 'o', color='orange',markersize=7, zorder=3,label='GN In')
#    ax3.grid(True)
#    ax3.set_title('B-axis,  $\sigma_2$\n')
#
#    # plot principle stresses
#    s1t,s1p = trend_plunge(s1)
#    s2t,s2p = trend_plunge(s2)
#    s3t,s3p = trend_plunge(s3)
#    ax.line(s1p, s1t, 'b*', markersize=20, zorder=13,alpha=0.8,mec='w')
#    ax2.line(s3p, s3t, 'b*', markersize=20, zorder=13,alpha=0.8,mec='w')
#    ax3.line(s2p, s2t, 'b*', markersize=20, zorder=13,alpha=0.8,mec='w')
#
#    ax3.legend(loc='upper center',numpoints=1, ncol=3, bbox_to_anchor=(0.5, 1.4))
#    fig.subplots_adjust(left=0.05,hspace=0.3,top=0.85)
#    return(fig)


def plot_sigma(strten, newfig=True, fnum=1, verbose=False):
    """
    Plot principle stresses
    :param strten:
    :param newfig:
    :param fnum:
    :param verbose:
    :return:
    """
    from ..StressInversion import principal_axes
    rval, s1, s2, s3 = principal_axes(strten)
    fig, axs = mplstereonet.subplots(num=fnum, projection='stereonet', figsize=(7, 6), facecolor='w', dpi=100)
    axs.cla()
    s1t, s1p = trend_plunge(s1)
    s2t, s2p = trend_plunge(s2)
    s3t, s3p = trend_plunge(s3)
    axs.line(s1p, s1t, 'r*', markersize=20, zorder=13)
    axs.line(s2p, s2t, 'g*', markersize=20, zorder=13)
    axs.line(s3p, s3t, 'b*', markersize=20, zorder=13)
    axs.grid(True)
    axs.set_title('R = %.2f' % rval, fontsize=20, loc='left')

    if verbose:
        print('Sigma 1: ' + str(int(s1t)) + ',' + str(int(s1p)))
        print('Sigma 2: ' + str(int(s2t)) + ',' + str(int(s2p)))
        print('Sigma 3: ' + str(int(s3t)) + ',' + str(int(s3p)))

    return fig


def plotfp_scat(strike, dip, fnum=1):
    """
    Plot fracture planes on a stereonet as points
    :param strike:
    :param dip:
    :param fnum:
    :return:
    """
    # create plot
    fig = plt.figure(num=fnum, facecolor='w', figsize=(7, 6), dpi=100)
    ax = fig.add_subplot(111, projection='stereonet')
    ax.pole(strike, dip, 'bo', markersize=7, zorder=3)
    # plot poles and planes of densest point
    ax.grid(True)
    fig.add_axes([0.8, 0.1, 0.1, 0.75], frameon=False, xticks=[], yticks=[])
    return fig


def plotfp_plane(strike, dip, fnum=1, linewidth=2, dots=False, **kwargs):
    """
    Plot fracture planes on a stereonet as planes
    :param strike:
    :param dip:
    :param fnum:
    :param linewidth:
    :param dots:
    :param kwargs:
    :return:
    """

    # create plot
    fig = plt.figure(num=fnum, facecolor='w', figsize=(7, 6), dpi=100)
    ax = fig.add_subplot(111, projection='stereonet')
    ax.plane(strike, dip, markersize=7, zorder=3, linewidth=linewidth, **kwargs)

    if dots:
        ax.pole(strike, dip, markersize=7, zorder=3, **kwargs)

    ax.grid(True)
    fig.add_axes([0.8, 0.1, 0.1, 0.75], frameon=False, xticks=[], yticks=[])
    return fig


def plotfp(strike, dip, dots=False, cmax=None, fnum=1, method='exponential_kamb', sigma=3, cmap=None):
    """
    Plot fracture planes on a stereonet as density
    :param strike: strike of fault
    :param dip: dip of fault
    :param dots: events to plot?
    :param cmax: maximum value for colors
    :param fnum: Figure number
    :param method: 'exponential_kamb','linear_kamb','kamb','schmidt' - method for density contour
    :param sigma: 1, 2 ,3
    :param cmap: color map to use in plots
    :return:
    """

    p_str, p_dip = finddensestpoint(strike, dip)
    fig = plt.figure(num=fnum, facecolor='w', figsize=(7, 6), dpi=100)
    fig.clf()
    ax = fig.add_subplot(111, projection='stereonet')
    if not dots:
        cax = ax.density_contourf(strike, dip, measurement='poles', zorder=1, alpha=1.0, vmax=cmax, method=method,
                                  sigma=sigma, cmap=cmap)
    else:
        cax = ax.density_contourf(strike, dip, measurement='poles', zorder=2, alpha=0.8, vmax=cmax, method=method,
                                  sigma=sigma, cmap=cmap)
        ax.pole(strike, dip, 'ko', markersize=5, zorder=1)
    ax.plane(p_str, p_dip, 'white', linewidth=2)
    ax.grid(True)
    ax2 = fig.add_axes([0.8, 0.1, 0.1, 0.75], frameon=False, xticks=[], yticks=[])
    _ = plt.colorbar(cax, shrink=0.9, pad=0.01, ax=ax2)
    return fig


def rosette(strike, binsize=10, fnum=1):
    """
    Rosette plot of strikes
    :param strike: strike of the fracture
    :param binsize: binsize to plot the rosettes in
    :param fnum: figure number
    :return:
    """
    # smtdb=sf.correct_fp(smtdb,slip='No')
    # st is fracture strike
    st1 = []
    st2 = []
    strike = np.mod(strike, 360.)
    for sta in strike:
        if sta < 180.:
            st1.append(sta)
            st2.append(sta + 180)
        else:
            st1.append(sta - 180.)
            st2.append(sta)
    sts = np.array(st1 + st2)
    d2r = np.pi / 180.
    fig = plt.figure(num=fnum, facecolor='w', figsize=(8, 8), dpi=100)
    n, bins, p = plt.hist(sts, np.arange(0., 361., binsize), visible=False)
    theta = (90 - binsize - bins[:-1]) * d2r
    fig.clf()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
    _ = ax.bar(theta, n, width=binsize * d2r, bottom=0.0)
    ax.set_thetagrids(range(0, 360, 45), ('E', 'NE', 'N', 'NW', 'W', 'SW', 'S', 'SE'))
    return fig


def rosette_rake(rake, binsize=10, fnum=1):
    """
    Rosette plot of the rakes
    :param rake: rake of the fracture
    :param binsize: bin size to plot the rosettes in
    :param fnum: figure number
    :return:
    """
    d2r = np.pi / 180.
    fig = plt.figure(num=fnum, facecolor='w', figsize=(8, 8), dpi=100)
    n, bins, p = plt.hist(rake, np.arange(0., 361., binsize), visible=False)
    fig.clf()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
    _ = ax.bar(bins[:-1] * d2r, n, width=binsize * d2r, bottom=0.0)
    ax.set_thetagrids(range(0, 360, 90), ('RL', 'TH', 'LL', 'NM'))
    return fig


# def rosette_dip(name,well,strike,dip,binsize=10,mindip=30.,ym=10):
#    #smtdb=sf.correct_fp(smtdb,slip='No')
#    strike=strike[dip>=mindip]
#    strike=strike[~np.isnan(strike)]
#    # st is fracture strike
#    st1 = []
#    st2 = []
#    for sta in strike:
#        if (sta<180.):
#            st1.append(sta)
#            st2.append(sta+180)
#        else:
#            st1.append(sta-180.)
#            st2.append(sta)
#    sts = array(st1+st2)
#    d2r = pi/180.
#    r2d = 180./pi
#    degree_symbol = unichr(0176).encode("latin-1")
#    n,bins,p = hist(sts,arange(0.,361.,binsize),visible=False)
#    theta = (90-binsize-bins[:-1])*d2r
#    fig = figure(facecolor='w',figsize=(8,8),dpi=100)
#    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
#    bars = ax.bar(theta, n, width=binsize*d2r, bottom=0.0)
#    ax.set_ylim(ymax=ym)
#    thetagrids(range(0,360,45), ('E','NE','N','NW','W','SW','S','SE') )
#    text(0.5,-0.1,name+'  '+well+', dip > '+str(int(mindip)),color='k',ha='center',fontsize=18,transform=ax.transAxes)
#    return(fig)

# def instability(n, mu, R, sig1, sig2, sig3):
#     n1, n2, n3 = n
#     nr = [n1 * sig1[0] + n2 * sig1[1] + n3 * sig1[2], \
#           n1 * sig2[0] + n2 * sig2[1] + n3 * sig2[2], \
#           n1 * sig3[0] + n2 * sig3[1] + n3 * sig3[2]]
#     nr1, nr2, nr3 = nr
#     sigm = nr1 * nr1 + (1. - 2. * R) * nr2 * nr2 - nr3 * nr3
#     tau = 2. * np.sqrt(
#         (R * R * nr1 * nr1 * nr2 * nr2 + (1. - R) * (1. - R) * nr2 * nr2 * nr3 * nr3 + nr1 * nr1 * nr3 * nr3))
#     insta = (tau - mu * (sigm - 1.)) / (mu + np.sqrt(1 + mu * mu))
#     return (insta, tau, sigm)


def plot_mc(smc, tuc, rval, fnum=1, sym='bo', newfig=True):
    """
    Plot (smc,tuc) points on Mohr circle with stress ratio R.
    :param smc:
    :param tuc:
    :param rval:
    :param fnum: the figure number
    :param sym: format for the symbols on the plot
    :param newfig: whether to plot a new figure
    """
    if newfig:
        fig = plt.figure(fnum, figsize=[12, 9], facecolor='w')
        fig.clf()
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], frameon=False, aspect='equal')
        ii = -1
        x1, y1 = np.zeros(181), np.zeros(181)
        d2r = np.pi / 180.
        for phi in range(-90, 91):
            ii += 1
            x1[ii], y1[ii] = np.sin(d2r * phi), np.cos(d2r * phi)
        ax.plot(x1, y1, 'k', lw=2)
        ax.plot((1 - rval) * x1 - rval, (1 - rval) * y1, 'k', lw=2)
        ax.plot(rval * x1 + 1 - rval, rval * y1, 'k', lw=2)
        ax.arrow(-1.2, 0, 2.4, 0, fc="k", ec="k", head_width=0.05, head_length=0.08)
        ax.arrow(-1.2, 0, 0, 1.1, fc="k", ec="k", head_width=0.05, head_length=0.08)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xlim([-1.3, 1.3])
        ax.set_ylim([-0.1, 1.2])
        fs = 28
        ax.text(1.3, 0, r'$\sigma$', va='center', fontsize=fs)
        ax.text(-1.2, 1.2, r'$\tau$', ha='center', fontsize=fs, zorder=0)
        if rval < 0.07:
            ax.text(-1, -0.1, r'$\sigma_3$', ha='center', fontsize=fs)
            ax.text(1 - rval, -0.1, r'$\sigma_2\ \sigma_1$', ha='center', fontsize=fs)
        elif rval > 0.93:
            ax.text(-rval, -0.1, r'$\sigma_3\ \sigma_2$', ha='center', fontsize=fs)
            ax.text(1, -0.1, r'$\sigma_1$', ha='center', fontsize=fs)
        else:
            ax.text(-1, -0.1, r'$\sigma_3$', ha='center', fontsize=fs)
            ax.text(1 - 2 * rval, -0.1, r'$\sigma_2$', ha='center', fontsize=fs)
            ax.text(1, -0.1, r'$\sigma_1$', ha='center', fontsize=fs)
    else:
        fig = plt.figure(fnum)
        ax = fig.gca()
    ax.plot(smc, abs(tuc), sym)
    return fig


def mohr_circle(smtdb, sig1, sig2, sig3, R):
    """
    Make a mohr circle plot
    :param smtdb:
    :param sig1: sigma 1 principal stress
    :param sig2: sigma 2 principal stress
    :param sig3: sigma 3 principal stress
    :param R:
    :return:
    """
    from DPUtil import fpstrikedip
    from ..StressInversion import calculate_instability
    R = np.squeeze(np.array(R))
    strike, dip = fpstrikedip(smtdb)
    nev = len(strike)
    ins, sig, tau = np.zeros(nev), np.zeros(nev), np.zeros(nev)
    for ii in range(nev):
        nv = normal_vector(strike[ii], dip[ii])
        ins[ii], tau[ii], sig[ii] = calculate_instability(nv, 0.6, R, sig1, sig2, sig3)
    fig = plot_mc(sig, tau, R, sym='bo')
    _ = fig.gca()
    return fig


def source_type_kde(events, fnum=1, labels=False, bw_method=None, cmap=None):
    """
    Make a density source type plot
    :param events: events to plot
    :param fnum: figure number
    :param labels: labels for parameters
    :param bw_method: None, silverman, scott, scalar number
    :param cmap: option to set cmap of output
    :return:
    """
    from matplotlib import patches
    from scipy import stats

    kall, tall = SMT2kt(events)
    # ign = find(events['Sol']=='GN')
    u, v = [], []
    # k,t = kall[ign], tall[ign]
    k, t = kall, tall
    for ki, ti in np.array([k, t]).T:
        tau = ti * (1. - abs(ki))
        if ((ki < 0.) & (tau > .0)) or ((ki > 0.) & (tau < 0.)):
            u.append(tau)
            v.append(ki)
        elif (ki > 0.) & (tau > 0.):
            if tau < 4 * ki:
                u.append(tau / (1. - tau / 2.))
                v.append(ki / (1. - tau / 2.))
            else:
                u.append(tau / (1. - 2. * ki))
                v.append(ki / (1. - 2. * ki))
        else:
            if tau > 4 * ki:
                u.append(tau / (1. + tau / 2.))
                v.append(ki / (1. + tau / 2.))
            else:
                u.append(tau / (1. + 2. * ki))
                v.append(ki / (1. + 2. * ki))
    values = np.c_[u, v]

    fig = plt.figure(fnum, figsize=[12, 9], facecolor='w')
    fig.clf()
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], frameon=False, xticks=[], yticks=[])

    if len(u) >= 3:
        kernel = stats.kde.gaussian_kde(values.T, bw_method=bw_method)
        xval, yval = np.mgrid[-4. / 3.:4. / 3.:100j, -1.:1.:100j]
        positions = np.c_[xval.ravel(), yval.ravel()]
        zval = np.reshape(kernel(positions.T).T, xval.T.shape)
        if cmap is None:
            im = plt.imshow(np.rot90(zval), extent=[-4. / 3., 4. / 3., -1., 1.])
        else:
            im = plt.imshow(np.rot90(zval), extent=[-4. / 3., 4. / 3., -1., 1.], cmap=cmap)
    else:
        if cmap is None:
            im = plt.imshow(np.zeros([100, 100]), extent=[-4. / 3., 4. / 3., -1., 1.])
        else:
            im = plt.imshow(np.zeros([100, 100]), extent=[-4. / 3., 4. / 3., -1., 1.], cmap=cmap)

    diamond = np.array([[0., 1.], [4. / 3., 1. / 3.], [0., -1.], [-4. / 3., -1. / 3.], [0., 1.]])
    patch = patches.Polygon(diamond, closed=True, transform=ax.transData)
    im.set_clip_path(patch)
    for ii in range(2, 10, 2):
        yi = float(ii) / 30.
        xi = yi * 4.
        ax.plot([0, xi, 0, -xi, 0], [1, yi, -1, -yi, 1], '0.75')

    for ii in range(2, 10, 2):
        tau = 1. - float(ii) / 10
        yr = float(ii) / 10. / (1. - tau / 2.)
        xr = tau / (1. - tau / 2.)
        yl = float(ii) / 10.
        xl = -1. + float(ii) / 10
        ax.plot([xl, 0, xr], [yl, yl, yr], '0.75')
        ax.plot([-xr, 0, -xl], [-yr, -yl, -yl], '0.75')

    ax.plot([0., 0.], [-1., 1.], 'w', lw=2)
    ax.plot([-1., 1.], [0., 0.], 'w', lw=2)
    ax.plot([-4. / 3., 4. / 3.], [-1. / 3., 1. / 3], 'w', lw=2)
    frame_x = [0., 4. / 3., 0, -4. / 3., 0.]
    frame_y = [1., 1. / 3., -1., -1. / 3., 1.]
    ax.plot(frame_x, frame_y, 'k', lw=2)
    if labels:
        ax.text(0, 1.03, 'Explosive', ha='center', fontsize=14)
        ax.text(0, -1.03, 'Implosive', ha='center', va='top', fontsize=14)
        ax.text(1.05, 0, '$-$ CLVD', ha='left', va='center', fontsize=14)
        ax.text(-1.03, 0, '+ CLVD', ha='right', va='center', fontsize=14)
        ax.text(0.73, -1. / 3., '$-$ Linear Dipole', ha='left', fontsize=14)
        ax.text(0.5, -5. / 9., 'Tensile Crack Closure', ha='left', fontsize=14)
        ax.text(-0.7, 1. / 3., '+ Linear Dipole', ha='right', fontsize=14)
        ax.text(-0.47, 5. / 9., 'Tensile Crack Opening', ha='right', fontsize=14)
        ax.text(0, 0, 'DC', ha='center', va='center', fontsize=14, bbox=dict(facecolor='w', edgecolor='w'))
    return fig


def plot_slip_vectors(ss, fnum=1):
    """
    Plot the slip vectors
    :param ss:
    :param fnum:
    :return:
    """
    tr, pl = trend_plunge(ss)
    # inormal = find(ss[2, :] > 0)
    inormal = np.nonzero(np.ravel(ss[2, :] > 0))
    # irevers = find(ss[2, :] < 0)
    irevers = np.nonzero(np.ravel(ss[2, :] < 0))
    fig = plt.figure(fnum)
    ax = fig.add_subplot(111, projection='stereonet')
    ax.line(pl[inormal], tr[inormal], 'bo')
    ax.line(pl[irevers], tr[irevers], 'ro')
    return fig


def plot_dip_hist(dips, bins=30):
    """
    Make a radial dip histogram
    This can be useful to separate data based on fracture plane dip
    :param dips:
    :param bins:
    :return:
    """

    # Remove any nan fracture dips
    dp_nonan = dips[~np.isnan(dips)]
    # convert to radians and negative down dips
    dp_rad = np.deg2rad(dp_nonan) * -1

    # make axes and plot histogram
    ax = plt.subplot(111, polar=True)

    ax.hist(dp_rad, bins=bins)

    # show only a quarter of the polar plot
    ax.set_thetamin(0)
    ax.set_thetamax(-90)

    return ax


def add_block_to_ax(ax, blockname, DSN, sqlstr=r"mgs\\mgs", label=True, blocktype=None, **kwargs):
    """

    :param ax: ax to add block to
    :param blockname: name of block in db
    :param DSN: database name
    :param sqlstr: database server path
    :param label: boolean to show block name
    :param blocktype: provide blocktype is the block id is duplicated between tables
    :return:
    """
    block = Database.readsqlblocks(DSN, sqlstr='MGS\\MGS')

    blockfilter = block[block['Block ID'] == blockname]

    if blocktype is not None:
        blockfilter = blockfilter[blockfilter['BlockType'] == blocktype]

    if len(blockfilter) == 0:
        raise Exception("Block to filter was not found.")
    elif len(blockfilter) > 1:
        raise Exception("Multiple blocks with this name are found.")

    blockrow = blockfilter.iloc[0]
    blocktype = blockrow['BlockType']

    if blocktype == "Mine Blocks":
        x_coords = np.array([blockrow.Emin, blockrow.Emax, blockrow.Emax, blockrow.Emin, blockrow.Emin])
        y_coords = np.array([blockrow.Nmin, blockrow.Nmin, blockrow.Nmax, blockrow.Nmax, blockrow.Nmin])

    elif blocktype == "RotatedBlocks":
        strike = blockrow.Strike  # azim from N
        dip = blockrow.Dip
        orn, ore, ordval = blockrow.OrN, blockrow.OrE, blockrow.OrD
        lenn, lene, lend = blockrow.LenN, blockrow.LenE, blockrow.LenD

        if dip != 0.0:
            raise Exception("The block dip is not zero. 3D rotation has not been implemented in the python code.")
        # rotate corners of rectangle to be in placement as per seisvi rotated block
        x_coords_unrot = np.array([ore, ore + lene, ore + lene, ore, ore])
        y_coords_unrot = np.array([orn, orn, orn + lenn, orn + lenn, orn])
        x_coords, y_coords = rotatecoord(x_coords_unrot, y_coords_unrot, -strike, origin=(ore, orn), inrad=False)

    elif blocktype == "VolumeBlocks":
        # Volume blocks
        # BlockID, BlockData
        blockdata_list = blockrow.BlockData.split(",")
        # zmin = blockdata_list[0]
        # zmax = blockdata_list[1]

        blockdata = np.array(blockdata_list[2:])

        blockdata = blockdata.reshape(int(len(blockdata)/2), 2)
        blockdata = blockdata.astype(float)

        y_coords = blockdata[:, 0]
        x_coords = blockdata[:, 1]

        y_coords = np.append(y_coords, y_coords[0])
        x_coords = np.append(x_coords, x_coords[0])

    else:
        raise Exception("The block type "+blocktype+" is not yet in the code.")

    ax.plot(x_coords, y_coords, **kwargs)

    if label:
        ax.text(np.min(x_coords), np.max(y_coords), blockname.strip())

    ax.axis('equal')

    return ax
