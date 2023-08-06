from uquake.core.inventory import (Network, Station, Channel,
                                   geophone_response, accelerometer_response)
from pickled_carrots.waveforms import HeaderLookups
import hashlib

lookup = HeaderLookups()


def inventory_from_hsf_header(head, network_name):
    channels = []

    stations = []
    for i, station_name in enumerate(np.unique(head['sensor_name'])):
        hash = hashlib.md5(station_name.encode('ascii')).hexdigest()
        station = Station(alternate_code=station_name, code=hash[:5],
                          historical_code=hash)
        stations.append(station)

    network = Network(code=network_name, stations=stations)

    for i, channel_name in enumerate(head['ch_descr']):
        if geophone in lookup.sensor_types[head['stype']]:
            response = geophone_response()
        channel = Channel(alternate_code=channel_name)
        for station in network:
            if station.alternate_code in channel_name:
                station.channels.append()