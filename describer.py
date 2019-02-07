from datetime import timedelta
from pathlib import Path

from parameters import *


def describe(histfile):
    historylines = open(histfile).readlines()
    fileformatline = historylines[1].strip()
    if fileformatline.startswith('FILEFORMAT'):
        try:
            ff = fileformatline.split()[-1]
            offset_top, offset_btm = offsets[ff]
        except KeyError:
            raise KeyError(f'{histfile}: Unknown fileformat: {ff}. Accepted are {list(offsets.keys())}')
    else:
        raise Exception(f'{histfile}: Fileformat not found on 2nd line: {fileformatline}')

    paramslines = historylines[:offset_top] + historylines[-offset_btm:]
    # energy_evolution = historylines[offset_top:-offset_btm]
    del historylines

    params = dict()
    for line in paramslines:
        parts = line.strip().split(' ', 1)
        params[parts[0]] = parts[1]

    params['FILE'] = str(histfile)

    try:
        # params['HEXGRID'] = str(list(hexgrid_loc.glob(f'hexgrid2C_*{params["SEED"]}.*.csv'))[0])
        l = list(Path(histfile).parent.glob(f'hexgrid2C_*{params["SEED"]}.*.csv'))
        if len(l) > 1:
            print(f'{histfile}: Several hexgrids found: {list(map(str, l))}')
        params['HEXGRID'] = str(l[0])
    except IndexError:
        print(f'{histfile}: Hexgrid not found')
        params['HEXGRID'] = None

    metadata = {
        'metadata': {
            'fileformat': params['FILEFORMAT'],
            'version': params['VERSION'],

            'seed': int(params['SEED']),

            'framefreq': int(params['EVERY_STEP']),
            'steps': int(params['STEPS']),
            'time': str(timedelta(seconds=float(params['TIME'][:-7]))),
        },

        'files': {
            'history': params['FILE'],
            'hexgrid': params['HEXGRID']
        },

        'plots': {
            'energy': None,
            'steps': None,
            'phi': None,
            'phi3x3': None,
            'theta': None,
            'theta3x3': None,
            # 'movements'
        },

        'cell': list(map(int, params['CELL'].split())),

        'parameters': {
            'B': float(params['B_BIQDR']),
            'D': float(params['D_DMI']),
            'J': list(map(float, params['J_EXC'].split())),
            'K4': float(params['K4_4SPIN']),
            'K': float(params['K_MGANIS']),
            'T': 0 if params['FILEFORMAT']=='V001' else params['TEMP']
        },
    }

    for i in range(8):
        metadata['parameters'][f'J{i+1}'] = metadata['parameters']['J'][i]

    del metadata['parameters']['J']

    return metadata
