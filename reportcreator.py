import json
from pathlib import Path
from pprint import pprint
from string import Template
import os, sys

from parameters import Parameters as P
from imagetemplates import image_templates

shorts = P.plot_types_shorts


def resource_path(relative_path):
    # https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def create_report(hashes:dict, jsondata:dict, dataforreport:dict):
    xaxis, yaxis = dataforreport['xaxis'], dataforreport['yaxis']
    condition = dataforreport['condition']
    filename = dataforreport['filename']
    template_type = dataforreport['template']

    others = {k:condition[k][0] for k in condition if len(condition[k]) == 1}

    description = f'''\
    Variables:
    <table>
        <tr>
            <td class="axis_desc"><b>X</b></td>
            <td class="header">{xaxis}</td>
            <td>{'</td><td>'.join(map(str, condition[xaxis]))}</td>
        </tr>
        <tr>
            <td class="axis_desc"><b>Y</b></td>
            <td class="header">{yaxis}</td>
            <td>{'</td><td>'.join(map(str, condition[yaxis]))}</td>
        </tr>
    </table>
    <br/>
    Fixed parameters:
    <table>
        <tr>
            {''.join('<td class="header">{}</td>'.format(x) for x in others)}
        </tr>
        <tr>
            {''.join('<td>{}</td>'.format(others[x]) for x in others)}
        </tr>
    </table>'''

    # imgpath = Path(jsondata['images_location']).as_uri()
    imgpath = Path(jsondata['images_location'])
    imagename_template = Template(f'{imgpath}/${{hash}}_${{type}}.{P.plot_format}')

    for i in range(len(condition[xaxis])):
        for j in range(len(condition[yaxis])):
            if (i, j) not in hashes.keys():
                hashes[(i, j)] = list()
                print(f'({i}, {j}) key is not in hashes dict')

    table = list()

    table.append('<tr>')
    table.append('<td class="header"></td>')
    for i in range(len(condition[xaxis])):
        table.append(f'<td class="header">{condition[xaxis][i]}</td>')
    table.append('</tr>')

    for j in range(len(condition[yaxis])):
        table.append('<tr>')
        table.append(f'<td class="header"><a id="{yaxis+str(condition[yaxis][j])}">{condition[yaxis][j]}</a></td>\n')

        for i in range(len(condition[xaxis])):
            table.append('<td>\n')

            for h in hashes[(i, j)]:
                table.append(image_templates[template_type].substitute(imgpath=imgpath, hash=h))
                # table.append('<br/>')
                table.append(' '.join(f'<a href="{imgpath}/{h}_{k}.{P.plot_format}" target="_blank">{shorts[k]}</a>' for k in jsondata['plot_types']))

            table.append('</td>\n')
        table.append('</tr>\n')


    # Map of numbers
    ton = [
        f'''\
<tr>
    <td colspan="2" rowspan="2"></td>
    <td class="axis_desc" colspan="{len(condition[xaxis])}">{xaxis}</td>
</tr>
<tr>'''
]

    for i in range(len(condition[xaxis])):
        ton.append(f'<td class="header">{condition[xaxis][i]}</td>')
    ton.append(f'</tr><tr><td class="axis_desc" rowspan="{len(condition[yaxis]) + 1}">{yaxis}</td>')
    for j in range(len(condition[yaxis])):
        ton.append(f'<tr><td class="header"><a href="#{yaxis+str(condition[yaxis][j])}">{condition[yaxis][j]}</a></td>')
        for i in range(len(condition[xaxis])):
            ton.append(f'<td>{len(hashes[(i, j)])}</td>')
        ton.append('</tr>\n')


    possiblevalues = ['<tr>']
    pv = {k:jsondata['tunables'][k] for k in jsondata['tunables'] if len(jsondata['tunables'][k]) > 1}
    for k in pv:
        possiblevalues.append(f'<td class="header">{k}</td>')
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
        'misc': open(resource_path('misc.html')).read(),
        'possiblevalues': ''.join(possiblevalues),
        'cssresourcepath': Path(resource_path('dmi-kmc-viewer.css')),
        'phi_colorbar_name': (Path(jsondata['images_location']) / P.phi_colorbar_name),
        'theta_colorbar_name': (Path(jsondata['images_location']) / P.theta_colorbar_name)
    }

    # if not (Path.cwd() / 'dmi-kmc-viewer.css').exists():
    with open('dmi-kmc-viewer.css', 'w') as f:
        f.write(open(resource_path('dmi-kmc-viewer.css')).read())

    with open(filename, 'w', encoding="utf-8") as html:
        html.write(
            Template(open(resource_path('template.html')).read()).safe_substitute(**substitutes)
        )
