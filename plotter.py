import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.gridspec as gridspec
from matplotlib.collections import PatchCollection
from matplotlib import rcParams

import numpy as np
from typing import List, Tuple
import functools
import os.path

from parameters import Parameters as P

np.set_printoptions(suppress=True)
for k in P.matplotlib_params:
    rcParams[k] = P.matplotlib_params[k]


def extract_history(jsondata:dict, metadata:dict) -> Tuple[np.ndarray, np.ndarray]:
    historylines = None
    with open(jsondata['data_location'] / metadata['files']['history']) as f:
        historylines = f.readlines()

    # historylines = open(jsondata['data_location'] / metadata['files']['history']).readlines()
    offset_top, offset_btm = P.offsets[metadata['metadata']['fileformat']]
    energy_evolution = historylines[offset_top:-offset_btm]
    del historylines

    hist, energies = list(), list()
    for line in energy_evolution:
        if line[0] == '+':
            hist.append(1)
            energies.append(float(line.strip().split()[-1]))
        else:
            hist.append(0)

    hist = np.array(hist, dtype=np.int)
    energies = np.array(energies, dtype=np.float)
    energies = np.cumsum(-energies)

    return hist, energies


def check_image_exists(f):
    def wrapper(jd:dict, md:dict, fn:str):
        ext = P.plot_format
        ffn = '.'.join((fn, ext))
        if os.path.exists(jd['images_location'] / ffn):
            print(f'{ffn} already exists')
        else:
            f(jd, md, fn)
    return wrapper


@check_image_exists
def plot_energy(jsondata:dict, metadata:dict, filename:str):
    _, energies = extract_history(jsondata, metadata)
    del _

    fig = plt.figure(figsize=(15, 4))
    ax = fig.gca()

    ax.plot(np.arange(energies.shape[0]), energies, lw=2, c='k')
    ax.set_xlabel(f'Successful steps ({energies.shape[0]} total)', rotation=0, labelpad=0, fontsize=20)
    ax.set_ylabel('Overall\n energy\n\n meV', rotation=0, ha='right', fontsize=20)
    ax.set_yticks(list(ax.get_yticks()) + [energies[-1],])
    ax.set_xlim(-energies.shape[0] * 0.01, energies.shape[0] * 1.01)
    ax.set_ylim(energies[-1] * 1.02, -energies[-1] * 0.02)
    # ax.set_title(f'At step {metadata["metadata"]["framefreq"] * ...}')

    ext = P.plot_format
    fig.savefig(jsondata['images_location'] / '.'.join((filename, ext)), format=ext, bbox_inches='tight')
    # metadata adding is possible
    plt.close()


@check_image_exists
def plot_steps(jsondata:dict, metadata:dict, filename:str):
    hist, energies = extract_history(jsondata, metadata)

    fig = plt.figure(figsize=(15, 4))
    ax = fig.gca()

    N, n = hist.shape[0], int(np.sqrt(hist.shape[0]) / 2)
    histsrc = hist[:(N // n) * n].reshape((N // n, n)).sum(axis=1)

    ax.plot(np.arange(N // n), histsrc)
    ax.axhline(c='r', lw=1)
    ax.axhline(n * 0.1, c='k', lw=1, ls='--')
    ax.axhline(n * 0.05, c='g', lw=1, ls='--')
    ax.set_xlabel(f'averaged over every {n} steps ({hist.shape[0]} steps total)', labelpad=0, fontsize=20)
    ax.set_ylabel('Number of\n successful\n steps', rotation=0, ha='right', fontsize=20)
    ax.set_xlim(0, energies.shape[0] / n * 1.00001)

    fig.canvas.draw()
    labels = [item.get_text() for item in ax.get_xticklabels()]
    labels = [int(x) * n for x in labels]
    ax.set_xticklabels(labels)

    ext = P.plot_format
    fig.savefig(jsondata['images_location'] / '.'.join((filename, ext)), format=ext, bbox_inches='tight')
    # metadata adding is possible
    plt.close()


@check_image_exists
def plot_phi(jsondata:dict, metadata:dict, filename:str):
    x,y,z,u,v,w = np.loadtxt(jsondata['data_location'] / metadata['files']['hexgrid'], skiprows=1, delimiter=',').T
    colorsuv = np.arctan2(u, v) # phi = [-pi, pi]
    colorsuv = (colorsuv + np.pi) / (2 * np.pi) # [0, 1]

    fig = plt.figure(figsize=(8, 8))
    ax = fig.gca()

    patches = list()
    for i in range(x.shape[0]):
        patches.append(mpatches.RegularPolygon((x[i], y[i]), 6, 0.58))

    collection_spins = PatchCollection(patches, facecolors=plt.get_cmap(P.phi_colormap)(colorsuv))
    ax.add_collection(collection_spins)

    xmin, xmax, ymin, ymax = x.min(), x.max(), y.min(), y.max()
    dx, dy = xmax - xmin, ymax - ymin

    ax.set_xlim(xmin - dx/25, xmax + dx/25)
    ax.set_ylim(ymin - dy/25, ymax + dy/25)
    # ax.set_title('Spin direction', ha='right', fontsize=20)

    ax.set_aspect('equal')
    ax.set_ylabel('Y', rotation=0, ha='right', fontsize=20)
    ax.set_xlabel('X', fontsize=20)

    ext = P.plot_format
    fig.savefig(jsondata['images_location'] / '.'.join((filename, ext)), format=ext, bbox_inches='tight')
    # metadata adding is possible
    plt.close()


@check_image_exists
def plot_theta(jsondata:dict, metadata:dict, filename:str):
    x,y,z,u,v,w = np.loadtxt(jsondata['data_location'] / metadata['files']['hexgrid'], skiprows=1, delimiter=',').T
    colors = np.arccos(w / np.sqrt(u**2 + v**2 + w**2)) # theta = [0, pi]
    colors /= np.pi # [0, 1]

    fig = plt.figure(figsize=(8, 8))
    ax = fig.gca()

    patches = list()
    for i in range(x.shape[0]):
        patches.append(mpatches.RegularPolygon((x[i], y[i]), 6, 0.58))

    collection_zdir = PatchCollection(patches, facecolors=plt.get_cmap(P.theta_colormap)(colors))
    ax.add_collection(collection_zdir)

    xmin, xmax, ymin, ymax = x.min(), x.max(), y.min(), y.max()
    dx, dy = xmax - xmin, ymax - ymin

    ax.set_xlim(xmin - dx/25, xmax + dx/25)
    ax.set_ylim(ymin - dy/25, ymax + dy/25)
    # ax.set_title('Z component', ha='left', fontsize=20)

    ax.set_aspect('equal')
    ax.set_ylabel('Y', rotation=0, ha='right', fontsize=20)
    ax.set_xlabel('X', fontsize=20)

    ext = P.plot_format
    fig.savefig(jsondata['images_location'] / '.'.join((filename, ext)), format=ext, bbox_inches='tight')
    # metadata adding is possible
    plt.close()


@check_image_exists
def plot_phi3x3(jsondata:dict, metadata:dict, filename:str):
    x,y,z,u,v,w = np.loadtxt(jsondata['data_location'] / metadata['files']['hexgrid'], skiprows=1, delimiter=',').T
    colorsuv = np.arctan2(u, v) # phi = [-pi, pi]
    colorsuv = (colorsuv + np.pi) / (2 * np.pi) # [0, 1]

    fig = plt.figure(figsize=(8, 8))
    ax = fig.gca()

    Nx, Ny = metadata['cell']
    patches = list()
    for dx in (-Nx, 0, Nx):
        for dy in (-Ny * 0.866, 0, Ny * 0.866):
            for i in range(x.shape[0]):
                patches.append(mpatches.RegularPolygon((x[i] + dx, y[i] + dy), 6, 0.58))

    collection_spinsp = PatchCollection(patches, facecolors=plt.get_cmap(P.phi_colormap)(colorsuv))

    ax.add_collection(collection_spinsp)

    xmin, xmax, ymin, ymax = x.min() - Nx, x.max() + Nx, y.min() - Ny * 0.866, y.max() + Ny * 0.866
    dx, dy = xmax - xmin, ymax - ymin

    ax.set_xlim(xmin - dx/25, xmax + dx/25)
    ax.set_ylim(ymin - dy/25, ymax + dy/25)

    ax.axvline(0, c='w', lw=0.3, ls='--')
    ax.axvline(Nx, c='w', lw=0.3, ls='--')
    ax.axhline(0, c='w', lw=0.3, ls='--')
    ax.axhline(Ny * 0.866, c='w', lw=0.3, ls='--')

    ax.set_aspect('equal')
    ax.set_ylabel('Y', rotation=0, ha='right', fontsize=20)
    ax.set_xlabel('X', fontsize=20)

    ext = P.plot_format
    fig.savefig(jsondata['images_location'] / '.'.join((filename, ext)), format=ext, bbox_inches='tight')
    # metadata adding is possible
    plt.close()


@check_image_exists
def plot_theta3x3(jsondata:dict, metadata:dict, filename:str):
    x,y,z,u,v,w = np.loadtxt(jsondata['data_location'] / metadata['files']['hexgrid'], skiprows=1, delimiter=',').T
    colors = np.arccos(w / np.sqrt(u**2 + v**2 + w**2)) # theta = [0, pi]
    colors /= np.pi # [0, 1]

    fig = plt.figure(figsize=(8, 8))
    ax = fig.gca()

    Nx, Ny = metadata['cell']
    patches = list()
    for dx in (-Nx, 0, Nx):
        for dy in (-Ny * 0.866, 0, Ny * 0.866):
            for i in range(x.shape[0]):
                patches.append(mpatches.RegularPolygon((x[i] + dx, y[i] + dy), 6, 0.58))

    collection_zdirp = PatchCollection(patches, facecolors=plt.get_cmap(P.theta_colormap)(colors))

    ax.add_collection(collection_zdirp)

    xmin, xmax, ymin, ymax = x.min() - Nx, x.max() + Nx, y.min() - Ny * 0.866, y.max() + Ny * 0.866
    dx, dy = xmax - xmin, ymax - ymin

    ax.set_xlim(xmin - dx/25, xmax + dx/25)
    ax.set_ylim(ymin - dy/25, ymax + dy/25)

    ax.axvline(0, c='w', lw=0.3, ls='--')
    ax.axvline(Nx, c='w', lw=0.3, ls='--')
    ax.axhline(0, c='w', lw=0.3, ls='--')
    ax.axhline(Ny * 0.866, c='w', lw=0.3, ls='--')

    ax.set_aspect('equal')
    ax.set_ylabel('Y', rotation=0, ha='right', fontsize=20)
    ax.set_xlabel('X', fontsize=20)

    ext = P.plot_format
    fig.savefig(jsondata['images_location'] / '.'.join((filename, ext)), format=ext, bbox_inches='tight')
    # metadata adding is possible
    plt.close()


def create_phi_colorbar(filename:str):
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    fig = plt.figure(figsize=(15, 0.2))
    ax = fig.gca()

    ticks = np.linspace(0, 1, 8+1) * 256
    ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(P.phi_colormap))
    ax.set_ylabel(r'$\varphi$', fontsize=20, rotation=0, ha='right', va='center')
    ax.set_xticks(ticks)
    ax.set_xticklabels([
        r'-$\pi$', r'-3$\pi$/4', r'-$\pi$/2', r'-$\pi$/4',
        r'0',
        r'$\pi$/4', r'$\pi$/2', r'3$\pi$/4', r'$\pi$'], fontsize=12)
    ax.set_yticks([])

    fig.savefig(filename, bbox_inches='tight')
    plt.close()


def create_theta_colorbar(filename:str):
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    fig = plt.figure(figsize=(15, 0.2))
    ax = fig.gca()

    ticks = np.linspace(0, 1, 4+1) * 256
    ax.imshow(gradient, aspect='auto', cmap=plt.get_cmap(P.theta_colormap))
    ax.set_ylabel(r'$\theta$', fontsize=20, rotation=0, ha='right', va='center')
    ax.set_xticks(ticks)
    ax.set_xticklabels([
        r'0', r'$\pi$/4', r'$\pi$/2', r'3$\pi$/4', r'$\pi$'], fontsize=12)
    ax.set_yticks([])

    fig.savefig(filename, bbox_inches='tight')
    plt.close()
