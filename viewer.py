import json
from pathlib import Path
from pprint import pprint
from string import Template
from hashlib import md5
import time

from parameters import Parameters as P
from imagetemplates import image_templates

jsondata = json.load(open('metadata.json'))

print('Choose 2 parameters for phase space from these')
print(' '.join(sorted(jsondata['tunables'])))

while True:
    # XXX
    # ans = input(' > ')
    ans = 'J1 D'
    xaxis, yaxis = ans.strip().split()
    if xaxis not in jsondata['tunables'] or yaxis not in jsondata['tunables']:
        print('Can\'t recognise axis, please repeat')
    else:
        break

condition = {
    xaxis: list(map(float, jsondata['tunables'][xaxis].keys())),
    yaxis: list(map(float, jsondata['tunables'][yaxis].keys()))
}

print(f'  X Y: {xaxis} {yaxis}')
print(f'  X ticks: {xaxis} = ' + ', '.join(map(str, condition[xaxis])))
print(f'  Y ticks: {yaxis} = ' + ', '.join(map(str, condition[yaxis])))

others = {x : None for x in jsondata['tunables'].keys() if x not in (xaxis, yaxis)}

print(f'Now fix other parameters: {" ".join(others.keys())}')
for o in others:
    if len(jsondata['tunables'][o]) > 1:
        print(f'{o}: {" ".join(jsondata["tunables"][o].keys())}')
        while True:
            # XXX
            # ans = input(' > ').strip()
            ans = '0.0'
            if ans in jsondata["tunables"][o]:
                others[o] = ans
                break
            else:
                print('Can\'t recognise, please repeat')
    else:
        print(f'{o}: {" ".join(jsondata["tunables"][o].keys())}')
        others[o] = list(jsondata["tunables"][o].keys())[0]
        # print(' > ' + others[o])

    condition[o] = [float(others[o]), ]

passed = list()
hashes = dict()

for metadata in jsondata['data']:

    passing = True
    for p in metadata['parameters']:
        if not float(metadata['parameters'][p]) in condition[p]:
            passing = False

    if passing:
        xi = condition[xaxis].index(float(metadata['parameters'][xaxis]))
        yi = condition[yaxis].index(float(metadata['parameters'][yaxis]))

        try:
            hashes[(xi, yi)].append(metadata['namehash'])
        except KeyError:
            hashes[(xi, yi)] = [metadata['namehash'], ]

        passed.append(metadata)

for k in hashes:
    hashes[k] = sorted(hashes[k])

# hashes dict is like {(i, j): [hashes], ...}
# it is everything we need to build a big html table


description = f'''\
Variables:
<table>
    <tr>
        <td class="axis_desc"><b>X</b></td>
        <th>{xaxis}</th>
        <td>{'</td><td>'.join(map(str, condition[xaxis]))}</td>
    </tr>
    <tr>
        <td class="axis_desc"><b>Y</b></td>
        <th>{yaxis}</th>
        <td>{'</td><td>'.join(map(str, condition[yaxis]))}</td>
    </tr>
</table>
<br/>
Fixed parameters:
<table>
    <tr>
        {''.join('<th>{}</th>'.format(x) for x in others)}
    </tr>
    <tr>
        {''.join('<td>{}</td>'.format(others[x]) for x in others)}
    </tr>
</table>'''

# imgpath = jsondata['images_location']
imgpath = Path('E:\\Cloud Mail.Ru\\Данные расчетов\\dmi-kmc\\14-12-18\\images').as_uri()
imagename_template = Template(f'{imgpath}/${{hash}}_${{type}}.{P.plot_format}')


table = list()

table.append('<tr>')
table.append('<th></th>')
for i in range(len(condition[xaxis])):
    table.append(f'<th>{condition[xaxis][i]}</th>')
table.append('</tr>')

for j in range(len(condition[yaxis])):
    table.append('<tr>')
    table.append(f'<th><a name="{yaxis+str(condition[yaxis][j])}">{condition[yaxis][j]}</a></th>\n')

    for i in range(len(condition[xaxis])):
        table.append('<td>\n')

        for h in hashes[(i, j)]:
            table.append(image_templates[P.template_type].substitute(imgpath=imgpath, hash=h))

        table.append('</td>\n')
    table.append('</tr>\n')


ton = ['<tr><th></th>']
for i in range(len(condition[xaxis])):
    ton.append(f'<th>{condition[xaxis][i]}</th>')
ton.append('</tr>')
for j in range(len(condition[yaxis])):
    ton.append(f'<tr><th><a href="#{yaxis+str(condition[yaxis][j])}">{condition[yaxis][j]}</a></th>')
    for i in range(len(condition[xaxis])):
        ton.append(f'<td>{len(hashes[(i, j)])}</td>')
    ton.append('</tr>\n')


possiblevalues = ['<tr>']
pv = {k:jsondata['tunables'][k] for k in jsondata['tunables'] if len(jsondata['tunables'][k]) > 1}
for k in pv:
    possiblevalues.append(f'<th>{k}</th>')
possiblevalues.append('</tr><tr>')
for k in pv:
    possiblevalues.append('<td>')
    for v in pv[k]:
        possiblevalues.append(f'{v}&nbsp;:&nbsp;{pv[k][v]}<br/>')
    possiblevalues.append('</td>')
possiblevalues.append('</tr>')


substitutes = {
    'description': description ,
    'table': ''.join(table),
    'tableofnumbers': ''.join(ton),
    'misc': open('misc.html').read(),
    'possiblevalues': ''.join(possiblevalues)
}

timehash = md5()
timehash.update(str(time.time()).encode('utf-8'))
timehash = timehash.hexdigest()[:10]
fixedvars = ''.join(f'{k}={others[k]}_' for k in list(pv.keys()) if k not in (xaxis, yaxis))

filename = f'{xaxis}vs{yaxis}_{fixedvars}{timehash}.html'
filename = 'test.html'

with open(filename, 'w') as html:
    html.write(
        Template(open('template.html').read()).safe_substitute(**substitutes)
    )
