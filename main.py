from pathlib import Path
from pprint import pprint
import json
import os.path
from hashlib import sha224
from tqdm import tqdm
import argparse

from plotter import *
from describer import *
from parameters import Parameters as P

parser = argparse.ArgumentParser(description='Describe dmi-kmc calculations results and optionally plot them')
parser.add_argument('-p', '--plot', action='store_true', help='activate plotting')
args = parser.parse_args()

if not args.plot:
    print('Skipping plotting')

hexgrid_loc = Path('.')/'data'
images_loc = Path('.')/'images'


images_loc.mkdir(exist_ok=True)

def name_hash(metadata:dict) -> str:
    h = sha224()
    sm = '{seed}{steps}{version}{time}'.format(**metadata['metadata'])
    sp = ''.join((f'{{{key}}}' for key in metadata['parameters'])).format(**metadata['parameters'])
    s = sm + sp + '{cell}'.format(**metadata)
    h.update(s.encode('utf-8'))
    return h.hexdigest()


jsondata = dict()
jsondata['data_location'] = hexgrid_loc
jsondata['images_location'] = images_loc
jsondata['plot_types'] = ['energy', 'steps', 'phi', 'theta', 'phi3x3', 'theta3x3']
jsondata['plot_format'] = P.plot_format

possible_values = dict()

metadata_list = list()
for histfile in tqdm(list(hexgrid_loc.glob('history*.txt')), ascii=True):
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

    if args.plot:
        # TODO parallel it
        for typ in jsondata['plot_types']:
            plotfunc = eval('plot_' + typ)
            plotfn = str(nhash + '_' + typ)

            plotfunc(jsondata, metadata, plotfn)
            # metadata['plots'][typ] = '.'.join((plotfn, plot_format))

    metadata_list.append(metadata)

    # pprint(metadata)

cb = jsondata['images_location'] / P.phi_colorbar_name
if not os.path.exists(cb):
    print('Recreate phi colorbar')
    create_phi_colorbar(str(cb.resolve()))

cb = jsondata['images_location'] / P.theta_colorbar_name
if not os.path.exists(cb):
    print('Recreate theta colorbar')
    create_theta_colorbar(str(cb.resolve()))


jsondata['data_location']   = str(jsondata['data_location'])
jsondata['images_location'] = str(jsondata['images_location'])
jsondata['tunables'] = {key: possible_values[key] for key in metadata['parameters']}

jsondata['data'] = metadata_list


json.dump(jsondata, open('metadata.json', 'w'), indent=4, sort_keys=True)
# print(json.dumps(jsondata, indent=4, sort_keys=True))
