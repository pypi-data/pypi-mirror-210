import os

from pickled_carrots import waveforms
from pickled_carrots.vinegar import core
from pickled_carrots.vinegar.event import uquake_event_from_letter_id
from uquake.core.logging import logger
from pathlib import Path
from time import time
from importlib import reload
import random
import pickle
from time import sleep

reload(waveforms)
reload(core)

input_path = Path('/data_2/GBC/')
fs = [f for f in input_path.glob('*.hsf')]
random.shuffle(fs)

catalog = pickle.load(open('/data_2/catalogues/GBC_catalog.pickle', 'rb'))

for f in fs:

    try:
        event = catalog[catalog['TrgID'] == int(f.stem)]
    except:
        continue

    event_type = uquake_event_from_letter_id(event['T'][0], 'GBC')

    # logger.info(f'reading the HSF file ({f})')

    # t0 = time()
    # hsf_handler = core.HSFHandler.read(f, 'GBC')
    # t1 = time()
    # logger.info(f'done reading the HSF file in {t1 - t0} seconds')
    #
    # cat = hsf_handler.file_bundle.catalog
    # cat[0].event_type = event_type
    logger.info(f'{event["T"][0]}, {event_type}')
    sleep(0.1)

