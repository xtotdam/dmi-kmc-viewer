from pathlib import Path
from pprint import pprint
import json
import os.path
from hashlib import sha224
from tqdm import tqdm

from plotter import *
from describer import *


hexgrid_loc = Path('.')/'data'
images_loc = Path('.')/'images'


images_loc.mkdir(exist_ok=True)

def name_hash(metadata:dict) -> str:
    h = sha224()
    sm = '{seed}{steps}{version}{time}'.format(**metadata['metadata'])
    sp = ''.join((f'{{{k}}}' for k in metadata['parameters'].keys())).format(**metadata['parameters'])
    # sp = '{B}{D}{J1}{J2}{J3}{J4}{J5}{J6}{J7}{J8}{K4}{K}{T}'.format(**metadata['parameters'])
    s = sm + sp + '{cell}'.format(**metadata)
    print(s)
    h.update(s.encode('utf-8'))
    return h.hexdigest()


metadata_list = list()
for histfile in tqdm(list(hexgrid_loc.glob('history*.txt'))[:2]):
    try:
        metadata = describe(histfile)
    except Exception as e:
        print(e, 'Skipping')
        continue

    nhash = name_hash(metadata)
    metadata['namehash'] = nhash

    # TODO parallel it
    for typ in ['energy', 'steps', 'phi', 'theta', 'phi3x3', 'theta3x3']:
        plotfunc = eval('plot_' + typ)
        plotfn = str(images_loc/(nhash + '_' + typ))

        plotfunc(metadata, plotfn)
        metadata['plots'][typ] = '.'.join((plotfn, plot_format))

    metadata_list.append(metadata)

    # pprint(metadata)
json.dump(metadata_list, open('metadata.json', 'w'), indent=4, sort_keys=True)



cb = images_loc / phi_colorbar_name
if not os.path.exists(cb):
    print('Recreate phi colorbar')
    create_phi_colorbar(str(cb.resolve()))

cb = images_loc / theta_colorbar_name
if not os.path.exists(cb):
    print('Recreate theta colorbar')
    create_theta_colorbar(str(cb.resolve()))
