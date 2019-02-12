from tkinter import *
from tkinter import ttk, simpledialog
import tkinter as tk
from tkinter.filedialog import askopenfilename
import tkinter.scrolledtext as tkst

from easygui import diropenbox, codebox

import json
import os
from pprint import pprint, pformat
from hashlib import md5
import time
import webbrowser
from pathlib import Path
import traceback

from parameters import Parameters as P
from reportcreator import create_report
from imagetemplates import image_templates

parameterscount = 13
secnames = [
    'md', # metadata
    'xy', # XY
    'fv', # fixed variables
    'ds'  # describer
    ]
seclengths = [5, 3, parameterscount-2+6, 0]
cumul_sl = [sum(seclengths[:i]) for i in range(len(seclengths))]
secstarts = {secnames[i] : cumul_sl[i] for i in range(len(seclengths))}


class StdoutRedirector(object):
    # https://stackoverflow.com/questions/18517084/how-to-redirect-stdout-to-a-tkinter-text-widget
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert(END, string)
        self.text_space.see(END)

    def flush(self):
        pass


def debugprint(s):
    print(s, file=sys.__stdout__)


class TextDialog(simpledialog.Dialog):
    # https://stackoverflow.com/questions/35923235/is-there-a-message-box-which-displays-copy-able-text-in-python-2-7
    def __init__(self, parent, title=None, text=None):
        self.data = text
        simpledialog.Dialog.__init__(self, parent, title=title)

    def body(self, parent):
        self.geometry("1200x600")
        self.text = tk.Text(self, width=40, height=4)
        self.text.pack(fill="both", expand=True)
        self.text.insert("1.0", self.data)
        return self.text


def report_callback_exception(*args):
    err = traceback.format_exception(*args)
    err = ''.join(err)
    debugprint(err)
    TextDialog(root, title="Exception caught", text=err)


root = Tk()
root.resizable(False, False)
root.title('dmi-kmc Viewer')
root.report_callback_exception = report_callback_exception

# c = ttk.Frame(root, padding=(5, 5, 12, 0))
# c.grid(column=0, row=0, sticky=(N,W,E,S))
# root.grid_columnconfigure(0, weight=1)
# root.grid_rowconfigure(0,weight=1)

################################
# Textarea section

textarea = tkst.ScrolledText(root, width=60)
textarea.grid(column=3, row=0, rowspan=sum(seclengths), padx=3, pady=3, sticky=(N,S,E))
sys.stdout = StdoutRedirector(textarea)
# sys.stderr = StdoutRedirector(textarea)

print('*** dmi-kmc Viewer ***')
print('* Choose metadata.json')

################################
# Metadata section

tk.Label(root, text='metadata.json location:').grid(column=0, row=secstarts['md'], columnspan=2)

metadatalocvar = StringVar(root)
tk.Label(root, textvariable=metadatalocvar, relief=GROOVE).grid(column=0, row=secstarts['md'] + 1, columnspan=3)


jsondata, possiblexy = dict(), list()
def OpenFile():
    # https://gist.github.com/Yagisanatode/0d1baad4e3a871587ab1
    name = askopenfilename(initialdir=os.getcwd(),
        filetypes =(("JSON", "*.json"),("All Files","*.*")),
        title = "Choose a file"
        )
    if name=='' or name is None:
        return

    print(f'Metadata file: {Path(name)}')

    global jsondata, possiblexy
    try:
        with open(name,'r') as UseFile:
            jsondata = json.load(UseFile)

            jsondata["data_location"] = Path(jsondata["data_location"]).resolve()
            jsondata["images_location"] = Path(jsondata["images_location"]).resolve()

            print('Metadata loaded')
            print(f'{len(jsondata["data"])} files described inside')
            print(f'Data dir: {jsondata["data_location"]}')
            print(f'Images dir: {jsondata["images_location"]}')
            print('* Choose XY axis')
            metadatalocvar.set(str(Path(name)))
            imageslocvar.set(jsondata['images_location'])
    except Exception as e:
        print(e)
        print(f'*** Error while opening file: {name}')
        metadatalocvar.set('Error!')
        # xyokbutton.config(state="disabled")
        return

    il = Path(jsondata['images_location'])
    if not il.exists() or not il.is_dir():
        print('Images location doesn\'t exist')
        print('Choosing images directory may be necessary')
    else:
        print('Images location directory exists')
        imagescount = len(list(il.glob(f'*.{P.plot_format}')))
        print(f'{imagescount} images found inside')
        if not imagescount == len(jsondata['data']) * len(jsondata['plot_types']) + 2:
            print('Some images may be missing')
            print('Choosing images directory may be necessary')

    xyokbutton.config(state="normal")

    possiblexy = [k for k in jsondata['tunables'] if len(jsondata['tunables'][k]) > 1]

    # https://stackoverflow.com/questions/17580218/changing-the-options-of-a-optionmenu-when-clicking-a-button
    xvar.set(possiblexy[0])
    try:
        yvar.set(possiblexy[1])
    except IndexError:
        yvar.set(possiblexy[0])
    xchooser['menu'].delete(0, END)
    ychooser['menu'].delete(0, END)

    for choice in possiblexy:
        xchooser['menu'].add_command(label=choice, command=tk._setit(xvar, choice))
        ychooser['menu'].add_command(label=choice, command=tk._setit(yvar, choice))


ttk.Button(root, text='Choose', command=OpenFile).grid(column=2, row=secstarts['md'])
tk.Label(root, text='Images location:').grid(column=0, columnspan=2, row=secstarts['md'] + 2)


def FindImagesFolder():
    name = diropenbox(title = "Choose images directory", default=os.getcwd())
    if name is None:
        return
    if 'images_location' not in jsondata.keys():
        print('Please open metadata file first')
        textarea.see(END)
        return

    name = Path(name).resolve()
    print(f'{name}')

    jsondata['images_location'] = name
    imageslocvar.set(str(name))

    imagescount = len(list(name.glob(f'*.{P.plot_format}')))
    print(f'{imagescount} images found inside')
    if not imagescount == len(jsondata['data']) * len(jsondata['plot_types']) + 2:
        print('Some images may be missing')
        print('Choosing images directory may be necessary')


ttk.Button(root, text='Choose', command=FindImagesFolder).grid(column=2, row=secstarts['md'] + 2)

imageslocvar = StringVar()
tk.Label(root, textvariable=imageslocvar, relief=GROOVE).grid(column=0, columnspan=3, row=secstarts['md'] + 3)

ttk.Separator(root).grid(column=0, row=secstarts['md'] + 4, columnspan=3, sticky=(E,W))

################################
# XY section

tk.Label(root, text='X axis').grid(column=0, row=secstarts['xy'], ipadx=10)
tk.Label(root, text='Y axis').grid(column=1, row=secstarts['xy'], ipadx=10)

xvar = StringVar(root)
xchooser = ttk.OptionMenu(root, xvar, 'X axis variable', *possiblexy)
xchooser.grid(column=0, row=secstarts['xy'] + 1)

yvar = StringVar(root)
ychooser = ttk.OptionMenu(root, yvar, 'Y axis variable', *possiblexy)
ychooser.grid(column=1, row=secstarts['xy'] + 1)


def on_xychosen():
    xaxis, yaxis = xvar.get(), yvar.get()
    if xaxis == yaxis:
        print('*** X and Y must be different!')
        textarea.see(END)
        fixedvarsokbutton.config(state="disabled")
        for i in range(fixedvars['count']):
            fixedvars['labelvars'][i].set('---')
            fixedvars['numlabelvars'][i].set('---')
            fixedvars['omvars'][i].set('---')
            fixedvars['optionmenus'][i]['menu'].delete(0, END)
        return None

    print(f'X : {xaxis} = {sorted(list(map(float, jsondata["tunables"][xaxis].keys())))}')
    print(f'Y : {yaxis} = {sorted(list(map(float, jsondata["tunables"][yaxis].keys())))}')
    print('* Freeze other variables')

    others = {x : None for x in jsondata['tunables'].keys() if x not in (xaxis, yaxis)}
    for o in others:
        others[o] = list(jsondata['tunables'][o].keys())
        print(f'{o} : {" ".join(others[o])}')
    textarea.see(END)

    pprint(others, stream=sys.__stdout__)
    fixedvarsokbutton.config(state="normal")

    otherslist = sorted(list(others.keys()))
    for i in range(fixedvars['count']):
        o = otherslist[i]
        fixedvars['labelvars'][i].set(o)
        fixedvars['keys'][i] = o
        fixedvars['numlabelvars'][i].set(f'{str(len(others[o]))} option{"s" if len(others[o]) > 1 else ""}')

        fixedvars['omvars'][i].set(others[o][0])
        fixedvars['optionmenus'][i]['menu'].delete(0, END)

        fixedvars['optionmenus'][i].config(state='normal')
        if len(others[o]) == 1:
            fixedvars['optionmenus'][i].config(state='disabled')

        for v in others[o]:
            fixedvars['optionmenus'][i]['menu'].add_command(label=f'{v} : [{jsondata["tunables"][o][v]}]', command=tk._setit(fixedvars['omvars'][i], v))


xyokbutton = ttk.Button(root, text='Ok', command=on_xychosen, state=DISABLED)
xyokbutton.grid(column=2, row=secstarts['xy'] + 1)

ttk.Separator(root).grid(column=0, row=secstarts['xy'] + 2, columnspan=3, sticky=(E,W))

######################################
# Fixed vars section

fixedvars = {
    'keys': list(),
    'count': parameterscount - 2,
    'optionmenus': list(),
    'labelvars': list(),
    'omvars': list(),
    'numlabelvars': list()
}

for i in range(fixedvars['count']):
    lv = StringVar(root, f'<{i+1}>')
    omv = StringVar(root, '---')
    nlv = StringVar(root, '---')

    tk.Label(root, textvariable=lv).grid(column=0, row=secstarts['fv'] + i + 1)
    tk.Label(root, textvariable=nlv).grid(column=2, row=secstarts['fv'] + i + 1)

    om = ttk.OptionMenu(root, omv, '---', *list())
    om.grid(column=1, row=secstarts['fv'] + i + 1)

    fixedvars['keys'].append('')
    fixedvars['labelvars'].append(lv)
    fixedvars['optionmenus'].append(om)
    fixedvars['omvars'].append(omv)
    fixedvars['numlabelvars'].append(nlv)


def on_fixedvarschosen():
    timehash = md5()
    timehash.update(str(time.time()).encode('utf-8'))
    timehash = timehash.hexdigest()[:10]
    xaxis, yaxis = xvar.get(), yvar.get()
    others = [x for x in jsondata['tunables'].keys() if x not in (xaxis, yaxis) and len(jsondata['tunables'][x]) > 1]
    fv = ''.join(f'{k}={fixedvars["omvars"][fixedvars["keys"].index(k)].get()}_' for k in others)

    filename = f'{xaxis}vs{yaxis}_{fv}{templatevar.get()}_{timehash}.html'
    htmlnamevar.set(filename)

    passed = list()
    hashes = dict()

    condition = {
        xaxis: list(map(float, jsondata['tunables'][xaxis].keys())),
        yaxis: list(map(float, jsondata['tunables'][yaxis].keys()))
    }
    for k in jsondata['tunables']:
        if k not in (xaxis, yaxis):
            condition[k] = [float(fixedvars["omvars"][fixedvars["keys"].index(k)].get()), ]

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

    dataforreport = {
        'xaxis': xaxis,
        'yaxis': yaxis,
        'condition': condition,
        'filename': filename,
        'template': templatevar.get()
    }

    create_report(hashes, jsondata, dataforreport)
    print(f'Report created: {filename}')
    textarea.see(END)
    if openinbrowser.get():
        webbrowser.open(filename)

openinbrowser = BooleanVar(root, True)
tk.Checkbutton(root, text='Open in browser', variable=openinbrowser).grid(column=0, columnspan=2, row=secstarts['ds']-4)

fixedvarsokbutton = ttk.Button(root, text='Ok', command=on_fixedvarschosen, state=DISABLED)
fixedvarsokbutton.grid(column=2, row=secstarts['ds']-4)

tk.Label(root, text='Template:').grid(column=0, row=secstarts['ds']-3)

templatevar = StringVar(root, P.template_type)
templatechooser = ttk.OptionMenu(root, templatevar, P.template_type, *list(image_templates.keys()))
templatechooser.grid(column=1, columnspan=2, row=secstarts['ds']-3)

htmlnamevar = StringVar(root)
tk.Label(root, textvariable=htmlnamevar, relief=GROOVE).grid(column=0, row=secstarts['ds']-2, columnspan=3)

root.mainloop()
