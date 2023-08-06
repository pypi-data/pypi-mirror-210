"""
Various functions to work with waveform data in hsf files and dsf files
Authors: Mike P, Lindsay S, Sara B, Josh W
"""

# importing modules
import glob
import numpy as np
import copy
import matplotlib.pyplot as plt
# import matplotlib.gridspec as gridspec
from io import StringIO
import configparser
import struct
import warnings
import os
import logging
import subprocess
from pickled_carrots.database import makeLinuxPath
# from IPython.display import display
from pickled_carrots.plot import plot_sensors
from pickled_carrots.mathutil import sta_lta_mask, trgid2hsfpath
from scipy import signal
import pandas as pd
from datetime import datetime
import time
from subprocess import call, Popen, PIPE
from ipdb import set_trace


class HeaderLookups(object):
    event_types = ['Event', 'Blast', 'RockBurst', 'CasingFailure',
                   'Background', 'Noise', 'Custom1', 'Custom2', 'Custom3',
                   'UnknownEvt', 'SgmEvent', 'Duplicate', 'none', 'none',
                   'none', 'none', 'none', 'none', 'none', 'none', 'none',
                   'none']
    sensor_types = ['GEOPHONE', 'ACCELEROMETER', 'SGM_GEOPHONE',
                    'FBA_ACCELEROMETER', 'BVM_MICROPHONE']


# simple function for reading in a segy stream
def read_segy(file_path):
    """
    Simple function for reading in an example segy file
    Author: Joshua Williams (joshua.williams@esgsolutions.com)
    :param file_path: path to the file to be read
    :type file_path: str
    :return Stream of data
    :returntype obspy stream object
    """
    from obspy.core import read
    # making the file path make sense
    file_path = makeLinuxPath(file_path)

    # reading in the traces
    st = read(file_path, format='SEGY', unpack_trace_headers=True)

    # setting the stations and headers
    for tr in st:
        tr.stats.station = str(tr.stats.segy.trace_header.original_field_record_number)

        # channel
        # makes an assumption here about the trace number and which component that corresponds to
        if tr.stats.segy.trace_header.trace_number_within_the_original_field_record == 2:
            tr.stats.channel = 'N'
        elif tr.stats.segy.trace_header.trace_number_within_the_original_field_record == 3:
            tr.stats.channel = 'E'
        elif tr.stats.segy.trace_header.trace_number_within_the_original_field_record == 1:
            tr.stats.channel = 'Z'

    # returning stream
    return st


# simple function to read in a seed file
def read_seed(file_path):
    """
    Simple function to read in a seed file
    Author: Joshua Williams (joshua.williams@esgsolutions.com)
    :param file_path: path to the file to be read in
    :type file_path: str
    :return stream of traces
    :returntype obspy stream object
    """
    from obspy.core import read
    # fixing file path
    file_path = makeLinuxPath(file_path)

    # reading in the traces
    st = read(file_path, format='MSEED')

    # returning obspy stream to the user
    return st


# function to convert hsf data into obspy structure
def hsf_to_obspy(file=None, head=None, data=None, rotate=True, correct_g_to_mss=True,
                 print_out=True,
                 groundmotion=True, rotate_to_zrt=False, force_positive_down=False,
                 experimental=False,
                 force_python_decompress=False, rotate_to_lqt=False, return_head=True):
    """
    Function to convert the information read from the hsf file by read_hsf into an obspy trace object
    There is some additional information saved to the header of each trace:
    stats.t0 - The P arrival time in seconds - 0 if there is no P arrival
    stats.t1 - The S arrival time in seconds - 0 if there is no S arrival
    stats.t2 - The origin time in seconds
    stats.t3 - The Sh arrival time in seconds - 0 if there is no Sh
    stats.t4 - The Sv arrival time in seconds - 0 if there is no Sv
    stats.kt2 - completion status of station in hsf
    stats.kt3 - time sync status of station in hsf
    stats.kt4 - enabled/disabled status of station/channel in hsf
    Author: Joshua Williams (joshua.williams@esgsolutions.com)
    :param head: the header information from read_hsf
    :param data: the (assumed acceleration) data read from the hsf file in the format
        [num traces, num points]
        Also using this to provide the AWS s3 data which we want to extract the hsf data from if relevant
    :param file: the name of the file to be used to read the hsf data from
    :param rotate: if True, rotates the data into a ZNE coordinate system
    :param correct_g_to_mss: if True, corrects accelerometer data from g to m/s/s
    :param print_out: if True, prints to screen when traces don't have P or S values
    :param groundmotion: if True, returns output in SI units rather than volts
    :param rotate_to_zrt: if True, rotates the data to radial and transverse - transverse contains mostly SH energy, and
        radial contains mostly P and Sv energy. Vertical component remains. For reference, H component in WaveVis is
        the same as the T component here, and the V component is the Radial. R component in WaveVis is the polarity 
        flipped down component, which is the same as the vertical component here. WaveVis uses down as positive 
        sometimes - might need futher work to build this in here.
        Also, we just obtain the azimuth from the earthquake location and station location saved in the file, we don't
        do anything fancy with detecting the ray path direction.
    :param force_positive_down: if True, then if the data has the use_elevation flag set to true, as in vertical motion
        is positive upwards, the code will flip this so the data has vertical motion positive downwards
    :param experimental: if True, uses the experimental version of read hsf rather than the normal version
    :param force_python_decompress: if True, forces code to use the Python decompression method
    :param rotate_to_lqt: if True, rotate to lqt instead of zrt (rotating to ray path)
    :param return_head: if True returns the header
    :return: An obspy stream of traces of the data in the hsf file
    """
    import obspy
    import math
    
    # making sure that rotate is turned on if rotate_to_zrt is turned on
    if rotate_to_zrt or rotate_to_lqt:
        rotate = True

    # setting experimental to True when on posix

    if os.name == 'posix':
        experimental = True
    
    # whether to run the read_hsf function
    if head is None:
        if experimental is False:
            tm, data, head = read_hsf(file=file, groundmotion=groundmotion, print_out=print_out,
                                      from_hsf_to_obspy=True)
        else:
            tm, data, head = read_hsf_exp(file=file, groundmotion=groundmotion, print_out=print_out,
                                          from_hsf_to_obspy=True, s3data=data,
                                          force_python_decompress=force_python_decompress)

    # letting the user know that we follow the esg standard and report the vertical as positive up
    if head['use_elevation'] == 1 and print_out:
        print('\n**************')
        print('NOTE: we follow the hsf settings here and vertical is positive upwards rather than down.')
        print('Changing to vertical positive down will change the amplitudes of the rotated traces due to\n'
              'the change in the dip')
        print('**************\n')
        if force_positive_down is True:
            # TODO the vertical amplitudes don't appear to be forced to be positive?
            print('You have chosen to force vertical amplitudes to be positive down.')

    # checking whether the data is None
    # this is for cases where I was having issues with files that did not have the correct amount of buffer for the 
    # given data size - not sure on the cause of this error but for now including this workaround
    # IF YOU FIND an example file that is triggering this issue, then please drop me an email at 
    # joshua.williams@esgsolutions.com or drop me a line on teams.
    if data is None:
        return None
    
    # setting up some header information
    stats = obspy.core.Stats()
    stats.network = 'esg'
    stats.sampling_rate = head['fs']  # in Hz
    stats.npts = head['npts']
    stats.starttime = obspy.UTCDateTime(head['dt'])

    # pulling out the event type
    # according to the header file for hsf files
    possible_types = ['Event', 'Blast', 'RockBurst', 'CasingFailure', 'Background', 'Noise', 'Custom1',
                      'Custom2', 'Custom3', 'UnknownEvt', 'SgmEvent', 'Duplicate', 'none', 'none', 'none', 'none',
                      'none', 'none', 'none', 'none', 'none', 'none']
    stats.evtype = possible_types[head['evtype']]

    # reading in the data to traces in obspy streams
    stream = obspy.Stream()
    for i in range(0, len(data)):
        tr = obspy.Trace(data[i, :], header=stats)
        stream.append(tr)

    # detecting the instrument type of the data using the stype part of the header
    possible_types = ['GEOPHONE', 'ACCELEROMETER', 'SGM_GEOPHONE', 'FBA_ACCELEROMETER', 'BVM_MICROPHONE']

    # figuring out which traces have incomplete data
    new_descr = []
    for ij in range(len(head['ch_descr'])):
        if head['ch_descr'][ij] not in new_descr:
            new_descr.append(head['ch_descr'][ij])
    new_descr = np.array(new_descr)
    incomplete_stations = new_descr[head['incomplete_data']]
    bad_time_sync_stations = new_descr[head['bad_sync']]
    enabled_stations = new_descr[head['enabled']]

    # assigning the channel names
    if head['ntr'] > 0 and len(head['ch_descr']) > 0:
        count = 0
        stcount = 0

        # saving the name of the first trace of the station to fix problems with inconsistent station
        # descriptions
        ch_descr_temp = head['ch_descr'][0].rstrip('\x00')

        # looping through each of the traces
        for k in range(0, head['ntr']):

            # these counters are needed to select the collect part of the sensor rotation
            # 'count' goes through the stations, I had to introduce this because otherwise the code
            # won't work for uniaxial and triaxial sensors mixed in the file
            # 'stcount' counts through the trace location for the particular station, so goes through each channel
            if k != 0:
                # so if we're onto a new station name and the number of sensors has gone past the number of channels
                # then we must be onto the next station
                if head['ch_descr'][k] != head['ch_descr'][k - 1] and stcount+1 > head['nch_sen'][count]:
                    count += 1
                    stcount = 0
                    ch_descr_temp = head['ch_descr'][k].rstrip('\x00')

            # saving the station name
            # old way of getting the station name
            # stream[k].stats.station = head['ch_descr'][k].split('_')[0].split('\'')[1]
            # new way of getting the station name
            stream[k].stats.station = ch_descr_temp

            # saving the incomplete status to the stream
            if ch_descr_temp in incomplete_stations:
                stream[k].stats.kt2 = 'incomplete'
            else:
                stream[k].stats.kt2 = 'complete'

            # saving the time sync status
            if ch_descr_temp in bad_time_sync_stations:
                stream[k].stats.kt3 = 'bad_time_sync'
            else:
                stream[k].stats.kt3 = 'good_time_sync'

            # saving the enabled status
            if ch_descr_temp in enabled_stations and not head['valid_flag_channelbad'][k]:
                stream[k].stats.kt4 = 'enabled'
            else:
                stream[k].stats.kt4 = 'disabled'

            # attempting to save the snr
            klist = list(head.keys())
            if 'p_snr' in klist:
                stream[k].stats.p_snr = head['p_snr'][count]
            if 's_snr' in klist:
                stream[k].stats.s_snr = head['s_snr'][count]
            if 'p_pol' in klist:
                stream[k].stats.p_pol = head['p_pol'][count]
            if 's_pol' in klist:
                stream[k].stats.s_pol = head['s_pol'][count]
            if 'sv_pol' in klist:
                stream[k].stats.sv_pol = head['sv_pol'][count]
            if 'sh_pol' in klist:
                stream[k].stats.sh_pol = head['sh_pol'][count]
            if 'senpos' in klist:
                stream[k].stats.easting = head['senpos'][count][0]
                stream[k].stats.northing = head['senpos'][count][1]
                stream[k].stats.depth = head['senpos'][count][2]
            # if 'sen_rot' in klist:
            #     stream[k].stats.c0_rot = head['sen_rot'][count][0]
            #     stream[k].stats.c1_rot = head['sen_rot'][count][0]
            #     stream[k].stats.c2_rot = head['sen_rot'][count][0]
            # if

            # saving the distance between the event and station to the header of the obspy trace
            stream[k].stats.distance = head['Distance'][count]

            # figuring out the instrument type
            actual_type = possible_types[head['stype'][count]]

            # and correcting for g depending on the instrument type
            mult_factor = 1
            if actual_type == 'ACCELEROMETER' or actual_type == 'FBA_ACCELEROMETER':
                # whether we want to correct the values of g to m/s/s
                if correct_g_to_mss is True:
                    mult_factor = 9.81
                stream[k].stats.instrument_type = 'ACC'

                # if the station is an accelerometer, then setting the second letter as N to try and
                # follow IRIS SEED naming conventions
                chan_str_2 = 'N'
            else:
                stream[k].stats.instrument_type = 'VEL'

                # if the station is a geophone, then setting the second letter as H to try and
                # follow IRIS SEED naming conventions
                chan_str_2 = 'P'

            # pulling out the channel name
            # got rid of the location based channel naming because the rotation should take care of that
            # plus if you base it off the orientation then some stations you will end up with the same name
            # for multiple channels
            stream[k].stats.channel = 'G'+chan_str_2+str(stcount+1)

            # estimating the angle of the station from North
            azimuth = None
            if head['sen_rot'][count][stcount][0] != 0:
                az_change = math.degrees(math.atan(head['sen_rot'][count][stcount][1] /
                                                   head['sen_rot'][count][stcount][0]))

                # then getting the azimuth depending on whether the east angle is positive or not
                # assessing which quadrant the azimuth should be in
                if head['sen_rot'][count][stcount][0] > 0:
                    # so the direction is north
                    if head['sen_rot'][count][stcount][1] > 0:
                        # in the north east quadrant
                        azimuth = 0 + az_change
                    elif head['sen_rot'][count][stcount][1] < 0:
                        # in the north west quadrant
                        azimuth = 360 + az_change
                elif head['sen_rot'][count][stcount][0] < 0:
                    # so its south
                    if head['sen_rot'][count][stcount][1] > 0:
                        # in the south east quadrant
                        azimuth = 180 + az_change
                    elif head['sen_rot'][count][stcount][1] < 0:
                        # in the south west quadrant
                        azimuth = 180 + az_change

            # if we're in the situation where one of the components is zero, then we can assign the azimuth pretty
            # easily
            if head['sen_rot'][count][stcount][0] == 0:
                # we are exactly along the east west line
                if head['sen_rot'][count][stcount][1] > 0:
                    # then the azimuth is exactly east
                    azimuth = 90
                elif head['sen_rot'][count][stcount][1] < 0:
                    # then the azimuth is exactly west
                    azimuth = 270
            if head['sen_rot'][count][stcount][1] == 0:
                # we are exactly along the north south line
                if head['sen_rot'][count][stcount][0] > 0:
                    # we are exactly north
                    azimuth = 0
                elif head['sen_rot'][count][stcount][0] < 0:
                    # we are exactly south
                    azimuth = 180

            # for the case where both north and east are zero then its a perfect vertical component
            if head['sen_rot'][count][stcount][0] == 0. and head['sen_rot'][count][stcount][1] == 0.:
                azimuth = 0

            # then calculating the back azimuth
            if azimuth < 180:
                back_azimuth = azimuth + 180
            else:
                back_azimuth = azimuth - 180
            stream[k].stats.back_azimuth = back_azimuth
            stream[k].stats.azimuth = azimuth

            # estimating the dip and inclination
            # accounting for cases where the user has selected to force positive down motions
            if head['use_elevation'] == 1 and force_positive_down is True:
                sen_rot_value = head['sen_rot'][count][stcount][2] * -1.
            else:
                sen_rot_value = head['sen_rot'][count][stcount][2]

            # computing the dip and inclination
            dip = math.degrees(math.acos(sen_rot_value)) - 90  # removed minus just before head
            inclination = 90 - math.degrees(math.acos(sen_rot_value))
            stream[k].stats.inclination = inclination
            stream[k].stats.dip = dip

            # and setting the P wave and S wave arrival times
            stream[k].stats.kt0 = 'P'
            stream[k].stats.kt1 = 'S'
            if experimental is False:
                stream[k].stats.t0 = head['parr'][count][0]
                stream[k].stats.t1 = head['sarr'][count][0]
                stream[k].stats.t3 = head['harr'][count][0]
                stream[k].stats.t4 = head['varr'][count][0]
            else:
                stream[k].stats.t0 = head['parr'][count]
                stream[k].stats.t1 = head['sarr'][count]
                stream[k].stats.t3 = head['harr'][count]
                stream[k].stats.t4 = head['varr'][count]

            # saving the origin time as well - haven't got this as t0 because of backwards compatability issues
            stream[k].stats.t2 = head['time0']

            # correction of instrument data from g to m/s/s
            # mult factor is determined above, so data will not be changed if the instrument units are m/s rather than
            # m/s/s
            stream[k].data = stream[k].data * mult_factor

            # warning user if there do not appear to be any P or S wave arrival picks
            if stream[k].stats.t0 == 0 and stream[k].stats.t1 == 0 and print_out is True:
                print('Warning: There do not appear to be P and S picks for the trace ' + stream[k].stats.network +
                      '.'+stream[k].stats.station + '.' + stream[k].stats.channel)

            # iterating the stcount value
            stcount += 1

    if rotate is False and print_out is True:
        print('rotation is off')
    if rotate is True:
        # and then rotating the traces to a ZNE alignment
        # pulling out the names of each station
        stat_names = []
        for tr in stream:
            if tr.stats.station not in stat_names:
                stat_names.append(tr.stats.station)

        # estimating the azimuth and back azimuth of the stations relative to the event and saving to a dictionary
        az_dict = dict()
        eq_loc = head['source']
        for jk in range(len(stat_names)):
            # pulling out the station location
            sen_loc = head['pos'][jk]

            # estimating the azimuth clockwise from north of the earthquake relative to the station and thus
            # the back azimuth of the station relative to the source
            # 90 - is to make sure the negative angles get flipped, % 360
            stat_azimuth = (360 + math.degrees(math.atan2(eq_loc[1] - sen_loc[1], eq_loc[0] - sen_loc[0]))) % 360
            if stat_azimuth < 180:
                stat_back_azimuth = stat_azimuth + 180
            else:
                stat_back_azimuth = stat_azimuth - 180

            # testing Dougs approach for calculating inclination
            xvalue = sen_loc[1] - eq_loc[1]
            yvalue = sen_loc[0] - eq_loc[0]
            zvalue = sen_loc[2] - eq_loc[2]
            rvalue = math.sqrt(xvalue * xvalue + yvalue * yvalue + zvalue * zvalue)
            # incvalue = (180 + math.degrees(math.acos(zvalue / rvalue)) * -1) % 180
            stat_inclination = (180 + math.degrees(math.acos(zvalue / rvalue))) % 180

            # saving to the dictionary
            az_dict[stat_names[jk] + ' az'] = stat_azimuth
            az_dict[stat_names[jk] + ' backaz'] = stat_back_azimuth
            az_dict[stat_names[jk] + ' inc'] = stat_inclination

        # making the inventory object using the stream
        inventory = create_obspy_inv(stream)
        if print_out is True:
            print('This code rotates traces into a ZNE coordinate system')
        for jk in range(len(stat_names)):
            stream_new = stream.select(station=stat_names[jk])
            good_station = check_rotation(stream_new)

            # checking if the stream can be rotated
            if good_station is True:
                try:
                    # noinspection PyProtectedMember
                    stream.select(station=stat_names[jk])._rotate_to_zne(inventory=inventory)
                except ValueError:
                    print('station ' + stat_names[jk] + ' could not be rotated to zne due to azimuth/dip problem')
                except NotImplementedError:
                    print('station ' + stat_names[jk] + ' could not be rotated due to hsf error.')
                    temp_st = stream.select(station=stat_names[jk])
                    for tr in temp_st:
                        stream.remove(tr)
        # stream._rotate_to_zne(inventory=inventory)

        # option for rotating to zrt format
        # error if both are true
        if rotate_to_zrt and rotate_to_lqt:
            raise ValueError('Cannot rotate to both ZRT and LQT')
        if rotate_to_zrt or rotate_to_lqt:
            # defaults to RT
            rot_method = 'NE->RT'
            if rotate_to_lqt:
                rot_method = 'ZNE->LQT'

            # looping through each of the stations
            for jk in range(len(stat_names)):
                # extracting the azimuth and back azimuth from the dictionary
                stat_azimuth = az_dict[stat_names[jk]+' az']
                stat_inclination = az_dict[stat_names[jk]+' inc']

                # now performing the rotation
                if print_out is True:
                    print('Be wary of the ZRT or LQT rotation, '
                          'there may be some issues with the obspy function so compare '
                          'the waveforms with WaveVis')
                stream.select(station=stat_names[jk]).rotate(rot_method,
                                                             back_azimuth=stat_azimuth,
                                                             inclination=stat_inclination)

                # flipping the amplitude of the Q component to agree with the output that we see in WaveVis
                if head['use_elevation']:
                    sttemp = stream.select(station=stat_names[jk], channel='**Q')
                    for tr in sttemp:
                        tr.data = tr.data * -1

    if return_head:
        return stream, head
    else:
        return stream


def create_obspy_inv(stream):
    """
    Function for creating an obspy inventory object from the stream without using a station xml
    Based on the obspy tutorials for creating xml files from scratch
    This inventory does not include the response data, just the data needed for rotation
    Author: Joshua Williams (joshua.williams@esgsolutions.com)
    :param stream: stream of data used
    :type stream: obspy stream
    :return: obspy inventory containing the station information
    :rtype: obspy inventory
    """
    # some handy imports
    from obspy import UTCDateTime
    from obspy.core.inventory import Inventory, Network, Station, Channel, Site, Latitude, Longitude

    # creating the overall inventory file
    inv = Inventory(
        # We'll add networks later.
        networks=[],
        # The source should be the id whoever create the file.
        source="esg")

    # then creating the network
    net = Network(
        # This is the network code according to the SEED standard.
        code="esg",
        # A list of stations
        stations=[],
        description="esg stations",
        # Start-and end dates are optional.
        start_date=UTCDateTime(1971, 1, 1))

    # then creating each station
    # pulling out the stations and channels out of the stream
    stat_names = []
    for tr in stream:
        if tr.stats.station not in stat_names:
            stat_names.append(tr.stats.station)

    # now creating each station for the inventory
    for ij in range(len(stat_names)):
        st_new = stream.select(station=stat_names[ij])
        sta = Station(
            # This is the station code according to the SEED standard.
            code=stat_names[ij],
            latitude=Latitude(10.),  # these other values don't matter for rotation
            longitude=Longitude(120.),
            elevation=0.,
            site=Site(name=stat_names[ij]))

        # looping through each channel in the stream
        for tr in st_new:
            cha = Channel(
                # This is the channel code according to the SEED standard.
                code=tr.stats.channel,
                # This is the location code according to the SEED standard.
                location_code=tr.stats.location,
                # Note that these coordinates can differ from the station coordinates.
                latitude=Latitude(10.),  # these other parameters don't matter for rotation
                longitude=Longitude(120.),
                elevation=0.,
                depth=1.,
                azimuth=tr.stats.azimuth,
                dip=tr.stats.dip,
                sample_rate=tr.stats.sampling_rate)

            # adding this channel to the station above
            sta.channels.append(cha)

        # adding the station to the networks
        net.stations.append(sta)

    # and adding the whole network into the inventory
    inv.networks.append(net)

    # and finally returning the inventory object
    return inv


def check_rotation(st, log=False):
    """
    Checking whether the direction cosines are viable and therefore whether rotation is appropriate
    :param st: stream of data traces
    :param log: If True, print warning to log rather than screen. Default: False
    :return:
    """
    # grabbing the function that creates the vectors used for rotation
    # noinspection PyProtectedMember
    from obspy.signal.rotate import _dip_azimuth2zne_base_vector

    # checking if its a triaxial station
    if len(st) == 3:
        # getting the azimuths and dips
        azimuths = [tr.stats.azimuth for tr in st]
        dips = [tr.stats.dip for tr in st]

        # making the base vectors
        base_vector_1 = _dip_azimuth2zne_base_vector(dips[0], azimuths[0])
        base_vector_2 = _dip_azimuth2zne_base_vector(dips[1], azimuths[1])
        base_vector_3 = _dip_azimuth2zne_base_vector(dips[2], azimuths[2])

        # forming matrix and calculating the determinant
        m = np.array([base_vector_1,
                      base_vector_2,
                      base_vector_3])
        det = np.linalg.det(m)

        # if determinant is less than 0.99 then don't rotate the trace
        if abs(det) < 0.99:
            if log is False:
                print('Station: ' + st[0].stats.station + ' cannot be rotated due to cosines \n '
                      'not combining to unit vector')
            else:
                logging.info('Station: ' + st[0].stats.station + ' cannot be rotated due to cosines \n '
                             'not combining to unit vector')
            # returning False if the station cannot be rotated
            return False
        else:
            return True
    else:
        # for uniaxial stations let obspy figure itself out
        return True


def readhsf(**kwargs):
    """
    Pass through function
    """
    print('Function readhsf has been renamed to read_hsf.')
    read_hsf(**kwargs)


def read_hsf(file, head_only=False, footer=0, groundmotion=False, print_out=True, stdout=True, from_hsf_to_obspy=False):
    """
    Function to read hsf files into a python format, kind of magic, based on old code from
    Mike Preiksaitis and Lindsay Smith
    Author: Joshua Williams (joshua.williams@esgsolutions.com)
    :param file: name of the file to read the data from
    :param head_only: whether to only output the header info, defaults to 0 which is False
    :param footer: whether to include the footer info, as in the editing information for the program
    :param groundmotion: whether to output the ground motion, if False then outputs voltage
    if True then assumes acceleration output
    Outputs motion without StripDC applied, so user may have to demean explicitly - didn't want to hard code this in
    :param print_out: if True, prints out warning about conversion of data units. Also turns off the warning that bad
        data has been reset to zero
    :param stdout: If True, then uncompress and give data directly to Python
    :param from_hsf_to_obspy: if True, stop the warning about acceleration data from printing out. Should only be set to
        true when read_hsf has been called from within the hsf_to_obspy function
    :return: the timing, the header information, and the data
    """

    # opening the file in read and byte mode
    try:
        f = open(file, 'rb')
    except OSError:
        time.sleep(30)
        f = open(file, 'rb')

    # not sure what this is doing
    try:
        h309 = f.read(309)
    except OSError:
        print(file)
        f.close()
        print('Got Invalid argument error')
        return None, None, None

    npt, nbit, npal, nsens, nch = struct.unpack('5i', h309[68:88])
    ntr = struct.unpack('i', h309[88:92])[0]
    wfst = struct.unpack('i', h309[92:96])[0]

    fs = float(struct.unpack('i', h309[42:46])[0])

    tm = np.arange(npt) / fs

    head = dict()
    head['npts'] = npt
    head['npal'] = npal
    head['nsen'] = nsens
    head['nchl'] = nch
    head['ntr'] = ntr
    head['nbit'] = nbit
    # type of compressions. 0 = none, 1 = zlib, 2 = minilzo, 3 = simple rice
    head['compress'] = struct.unpack('i', h309[12:16])[0]
    head['resample'] = struct.unpack('B', h309[301:302])[0]
    # number of bytes used for compressed waveform data
    head['compresssize'] = struct.unpack('i', h309[16:20])[0]
    head['groupid'] = struct.unpack('10c', h309[20:30])[0]
    head['lm'] = struct.unpack('i', h309[30:34])[0]
    # use elevation 0 if z axis for event locations is down, up if 1
    head['use_elevation'] = struct.unpack('i', h309[38:42])[0]
    # head['input_voltage'] = struct.unpack('i',h309[64:68])[0]
    # offset to the waveform data from the beginning of the hsf file
    head['data_offs'] = struct.unpack('i', h309[92:96])[0]
    head['source'] = np.array(struct.unpack('3f', h309[112:124]))
    head['evtype'] = struct.unpack('h', h309[251:253])[0]
    head['time0'] = struct.unpack('f', h309[253:257])[0]
    head['knownt0'] = struct.unpack('f', h309[302:306])[0]
    head['fs'] = struct.unpack('i', h309[42:46])[0]
    head['t0_s'] = struct.unpack('i', h309[96:100])[0]
    head['t0_us'] = struct.unpack('i', h309[100:104])[0]
    # generate datetime of t0
    head['dt'] = datetime.fromtimestamp(head['t0_s']).replace(microsecond=head['t0_us'])
    head['site_vp'] = struct.unpack('f', h309[126:130])
    head['site_vs'] = struct.unpack('f', h309[130:134])
    # should be source_v not site_v - Gisela
    head['source_vp'] = struct.unpack('f', h309[126:130])
    head['source_vs'] = struct.unpack('f', h309[130:134])
    head['mw'] = struct.unpack('f', h309[164:168])[0]
    head['moment'] = struct.unpack('f', h309[168:172])[0]
    head['nrgval'] = struct.unpack('f', h309[172:176])[0]
    head['esep'] = struct.unpack('f', h309[176:180])[0]
    head['srcrad'] = struct.unpack('f', h309[180:184])[0]
    head['asprad'] = struct.unpack('f', h309[184:188])[0]
    head['ststdp'] = struct.unpack('f', h309[188:192])[0]
    head['appstr'] = struct.unpack('f', h309[192:196])[0]
    head['dystdp'] = struct.unpack('f', h309[196:200])[0]
    head['mxdisp'] = struct.unpack('f', h309[200:204])[0]
    head['pkvelp'] = struct.unpack('f', h309[204:208])[0]
    head['pkaccp'] = struct.unpack('f', h309[208:212])[0]
    head['textfooterlength'] = struct.unpack('i', h309[243:247])[0]

    hrem = f.read(wfst - 309)

    nch_sen, rot_win, eig_rot, eig_val, pos, ttt, snstvt, stp = [], [], [], [], [], [], [], []
    qp, qs, qsv, qsh = [], [], [], []
    vp, vs = [], []
    dis, raydir, sv_ttt = [], [], []
    sensor_name, volt_range, senmodel = [], [], []
    p_snr, s_snr = [], []
    enabled, bad_sync, incomplete_data = [], [], []
    dir_error, sensor_id, station_ind, pre_amp = [], [], [], []

    senh = 26 * npal
    for isen in range(nsens):
        stp.append(int(struct.unpack('i', hrem[senh:senh + 4])[0]))
        nch_sen.append(int(struct.unpack('i', hrem[senh + 4:senh + 8])[0]))
        pos.append(np.array(struct.unpack('3f', hrem[senh + 12:senh + 24])))
        snstvt.append(np.array(struct.unpack('f', hrem[senh + 24:senh + 28]))[0])
        ttt.append(np.array(struct.unpack('2f', hrem[senh + 32:senh + 40])))
        rot_win.append(np.array(struct.unpack('2i', hrem[senh + 40:senh + 48])))
        eig_rot.append(np.array(struct.unpack('9f', hrem[senh + 48:senh + 84])).reshape(3, 3))
        eig_val.append(np.array(struct.unpack('3f', hrem[senh + 84:senh + 96])))
        # print('sensor')
        # print(pos[isen])
        # print('event')
        # print(head['source'])
        dis.append(np.math.sqrt((pos[isen][0] - head['source'][0]) ** 2 + (pos[isen][1] - head['source'][1]) ** 2 + (
                pos[isen][2] - head['source'][2]) ** 2))

        dir_error.append(np.array(struct.unpack('3f', hrem[senh + 96:senh + 108])))
        sensor_id.append(struct.unpack('h', hrem[senh + 108:senh + 110])[0])
        station_ind.append(int(struct.unpack('i', hrem[senh + 110:senh + 114])[0]))
        pre_amp.append(np.array(struct.unpack('f', hrem[senh + 114:senh + 118]))[0])
        enabled.append(bool(struct.unpack('i', hrem[senh + 118:senh + 122])[0]))
        sensor_name.append(str(hrem[senh + 122:senh + 134]).split('\\x00')[0])
        # TODO incomplete data is accurate, not sure about bad sync and enabled though
        bad_sync.append(bool(struct.unpack('i', hrem[senh + 134:senh + 138])[0]))
        incomplete_data.append(bool(struct.unpack('i', hrem[senh + 144:senh + 148])[0]))
        raydir.append(struct.unpack('3f', hrem[senh + 154:senh + 166]))
        sv_ttt.append(struct.unpack('f', hrem[senh + 166:senh + 170]))
        # load sensor model
        senmodel.append(struct.unpack('h', hrem[senh + 170:senh + 172]))
        # saving what might be the snr values from hsf
        p_snr.append(struct.unpack('f', hrem[senh + 172:senh + 176]))
        s_snr.append(struct.unpack('f', hrem[senh + 176:senh + 180]))

        # saving the Q value (attenuation?) and velocity at site
        qp.append(struct.unpack('f', hrem[senh + 186:senh + 190]))
        qs.append(struct.unpack('f', hrem[senh + 190:senh + 194]))
        # qs and qsv are same byte locations. if qsh does not exist then it is before the two were saved separately
        qsv.append(struct.unpack('f', hrem[senh + 190:senh + 194]))
        qsh.append(struct.unpack('f', hrem[senh + 194:senh + 198]))
        vp.append(struct.unpack('f', hrem[senh + 199:senh + 203]))
        vs.append(struct.unpack('f', hrem[senh + 203:senh + 207]))

        vr = struct.unpack('f', hrem[senh + 207:senh + 211])
        if vr[0] > 6:
            vr = (4.096,)
        elif vr[0] == 0.0:
            vr = (4.096,)  # old files may have anomalous values above 6 volts
        volt_range.append(vr[0])
        # 10 bits left in dummy as buffer at the end
        senh = senh + 222

    head['nch_sen'] = nch_sen
    head['dir_error'] = dir_error
    head['sensor_id'] = sensor_id
    head['station_ind'] = station_ind
    head['pre_amp'] = pre_amp
    head['rot_win'] = rot_win
    head['eig_rot'] = eig_rot
    head['eig_val'] = eig_val
    head['Distance'] = dis
    head['senpos'] = pos
    head['pos'] = pos
    head['ttt'] = ttt
    head['snstvt'] = snstvt
    head['raydir'] = raydir
    head['stype'] = stp
    head['enabled'] = enabled
    head['bad_sync'] = bad_sync
    head['incomplete_data'] = incomplete_data
    head['sensor_name'] = sensor_name
    head['qp'], head['qs'], head['qsv'], head['qsh'] = qp, qs, qsv, qsh
    head['sv_ttt'] = sv_ttt
    head['senmodel'] = senmodel
    head['p_snr'] = p_snr
    head['s_snr'] = s_snr
    head['vp_sensor'], head['vs_sensor'] = vp, vs
    head['volt_range'] = volt_range

    # performing a quick check to see if any of the sensors are accelerometers and printing a warning if they are
    possible_types = ['GEOPHONE', 'ACCELEROMETER', 'SGM_GEOPHONE', 'FBA_ACCELEROMETER', 'BVM_MICROPHONE']
    for count in range(len(head['stype'])):
        actual_type = possible_types[head['stype'][count]]
        if (actual_type == 'ACCELEROMETER' or actual_type == 'FBA_ACCELEROMETER') and print_out is True and \
                from_hsf_to_obspy is True:
            print('BEWARE you will need to adjust the data for accelerometers by multiplying by 9.81\n'
                  'Using hsf_to_obspy will automatically do this for you though.')
            break

    gain, ch_snstvt, descr = [], [], []
    ch_enabled = []
    low_f, high_f = [], []
    rms_amp, peak_amp = [], []
    sen_rot, parr, sarr, harr, varr = [], [], [], [], []
    p_pol, sv_pol, sh_pol = [], [], []
    p_pol_old, sv_pol_old, sh_pol_old = [], [], []
    omega_p, omega_s, corner_p, corner_s, energy_p, energy_s = [], [], [], [], [], []
    omega_sv, omega_sh, corner_sv, corner_sh, energy_sv, energy_sh = [], [], [], [], [], []
    acq_chan_ind,  ppick_used, spick_used = [], [], []
    valid_flag_pickused, valid_flag_newpolarity, valid_flag_sensorhealthknown = [], [], []
    valid_flag_sensorhealth, valid_flag_sensorhealthcheck, valid_flag_sensorusedintriggering = [], [], []
    valid_flag_channelbad = []
    raw_descr = []

    for isen in range(nsens):
        ori = []
        parr.append(np.array(struct.unpack('f', hrem[senh + 58:senh + 62])))
        p_pol.append(float(struct.unpack('h', hrem[senh + 94:senh + 96])[0]) / 32767.)
        p_pol_old.append(struct.unpack('h', hrem[senh + 52:senh + 54])[0])

        if nch_sen[isen] == 3:
            sarr.append(np.array(struct.unpack('f', hrem[senh + 62:senh + 66])))
            varr.append(np.array(struct.unpack('f', hrem[senh + 220:senh + 224])))
            harr.append(np.array(struct.unpack('f', hrem[senh + 378:senh + 382])))
            sv_pol.append(float(struct.unpack('h', hrem[senh + 254:senh + 256])[0]) / 32767.)
            sh_pol.append(float(struct.unpack('h', hrem[senh + 412:senh + 414])[0]) / 32767.)
            sv_pol_old.append(struct.unpack('h', hrem[senh + 212:senh + 214])[0])
            sh_pol_old.append(struct.unpack('h', hrem[senh + 370:senh + 372])[0])
            omega_p.append(np.array(struct.unpack('f', hrem[senh + 98:senh + 102])))
            omega_s.append(np.array(struct.unpack('f', hrem[senh + 102:senh + 106])))
            corner_p.append(np.array(struct.unpack('f', hrem[senh + 106:senh + 110])))
            corner_s.append(np.array(struct.unpack('f', hrem[senh + 110:senh + 114])))
            energy_p.append(np.array(struct.unpack('f', hrem[senh + 114:senh + 118])))
            energy_s.append(np.array(struct.unpack('f', hrem[senh + 118:senh + 122])))
            for ich in range(3):
                ch_enabled.append(struct.unpack('i', hrem[senh + 4:senh + 8])[0])
                gain.append(struct.unpack('f', hrem[senh + 8:senh + 12])[0])
                ori.append(np.array(struct.unpack('3f', hrem[senh + 12:senh + 24])))
                low_f.append(struct.unpack('f', hrem[senh + 24:senh + 28])[0])
                high_f.append(struct.unpack('f', hrem[senh + 28:senh + 32])[0])
                rms_amp.append(struct.unpack('f', hrem[senh + 44:senh + 48])[0])
                peak_amp.append(struct.unpack('f', hrem[senh + 48:senh + 52])[0])
                ch_snstvt.append(struct.unpack('f', hrem[senh + 66:senh + 70])[0])
                descr.append(hrem[senh + 70:senh + 87].decode('ISO-8859-1').rstrip("\x00"))  # 17 char
                acq_chan_ind.append(struct.unpack('h', hrem[senh + 87:senh + 89])[0])
                ppick_used.append(struct.unpack('h', hrem[senh + 89:senh + 91])[0])
                spick_used.append(struct.unpack('h', hrem[senh + 91:senh + 93])[0])

                # pulling out the valid flags
                temp = hrem[senh + 93:senh + 94]
                vf_pickused, vf_polarity, vf_shk, vf_sh, vf_shc, vf_strig, vf_bad = extract_valid_flags(temp)
                valid_flag_pickused.append(vf_pickused)
                valid_flag_newpolarity.append(vf_polarity)
                valid_flag_sensorhealthknown.append(vf_shk)
                valid_flag_sensorhealth.append(vf_sh)
                valid_flag_sensorhealthcheck.append(vf_shc)
                valid_flag_sensorusedintriggering.append(vf_strig)
                valid_flag_channelbad.append(vf_bad)

                if ich == 1:
                    omega_sv.append(np.array(struct.unpack('f', hrem[senh + 102:senh + 106])))
                    corner_sv.append(np.array(struct.unpack('f', hrem[senh + 110:senh + 114])))
                    energy_sv.append(np.array(struct.unpack('f', hrem[senh + 118:senh + 122])))
                elif ich == 2:
                    omega_sh.append(np.array(struct.unpack('f', hrem[senh + 102:senh + 106])))
                    corner_sh.append(np.array(struct.unpack('f', hrem[senh + 110:senh + 114])))
                    energy_sh.append(np.array(struct.unpack('f', hrem[senh + 118:senh + 122])))

                senh = senh + 158
        elif nch_sen[isen] == 1:
            sarr.append(np.array(struct.unpack('f', hrem[senh + 62:senh + 66])))
            harr.append(np.array([np.nan]))
            varr.append(np.array([np.nan]))
            # sv_pol.append(float(struct.unpack('h',hrem[senh+254:senh+256])[0])/32767.)
            # sh_pol.append(float(struct.unpack('h',hrem[senh+412:senh+414])[0])/32767.)
            sv_pol_old.append(struct.unpack('h', hrem[senh + 54:senh + 56])[0])
            sh_pol_old.append(struct.unpack('h', hrem[senh + 54: senh + 56])[0])
            acq_chan_ind.append(struct.unpack('h', hrem[senh + 87:senh + 89])[0])
            ppick_used.append(struct.unpack('h', hrem[senh + 89:senh + 91])[0])
            spick_used.append(struct.unpack('h', hrem[senh + 91:senh + 93])[0])

            # pulling out the valid flags
            temp = hrem[senh + 93:senh + 94]
            vf_pickused, vf_polarity, vf_shk, vf_sh, vf_shc, vf_strig, vf_bad = extract_valid_flags(temp)
            valid_flag_pickused.append(vf_pickused)
            valid_flag_newpolarity.append(vf_polarity)
            valid_flag_sensorhealthknown.append(vf_shk)
            valid_flag_sensorhealth.append(vf_sh)
            valid_flag_sensorhealthcheck.append(vf_shc)
            valid_flag_sensorusedintriggering.append(vf_strig)
            valid_flag_channelbad.append(vf_bad)

            omega_p.append(np.array(struct.unpack('f', hrem[senh + 98:senh + 102])))
            omega_s.append(np.array(struct.unpack('f', hrem[senh + 102:senh + 106])))
            corner_p.append(np.array(struct.unpack('f', hrem[senh + 106:senh + 110])))
            corner_s.append(np.array(struct.unpack('f', hrem[senh + 110:senh + 114])))
            energy_p.append(np.array(struct.unpack('f', hrem[senh + 114:senh + 118])))
            energy_s.append(np.array(struct.unpack('f', hrem[senh + 118:senh + 122])))
            omega_sv.append(np.array(struct.unpack('f', hrem[senh + 102:senh + 106])))
            corner_sv.append(np.array(struct.unpack('f', hrem[senh + 110:senh + 114])))
            energy_sv.append(np.array(struct.unpack('f', hrem[senh + 118:senh + 122])))

            omega_sh.append(np.array(struct.unpack('f', hrem[senh + 102:senh + 106])))
            corner_sh.append(np.array(struct.unpack('f', hrem[senh + 110:senh + 114])))
            energy_sh.append(np.array(struct.unpack('f', hrem[senh + 118:senh + 122])))

            ch_enabled.append(struct.unpack('i', hrem[senh + 4:senh + 8])[0])
            gain.append(struct.unpack('f', hrem[senh + 8:senh + 12])[0])
            ori.append(np.array(struct.unpack('3f', hrem[senh + 12:senh + 24])))
            low_f.append(struct.unpack('f', hrem[senh + 24:senh + 28])[0])
            high_f.append(struct.unpack('f', hrem[senh + 28:senh + 32])[0])
            rms_amp.append(struct.unpack('f', hrem[senh + 44:senh + 48])[0])
            peak_amp.append(struct.unpack('f', hrem[senh + 48:senh + 52])[0])
            ch_snstvt.append(struct.unpack('f', hrem[senh + 66:senh + 70])[0])
            # descr.append(hrem[senh+70:senh+87].split('\x00')[0].strip())
            # ori.append(np.array(struct.unpack('3f',hrem[senh+12:senh+24])))
            # ori.append(np.array([0,0,0]))
            # ori.append(np.array([0,0,0]))
            sv_pol.append([0., 0.])
            sh_pol.append([0., 0.])
            sv_pol_old.append([0, 0])
            sh_pol_old.append([0, 0])
            raw_descr.append(hrem[senh + 70:senh + 87])
            descr.append(hrem[senh + 70:senh + 87].decode('ISO-8859-1').rstrip("\x00"))
            senh = senh + 158
        sen_rot.append(np.array(ori))

    head['parr'] = parr
    head['sarr'] = sarr
    head['harr'] = harr
    head['varr'] = varr
    head['p_pol'], head['sv_pol'], head['sh_pol'] = p_pol, sv_pol, sh_pol
    head['ch_enabled'] = ch_enabled
    head['gain'] = gain
    head['low_f'] = low_f
    head['high_f'] = high_f
    head['rms_amp'] = rms_amp
    head['peak_amp'] = peak_amp
    head['ch_snstvt'] = ch_snstvt
    head['sen_rot'] = sen_rot
    head['ch_descr'] = descr
    head['raw_descr'] = raw_descr
    head['omega_p'] = omega_p
    head['omega_s'] = omega_s
    head['omega_sv'] = omega_sv
    head['omega_sh'] = omega_sh
    head['corner_p'] = corner_p
    head['corner_s'] = corner_s
    head['corner_sv'] = corner_sv
    head['corner_sh'] = corner_sh
    head['energy_p'] = energy_p
    head['energy_s'] = energy_s
    head['energy_sv'] = energy_sv
    head['energy_sh'] = energy_sh
    head['acq_chan_ind'] = acq_chan_ind
    head['ppick_used'] = ppick_used
    head['spick_used'] = spick_used
    head['valid_flag_pickused'] = valid_flag_pickused
    head['valid_flag_newpolarity'] = valid_flag_newpolarity
    head['valid_flag_sensorhealthknown'] = valid_flag_sensorhealthknown
    head['valid_flag_sensorhealth'] = valid_flag_sensorhealth
    head['valid_flag_sensorhealthcheck'] = valid_flag_sensorhealthcheck
    head['valid_flag_sensorusedintriggering'] = valid_flag_sensorusedintriggering
    head['valid_flag_channelbad'] = valid_flag_channelbad

    # If we want to read the header only then we are done. close the file and return the header
    if head_only:
        f.close()
        return head
    elif footer:
        # determine offset to start of footer
        if head['compress'] != 0 or head['resample'] != 0:
            # compressed or resampled -- waveform block size is given by compressed size
            offset = head['data_offs'] + head['compresssize']
        else:  # not compressed
            offset = head['data_offs'] + (head['npts'] + head['ntr']) * 4

        # all footer
        f.seek(offset)
        n = f.read()
        # decode binary to string
        # end of textfooter head['textfooterlength']
        allfooter = n
        allfooter_str = allfooter.decode('cp437')

        # skip to footer
        f.seek(offset)

        # read footer
        foot = {}

        nsize = struct.unpack('I', n[-4:])[0]  # size of blob block

        # deal with proc reports
        footerblobdirectory = n[len(n) - nsize - 4:len(n) - 4]
        directories = str(footerblobdirectory).split('\\n')[1:]

        for d in directories:
            if '=' in d:
                report, index = d.split('=')
                index = np.int(index)
                length = struct.unpack('I', n[index - offset + len(report) +
                                              2 + 1:index - offset + len(report) + 2 + 4 + 1])[0]
                data = n[index - offset + len(report) + 2 + 4 + 1:index - offset + len(report) + 2 + 4 + 1 + length]
                # parse report into dictionary
                try:
                    buf = StringIO(data.decode())
                    cfg = configparser.ConfigParser()
                    cfg.read_file(buf)
                    # noinspection PyProtectedMember
                    data_dict = dict(cfg._sections)
                    foot[report] = data_dict
                except configparser.ParsingError:
                    print('Footer Parsing Error with ' + report)

        f.close()

        # find event history
        historystart = allfooter_str.find('<<SEVHistory:') + 15
        historyend = allfooter_str.find('>>', historystart)

        evthistory = allfooter_str[historystart:historyend]
        evthistory_header = ['ModTime', 'UserName', 'Program', 'Type', 'Action']
        evthistory = pd.read_csv(StringIO(evthistory.replace('####', '\n').replace('##', ',').replace('|', ',')),
                                 header=None, names=evthistory_header)

        # getting the valid start and end times
        try:
            validstart = allfooter_str.find('<<ValidStart:') + len('<<ValidStart:')
            validend = allfooter_str.find('>>', validstart)
            lastvalidstart = allfooter_str.find('<<LastValid:') + len('<<LastValid:')
            lastvalidend = allfooter_str.find('>>', lastvalidstart)
            foot['ValidStart'] = float(allfooter_str[validstart:validend])
            foot['ValidEnd'] = float(allfooter_str[lastvalidstart:lastvalidend])
        except ValueError:
            foot['ValidStart'] = None
            foot['ValidEnd'] = None

        # saving information to the footer
        foot['evthistory'] = evthistory
        foot['allfooter'] = allfooter
        return head, foot

    else:  # If we want to also read the waveform data then continue

        hsfcompressor = r"C:\esg\hsfcompressor.exe"  # location of the hsf compressor program

        # if compressed check the platform
        if head['compress'] != 0:
            if not glob.os.path.exists(hsfcompressor) and os.name == 'nt':
                raise Exception("HSF file is compressed or resampled and HSFCompressor is missing. "
                                "Install Hsfcompress.exe to c:\\esg_utils")
            elif os.name != 'nt' and not glob.os.path.exists('/home/share/wine/HSFCompressor.exe'):
                raise Exception("HSF file is compressed or resampled and HSFCompressor is missing on linux. "
                                "Install Hsfcompress.exe to /home/share/wine")

        if os.name != "nt":
            # if we are on the jupyter server
            # adjusting the path of the hsf compressor call
            hsfcompressor = '/usr/bin/wine /home/share/wine/HSFCompressor.exe'

        if stdout:
            # Stdout option exists to directly pass waveform data to python
            p = Popen(hsfcompressor + ' -none -stdout ' + file, stdout=PIPE, stderr=PIPE, shell=True)
            hbin = ''
            err = ''
            try:
                hbin, err = p.communicate()
            except IOError:
                print('IOError: ' + str(IOError))
            if hbin == '':
                print('Output returned is blank.' + err)
            hbin = hbin[wfst:]  # Remove header
        else:  # old method: uncompress, read in, and then recompress
            if head['compress'] != 0 or head['resample'] != 0:  # if the header says the file is compressed or resampled
                f.close()  # close the file so that we can uncompress it
                _ = call(hsfcompressor + ' -none ' + file, shell=True)  # uncompress file

            try:
                f = open(file, 'rb')  # reopen the uncompressed file
            except FileNotFoundError:
                time.sleep(30)
                try:
                    f = open(file, 'rb')
                except FileNotFoundError:
                    print('File not found!')
                    return None, None, None

            f.seek(wfst)  # jump past the header
            hbin = f.read()  # read in the rest of the data
            f.close()

            if head['compress'] != 0 or head['resample']:  # if the file was compressed lets recompress it
                resamp_args = ''
                if head['resample'] != 0:
                    downsample = head['resample'] & 0x0F  # last 4 bits store downsampling
                    upsample = (head['resample'] & 0xF0) >> 4  # first 4 bits store upsampling
                    resamp_args = '-decimate ' + str(downsample) + ' -upsample ' + str(upsample) + ' '
                p = call(hsfcompressor + ' -rice ' + resamp_args + file, shell=True)

        num_elements = nch * npt
        frmt = str(num_elements) + 'i'

        # this is for cases where I was having issues with files that did not have the correct amount of buffer for the 
        # given data size - not sure on the cause of this error but for now including this workaround
        # IF YOU FIND an example file that is triggering this issue, then please drop me an email at 
        # joshua.williams@esgsolutions.com or drop me a line on teams.
        try:
            data = np.array(struct.unpack_from(frmt, hbin))
        except:
            time.sleep(20)
            try:
                data = np.array(struct.unpack_from(frmt, hbin))
            except:
                print('Something went wrong with the data structure')
                return None, None, None
        ibd = np.where(data == 16843009)[0]  # find bad data values
        if len(ibd) > 0:
            data[ibd] = 0
            if print_out is True:
                warnings.warn('Bad data reset to 0')
        data_array = np.reshape(data, (npt, nch))  # housekeeping to reformat the data
        data_array = np.transpose(data_array)
        data_array = np.array(data_array, dtype=int)

        # # initialising some counter values
        # count = 0
        # stcount = 1
        #
        # # for each trace
        # # iterate in case gains and sensitivity change between sensors
        # for i in range(0, len(data_array)):
        #     # need to pick the sensitivity
        #     # iterating through count variable to make sure the snstvt and volt_range is correct
        #
        #     # skip the first iteration because i-1 will cause an error
        #     # if the station description has changed and we have gone over the number of channels on the
        #     # sensor, then we must be onto a new station
        #     if i != 0 and head['ch_descr'][i] != head['ch_descr'][i - 1] and stcount > head['nch_sen'][count]:
        #         count += 1
        #         stcount = 1
        #
        #     # correcting for gain and sensitivity is ground motion is True
        #     # otherwise just outputting the raw data
        #     if groundmotion is True:
        #         div_value = head['gain'][i] * head['snstvt'][count]
        #     else:
        #         div_value = 1.
        #
        #     # outputs the data in acceleration for accelerometers and velocity for geophones
        #     # acceleration might be in g though as opposed to m/s/s
        #     data_array[i] = (data_array[i] / div_value / (
        #             2 ** (head['nbit'] - 1) / head['volt_range'][count]))
        #
        #     # iterating the variable to count through the number of traces in the station
        #     stcount += 1

        return tm, data_array, head


def read_hsf_exp(file, head_only=0, footer=0, groundmotion=False, print_out=True, from_hsf_to_obspy=False, s3data=None,
                 force_python_decompress=False):
    """
    Function to read hsf files into a python format, kind of magic, based on old code from
    Mike Preiksaitis and Lindsay Smith
    Author: Joshua Williams (joshua.williams@esgsolutions.com)
    Experimental version using numpy to extract values from buffer
    :param file: name of the file to read the data from
    :param head_only: whether to only output the header info, defaults to 0 which is False
    :param footer: whether to include the footer info, as in the editing information for the program
    :param groundmotion: whether to output the ground motion, if False then outputs voltage
    if True then assumes acceleration output
    Outputs motion without StripDC applied, so user may have to demean explicitly - didn't want to hard code this in
    :param print_out: if True, prints out warning about conversion of data units. Also turns off the warning that bad
        data has been reset to zero
    :param from_hsf_to_obspy: if True, stop the warning about acceleration data from printing out. Should only be set to
        true when read_hsf has been called from within the hsf_to_obspy function
    :param s3data: if not None then we are trying to load the file from s3 and therefore we can skip over some of the
        loading steps
    :param force_python_decompress: option to force the python decompression method to be used
    :return: the timing, the header information, and the data
    """

    # opening the file in read and byte mode
    f = None
    if s3data is None:
        try:
            f = open(file, 'rb')
        except OSError:
            time.sleep(30)
            f = open(file, 'rb')

        # reads the first 309 bytes of the file
        try:
            h309 = f.read(309)
        except OSError:
            print(file)
            f.close()
            print('Got Invalid argument error')
            return None, None, None
    else:
        h309 = s3data[:309]

    # extracting some initial useful information
    npt, nbit, npal, nsens, nch = struct.unpack('5i', h309[68:88])
    wfst = np.ndarray((1,), buffer=h309, offset=92, dtype='i')[0]
    fs = float(np.ndarray((1,), buffer=h309, offset=42, dtype='i')[0])
    tm = np.arange(npt) / fs

    """
    Reading in the main config from the header
    """

    # starting up head dictionary
    head = dict()

    # getting the event header information
    head['npts'] = npt
    head['npal'] = npal
    head['nsen'] = nsens
    head['nchl'] = nch
    head['ntr'] = np.ndarray((1,), buffer=h309, offset=88, dtype='i')[0]
    head['nbit'] = nbit
    # type of compressions. 0 = none, 1 = zlib, 2 = minilzo, 3 = simple rice
    head['compress'] = np.ndarray((1,), buffer=h309, offset=12, dtype='i')[0]
    head['resample'] = np.ndarray((1,), buffer=h309, offset=301, dtype='B')[0]
    # number of bytes used for compressed waveform data
    head['compresssize'] = np.ndarray((1,), buffer=h309, offset=16, dtype='i')[0]
    head['groupid'] = struct.unpack('10c', h309[20:30])[0]
    head['lm'] = np.ndarray((1,), buffer=h309, offset=30, dtype='i')[0]
    # use elevation 0 if z axis for event locations is down, up if 1
    head['use_elevation'] = np.ndarray((1,), buffer=h309, offset=38, dtype='i')[0]
    # head['input_voltage'] = struct.unpack('i',h309[64:68])[0]
    # offset to the waveform data from the beginning of the hsf file
    head['data_offs'] = np.ndarray((1,), buffer=h309, offset=92, dtype='i')[0]
    head['source'] = np.ndarray((3,), buffer=h309, offset=112, dtype='f')
    head['evtype'] = np.ndarray((1,), buffer=h309, offset=251, dtype='h')[0]
    head['time0'] = np.ndarray((1,), buffer=h309, offset=253, dtype='f')[0]
    head['knownt0'] = np.ndarray((1,), buffer=h309, offset=302, dtype='f')[0]
    head['fs'] = np.ndarray((1,), buffer=h309, offset=42, dtype='i')[0]
    head['t0_s'] = np.ndarray((1,), buffer=h309, offset=96, dtype='i')[0]
    head['t0_us'] = np.ndarray((1,), buffer=h309, offset=100, dtype='i')[0]
    # generate datetime of t0
    head['dt'] = datetime.fromtimestamp(head['t0_s']).replace(microsecond=head['t0_us'])
    head['site_vp'] = np.ndarray((1,), buffer=h309, offset=126, dtype='f')[0]
    head['site_vs'] = np.ndarray((1,), buffer=h309, offset=130, dtype='f')[0]
    # should be source_v not site_v - Gisela
    head['source_vp'] = np.ndarray((1,), buffer=h309, offset=126, dtype='f')[0]
    head['source_vs'] = np.ndarray((1,), buffer=h309, offset=130, dtype='f')[0]
    head['mw'] = np.ndarray((1,), buffer=h309, offset=164, dtype='f')[0]
    head['moment'] = np.ndarray((1,), buffer=h309, offset=168, dtype='f')[0]
    head['nrgval'] = np.ndarray((1,), buffer=h309, offset=172, dtype='f')[0]
    head['esep'] = np.ndarray((1,), buffer=h309, offset=176, dtype='f')[0]
    head['srcrad'] = np.ndarray((1,), buffer=h309, offset=180, dtype='f')[0]
    head['asprad'] = np.ndarray((1,), buffer=h309, offset=184, dtype='f')[0]
    head['ststdp'] = np.ndarray((1,), buffer=h309, offset=188, dtype='f')[0]
    head['appstr'] = np.ndarray((1,), buffer=h309, offset=192, dtype='f')[0]
    head['dystdp'] = np.ndarray((1,), buffer=h309, offset=196, dtype='f')[0]
    head['mxdisp'] = np.ndarray((1,), buffer=h309, offset=200, dtype='f')[0]
    head['pkvelp'] = np.ndarray((1,), buffer=h309, offset=204, dtype='f')[0]
    head['pkaccp'] = np.ndarray((1,), buffer=h309, offset=208, dtype='f')[0]
    head['textfooterlength'] = np.ndarray((1,), buffer=h309, offset=243, dtype='i')[0]

    """
    Reading in the sensor config from the header
    """
    # reading in the next bit of the file
    if s3data is None:
        hrem = f.read(wfst - 309)
    else:
        hrem = s3data[309: wfst]

    dis, sensor_name = [], []

    senh = 26 * npal
    srd = 222
    head['stype'] = np.ndarray((nsens,), buffer=hrem, offset=senh, dtype='i', strides=(srd,))
    head['nch_sen'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 4, dtype='i', strides=(srd,))
    head['pos'] = np.ndarray((nsens, 3), buffer=hrem, offset=senh + 12, dtype='f', strides=(srd, 4))
    head['snstvt'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 24, dtype='f', strides=(srd,))
    head['ttt'] = np.ndarray((nsens, 2), buffer=hrem, offset=senh + 32, dtype='f', strides=(srd, 4))
    head['rot_win'] = np.ndarray((nsens, 2), buffer=hrem, offset=senh + 40, dtype='i', strides=(srd, 4))
    eig_rot = np.ndarray((nsens, 9), buffer=hrem, offset=senh + 48, dtype='f', strides=(srd, 4))
    # making the copy to allow the array to be reshaped
    eig_rot = eig_rot.copy()
    head['eig_rot'] = eig_rot.reshape(nsens, 3, 3)
    head['eig_val'] = np.ndarray((nsens, 3), buffer=hrem, offset=senh + 84, dtype='f', strides=(srd, 4))
    head['dir_error'] = np.ndarray((nsens, 3), buffer=hrem, offset=senh + 96, dtype='f', strides=(srd, 4))
    head['sensor_id'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 108, dtype='h', strides=(srd,))
    head['station_ind'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 110, dtype='i', strides=(srd,))
    head['pre_amp'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 114, dtype='f', strides=(srd,))
    head['enabled'] = np.array(np.ndarray((nsens,), buffer=hrem, offset=senh + 118, dtype='i', strides=(srd,)),
                               dtype=bool)
    # TODO incomplete data is accurate, not sure about bad sync and enabled though
    head['bad_sync'] = np.array(np.ndarray((nsens,), buffer=hrem, offset=senh + 134, dtype='i', strides=(srd,)),
                                dtype=bool)
    head['incomplete_data'] = np.array(np.ndarray((nsens,), buffer=hrem, offset=senh + 144, dtype='i', strides=(srd,)),
                                       dtype=bool)
    head['raydir'] = np.ndarray((nsens, 3), buffer=hrem, offset=senh + 154, dtype='f', strides=(srd, 4))
    head['sv_ttt'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 166, dtype='f', strides=(srd,))
    # load sensor model
    head['senmodel'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 170, dtype='h', strides=(srd,))
    # saving what might be the snr values from hsf
    head['p_snr'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 172, dtype='f', strides=(srd,))
    head['s_snr'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 176, dtype='f', strides=(srd,))
    # saving the Q value (attenuation?) and velocity at site
    head['qp'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 186, dtype='f', strides=(srd,))
    head['qs'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 190, dtype='f', strides=(srd,))
    # qs and qsv are same byte locations. if qsh does not exist then it is before the two were saved separately
    head['qsv'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 190, dtype='f', strides=(srd,))
    head['qsh'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 194, dtype='f', strides=(srd,))
    head['vp'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 199, dtype='f', strides=(srd,))
    head['vs'] = np.ndarray((nsens,), buffer=hrem, offset=senh + 203, dtype='f', strides=(srd,))

    # pulling out the volt range
    volt_range = np.ndarray((nsens,), buffer=hrem, offset=senh + 207, dtype='f', strides=(srd,))
    # have to copy it to allow it to be writeable
    volt_range = volt_range.copy()
    # correcting for old files which may have anomalous values above 6 volts
    ix = np.where(np.logical_or(volt_range == 0, volt_range > 6))[0]
    volt_range[ix] = 4.096

    # pulling out parameters that are a little trickier
    for isen in range(nsens):
        dis.append(np.math.sqrt((head['pos'][isen][0] - head['source'][0]) ** 2 +
                                (head['pos'][isen][1] - head['source'][1]) ** 2 + (
                head['pos'][isen][2] - head['source'][2]) ** 2))

        sensor_name.append(str(hrem[senh + 122:senh + 134]).split('\\x00')[0])
        # 10 bits left in dummy as buffer at the end
        senh = senh + srd

    head['Distance'] = dis
    head['sensor_name'] = sensor_name
    head['volt_range'] = volt_range

    # performing a quick check to see if any of the sensors are accelerometers and printing a warning if they are
    possible_types = ['GEOPHONE', 'ACCELEROMETER', 'SGM_GEOPHONE', 'FBA_ACCELEROMETER', 'BVM_MICROPHONE']
    for count in range(len(head['stype'])):
        actual_type = possible_types[head['stype'][count]]
        if (actual_type == 'ACCELEROMETER' or actual_type == 'FBA_ACCELEROMETER') and print_out is True and \
                from_hsf_to_obspy is True:
            print('BEWARE you will need to adjust the data for accelerometers by multiplying by 9.81\n'
                  'Using hsf_to_obspy will automatically do this for you though.')
            break

    """
    Reading in the channel config from the header
    """

    descr, sen_rot = [], []
    valid_flag_pickused, valid_flag_newpolarity, valid_flag_sensorhealthknown = [], [], []
    valid_flag_sensorhealth, valid_flag_sensorhealthcheck, valid_flag_sensorusedintriggering = [], [], []
    valid_flag_channelbad = []

    # replacing what I can with the new approach
    nch_sen = head['nch_sen']
    srd = 158
    nchans = np.sum(nch_sen)
    head['ch_enabled'] = np.ndarray((nchans,), buffer=hrem, offset=senh + 4, dtype='i', strides=(srd,))
    head['gain'] = np.ndarray((nchans,), buffer=hrem, offset=senh + 8, dtype='f', strides=(srd,))
    head['low_f'] = np.ndarray((nchans,), buffer=hrem, offset=senh + 24, dtype='f', strides=(srd,))
    head['high_f'] = np.ndarray((nchans,), buffer=hrem, offset=senh + 28, dtype='f', strides=(srd,))
    head['rms_amp'] = np.ndarray((nchans,), buffer=hrem, offset=senh + 44, dtype='f', strides=(srd,))
    head['peak_amp'] = np.ndarray((nchans,), buffer=hrem, offset=senh + 48, dtype='f', strides=(srd,))
    head['p_pol_old'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 52, dtype='h', strides=(srd,)),
                                     nch_sen)
    head['sv_pol_old'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 54, dtype='h', strides=(srd,)),
                                      nch_sen, keep_ind=1)
    head['sh_pol_old'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 54, dtype='h', strides=(srd,)),
                                      nch_sen, keep_ind=-1)
    head['parr'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 58, dtype='f', strides=(srd,)),
                                nch_sen)
    head['sarr'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 62, dtype='f', strides=(srd,)),
                                nch_sen)
    head['varr'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 62, dtype='f', strides=(srd,)),
                                nch_sen, keep_ind=1)
    head['harr'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 62, dtype='f', strides=(srd,)),
                                nch_sen, keep_ind=-1)
    head['ch_snstvt'] = np.ndarray((nchans,), buffer=hrem, offset=senh + 66, dtype='f', strides=(srd,))
    # descr is pulled from here
    head['acq_chan_ind'] = np.ndarray((nchans,), buffer=hrem, offset=senh + 87, dtype='h', strides=(srd,))
    head['ppick_used'] = np.ndarray((nchans,), buffer=hrem, offset=senh + 89, dtype='h', strides=(srd,))
    head['spick_used'] = np.ndarray((nchans,), buffer=hrem, offset=senh + 91, dtype='h', strides=(srd,))
    p_pol = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 94, dtype='h', strides=(srd,)), nch_sen)
    p_pol = p_pol.copy()
    head['p_pol'] = np.divide(p_pol, 32767)
    sv_pol = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 96, dtype='h', strides=(srd,)), nch_sen,
                          keep_ind=1)
    sv_pol = sv_pol.copy()
    head['sv_pol'] = np.divide(sv_pol, 32767)
    sh_pol = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 96, dtype='h', strides=(srd,)), nch_sen,
                          keep_ind=-1)
    sh_pol = sh_pol.copy()
    head['sh_pol'] = np.divide(sh_pol, 32767)
    head['omega_p'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 98, dtype='f', strides=(srd,)),
                                   nch_sen)
    head['omega_s'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 102, dtype='f', strides=(srd,)),
                                   nch_sen)
    head['corner_p'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 106, dtype='f', strides=(srd,)),
                                    nch_sen)
    head['corner_s'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 110, dtype='f', strides=(srd,)),
                                    nch_sen)
    head['energy_p'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 114, dtype='f', strides=(srd,)),
                                    nch_sen)
    head['energy_s'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 118, dtype='f', strides=(srd,)),
                                    nch_sen)
    head['omega_sv'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 102, dtype='f', strides=(srd,)),
                                    nch_sen, keep_ind=1)
    head['corner_sv'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 110, dtype='f', strides=(srd,)),
                                     nch_sen, keep_ind=1)
    head['energy_sv'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 118, dtype='f', strides=(srd,)),
                                     nch_sen, keep_ind=1)
    head['omega_sh'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 102, dtype='f', strides=(srd,)),
                                    nch_sen, keep_ind=-1)
    head['corner_sh'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 110, dtype='f', strides=(srd,)),
                                     nch_sen, keep_ind=-1)
    head['energy_sh'] = simp_to_chan(np.ndarray((nchans,), buffer=hrem, offset=senh + 118, dtype='f', strides=(srd,)),
                                     nch_sen, keep_ind=-1)

    # the loop originally in the function
    for isen in range(nsens):
        ori = []

        if nch_sen[isen] == 3:
            for ich in range(3):
                # pulling out the valid flags
                temp = hrem[senh + 93:senh + 94]
                vf_pickused, vf_polarity, vf_shk, vf_sh, vf_shc, vf_strig, vf_bad = extract_valid_flags(temp)
                valid_flag_pickused.append(vf_pickused)
                valid_flag_newpolarity.append(vf_polarity)
                valid_flag_sensorhealthknown.append(vf_shk)
                valid_flag_sensorhealth.append(vf_sh)
                valid_flag_sensorhealthcheck.append(vf_shc)
                valid_flag_sensorusedintriggering.append(vf_strig)
                valid_flag_channelbad.append(vf_bad)

                # and the other values
                ori.append(np.array(struct.unpack('3f', hrem[senh + 12:senh + 24])))
                descr.append(hrem[senh + 70:senh + 87].decode('ISO-8859-1').rstrip("\x00"))  # 17 char
                senh = senh + srd
        elif nch_sen[isen] == 1:
            ori.append(np.array(struct.unpack('3f', hrem[senh + 12:senh + 24])))
            descr.append(hrem[senh + 70:senh + 87].decode('ISO-8859-1').rstrip("\x00"))

            # pulling out the valid flags
            temp = hrem[senh + 93:senh + 94]
            vf_pickused, vf_polarity, vf_shk, vf_sh, vf_shc, vf_strig, vf_bad = extract_valid_flags(temp)
            valid_flag_pickused.append(vf_pickused)
            valid_flag_newpolarity.append(vf_polarity)
            valid_flag_sensorhealthknown.append(vf_shk)
            valid_flag_sensorhealth.append(vf_sh)
            valid_flag_sensorhealthcheck.append(vf_shc)
            valid_flag_sensorusedintriggering.append(vf_strig)
            valid_flag_channelbad.append(vf_bad)

            senh = senh + srd
        sen_rot.append(np.array(ori))

    head['valid_flag_pickused'] = np.array(valid_flag_pickused)
    head['valid_flag_newpolarity'] = np.array(valid_flag_newpolarity)
    head['valid_flag_sensorhealth'] = np.array(valid_flag_sensorhealth)
    head['valid_flag_sensorhealthknown'] = np.array(valid_flag_sensorhealthknown)
    head['valid_flag_sensorhealthcheck'] = np.array(valid_flag_sensorhealthcheck)
    head['valid_flag_sensorusedintriggering'] = np.array(valid_flag_sensorusedintriggering)
    head['valid_flag_channelbad'] = np.array(valid_flag_channelbad)
    head['sen_rot'] = sen_rot
    head['ch_descr'] = descr

    """
    If we want the footer
    """

    # If we want to read the header only then we are done. close the file and return the header
    if head_only:
        # catching case where we are using s3data rather than a hsf file
        if f is not None:
            f.close()

        # returning the header of the file
        return head

    elif footer:
        # determine offset to start of footer
        if head['compress'] != 0 or head['resample'] != 0:
            # compressed or resampled -- waveform block size is given by compressed size
            offset = head['data_offs'] + head['compresssize']
        else:  # not compressed
            offset = head['data_offs'] + (head['npts'] + head['ntr']) * 4

        # all footer
        # catching case where we are using s3data rather than a direct hsf file
        if f is not None:
            f.seek(offset)
            n = f.read()
        else:
            n = s3data[offset:]

        # decode binary to string
        # end of textfooter head['textfooterlength']
        allfooter = n
        allfooter_str = allfooter.decode('cp437')

        # skip to footer
        # f.seek(offset)

        # read footer
        foot = {}

        nsize = struct.unpack('I', n[-4:])[0]  # size of blob block

        # deal with proc reports
        footerblobdirectory = n[len(n) - nsize - 4:len(n) - 4]
        directories = str(footerblobdirectory).split('\\n')[1:]

        for d in directories:
            if '=' in d:
                report, index = d.split('=')
                index = np.int(index)
                length = struct.unpack('I', n[index - offset + len(report) +
                                              2 + 1:index - offset + len(report) + 2 + 4 + 1])[0]
                data = n[index - offset + len(report) + 2 + 4 + 1:index - offset + len(report) + 2 + 4 + 1 + length]
                # parse report into dictionary
                try:
                    buf = StringIO(data.decode())
                    cfg = configparser.ConfigParser()
                    cfg.read_file(buf)
                    # noinspection PyProtectedMember
                    data_dict = dict(cfg._sections)
                    foot[report] = data_dict
                except configparser.ParsingError:
                    print('Footer Parsing Error with ' + report)

        # catching case where we are using s3 data rather than a hsf file
        if f is not None:
            f.close()

        # find event history
        historystart = allfooter_str.find('<<SEVHistory:') + 15
        historyend = allfooter_str.find('>>', historystart)

        evthistory = allfooter_str[historystart:historyend]
        evthistory_header = ['ModTime', 'UserName', 'Program', 'Type', 'Action']
        evthistory = pd.read_csv(StringIO(evthistory.replace('####', '\n').replace('##', ',').replace('|', ',')),
                                 header=None, names=evthistory_header)

        # getting the valid start and end times
        try:
            validstart = allfooter_str.find('<<ValidStart:') + len('<<ValidStart:')
            validend = allfooter_str.find('>>', validstart)
            lastvalidstart = allfooter_str.find('<<LastValid:') + len('<<LastValid:')
            lastvalidend = allfooter_str.find('>>', lastvalidstart)
            foot['ValidStart'] = float(allfooter_str[validstart:validend])
            foot['ValidEnd'] = float(allfooter_str[lastvalidstart:lastvalidend])
        except ValueError:
            foot['ValidStart'] = None
            foot['ValidEnd'] = None

        # saving information to the footer
        foot['evthistory'] = evthistory
        foot['allfooter'] = allfooter

        # returning the header and the footer of the file
        return head, foot

    else:  # If we want to also read the waveform data then continue
        """
        If we want the waveform data as well
        """
        hsf_compress_exists = True
        hsfcompressor = r"C:\esg\hsfcompressor.exe"  # location of the hsf compressor program

        if os.name != "nt" or s3data is not None or force_python_decompress is True:
            # if we are on the jupyter server
            # also if we are using s3data
            # adjusting the path of the hsf compressor call
            # hsfcompressor = '/home/share/wine/wine-6.0/wine /home/share/wine/HSFCompressor.exe'
            hsf_compress_exists = False

        # making sure the file is closed
        # catching case where we are using s3 data rather than hsf file
        if f is not None:
            f.close()

        data_array = None
        # if compressed check the platform and extract the data using hsf compressor
        if head['compress'] != 0:
            # make sure the hsf compressor exists
            if not glob.os.path.exists(hsfcompressor) and os.name == 'nt':
                hsf_compress_exists = False
                if print_out:
                    print("HSF file is compressed or resampled and HSFCompressor is missing. "
                          "Install Hsfcompress.exe to c:\\esg_utils")
                    print('Instead using the in-Python approach, which is significantly slower')
            elif os.name != 'nt' and not glob.os.path.exists('/home/share/wine/HSFCompressor.exe'):
                hsf_compress_exists = False
                if print_out:
                    print("HSF file is compressed or resampled and HSFCompressor is missing on linux. "
                          "Install Hsfcompress.exe to /home/share/wine")
                    print('Instead using the in-Python approach, which is significantly slower')

            # running hsf compressor if it is present
            if hsf_compress_exists:
                # running the hsf compressor to extract the data
                # data is directly piped into Python
                p = Popen(hsfcompressor + ' -none -stdout ' + file, stdout=PIPE, stderr=PIPE, shell=True)
                hbin = ''
                err = ''
                try:
                    hbin, err = p.communicate()
                except IOError:
                    print('IOError: ' + str(IOError))
                if hbin == '':
                    print('Output returned is blank.' + err)

                # removing the header information
                hbin = hbin[wfst:]
            else:
                if s3data is None:
                    # opening and reading the file
                    f = open(file, 'rb')

                    # removing the header information
                    f.seek(wfst)

                    # reading in the data and closing the file object
                    hbin = f.read()
                    f.close()
                else:
                    hbin = s3data[wfst:]

                # checking if the file is waveless
                if head['compress'] == -1:
                    warnings.warn('File is waveless, so extracting from original')
                    # if it is waveless, then we will need to read the data from the other file
                    # getting the file name
                    thbin = hbin.decode('cp437')
                    tfname = makeLinuxPath(thbin.split('.hsf')[0] + '.hsf')

                    # reading the data
                    # TODO risk of recursion here?
                    ttm, data_array, thead = read_hsf_exp(tfname, head_only=head_only, footer=footer,
                                                          groundmotion=groundmotion,
                                                          print_out=print_out, from_hsf_to_obspy=from_hsf_to_obspy,
                                                          s3data=s3data,
                                                          force_python_decompress=force_python_decompress)
                else:
                    # extracting the decompressed data
                    data_array = decompress_hsf_python(hbin, head['compresssize'], nch, npt, invalid_value=16843009)

        # else if the hsf file is not compressed, we can read the data directly
        else:
            if s3data is None:
                # opening and reading the file
                f = open(file, 'rb')

                # removing the header information
                f.seek(wfst)

                # reading in the data and closing the file object
                hbin = f.read()
                f.close()
            else:
                hbin = s3data[wfst:]

        # how many data points we expect
        num_elements = nch * npt

        # this is for cases where I was having issues with files that did not have the correct amount of buffer for the
        # given data size - not sure on the cause of this error but for now including this workaround
        # IF YOU FIND an example file that is triggering this issue, then please drop me an email at
        # joshua.williams@esgsolutions.com or drop me a line on teams.
        if data_array is None:
            try:
                data_array = np.ndarray((num_elements,), buffer=hbin, offset=0, dtype='i').copy()
            except:
                print('Something went wrong with the data structure')
                return None, None, None

        # setting bad data values to 0
        ibd = np.where(data_array == 16843009)  # find bad data values
        if len(data_array.shape) == 1:
            ibd = ibd[0]
        if len(ibd) > 0:
            data_array[ibd] = 0
            if print_out is True:
                warnings.warn('Bad data reset to 0')

        # housekeeping to reformat the data - only doing this if hsf compressor has been run
        if hsf_compress_exists:
            data_array = np.reshape(data_array, (npt, nch))
            data_array = np.transpose(data_array)
            data_array = np.array(data_array, dtype=np.float)

        # initialising some counter values
        count = 0
        stcount = 1

        """
        Converting the amplitudes if necessary
        """

        # for each trace
        # iterate in case gains and sensitivity change between sensors
        for i in range(0, len(data_array)):
            # need to pick the sensitivity
            # iterating through count variable to make sure the snstvt and volt_range is correct

            # skip the first iteration because i-1 will cause an error
            # if the station description has changed and we have gone over the number of channels on the
            # sensor, then we must be onto a new station
            if i != 0 and head['ch_descr'][i] != head['ch_descr'][i - 1] and stcount > head['nch_sen'][count]:
                count += 1
                stcount = 1

            # correcting for gain and sensitivity is ground motion is True
            # otherwise just outputting the raw data
            if groundmotion is True:
                div_value = head['gain'][i] * head['snstvt'][count]
            else:
                div_value = 1.

            # outputs the data in acceleration for accelerometers and velocity for geophones
            # acceleration might be in g though as opposed to m/s/s
            data_array[i] = (data_array[i] / div_value / (
                    2 ** (head['nbit'] - 1) / head['volt_range'][count]))

            # iterating the variable to count through the number of traces in the station
            stcount += 1

        return tm, data_array, head


# small function to simplify down the results
def simp_to_chan(vals, num_chans_psen, keep_ind=0):
    """
    Simplify array down to a per sensor value rather than per channel
    :param vals: array of vals to simplify
    :param num_chans_psen: number of channels for each sensor
    :param keep_ind: which index to keep, defaults to 0
    :return:
    """
    nvals = []
    scount = 0
    for ij in range(len(num_chans_psen)):
        tvals = vals[scount: scount + num_chans_psen[ij]]
        if len(tvals) > keep_ind:
            nvals.append(tvals[keep_ind])
        else:
            nvals.append(tvals[0])
        scount += num_chans_psen[ij]

    return np.array(nvals)


def extract_valid_flags(byte):
    """
    Extracting the valid flags from the byte parsed from the hsf
    :param byte: the byte that we are going to parse
    :return:
    """
    # getting each bit
    byte = ord(byte)
    byte = bin(byte)[2:].rjust(8, '0')
    # was the arrival time used in location
    if byte[-1] == '1':
        valid_flag_pickused = True
    else:
        valid_flag_pickused = False
    # true if new polarities are valid
    if byte[-2] == '1':
        valid_flag_newpolarity = True
    else:
        valid_flag_newpolarity = False
    if byte[-3] == '1':
        valid_flag_sensorhealthknown = True
    else:
        valid_flag_sensorhealthknown = False
    # true if sensor healthy, false if unhealthy
    if byte[-4] == '1':
        valid_flag_sensorhealth = True
    else:
        valid_flag_sensorhealth = False
    # true if health check was done
    if byte[-5] == '1':
        valid_flag_sensorhealthcheck = True
    else:
        valid_flag_sensorhealthcheck = False
    # true if used in triggering
    if byte[-6] == '1':
        valid_flag_sensorusedintriggering = True
    else:
        valid_flag_sensorusedintriggering = False
    # true if channel is bad and disabled
    if byte[-7] == '1':
        valid_flag_channelbad = True
    else:
        valid_flag_channelbad = False

    return valid_flag_pickused, valid_flag_newpolarity, valid_flag_sensorhealthknown, valid_flag_sensorhealth, \
        valid_flag_sensorhealthcheck, valid_flag_sensorusedintriggering, valid_flag_channelbad


def readdsf(filepath):
    """
        Read in Statsvis DSF files.

        There will be a different DSF file for each day.

        Usage: readdsf(filepath)

        Output: header, dictionary which includes DataFrame for each parameter

        Parameters typically include Noise Floor, RMS Amplitude, etc..

    """

    badstatsval = 1e10  # value for null data

    f = open(filepath, 'rb')

    head = {}  # blank dictionary for the data
    # stats_param = {}
    # stats_chan = {}

    # statsheader
    statsheader = f.read(64)

    head['ver'] = struct.unpack('<l', statsheader[0:4])[0]
    # Year, Month, Day of DSF file
    head['year'] = struct.unpack('<l', statsheader[4:8])[0]
    head['month'] = struct.unpack('<l', statsheader[8:12])[0]
    head['day'] = struct.unpack('<l', statsheader[12:16])[0]
    head['num_chan'] = struct.unpack('<l', statsheader[16:20])[0]
    # length of frame in seconds
    head['frame_length'] = struct.unpack('<l', statsheader[20:24])[0]
    # number of parameters for each channel
    head['num_param'] = struct.unpack('<l', statsheader[24:28])[0]
    # offset to the empty space in stats file, or size of file if file finished
    head['curr_offs'] = struct.unpack('<l', statsheader[28:32])[0]
    # if > 0, file combined from acq groups in HNAS
    head['num_groups'] = struct.unpack('<l', statsheader[32:36])[0]
    # dsf flags
    head['dsf_flags'] = struct.unpack('<l', statsheader[36:40])[0]

    # Read in rest of the header
    head_stats_param = f.read(head['num_param'] * 128)
    head_stats_chan = f.read(head['num_chan'] * 128)

    paraminfo, paramunits = [], []
    instdesc, typesen, units, ned, orient, group_ind, group_off = [], [], [], [], [], [], []

    # loop over stats_param
    for i in range(head['num_param']):
        # Parameter description
        paraminfo.append(head_stats_param[i * 128:i * 128 + 64].decode('windows-1252').rstrip("\x00"))
        # Parameter units
        paramunits.append(head_stats_param[i * 128 + 64:i * 128 + 80].decode('windows-1252').rstrip("\x00"))
        # windows-1252 decoding seems to be required for accelerometers that have units of m/s2

    # Loop over stats_chan
    for i in range(head['num_chan']):
        # instrument description
        instdesc.append(head_stats_chan[i * 128:128 + i * 128 + 64].decode(errors="replace").split('\x00')[0])
        # type of instrument
        typesen.append(head_stats_chan[i * 128 + 64:128 + i * 128 + 80].decode(errors="replace").split('\x00')[0])
        # units
        units.append(str(head_stats_chan[i * 128 + 80:128 + i * 128 + 96]).split('\\x00')[0])
        # NED
        ned.append(struct.unpack('3f', head_stats_chan[i * 128 + 96:i * 128 + 108]))
        # Orient
        orient.append(struct.unpack('3f', head_stats_chan[i * 128 + 108:i * 128 + 120]))
        # group_ind
        group_ind.append(struct.unpack('i', head_stats_chan[i * 128 + 120:i * 128 + 124])[0])
        # group_offs
        group_off.append(struct.unpack('i', head_stats_chan[i * 128 + 124:i * 128 + 128])[0])

    # Add stats_chan info to the header
    head['instdesc'] = instdesc
    head['typesen'] = typesen
    head['units'] = units
    head['ned'] = ned
    head['orient'] = orient
    head['group_ind'] = group_ind
    head['group_off'] = group_off

    restofdata = f.read()
    f.close()

    # calculate the number of data points to read in
    npts = head['num_param'] * head['num_chan'] * 86400 / head['frame_length']
    npts = int(npts)
    data = struct.unpack(str(npts) + 'f', restofdata[0:npts * 4])
    data = pd.Series(data)

    # build list of datetimes to make an index
    t0 = datetime(head['year'], head['month'], head['day'])
    daterange = pd.date_range(t0, t0.replace(hour=23, minute=59, second=55), freq=str(head['frame_length']) + 's')

    pts_in_a_day = int(86400 / head['frame_length'])
    pts_range = np.arange(0, pts_in_a_day)
    chan_range = np.arange(0, head['num_chan'])
    param_range = np.arange(0, head['num_param'])

    dataframes = {}
    for param in param_range:
        # start with a blank zeros dataframe
        df = np.zeros((pts_in_a_day, head['num_chan'], head['num_param']))
        # index = []
        # load in each channel
        for ch in chan_range:
            index = pts_range * head['num_chan'] * head['num_param'] + ch * head['num_param'] + param
            df[:, ch, param] = data[index]

        dataframes[paraminfo[param]] = pd.DataFrame(df[:, :, param], index=daterange)
        # Check for invalid values and set them to nan
        dataframes[paraminfo[param]].replace(badstatsval, np.nan, inplace=True)

    return head, dataframes


def load_dsf_list(dsffile_list, debug=False, downsample=None):
    """
    Function to load and combine the dataframes from multiple DSF files

    Only a single header is returned currently

    :param dsffile_list: list of dsf file paths
    :param debug: boolean to be verbose and list files loaded
    :param downsample: # TODO needs documentation
    :return: header dictionary and dictionary of combined dataframes
    """
    # head_all = []
    dfs_all = []
    head = None
    for filepath in dsffile_list:
        if debug:
            print("Loading " + filepath)

        head, dfs = readdsf(filepath)

        if downsample is not None:
            for df_name in dfs.keys():
                dfs[df_name] = dfs[df_name][dfs[df_name] > 0].resample(downsample).min()

        # head_all.append(head)
        dfs_all.append(dfs)

    df_dict = {}

    for key in dfs_all[0].keys():
        try:
            dfs = [df[key] for df in dfs_all]
            df_dict[key] = pd.concat(dfs)
        except KeyError:
            print("A DSF is missing the key " + key + " so skipping this key")
            pass

    return head, df_dict


def compile_dsf_path(rootpath, date, dsftype="Stats", debug=False):
    """
    Function to compile a specific DSF file path and return 1 if failure
    :param rootpath: dsn root path
    :param date:  date of file
    :param dsftype: denote type of dsf file - Stats, Diagnostic or Instrumentation
    :param debug: verbose debugging explanation
    :return:
    """

    # filename appendix
    if dsftype == "Stats":
        suffix = ""
    elif dsftype == "Diagnostics":
        suffix = "_Diag"
    elif dsftype == "Instrumentation":
        suffix = "_Instr"
    else:
        raise Exception("Invalid type of DSF file.")

    if os.name == 'nt':  # WINDOWS
        slash = '\\'
    elif os.name == 'posix':  # LINUX
        slash = '/'
    else:
        raise Exception("No platform found ")

    # if ends with a slash, remove the slash
    if rootpath[-1] == slash:
        rootpath = rootpath[0:-1]
    # extract dsn from rootpath
    dsn = rootpath.split(slash)[-1]

    # dsffile_list = []

    # build path
    filename = os.path.join(rootpath, str(date.year))
    filename = os.path.join(filename, str(date.month).zfill(2))
    filename = os.path.join(filename, str(date.day).zfill(2))
    filename = os.path.join(filename,
                            dsn + suffix +
                            str(date.year).zfill(2) +
                            str(date.month).zfill(2) +
                            str(date.day).zfill(2) + ".dsf")
    if debug:
        print("Looking for DSF file: " + filename)

    if os.path.exists(filename):
        if debug:
            print("DSF file found: " + filename)
        return filename
    else:
        if debug:
            print("DSF file not found: " + filename)
        return 1


def compile_dsf_paths(rootpath, start=None, end=None, dsftype="Stats", debug=False):
    """
    Function to compile list of dsf files within a DSN rootpath.

    Example Usage:
    dsf_files = WaveformData.compile_dsf_paths("\\\\esg_utils.net\\datashare\\Frac3\\EOG_Telluride",debug=True)

    :param rootpath: dsn root path
    :param start: start date of search (inclusive)
    :param end: end date of search (inclusive)
    :param dsftype: denote type of dsf file - Stats, Diagnostic or Instrumentation
    :param debug: verbose debugging explanation
    :return:
    """

    if start is None:
        mindate = pd.datetime(1979, 1, 1)
    else:
        mindate = start

    if end is None:
        maxdate = pd.datetime.now()+pd.Timedelta("1 day")
    else:
        maxdate = end

    # filename appendix
    if dsftype == "Stats":
        suffix = ""
    elif dsftype == "Diagnostics":
        suffix = "_Diag"
    elif dsftype == "Instrumentation":
        suffix = "_Instr"
    else:
        raise Exception("Invalid type of DSF file.")

    if os.name == 'nt':  # WINDOWS
        slash = '\\'
    elif os.name == 'posix':  # LINUX
        slash = '/'
    else:
        raise Exception("No platform found ")

    # if ends with a slash, remove the slash
    if rootpath[-1] == slash:
        rootpath = rootpath[0:-1]
    # extract dsn from rootpath
    dsn = rootpath.split(slash)[-1]

    dsffile_list = []

    # get all folders in rootpath
    year_list = [name for name in os.listdir(rootpath) if np.logical_and(os.path.isdir(os.path.join(rootpath, name)),
                                                                         name.isdigit())]

    for year in year_list:
        year_path = rootpath + slash + year
        month_list = [name for name in os.listdir(year_path) if np.logical_and(os.path.isdir(os.path.join(year_path,
                                                                                                          name)),
                                                                               name.isdigit())]

        for month in month_list:
            month_path = year_path + slash + month
            day_list = [name for name in os.listdir(month_path) if np.logical_and(os.path.isdir(os.path.join(month_path,
                                                                                                             name)),
                                                                                  name.isdigit())]

            for day in day_list:
                # ymd_path = rootpath + slash + year + slash + month + slash + day
                folder_dt = datetime(int(year), int(month), int(day))

                if np.logical_and(folder_dt >= mindate, folder_dt <= maxdate):
                    # get all dsf files within day folder
                    day_path = month_path + slash + day

                    filename = day_path + slash + dsn + suffix + year + month + day + ".dsf"
                    if os.path.exists(filename):
                        if debug:
                            print("DSF file found: " + filename)

                        dsffile_list.append(filename)

                    else:
                        if debug:
                            print("DSF file not found: " + filename)

    return dsffile_list


def read_sen(file_path):
    """
    Function to read in a sensor file

    It may not work well on older sensor file versions.

    :param file_path:
    :return sensor_file dictionary
    """

    f = open(file_path)
    ver = float(f.readline().split()[0][1:])
    f.close()

    import numpy.lib.recfunctions

    sensorfile = None
    if ver <= 2.0:
        headers = (
                   'Description', 'Northing', 'Easting', 'Depth', 'S', 'Type', 'Cmp', 'ID', 'Gain', 'Sensitivity',
                   'Vmax', 'LowFreq', 'HighFreq', 'CosineN', 'CosineE', 'CosineD', 'Se', 'Zone')
        formats = ('a10', 'f8', 'f8', 'f2', 'i', 'a2', 'i', 'i', 'f2', 'f2', 'f2', 'f2', 'f2', 'f2', 'f2', 'f2',
                   'i', 'i')
        sensorfile = numpy.loadtxt(file_path, skiprows=9, dtype={'names': headers, 'formats': formats})

    if ver == 2.1:
        headers = (
                   'Description', 'Northing', 'Easting', 'Depth', 'S', 'Type', 'Mod', 'Cmp', 'ID', 'Gain',
                   'Sensitivity', 'AmpCor', 'Vmax', 'LowFreq', 'HighFreq', 'CosineN', 'CosineE', 'CosineD', 'Se',
                   'Zone')
        formats = (
                   'a17', 'f8', 'f8', 'f2', 'i', 'a2', 'i', 'i', 'i', 'f2', 'f2', 'f2', 'f2', 'f2', 'f2', 'f2',
                   'f2', 'f2', 'i', 'i')

        sensorfile = numpy.loadtxt(file_path, skiprows=9, dtype={'names': headers, 'formats': formats})
    if ver == 3.0:
        headers = (
                   'Description', 'Northing', 'Easting', 'Depth', 'S', 'Type', 'Mod', 'Cmp', 'ID', 'Gain',
                   'Sensitivity', 'AmpCor', 'Vmax', 'LowFreq', 'HighFreq', 'CosineN', 'CosineE', 'CosineD', 'Se',
                   'Zone', 'MDepth', 'LegacyNames')
        formats = (
                   'a17', 'f8', 'f8', 'f2', 'i', 'a2', 'i', 'i', 'i', 'f2', 'f2', 'f2', 'f2', 'f2', 'f2', 'f2', 'f2',
                   'f2', 'i', 'i', 'f2', 'a12')

        i = 0
        skip = None
        colsrow = None
        datarow = None
        nbits_row = None
        for line in open(file_path, 'r'):
            i = i + 1
            if line[0:3] == '//.':  # identify last row before the data begins
                skip = i
            if line[0:4] == '~COL':  # identify start of column description section
                colsrow = i
            if line[0:5] == '~DATA':  # identify row before table headers
                datarow = i
            if line[:4] == 'BITS':
                nbits_row = line

        # error catching
        if skip is None:
            raise ValueError('Could not identify last row before data begins.')
        if colsrow is None:
            raise ValueError('Could not identify start of column description section.')
        if datarow is None:
            raise ValueError('Could not identify row before table headers.')

        # getting the NBITS out of the initial header
        nbits = int(nbits_row.split('=')[-1])

        # reading in the data
        col_df = pd.read_csv(file_path, sep=':', skiprows=colsrow, nrows=datarow - colsrow - 1,
                             names=('Name', 'Description'))
        col_df['Name'] = col_df['Name'].map(str.strip)

        # read in sensor file table section
        sensorfile = pd.read_csv(file_path, header=None, sep=r'\s+', quotechar='"', skiprows=skip)

        if len(sensorfile.columns) == len(col_df.Name):
            sensorfile.columns = col_df.Name
        else:
            Exception("Wrong number of columns somehow")

        # keep some old column names for legacy reasons...
        sensorfile['CosineN'] = sensorfile.U
        sensorfile['CosineE'] = sensorfile.V
        sensorfile['CosineD'] = sensorfile.W

        # Calculate azimuth and dip
        azim = np.arctan2(sensorfile['CosineE'].astype('float64'),
                          sensorfile['CosineN'].astype('float64')) * 180 / np.pi
        dip = np.arcsin(sensorfile['CosineD'].astype('float64') / np.sqrt(
            sensorfile['CosineN'].astype('float64') ** 2 + sensorfile['CosineE'].astype('float64') ** 2 + sensorfile[
                'CosineD'].astype('float64') ** 2)) * 180.0 / np.pi

        for i in range(0, len(azim)):
            if azim[i] < 0:
                azim[i] = azim[i] + 360
            if azim[i] >= 360:
                azim[i] = azim[i] - 360

        if ver != 3.0:
            sensorfile = numpy.lib.recfunctions.append_fields(sensorfile, ('Azimuth', 'Dip'), (azim, dip),
                                                              usemask=False)
        else:
            sensorfile['Azimuth'], sensorfile['Dip'] = azim, dip

        # computing the correction to ground motion
        # WE ARE ASSUMING HERE THAT NBIT == 2
        sensorfile['DIV_TO_GET_GM'] = (sensorfile['GAIN'] * sensorfile['SENSITIVITY']) / (
                2 ** (nbits - 1) / sensorfile['VOLTAGE_RANGE'])

    if sensorfile is None:
        raise ValueError('Something went wrong when trying to read the sensor file.')

    return sensorfile


def waveform_vel_shift(vel, sens, data_to_shift, norm_method, sensornames_by_ch, head, plot=True, downgoing=True):
    """
        Function to shift sensors by an apparent velocity

        vel - velocity to shift
        sens - enabled sensors
        data_to_plot - STA/LTA data set
        norm_method - how to normalize data
        sensornames - name of all sensors
        plot - produce plots
        downgoing - direction to shift

    """

    # each sensor is 100 ft apart
    spacing = 100
    # Calculate shift of STALTA data
    data_shift = data_to_shift.copy()
    stack = []

    tracelen = len(data_shift[0, :])

    # Sensor spacing by channel
    spacing_by_ch = np.hstack([np.ones(3) * i * 100 for i in range(0, int(len(data_to_shift) / 3.0))])

    # Loop over every channel
    for i in range(0, len(data_shift)):
        # s to ms, 4 data points per millisecond, sensor times spacing divided by velocity
        nstart = int(1000 * 4 * (spacing_by_ch[i] / vel))

        # if enabled sensor
        if sensornames_by_ch[i] in sens:
            if downgoing:
                ch_shift_result = np.append(data_shift[i, nstart:], np.zeros(nstart))
            else:  # upgoing
                nend = tracelen - nstart
                ch_shift_result = np.append(np.zeros(nstart), data_shift[i, 0:nend])

            if nstart > len(data_shift[i, :]):
                # trying to shift more than the whole trace so lets zero it out
                ch_shift_result = np.ones(len(data_shift[i, :]))

            data_shift[i, :] = ch_shift_result
            stack.append(ch_shift_result)
        else:  # if disabled sensor zero out
            ch_shift_result = np.zeros(len(data_shift[0]))
            data_shift[i, :] = ch_shift_result
            stack.append(ch_shift_result)

    # plot sensors
    if plot:
        plot_sensors(data_shift, head)

    norm_stack = None
    if norm_method == 'Current normalization - norm by sum of max amplitude of traces':
        # figure out normalized stack score
        norm = np.sum(np.max(stack, axis=1), axis=0)
        norm_stack = np.sum(stack / norm, axis=0)
    if norm_method == 'Norm by median amplitude':
        # figure out normalized stack score
        norm = np.median(stack)
        norm_stack = np.sum(stack / norm, axis=0)
    elif norm_method == 'None - amplitude stack':
        norm_stack = np.sum(stack, axis=0)
    elif norm_method == "Norm by number of channels enabled":
        norm_stack = np.sum(stack, axis=0) / (len(sens) * 3)

    # error catching
    if norm_stack is None:
        raise ValueError('Something went wrong with the normalisation - possibly the norm method wasnt recognised')

    if plot:
        fig, ax = plt.subplots(figsize=(16, 2))
        ax.plot(norm_stack, 'black')
        ax.set_title(norm_method)

    return np.max(norm_stack, axis=0)


def tubeWaveDetector(head, data, sta, lta, sens, norm_method="Norm by number of channels enabled",
                     downgoing=True, metric=False):
    """
    Classify if an event is a tube-wave based on the velocity shift required to produce a maximal stack

    sta - short term average in milliseconds
    lta - long term average in milliseconds

    :return:
    """

    # Sampling to convert milliseconds to data points
    sampling = int(1/(1000/head['fs']))

    # List of sensornames
    sensornames = pd.Series(head['ch_descr'][::3])
    sensornames = sensornames.str.split("\x00").str[0]
    sensornames = sensornames.to_list()
    sensornames_by_ch = pd.Series(head['ch_descr'])
    sensornames_by_ch = sensornames_by_ch.str.split("\x00").str[0]

    # Detrend
    for i in range(0, len(data)):
        data[i, :] = signal.detrend(data[i, :])

    data_stalta = data.copy()

    for i in range(0, len(data)):
        data_stalta[i, :] = sta_lta_mask(data_stalta[i, :], sta_w=sta * sampling, lta_w=lta * sampling)

    max_val = 0
    best_v = None

    for v in np.arange(300.0, 10000.0, 10):
        # velocity (convert m/s to ft/s)
        if metric is False:
            v *= 3.28084

        val = waveform_vel_shift(v, sens, data_stalta, norm_method, sensornames_by_ch, head, False, downgoing)

        if val > max_val:
            # Best so far
            max_val = val
            best_v = v

    print("Best velocity: "+str(best_v))
    print("Max Stack Score: "+str(max_val))

    tube_max = 1500
    tube_min = 1350

    if metric is False:
        tube_max *= 3.28084
        tube_min *= 3.28084

    if (best_v > tube_min) & (best_v < tube_max) & (max_val > 1.5):
        tubewave = True
    else:
        tubewave = False

    print("Tube Wave: "+str(tubewave))

    return tubewave, best_v, max_val


def generateHSFFilePathFile(trgids, DSN, basepath, HSFListFile):
    """
    For a dataframe of database entries, create the file path and alternate file
    path for those entries.
    :param trgids:
    :param DSN:
    :param basepath:
    :param HSFListFile:
    """
    if isinstance(trgids, list):
        trgids = pd.Series(trgids)
    if trgids.dtype != np.str:
        # noinspection PyTypeChecker
        trgids = trgids.apply(int).apply(str)

    filepaths = [trgid2hsfpath(DSN, trgid, basepath) for trgid in trgids]

    filepaths = pd.Series(filepaths)

    with open(HSFListFile, 'w') as f:
        filepaths.to_csv(HSFListFile, index=False, header=False)


def processHSFs(PRCPath, HSFListPath, logfilepath, debug=False):
    """
    Run a PRC file on specific events
    :param PRCPath: path to the .prc file
    :param HSFListPath: list of hsf files
    :param logfilepath: path to save batch log file
    :param debug: show path to log file
    :return:
    """

    # The path to batchjobprocessor
    batchjobprocessor = 'C:\\esg\\BatchJobProcessor.exe'
    # A path for the logfile.
    logfilepath = os.path.join(logfilepath, 'Batchlogfile.txt')

    # call batchjobprocessor with arguments.
    args = batchjobprocessor + " -1 " + PRCPath + " " + HSFListPath + " " + logfilepath

    if debug:
        print(args)
    _ = subprocess.call(args)

    print("Batch complete")


def get_cc_values(tr1, tr2, arriv1_loc, arriv2_loc, window=0.5, allowed_shift=0.5, plot_result=False,
                  sampling_frequency=100, debug=False, orig_diff=0, return_shift_val=False):
    """
    Estimating the cross correlation differential times between two events for a particular phase
    :param tr1: the data for the first event (just a numpy array of values)
    :param tr2: the data for the second event (numpy array of values)
    :param arriv1_loc: the arrival time of the first event in samples (must be correct relative to the start of the data
        provided in tr1)
    :param arriv2_loc: the arrival time of the second event in samples (must be correct relative to the start of the
        data provided in tr2)
    :param allowed_shift: time window in seconds of shifts allowed
    :param window: time window in seconds around the waveform
    :param plot_result: if True then the results of the cross correlation will be plotted to be examined
    :param sampling_frequency: sampling frequency of the waveform
    :param debug: if True then we're debugging the code to identify an issue so turn on print outs
    :param orig_diff: default 0, shifting the differential cc times by the difference in origin time if necessary.
        If you are providing a value for this, it should be the origin time of the first event minus the origin time of
        the second event, and the origin times must be expressed in seconds since the start of the waveform
    :param return_shift_val: option to return the shift val as well the diff cc time
    :return: the differential time and the max cross correlation coefficient
    Differential time is measured as arriv1loc_shifted - arriv2loc_shifted
    """
    # converting time window to samples
    window = int(window * sampling_frequency)
    allowed_shift = int(allowed_shift * sampling_frequency)

    # grabbing a 1 second window around the P pick and S pick for event 1
    win_1 = tr1[arriv1_loc - window:arriv1_loc + window]
    if debug:
        print('Calculating cc times')
        print('Trace 1')
        print(len(tr1))
        print(arriv1_loc)
        print(arriv1_loc - window)
        print(arriv1_loc + window)
        print('data')
        print(win_1)

    # now looping through a set of shifts to extract the window to correlate from the other event
    shifts = np.arange(-allowed_shift, allowed_shift + 1, 1)

    if debug:
        print('test trace 2 data')
        print(tr2)
        print(tr2[arriv2_loc - window: arriv2_loc + window])

    # making the array of tr2 values
    tr2_arr = np.repeat(tr2[:, np.newaxis], len(shifts), axis=1).T

    # now shifting all the copies in that array by different amounts
    arr_roll = tr2_arr[:, [*range(tr2_arr.shape[1]), *range(tr2_arr.shape[1] - 1)]].copy()  # need `copy`
    strd_0, strd_1 = arr_roll.strides
    n = tr2_arr.shape[1]
    # need to be careful that this function doesn't result in errors due to memory allocation (see docs)
    result = np.lib.stride_tricks.as_strided(arr_roll, (*tr2_arr.shape, n), (strd_0, strd_1, strd_1))
    # had to change n-shifts to n+shifts because behaviour was not as I expected
    shifted = result[np.arange(tr2_arr.shape[0]), (n + shifts) % n]

    # now indexing the shifted arrays
    # have to flip the order because they come out in the wrong order
    arr_var = np.flip(shifted[:, arriv2_loc - window:arriv2_loc + window], axis=0)
    if debug:
        print('Trace 2')
        print(len(tr2))
        print(arriv2_loc)
        print(arriv2_loc - window)
        print(arriv2_loc + window)
        print('data')
        print(arr_var[0])

    # now computing the cross correlation
    cc_var = np.corrcoef(win_1, arr_var)[0, 1:]

    # and identifying the best shift
    ccc_max = np.max(cc_var)
    # plt.figure()
    # plt.plot(shifts, cc_var)
    # plt.show()
    if len(np.argwhere(cc_var == ccc_max).flatten()) == 0 or debug is True:
        print(cc_var)
        print(ccc_max)
    tloc = np.argwhere(cc_var == ccc_max).flatten()[0]
    shift_val = shifts[tloc]

    # once we have identified the shift with the highest value then we need to translate the shift into
    # a cross correlation differential time
    # so apply the shift to the original pick time
    # I think this should be a subtraction, because if we're moving the second waveform to the right then we're
    # moving the second P pick to the left and vice versa
    loc_shift = arriv2_loc - shift_val

    # adjust both sets of picks so they are in seconds
    # don't need to adjust for difference between start and origin time because the window is constant
    # length for all events
    arriv2_loc_shift = loc_shift / sampling_frequency
    arriv1_loc_shift = arriv1_loc / sampling_frequency

    # now compute the differential time in seconds
    # REMEMBER, this has to be in event 1 minus event2
    arriv_diff = arriv1_loc_shift - arriv2_loc_shift - orig_diff

    # option to plot out the result
    if plot_result is True:
        plt.figure()
        plt.plot(win_1/np.max(win_1), 'b-')
        plt.plot(arr_var[tloc]/np.max(arr_var[tloc]), 'g-', alpha=0.2)
        plt.plot(tr2[arriv2_loc - window:arriv2_loc + window]/np.max(arr_var[tloc]), 'r-', alpha=0.2)
        print('arrivs')
        print(arriv1_loc)
        print(arriv2_loc)
        print(shift_val)
        print(arriv_diff)
        plt.show()

    # returning the differential time and its cross correlation coefficient estimate
    if return_shift_val is False:
        return arriv_diff, ccc_max
    else:
        return arriv_diff, ccc_max, shift_val


def get_mcc_values(tr1, tr2, arriv1_loc, arriv2_loc, window=0.5, allowed_shift=0.5, plot_result=False,
                   sampling_frequency=100, debug=False, orig_diff=0, return_shift_val=False):
    """
    Estimating the cross correlation differential times between two events for a particular phase. Essentially the same
    code as get_cc_values but with added capability of using "anti-correlated" signals to compensate for signal
    sign variability depending on source radiation pattern.
    Author: Doug Angus (adapted from get_cc_values by Joshua Williams)
    :param tr1: the data for the first event (just a numpy array of values)
    :param tr2: the data for the second event (numpy array of values)
    :param arriv1_loc: the arrival time of the first event in samples (must be correct relative to the start of the data
        provided in tr1)
    :param arriv2_loc: the arrival time of the second event in samples (must be correct relative to the start of the
        data provided in tr2)
    :param allowed_shift: time window in seconds of shifts allowed
    :param window: time window in seconds around the waveform
    :param plot_result: if True then the results of the cross correlation will be plotted to be examined
    :param sampling_frequency: sampling frequency of the waveform
    :param debug: if True then we're debugging the code to identify an issue so turn on print outs
    :param orig_diff: default 0, shifting the differential cc times by the difference in origin time if necessary.
        If you are providing a value for this, it should be the origin time of the first event minus the origin time of
        the second event, and the origin times must be expressed in seconds since the start of the waveform
    :param return_shift_val: option to return the shift val as well the diff cc time
    :return: the differential time, and the max and min cross correlation coefficient
    Differential time is measured as arriv1loc_shifted - arriv2loc_shifted
    """
    # converting time window to samples
    window = int(window * sampling_frequency)
    allowed_shift = int(allowed_shift * sampling_frequency)

    # grabbing a window around the P pick and S pick for event 1
    win_1 = tr1[arriv1_loc - window:arriv1_loc + window]
    if debug:
        print('Calculating cc times')
        print('Trace 1')
        print(len(tr1))
        print(arriv1_loc)
        print(arriv1_loc - window)
        print(arriv1_loc + window)
        print('data')
        print(win_1)

    # now looping through a set of shifts to extract the window to correlate from the other event
    shifts = np.arange(-allowed_shift, allowed_shift + 1, 1)

    if debug:
        print('test trace 2 data')
        print(tr2)
        print(tr2[arriv2_loc - window: arriv2_loc + window])

    # making the array of tr2 values
    tr2_arr = np.repeat(tr2[:, np.newaxis], len(shifts), axis=1).T

    # now shifting all the copies in that array by different amounts
    arr_roll = tr2_arr[:, [*range(tr2_arr.shape[1]), *range(tr2_arr.shape[1] - 1)]].copy()  # need `copy`
    strd_0, strd_1 = arr_roll.strides
    n = tr2_arr.shape[1]
    # need to be careful that this function doesn't result in errors due to memory allocation (see docs)
    result = np.lib.stride_tricks.as_strided(arr_roll, (*tr2_arr.shape, n), (strd_0, strd_1, strd_1))
    # had to change n-shifts to n+shifts because behaviour was not as I expected
    shifted = result[np.arange(tr2_arr.shape[0]), (n + shifts) % n]

    # now indexing the shifted arrays
    # have to flip the order because they come out in the wrong order
    arr_var = np.flip(shifted[:, arriv2_loc - window:arriv2_loc + window], axis=0)
    if debug:
        print('Trace 2')
        print(len(tr2))
        print(arriv2_loc)
        print(arriv2_loc - window)
        print(arriv2_loc + window)
        print('data')
        print(arr_var[0])

    # now computing the cross correlation
    cc_var = np.corrcoef(win_1, arr_var)[0, 1:]

    # and identifying the best shift
    ccc_max = np.max(cc_var)
    ccc_min = np.min(cc_var)
    if len(np.argwhere(cc_var == ccc_max).flatten()) == 0 or debug is True:
        print(cc_var)
        print(ccc_max)
    if len(np.argwhere(cc_var == ccc_min).flatten()) == 0 or debug is True:
        print(cc_var)
        print(ccc_min)

    if ccc_max >= abs(ccc_min):
        tloc = np.argwhere(cc_var == ccc_max).flatten()[0]
        cc_max = ccc_max
    else:
        tloc = np.argwhere(cc_var == ccc_min).flatten()[0]
        cc_max = ccc_min
    shift_val = shifts[tloc]

    # once we have identified the shift with the highest value then we need to translate the shift into
    # a cross correlation differential time
    # so apply the shift to the original pick time
    # I think this should be a subtraction, because if we're moving the second waveform to the right then we're
    # moving the second P pick to the left and vice versa
    loc_shift = arriv2_loc - shift_val

    # adjust both sets of picks so they are in seconds
    # don't need to adjust for difference between start and origin time because the window is constant
    # length for all events
    arriv2_loc_shift = loc_shift / sampling_frequency
    arriv1_loc_shift = arriv1_loc / sampling_frequency

    # now compute the differential time in seconds
    # REMEMBER, this has to be in event 1 minus event2
    arriv_diff = arriv1_loc_shift - arriv2_loc_shift - orig_diff

    # option to plot out the result
    if plot_result is True:
        # plt.figure()
        # plt.plot(win_1/np.max(win_1), 'b-')
        # plt.plot(arr_var[tloc]/np.max(arr_var[tloc]), 'g-', alpha=0.2)
        # plt.plot(tr2[arriv2_loc - window:arriv2_loc + window]/np.max(arr_var[tloc]), 'r-', alpha=0.2)
        fig, axs = plt.subplots(5)
        fig.suptitle('MCC results')
        axs[0].plot(win_1/np.max(win_1), 'b-')
        axs[1].plot(arr_var[tloc]/np.max(arr_var[tloc]), 'g-', alpha=0.2)
        axs[2].plot(tr2[arriv2_loc - window:arriv2_loc + window]/np.max(arr_var[tloc]), 'r-', alpha=0.2)
        axs[3].plot(tr1[arriv1_loc - 2*window:arriv1_loc + 4*window], 'g-', alpha=0.2)
        axs[4].plot(tr2[arriv2_loc - 2*window:arriv2_loc + 4*window], 'r-', alpha=0.2)
        plt.show()

        print('cc values')
        print('cc_max:', ccc_max)
        print('cc_min:', ccc_min)
        print('Shift :', shift_val)
        print('dT    :', arriv_diff)
        plt.show()

    # returning the differential time and its cross correlation coefficient estimate
    if return_shift_val is False:
        return arriv_diff, cc_max
    else:
        return arriv_diff, cc_max, shift_val


"""
Below are functions to decompress hsf files using python only rather than using the hsfcompressor.exe
This approach is slower than the .exe currently by a factor of 2 on a laptop and a factor of 40 on a PC
But might be a useful fall back
Functions include some numpy_ functions which get the values out of the array of integers, and the main function which
is called decompress_hsf
"""


def numpy_init_values(bits, debug=False, out_size=None):
    """
    Get specified number of bits as an integer
    :param bits: array of integers
    :param debug: optional debug parameter
    :param out_size: expected size of the output
    :return:
    """
    # defaulting the output size
    if out_size is None:
        out_size = len(bits)

    # setting up some constants
    allf = 0xffffffff
    constant2 = 0x1F
    constant3 = 2 ** 32
    lshift1 = 1 << 32
    lshift2 = 1 << 31

    # debug call
    if debug:
        breakpoint()

    # getting the locations
    loc = np.arange(0, out_size)

    # getting the position of the value to pull out
    p1 = np.right_shift(loc, 5)

    # and getting the number of bits to shift by
    b = np.bitwise_and(loc, constant2)

    # left shifting the value, and then making sure it can only be a 32 bit integer using the and symbol
    v = np.array(bits[p1], dtype=np.int64)
    v[v < 0] += constant3
    v = np.bitwise_and(np.left_shift(v, b), allf)

    # forcing the values to be negative if they exceed the expected 32 bit length to match the behavior with java
    v[v >= lshift2] -= lshift1

    # getting v2 as well
    v2 = np.array(bits[p1 + 1], dtype=np.int64)

    return p1, b, v, v2


def numpy_get_int(bits, num_bits, debug=False, out_size=None, v=None, v2=None, b=None, adjust_v2=True):
    """
    Convert each integer in the array using the specific number of bits
    :param bits: the array of integers that we will extract values from
    :param num_bits: number of bits
    :param debug: optional debug parameter
    :param out_size: expected size of the output, defaults to the length of the bits
    :param v: option to include v if precalculating it
    :param v2: option to include v2 if precalculating it
    :param b: option to include b if precalculating it
    :param adjust_v2: if True then adjust negative values of v2, otherwise don't
    :return:
    """
    # defaulting the out size
    if out_size is None:
        out_size = len(bits)

    # just the one constant that is shared
    constant3 = 2 ** 32

    # debug call
    if debug:
        breakpoint()

    # this code doesn't use num_bits at all, so technically it should be the same for all num bits values
    # this code is only run if the other parameters haven't been provided in the function call
    if v is None:
        # setting up some constants
        allf = 0xffffffff
        lshift1 = 1 << 32
        lshift2 = 1 << 31
        constant2 = 0x1F

        # getting the range of locations
        loc = np.arange(0, out_size)

        # getting the position of the value to pull out
        p1 = np.right_shift(loc, 5)

        # and getting the number of bits to shift by
        b = np.bitwise_and(loc, constant2)

        # left shifting the value, and then making sure it can only be a 32 bit integer using the and symbol
        v = np.array(bits[p1], dtype=np.int64)
        ix = np.argwhere(v < 0).flatten()
        v[ix] = np.add(v[ix], constant3)
        v = np.bitwise_and(np.left_shift(v, b), allf)

        # forcing the values to be negative if they exceed the expected 32 bit length to match the behavior with java
        ix = np.argwhere(v >= lshift2).flatten()
        v[ix] = np.subtract(v[ix], lshift1)
        v2 = np.array(bits[p1 + 1], dtype=np.int64)

    # only performing this step if the bit shift is larger than 32
    nbdiff = 32 - num_bits
    ix2 = np.argwhere(b > nbdiff).flatten()

    # reindexing the v2 and b values to speed up the code
    v2 = v2[ix2]
    b = b[ix2]

    # adding the constant where the v2 values are negative
    if adjust_v2:
        v2[v2 < 0] += constant3

    # simplified this a little to reduce the number of calculations required
    bsub = np.subtract(32, b)
    v2 = np.right_shift(v2, bsub)
    v[ix2] = np.bitwise_or(v[ix2], v2)

    # where the shift will be applied, make sure to flip the integer first before shifting it
    if nbdiff != 0:
        v[v < 0] += constant3
        v = np.right_shift(v, nbdiff)

    return v


def numpy_get(bits, out_size=None, p1=None, b=None):
    """
    Convert each integer in the array to a bool following the procedure below
    :param bits: the array of integers
    :param out_size: expected size of the output
    :param p1: option to specify p1 if it is precalculated
    :param b: option to include b if it is precalculated
    :return:
    """
    # defaulting the output size
    if out_size is None:
        out_size = len(bits)

    # setting up some constants
    constant = 0x80000000
    constant2 = 0x1F

    # calculating p1 and b if they have not been provided
    if p1 is None:
        loc = np.arange(0, out_size)
        p1 = np.right_shift(loc, 5)
        b = np.bitwise_and(loc, constant2)

    # estimating the actual values
    val = np.bitwise_and(bits[p1], np.right_shift(constant, b)) != 0

    return val


def decompress_hsf_python(hbin, compresssize, nch, npt, invalid_value=16843009):
    """
    Adapting the decompression code to decompress the Rice/Golomb encoded data in hsfs
    This is based on the algorithm that Dan wrote in javascript
    :return:
    """

    # extracting the waveform data
    blob = hbin[:compresssize]

    # getting the individual bits in little endian
    blob_arr = np.ndarray((int(len(blob)/4), ), buffer=blob, offset=0, dtype='<i')

    # expect the first bit to be zero, non-zero value may be due to new compression format that this version
    # does not understand
    get_vals = numpy_get(blob_arr, out_size=1)
    loc = 0
    temp = get_vals[loc]
    if temp:
        raise ValueError('Unrecognized compression format')
    loc += 1

    # getting the size of the data we expect to extract
    temp_v_vals = numpy_get_int(blob_arr, 32, out_size=2)
    n_out_size = temp_v_vals[loc]
    loc += 32

    # identifying what the true output size should be
    temploc = np.arange(0, n_out_size * 32)
    tempp1 = np.right_shift(temploc, 5)
    bad_loc = np.argwhere(tempp1 > len(blob_arr) - 2).flatten()
    true_out_size = bad_loc[0]

    # initialising the values which aren't affected by the change in number of bits to speed up the code
    p1, b, v, v2 = numpy_init_values(blob_arr, out_size=true_out_size)

    # making adjustment to v2 to fix negative values
    constant3 = 2 ** 32
    v2[v2 < 0] += constant3

    # recreating the dictionaries now that we know how many values there will be
    v_vals = dict()
    call_vals = dict()
    for ij in range(0, 33):
        # start_time4 = time.time()
        if ij in [5, 16]:
            v_vals[ij] = numpy_get_int(blob_arr, ij, out_size=true_out_size, v=v.copy(), b=b,
                                       v2=v2.copy(), adjust_v2=False)
        call_vals[ij] = []
        # print('Time taken for initial value calculations for ' + str(ij) + ':' + str(time.time() - start_time4))

    # getting the boolean values as well
    get_vals = numpy_get(blob_arr, out_size=true_out_size, p1=p1, b=b)

    # checking whether the data is split into individual blocks or just on large block
    b_use_blocks = get_vals[loc]
    loc += 1

    # creating the array to store the data output
    pnout = np.empty([n_out_size])

    # iterating through to extract all the data points
    orig_loc = copy.deepcopy(loc)
    p = 0
    while p < n_out_size:
        # setting the size of the block
        n_this_block_size = n_out_size

        # if we are using blocks then the first byte is the size of the blocks
        if b_use_blocks:
            n_this_block_size = v_vals[16][loc]
            call_vals[16].append(loc)
            loc += 16

        # checking if this is a special block
        b_special_block = get_vals[loc]
        loc += 1

        # if it is a special block
        if b_special_block:
            # check if it is a block of constant values
            b_constant_block = get_vals[loc]
            loc += 1

            # if it is a block of constant values
            if b_constant_block:
                # is it a block of invalid points
                b_invalid_pts = get_vals[loc]
                loc += 1

                # if it it is just invalid points then just add in the number of points
                if b_invalid_pts:
                    pass
                else:
                    # if just constant points then creating the block full of constant points
                    # the constant value
                    call_vals[32].append(loc)
                    loc += 32

                # and iterating the counter
                p += n_this_block_size
        else:
            # identify the number to add to each data point
            call_vals[32].append(loc)
            loc += 32

            # extract the number of bits which we will use to get the remainder
            mbits = v_vals[5][loc]
            call_vals[5].append(loc)
            loc += 5

            # looping through the block
            for i in range(n_this_block_size):

                # get the quotient by counting the number of zeroes
                tval = get_vals[loc]
                loc += 1
                while not tval:
                    tval = get_vals[loc]
                    loc += 1

                # get the sign
                loc += 1

                # get the remainder by interpreting
                call_vals[mbits].append(loc)
                loc += mbits

                # increasing iteration counter
                p += 1

    # getting the values and setting up the locations counters for each different number of bits
    v_vals = dict()
    loc_vals = dict()
    for ij in range(0, 33):
        loc_vals[ij] = 0
        if len(call_vals[ij]) != 0:
            ix = np.array(call_vals[ij])
            v_vals[ij] = numpy_get_int(blob_arr, ij, out_size=true_out_size, v=v[ix], b=b[ix],
                                       v2=v2[ix], adjust_v2=False)

    # iterating through to extract all the data points
    loc = orig_loc
    p = 0
    while p < n_out_size:
        # setting the size of the block
        n_this_block_size = n_out_size

        # if we are using blocks then the first byte is the size of the blocks
        if b_use_blocks:
            n_this_block_size = v_vals[16][loc_vals[16]]
            loc_vals[16] += 1
            loc += 16

        # checking if this is a special block
        b_special_block = get_vals[loc]
        loc += 1

        # if it is a special block
        if b_special_block:
            # check if it is a block of constant values
            b_constant_block = get_vals[loc]
            loc += 1

            # if it is a block of constant values
            if b_constant_block:
                # is it a block of invalid points
                b_invalid_pts = get_vals[loc]
                loc += 1

                # if it it is just invalid points then just add in the number of points
                if b_invalid_pts:
                    pnout[p:p + n_this_block_size] = invalid_value
                else:
                    # if just constant points then creating the block full of constant points
                    # the constant value
                    constant_val = v_vals[32][loc_vals[32]]
                    loc_vals[32] += 1
                    loc += 32

                    # filling
                    pnout[p:p + n_this_block_size] = constant_val

                # and iterating the counter
                p += n_this_block_size
        else:
            # if it not a special block
            # pre_pre_loc = bitstream.loc
            # identify the number to add to each data point
            dc_offset = v_vals[32][loc_vals[32]]
            loc_vals[32] += 1
            loc += 32

            # extract the number of bits which we will use to get the remainder
            mbits = v_vals[5][loc_vals[5]]
            loc_vals[5] += 1
            loc += 5

            # looping through the block
            for i in range(n_this_block_size):

                # get the quotient by counting the number of zeroes
                q = 0
                tval = get_vals[loc]
                loc += 1
                while not tval:
                    q += 1
                    tval = get_vals[loc]
                    loc += 1

                # get the sign
                negative = get_vals[loc]
                loc += 1

                # get the remainder by interpreting
                r = v_vals[mbits][loc_vals[mbits]]
                loc_vals[mbits] += 1
                loc += mbits

                # construct the decoded integer
                v = (q << mbits) | r

                # checking if the value is negative
                if negative:
                    # if value is zero then just use the invalid data point value
                    if v == 0:
                        pnout[p] = invalid_value
                    else:
                        # if it is a viable value then subtract it from dcOffset
                        pnout[p] = dc_offset - v

                else:
                    # if the value is positive then add it to dcoffset
                    pnout[p] = dc_offset + v

                # increasing iteration counter
                p += 1

    pnout = np.array(pnout, dtype=float)
    pnout = np.reshape(pnout, (nch, npt))

    return pnout


def combine_segy_for_wavevis(output_filename, folder=None, filenames=None):
    """
    Function to combine multiple segy files into one segy file that can be opened in WaveVis
    :param output_filename: the file name and path to save the file to
    :param folder: if not None, folder which should contain the segy files you want to use, overrides filenames value
        if provided
    :param filenames: if not None, list of filenames to be read in. Is overridden if folder is provided
    :return: Outputs a single segy file that can be opened in WaveVis
    """
    from obspy import Stream

    # reading in the files
    st = Stream()

    output_filename = makeLinuxPath(output_filename)

    # making sure the folder and files are linux paths
    if folder is not None:
        folder = makeLinuxPath(folder)

        # if output file name does not include folder then just put it in the specified folder
        if os.path.sep not in output_filename:
            output_filename = os.path.join(folder, output_filename)

    if filenames is not None:
        filenames = [makeLinuxPath(fname) for fname in filenames]

    # error catch
    if folder is None and filenames is None:
        raise ValueError('One of folder or filenames must be provided.')

    # getting file names if folder is provided
    if folder is not None:
        filenames = [os.path.join(folder, fname) for fname in os.listdir(folder)
                     if os.path.isfile(os.path.join(folder, fname))]

    # reading in each file
    for fname in filenames:
        st += read_segy(fname)

    # merging
    st.merge()

    # checking the npts
    for tr in st:
        if tr.stats.npts > 32767:
            print('Number of points in trace: ' + str(tr.stats.npts))
            raise ValueError('Cannot write out SEGY files with more than 32767 samples, '
                             'use a shorter time window of files')

    # writing out the file
    st.write(output_filename, format='SEGY')
