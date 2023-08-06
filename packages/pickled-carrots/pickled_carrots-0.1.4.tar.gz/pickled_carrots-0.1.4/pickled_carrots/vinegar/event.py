from uquake.core.stream import Stream
from uquake.core.event import (Catalog, Event, Magnitude, Origin, Pick,
                               Arrival, WaveformStreamID)
from uquake.core import UTCDateTime
from uquake.waveform.pick import calculate_snr
import numpy as np
from datetime import datetime
from pickled_carrots.waveforms import HeaderLookups


def esg_quakeml_event_type_conversion(esg_event_type):
    if esg_event_type == 'Event':
        return 'earthquake'
    if esg_event_type == 'Blast':
        return 'explosion'
    return 'other event'


def create_event(hsf_stream, head, network):

    # unfortunately the hsf files does not contain any information on whether the
    # event was processed manuall or automatically.
    evaluation_mode = 'automatic'
    evaluation_status = 'preliminary'

    picks, arrivals = pick_from_hsf(hsf_stream, network, head, evaluation_mode,
                                    evaluation_status)

    origin = origin_from_catalog(head, arrivals, evaluation_mode,
                                 evaluation_status)

    event_type = esg_quakeml_event_type_conversion(
        HeaderLookups.event_types[head['evtype']])

    magnitudes = magnitudes_from_catalog(head, evaluation_mode,
                                         evaluation_status)

    event = Event(origins=[origin], magnitudes=magnitudes,
                  event_type=event_type,
                  evaluation_mode=evaluation_mode,
                  evaluation_status=evaluation_status,
                  picks=picks)

    event.preferred_origin_id = origin.resource_id
    event.preferred_magnitude_id = magnitudes[0].resource_id

    return event


def magnitudes_from_catalog(head, evaluation_mode, evaluation_status):
    magnitudes = []

    energy = head['energy_p'] + head['energy_sh'] + head['energy_sh']
    energy = energy[np.nonzero(energy)]
    energy = np.median(energy)
    # energy = 1
    magnitude = Magnitude()
    magnitude.magnitude_type = 'Mw'
    magnitude.mag = head['mw']
    # magnitude.seismic_moment = catalog_line['SeiMoment']
    e_p = energy / (1 + head['esep'])
    e_s = e_p * head['esep']
    magnitude.energy_s_joule = e_s
    magnitude.energy_p_joule = e_p
    magnitude.energy_joule = e_s + e_p
    magnitude.moment_magnitude_uncertainty = 0
    magnitude.corner_frequency_p_hz = np.median(head['corner_p'][np.nonzero(
        head['corner_p'])])
    magnitude.corner_frequency_s_hz = np.median(head['corner_s'][np.nonzero(
        head['corner_s'])])
    magnitude.corner_frequency_hz = np.median(head['corner_p'][np.nonzero(
        head['corner_p'])])
    magnitude.evaluation_mode = evaluation_mode
    magnitude.evaluation_status = evaluation_status

    magnitudes.append(magnitude)

    # local_magnitude = Magnitude()
    # local_magnitude.magnitude_type = 'Ml'
    # local_magnitude.mag = head['lm']
    # local_magnitude.evaluation_mode = evaluation_mode
    # local_magnitude.evaluation_status = evaluation_status

    # magnitudes.append(local_magnitude)

    return magnitudes


def origin_from_catalog(head, arrivals, evaluation_mode,
                        evaluation_status):

    origin = Origin()
    eloc = head['source']
    origin.x = eloc[0]
    origin.y = eloc[1]
    origin.z = eloc[2]
    origin.time = UTCDateTime(datetime.fromtimestamp(head['t0_s'] + head['t0_us'] / 1e6))
    origin.evaluation_mode = evaluation_mode
    origin.evaluation_status = evaluation_status

    origin.arrivals = arrivals

    return origin


def pick_from_hsf(hsf_stream, network, head, evaluation_mode, evaluation_status):

    picks = []
    arrivals = []
    processed_sites = []
    for tr, used in zip(hsf_stream, head['valid_flag_pickused']):
        if not used:
            continue
        if tr.stats.site in processed_sites:
            continue
        processed_sites.append(tr.stats.site)
        t0 = tr.stats.starttime
        tp = tr.stats.t0
        ts = tr.stats.t1

        if (tp == 0) and (ts == 0):
            continue

        waveform_id = WaveformStreamID(network_code=network,
                                       station_code=tr.stats.station,
                                       location_code=tr.stats.location,
                                       channel_code=tr.stats.channel)
        if tp != 0:
            pick, arrival = create_pick_arrival(tr, t0 + tp, 'P', waveform_id,
                                                evaluation_mode,
                                                evaluation_status)

        if ts != 0:
            pick, arrival = create_pick_arrival(tr, t0 + ts, 'S', waveform_id,
                                                evaluation_mode,
                                                evaluation_status)

        picks.append(pick)
        arrivals.append(arrival)

    return picks, arrivals


def create_pick_arrival(tr, time, phase, waveform_id, evaluation_mode,
                        evaluation_status):
    pk = Pick()
    pk.waveform_id = waveform_id
    pk.time = time
    pk.phase_hint = phase.upper()
    pk.evaluation_mode = 'automatic'
    pk.evaluation_status = 'preliminary'
    pk.snr = calculate_snr(tr, time)
    pk.evaluation_mode = evaluation_mode
    pk.evaluation_status = evaluation_status

    arrival = Arrival()
    arrival.pick_id = pk.resource_id
    arrival.phase = phase.upper()
    arrival.distance = tr.stats.distance
    arrival.azimuth = tr.stats.azimuth
    arrival.time_residual = 0

    return pk, arrival





