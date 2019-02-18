from pathlib import Path
from datetime import timedelta
from pprint import pprint
import json
import os.path
from hashlib import sha224
import argparse
import sys
import shutil

from easygui import diropenbox, indexbox
from tqdm import tqdm

from plotter import *
from parameters import Parameters as P
# from _version import __version__, __lastcommitdate__


def name_hash(s:str) -> str:
    h = sha224()
    h.update(s.encode('utf-8'))
    return h.hexdigest()


def describe(histfile):
    with open(histfile, 'r') as jsonfile:
        try:
            history = json.load(jsonfile)
        except json.JSONDecodeError as e:
            print(e.msg)
            raise e

    del history['DATA']     # we don't need it now, but it is heavy

    # frames
    frames_list = list(range(history['STEPS'] // history['EVERY_STEP']))
    stepfiles = list()
    for frame in frames_list:
        try:
            l = list(Path(histfile).parent.glob(f'hexgrid2C_*{history["SEED"]}.{frame:05d}.csv'))
            if len(l) > 1:
                print(f'{histfile}: Several hexgrids found: {list(map(str, l))}. Using only first!')

            stepfiles.append({
                'step': (frame + 1) * history['EVERY_STEP'],
                'file': l[0].name,
                'namehash': name_hash(history['VERSION'] + l[0].name)
                })

        except IndexError:
            print(f'{histfile}: Hexgrid not found')
            stepfiles.append(None)


    metadata = {
        'metadata': {
            'fileformat':   history['FILEFORMAT'],
            'version':      history['VERSION'],

            'seed':         history['SEED'],

            'framefreq':    history['EVERY_STEP'],
            'steps':        history['STEPS'],
            'time':         str(timedelta(seconds=int(round(history['TIME'])))),
        },

        'files': {
            'history':      Path(histfile).name,
            'frames':       stepfiles,
        },

        'cell':             history['CELL'],

        'parameters': {
            'B':            history['B_BIQDR'],
            'D':            history['D_DMI'],
            'J':            history['J_EXC'],
            'K4':           history['K4_4SPIN'],
            'K':            history['K_MGANIS'],
            'T':            history['TEMP']
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

    for histfile in tqdm(list(jsondata['data_location'].glob('history*.json')), ascii=True):
        metadata = dict()
        try:
            metadata = describe(histfile)
        except Exception as e:
            print('\n', e, 'Skipping')
            continue

        for key in metadata['parameters']:
            if key in possible_values.keys():
                if metadata['parameters'][key] in possible_values[key].keys():
                    possible_values[key][metadata['parameters'][key]] += 1
                else:
                    possible_values[key][metadata['parameters'][key]] = 1
            else:
                possible_values[key] = {metadata['parameters'][key] : 1}

        if 'frames' not in possible_values.keys():
            possible_values['frames'] = dict()
        for frame in metadata['files']['frames']:
            s = str(frame['step'])
            if s in possible_values['frames'].keys():
                possible_values['frames'][s] += 1
            else:
                possible_values['frames'][s] = 1

        if do_plot:
            # TODO parallel it
            historyfile = jsondata['data_location'] / metadata['files']['history']
            plotfn_hash_0 = metadata['files']['frames'][0]['namehash']

            for i, frame in enumerate(metadata['files']['frames']):
                hexgridfile = jsondata['data_location'] / frame['file']
                plotfn_hash = metadata['files']['frames'][i]['namehash']

                for typ in jsondata['plot_types']:
                    plotfunc = eval('plot_' + typ)
                    plotfile = jsondata['images_location'] / f'{plotfn_hash}_{typ}.{P.plot_format}'

                    if i == 0:
                        plotfunc(historyfile, hexgridfile, plotfile, cell=metadata['cell'])
                    else:
                        if typ in P.plot_types_copyable:
                            shutil.copy(
                                jsondata['images_location'] / f'{plotfn_hash_0}_{typ}.{P.plot_format}',
                                plotfile
                                )
                            print(f'Copying 0 -> {i}: {typ}')
                        else:
                            plotfunc(historyfile, hexgridfile, plotfile, cell=metadata['cell'])

        metadata_list.append(metadata)
        # pprint(metadata)


    print('\nAll files were described')

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
    # jsondata['tunables'] = {key: possible_values[key] for key in metadata['parameters']}
    jsondata['tunables'] = possible_values
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
    cli_only = True

    if cli_only:
        parser = argparse.ArgumentParser(description='Describe dmi-kmc calculations results and optionally plot them')
        parser.add_argument('-p', '--plot', action='store_true', help='activate plotting')
        args = parser.parse_args()
        do_plot = args.plot

        data_loc = Path('.')/'data'
        images_loc = Path('.')/'images'
    else:
        data_loc = get_rel_location('Choose data folder')
        images_loc = get_rel_location('Choose images folder')

        answer = indexbox(
            title=f'Describer',
            # title=f'Describer --- version {__version__} ({__lastcommitdate__})',
            msg=f'Data location: {data_loc}\nImages location: {images_loc}\n\nContinue?',
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
