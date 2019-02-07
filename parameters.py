# (x, y) means that in history file tagged data is in first x and last y lines
# all other is actual history
offsets = {
    'V001': (11, 1),
    'V002': (12, 1),
}


phi_colormap = 'hsv'
theta_colormap = 'PRGn'

plot_format = 'png'

phi_colorbar_name = 'colorbar_phi.png'
theta_colorbar_name = 'colorbar_theta.png'

savefig_dpi = 120


# matplotlib parameters
matplotlib_params = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Times New Roman'],
    'font.serif': ['Times New Roman'],
    'font.size': 15,
    'axes.formatter.useoffset': False,
}
