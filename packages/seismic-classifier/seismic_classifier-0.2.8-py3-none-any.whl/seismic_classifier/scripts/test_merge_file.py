from pickled_carrots.vinegar.core import HSFHandler
from pathlib import Path
from tqdm import tqdm
from ipdb import set_trace
import numpy as np
from datetime import datetime

i = 0

filenames = np.sort([fpath for fpath in Path('/data_2/GBC').glob('20*.hsf')])
ts = [datetime.strptime('YYYYmmddHHMMSS', f.stem[:-3]) for f in filenames]


for hsf_file in tqdm(filenames, total=10):
    sites = []
    fb = HSFHandler.read(hsf_file, 'GBC').file_bundle
    st_tmp = fb.stream
    cat = fb.catalog
    print(f'{cat[0].preferred_origin().time}/{cat[0].event_type}')
    for pick in cat[0].picks:
        station = pick.waveform_id.station_code
        location = pick.waveform_id.location_code
        sites.append((station, location))
    inventory = fb.inventory

    st_tmp = st_tmp.detrend('demean')
    if i == 0:
        st = st_tmp
        starttime = st_tmp[0].stats.starttime
    else:
        if st_tmp[0].stats.starttime - starttime < 10:
            for tr in st_tmp:
                st.traces.append(tr)
            set_trace()
        else:
            if i == 1:
                i == 0
                continue
            sites = set(sites)
            # stations = [site[0] for site in sites]
            # locations = [site[1] for site in sites]
            for j, site in tqdm(enumerate(sites)):
                if j == 0:
                    st2 = st.copy().select(station=site[0], location=site[1])
                else:
                    for tr in st.copy().select(station=site[0], location=site[1]):
                        st2.traces.append(tr)
            break
    i += 1

    if i == 10:
        set_trace()
        st.merge(fill_value=0)
