from tkinter import *
from tkinter import ttk
import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
import tkinter.scrolledtext as tkst

import json
import os
from pprint import pprint, pformat
from hashlib import md5
import time
import webbrowser
from pathlib import Path

from parameters import Parameters as P
from reportcreator import create_report

parameterscount = 13
secnames = [
    'md', # metadata
    'xy', # XY
    'fv', # fixed variables
    'ds'  # describer
    ]
seclengths = [5, 3, 13-2+4, 5]
cumul_sl = [sum(seclengths[:i]) for i in range(len(seclengths))]
secstarts = {secnames[i] : cumul_sl[i] for i in range(len(seclengths))}

root = Tk()

# c = ttk.Frame(root, padding=(5, 5, 12, 0))
# c.grid(column=0, row=0, sticky=(N,W,E,S))
# root.grid_columnconfigure(0, weight=1)
# root.grid_rowconfigure(0,weight=1)

# Textarea section

textarea = tkst.ScrolledText(root, width=60)
textarea.grid(column=3, row=0, rowspan=sum(seclengths), padx=3, pady=3, sticky=(N,S,E))
textarea.insert(END, '*** dmi-kmc Viewer ***\n')
textarea.insert(END, '* Choose metadata.json\n')

# Metadata section

metadatalabel = tk.Label(root, text='metadata.json location:')
metadatalabel.grid(column=0, row=secstarts['md'], columnspan=2)

metadatalocvar = StringVar(root)
metadatalocvar.set('')
metadatalocationlabel = tk.Label(root, textvariable=metadatalocvar, relief=GROOVE)
metadatalocationlabel.grid(column=0, row=secstarts['md'] + 1, columnspan=3)

jsondata, possiblexy = dict(), list()
def OpenFile():
    # https://gist.github.com/Yagisanatode/0d1baad4e3a871587ab1
    name = askopenfilename(initialdir=os.getcwd(),
        filetypes =(("JSON", "*.json"),("All Files","*.*")),
        title = "Choose a file"
        )

    textarea.insert(END, 'Metadata file: ' + name + '\n')

    global jsondata, possiblexy
    try:
        with open(name,'r') as UseFile:
            jsondata = json.load(UseFile)

            jsondata["data_location"] = Path(jsondata["data_location"]).resolve()
            jsondata["images_location"] = Path(jsondata["images_location"]).resolve()

            textarea.insert(END, 'Metadata loaded\n')
            textarea.insert(END, f'{len(jsondata["data"])} files described inside\n')
            textarea.insert(END, f'Data dir: {jsondata["data_location"]}\n')
            textarea.insert(END, f'Images dir: {jsondata["images_location"]}\n')
            textarea.insert(END, '* Choose XY axis\n')
            metadatalocvar.set(name)
            imageslocvar.set(jsondata['images_location'])
    except Exception as e:
        print("No file exists")
        textarea.insert(END, str(e) + '\n')
        textarea.insert(END, '*** Error while opening file:' + name + '\n')
        metadatalocvar.set('Error!')
        # xyokbutton.config(state="disabled")
        return
    finally:
        textarea.see("end")

    il = Path(jsondata['images_location'])
    if not il.exists() or not il.is_dir():
        textarea.insert(END, 'Images location doesn\'t exist\n')
        textarea.insert(END, 'Choosing images directory may be necessary\n')
    else:
        textarea.insert(END, 'Images location directory exists\n')
        imagescount = len(list(il.glob(f'*.{P.plot_format}')))
        textarea.insert(END, f'{imagescount} images found inside\n')
        if not imagescount == len(jsondata['data']) * len(jsondata['plot_types']) + 2:
            textarea.insert(END, 'Some images may be missing\n')
            textarea.insert(END, 'Choosing images directory may be necessary\n')
    textarea.see("end")

    xyokbutton.config(state="normal")

    possiblexy = [k for k in jsondata['tunables'] if len(jsondata['tunables'][k]) > 1]

    # https://stackoverflow.com/questions/17580218/changing-the-options-of-a-optionmenu-when-clicking-a-button
    xvar.set(possiblexy[0])
    try:
        yvar.set(possiblexy[1])
    except IndexError:
        yvar.set(possiblexy[0])
    xchooser['menu'].delete(0, 'end')
    ychooser['menu'].delete(0, 'end')

    for choice in possiblexy:
        xchooser['menu'].add_command(label=choice, command=tk._setit(xvar, choice))
        ychooser['menu'].add_command(label=choice, command=tk._setit(yvar, choice))

metadatabutton = ttk.Button(root, text='Choose', command=OpenFile)
metadatabutton.grid(column=2, row=secstarts['md'])

imloclabel = tk.Label(root, text='Images location (choose any file inside):')
imloclabel.grid(column=0, columnspan=2, row=secstarts['md'] + 2)

def FindImagesFolder():
    name = askopenfilename(initialdir=os.getcwd(),
        title = "Choose images directory",
        # mustexist = True
        )

    name = str(Path(name).resolve().parent)

    jsondata['images_location'] = name
    imageslocvar.set(name)

    il = Path(jsondata['images_location'])
    if not il.exists() or not il.is_dir():
        textarea.insert(END, 'Images location doesn\'t exist\n')
        textarea.insert(END, 'Choosing images directory may be necessary\n')
    else:
        textarea.insert(END, 'Images location directory exists\n')
        imagescount = len(list(il.glob(f'*.{P.plot_format}')))
        textarea.insert(END, f'{imagescount} images found inside\n')
        if not imagescount == len(jsondata['data']) * len(jsondata['plot_types']) + 2:
            textarea.insert(END, 'Some images may be missing\n')
            textarea.insert(END, 'Choosing images directory may be necessary\n')
    textarea.see("end")

imageslocbutton = ttk.Button(root, text='Choose', command=FindImagesFolder)
imageslocbutton.grid(column=2, row=secstarts['md'] + 2)

imageslocvar = StringVar()
imagesloclabel = tk.Label(root, textvariable=imageslocvar, relief=GROOVE)
imagesloclabel.grid(column=0, columnspan=3, row=secstarts['md'] + 3)

sep1 = ttk.Separator(root)
sep1.grid(column=0, row=secstarts['md'] + 4, columnspan=3, sticky=(E,W))

# XY section

xvarlabel = tk.Label(root, text='X axis')
xvarlabel.grid(column=0, row=secstarts['xy'], ipadx=10)

yvarlabel = tk.Label(root, text='Y axis')
yvarlabel.grid(column=1, row=secstarts['xy'], ipadx=10)

xvar = StringVar(root)
xchooser = ttk.OptionMenu(root, xvar, 'X axis variable', *possiblexy)
xchooser.grid(column=0, row=secstarts['xy'] + 1)

yvar = StringVar(root)
ychooser = ttk.OptionMenu(root, yvar, 'Y axis variable', *possiblexy)
ychooser.grid(column=1, row=secstarts['xy'] + 1)


def on_xychosen():
    xaxis, yaxis = xvar.get(), yvar.get()
    if xaxis == yaxis:
        textarea.insert(END, '*** X and Y must be different!\n')
        textarea.see('end')
        fixedvarsokbutton.config(state="disabled")
        for i in range(fixedvars['count']):
            fixedvars['labelvars'][i].set('---')
            fixedvars['numlabelvars'][i].set('---')
            fixedvars['omvars'][i].set('---')
            fixedvars['optionmenus'][i]['menu'].delete(0, 'end')
        return None

    textarea.insert(END, 'X : ' + xaxis + '\n')
    textarea.insert(END, 'Y : ' + yaxis + '\n')
    textarea.insert(END, '* Freeze other variables\n')

    others = {x : None for x in jsondata['tunables'].keys() if x not in (xaxis, yaxis)}
    for o in others:
        others[o] = list(jsondata['tunables'][o].keys())
        textarea.insert(END, f'{o} : {" ".join(others[o])}\n')
    textarea.see("end")

    pprint(others)
    fixedvarsokbutton.config(state="normal")

    otherslist = sorted(list(others.keys()))
    for i in range(fixedvars['count']):
        o = otherslist[i]
        fixedvars['labelvars'][i].set(o)
        fixedvars['keys'][i] = o
        fixedvars['numlabelvars'][i].set(f'{str(len(others[o]))} option{"s" if len(others[o]) > 1 else ""}')

        fixedvars['omvars'][i].set(others[o][0])
        fixedvars['optionmenus'][i]['menu'].delete(0, 'end')

        fixedvars['optionmenus'][i].config(state='normal')
        if len(others[o]) == 1:
            fixedvars['optionmenus'][i].config(state='disabled')

        for v in others[o]:
            fixedvars['optionmenus'][i]['menu'].add_command(label=f'{v} : [{jsondata["tunables"][o][v]}]', command=tk._setit(fixedvars['omvars'][i], v))

xyokbutton = ttk.Button(root, text='Ok', command=on_xychosen, state=DISABLED)
xyokbutton.grid(column=2, row=secstarts['xy'] + 1)

sep2 = ttk.Separator(root)
sep2.grid(column=0, row=secstarts['xy'] + 2, columnspan=3, sticky=(E,W))

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
    lv = StringVar(root, str(i))
    omv = StringVar(root, '---')
    nlv = StringVar(root, '0')

    l = tk.Label(root, textvariable=lv)
    om = ttk.OptionMenu(root, omv, '---', *list())
    ln = tk.Label(root, textvariable=nlv)

    l.grid(column=0, row=secstarts['fv'] + i + 1)
    om.grid(column=1, row=secstarts['fv'] + i + 1)
    ln.grid(column=2, row=secstarts['fv'] + i + 1)

    fixedvars['keys'].append('')
    fixedvars['labelvars'].append(lv)
    fixedvars['optionmenus'].append(om)
    fixedvars['omvars'].append(omv)
    fixedvars['numlabelvars'].append(nlv)

htmlnamelabel = tk.Label(root, text='', relief=GROOVE)
htmlnamelabel.grid(column=0, row=secstarts['ds']-2, columnspan=3)

def on_fixedvarschosen():
    timehash = md5()
    timehash.update(str(time.time()).encode('utf-8'))
    timehash = timehash.hexdigest()[:10]
    xaxis, yaxis = xvar.get(), yvar.get()
    others = [x for x in jsondata['tunables'].keys() if x not in (xaxis, yaxis) and len(jsondata['tunables'][x]) > 1]
    fv = ''.join(f'{k}={fixedvars["omvars"][fixedvars["keys"].index(k)].get()}_' for k in others)

    filename = f'{xaxis}vs{yaxis}_{fv}{timehash}.html'
    # filename = 'test.html'
    htmlnamelabel.config(text=filename)

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
        'filename': filename
    }

    create_report(hashes, jsondata, dataforreport)
    textarea.insert(END, f'Report created: {filename}\n')
    textarea.see('end')
    if openinbrowser.get():
        webbrowser.open(filename)

openinbrowser = BooleanVar(root)
openinbrowser.set(True)
openinbrowsercheckbox = tk.Checkbutton(root, text='Open in browser', variable=openinbrowser)
openinbrowsercheckbox.grid(column=0, columnspan=2, row=secstarts['ds']-3)

fixedvarsokbutton = ttk.Button(root, text='Ok', command=on_fixedvarschosen, state=DISABLED)
fixedvarsokbutton.grid(column=2, row=secstarts['ds']-3)

sep3 = ttk.Separator(root)
sep3.grid(column=0, row=secstarts['ds']-1, columnspan=3, sticky=(E,W))

# Describer section

describerlabel = tk.Label(root, text='Describer (WIP)', relief=RAISED)
describerlabel.grid(column=0, row=secstarts['ds'], columnspan=3)

datapathlabel = tk.Label(root, text='Data path')
datapathlabel.grid(column=0, row=secstarts['ds'] + 1, sticky=(W,))

imagespathlabel = tk.Label(root, text='Images path')
imagespathlabel.grid(column=0, row=secstarts['ds'] + 1, sticky=(W,))

plotvar = BooleanVar()
plotcheckbox = tk.Checkbutton(root, text='plot', variable=plotvar)
plotcheckbox.grid(column=0, row=secstarts['ds'] + 2)

describebutton = ttk.Button(root, text='Describe')
describebutton.grid(column=1, row=secstarts['ds'] + 2)

describeprogressbar = ttk.Progressbar(root)
describeprogressbar.grid(column=0, columnspan=3, row=secstarts['ds'] + 3, sticky=(E,W))

root.mainloop()
