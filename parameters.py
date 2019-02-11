from dataclasses import dataclass   # for py3.6 install from pip

@dataclass(init=False, repr=True, eq=False, frozen=True)
class _Parameters:

    ### Describer parameters
    # (x, y) means that in history file tagged data is in first x and last y lines
    # all other is actual history
    offsets = {
        'V001': (11, 1),
        'V002': (12, 1),
    }


    ### Plotter parameters
    plot_types_shorts = {
        "energy": 'e',
        "steps": 's',
        "phi": '&varphi;',
        "theta": '&theta;',
        "phi3x3": '&varphi;3',
        "theta3x3": '&theta;3',
        # first movements

    }
    plot_types = list(plot_types_shorts.keys())

    phi_colormap = 'hsv'
    theta_colormap = 'PRGn'

    plot_format = 'png'

    phi_colorbar_name = 'colorbar_phi.png'
    theta_colorbar_name = 'colorbar_theta.png'

    savefig_dpi = 120

    matplotlib_params = {
        'font.family': 'sans-serif',
        'font.sans-serif': ['Times New Roman'],
        'font.serif': ['Times New Roman'],
        'font.size': 15,
        'axes.formatter.useoffset': False,
    }


    ### Viewer parameters
    image_width = 200
    template_type = 'phi+theta'

Parameters = _Parameters()

if __name__ == '__main__':
    from pprint import pprint

    fields = sorted(x for x in dir(Parameters) if not x.startswith('__'))
    params = {k : getattr(Parameters, k) for k in fields}
    pprint(params)
