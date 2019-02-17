from pathlib import Path
from datetime import timedelta
from pprint import pprint
import json
import os.path
from hashlib import sha224
import argparse
import sys

from easygui import diropenbox, indexbox
from tqdm import tqdm

from plotter import *
from parameters import Parameters as P
# from _version import __version__, __lastcommitdate__


def name_hash(metadata:dict) -> str:
    h = sha224()
    sm = '{seed}{steps}{version}{time}'.format(**metadata['metadata'])
    sp = ''.join((f'{{{key}}}' for key in metadata['parameters'])).format(**metadata['parameters'])
    s = sm + sp + '{cell}'.format(**metadata)
    h.update(s.encode('utf-8'))
    return h.hexdigest()


def describe(histfile):
    historylines = open(histfile).readlines()
    fileformatline = historylines[1].strip()
    if fileformatline.startswith('FILEFORMAT'):
        try:
            ff = fileformatline.split()[-1]
            offset_top, offset_btm = P.offsets[ff]
        except KeyError:
            raise KeyError(f'{histfile}: Unknown fileformat: {ff}. Accepted are {list(P.offsets.keys())}')
    else:
        raise Exception(f'{histfile}: Fileformat not found on 2nd line: {fileformatline}')

    paramslines = historylines[:offset_top] + historylines[-offset_btm:]
    del historylines

    params = dict()
    for line in paramslines:
        parts = line.strip().split(' ', 1)
        params[parts[0]] = parts[1]

    params['FILE'] = str(histfile)

    try:
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
            'history': Path(params['FILE']).name,
            'hexgrid': Path(params['HEXGRID']).name
        },

        'cell': list(map(int, params['CELL'].split())),

        'parameters': {
            'B': float(params['B_BIQDR']),
            'D': float(params['D_DMI']),
            'J': list(map(float, params['J_EXC'].split())),
            'K4': float(params['K4_4SPIN']),
            'K': float(params['K_MGANIS']),
            'T': 0.0 if params['FILEFORMAT']=='V001' else float(params['TEMP'])
        },
    }

    for i in range(8):
        metadata['parameters'][f'J{i+1}'] = metadata['parameters']['J'][i]
    del metadata['parameters']['J']

    return metadata


def create_metadata(data_loc:Path, images_loc:Path, metadatafilename='metadata.json', do_plot=False):
    jsondata = dict()
    jsondata['data_location'] = Path(data_loc)
    jsondata['images_location'] = Path(images_loc)
    jsondata['plot_types'] = P.plot_types
    jsondata['plot_format'] = P.plot_format

    if do_plot:
        jsondata['images_location'].mkdir(exist_ok=True)

    possible_values = dict()
    metadata_list = list()

    for histfile in tqdm(list(jsondata['data_location'].glob('history*.txt')), ascii=True):
        metadata = dict()
        try:
            metadata = describe(histfile)
        except Exception as e:
            print(e, 'Skipping')
            continue

        nhash = name_hash(metadata)
        metadata['namehash'] = nhash

        for key in metadata['parameters']:
            if key in possible_values.keys():
                if metadata['parameters'][key] in possible_values[key].keys():
                    possible_values[key][metadata['parameters'][key]] += 1
                else:
                    possible_values[key][metadata['parameters'][key]] = 1
            else:
                possible_values[key] = {metadata['parameters'][key] : 1}

        if do_plot:
            # TODO parallel it
            for typ in jsondata['plot_types']:
                plotfunc = eval('plot_' + typ)
                plotfn = str(nhash + '_' + typ)

                plotfunc(jsondata, metadata, plotfn)
                # metadata['plots'][typ] = '.'.join((plotfn, plot_format))

        metadata_list.append(metadata)
        # pprint(metadata)


    print('All files were described')

    if do_plot:
        cb = jsondata['images_location'] / P.phi_colorbar_name
        if not os.path.exists(cb):
            print('Recreating phi colorbar')
            create_phi_colorbar(str(cb.resolve()))

        cb = jsondata['images_location'] / P.theta_colorbar_name
        if not os.path.exists(cb):
            print('Recreating theta colorbar')
            create_theta_colorbar(str(cb.resolve()))

    jsondata['data_location']   = str(jsondata['data_location'])
    jsondata['images_location'] = str(jsondata['images_location'])
    jsondata['tunables'] = {key: possible_values[key] for key in metadata['parameters']}
    jsondata['data'] = metadata_list

    json.dump(jsondata, open('metadata.json', 'w'), indent=4, sort_keys=True)
    # print(json.dumps(jsondata, indent=4, sort_keys=True))

    print('metadata.json was written to disc')


def get_rel_location(wtitle):
    name = diropenbox(default=os.getcwd(), title=wtitle)
    if name is None:
        sys.exit()

    name = Path(name).resolve()
    try:
        name = name.relative_to(Path.cwd())
    except ValueError:
        pass

    return name


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='Describe dmi-kmc calculations results and optionally plot them')
    # parser.add_argument('-p', '--plot', action='store_true', help='activate plotting')
    # args = parser.parse_args()

    # data_loc = Path('.')/'data'
    # images_loc = Path('.')/'images'

    data_loc = get_rel_location('Choose data folder')
    images_loc = get_rel_location('Choose images folder')

    answer = indexbox(
        title=f'Describer',
        # title=f'Describer --- version {__version__} ({__lastcommitdate__})',
        msg=f'V001 + V002 only!\n\nData location: {data_loc}\nImages location: {images_loc}\n\nContinue?',
        choices=['Plot images', 'Don\'t plot images', 'Abort'],
        default_choice='Don\'t plot images',
        cancel_choice='Abort'
        )

    do_plot = False

    if answer == 0:
        do_plot = True
    elif answer == 1:
        do_plot = False
    elif answer == 2:
        sys.exit()
    else:
        print('Unidentified reply from indexbox:', answer)

    if not do_plot:
        print('Skipping plotting')
    else:
        images_loc.mkdir(exist_ok=True)

    create_metadata(data_loc, images_loc, metadatafilename='metadata.json', do_plot=do_plot)

    input('Press any key to exit')
