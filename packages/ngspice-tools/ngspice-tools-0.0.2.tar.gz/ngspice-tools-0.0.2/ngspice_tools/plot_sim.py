"""
Module containing the command to plot data from ngspice
"""
from itertools import cycle
from .ngspice_input import parse_ngspice_sim_output
from .plot_colors import PALETTS
import matplotlib.pyplot as plt
import click


@click.command()
@click.argument(
    "infile",
    type=click.File(mode='r'))
@click.argument(
    "OUTPUT",
    type=click.Path(exists=False),
)
@click.option("-w", "--width", type=float, default=10,
              help="Width of the figure in inch (default 10)")
@click.option("-h", "--height", type=float, default=5,
              help="Height of the figure in inch (default 5)")
@click.option("-d", "--dark", is_flag=True, default=False, show_default=True,
              help="Set the plot to dark background")
@click.option("-c", "--colors",
              type=click.Choice([k for k in PALETTS.keys()],
                                case_sensitive=False), default="blue-green",
              help="choose the color palette for the lines in the plot"
              )
@click.option('-t', '--filetype',
              type=click.Choice(["svg", "png", "pdf", "jpg"],
                                case_sensitive=False),
              default="pdf",
              help="set the filetype of the image produced")
def plot_ngspice(infile: click.File, output: click.Path,
                 width: float, height: float,
                 dark: bool, colors: str, filetype: str):
    """
    Plot the variables in an ascii formatted ngspice ouptut file
    """
    if dark:
        plt.style.use('dark_background')
    clrs = cycle(PALETTS[colors])
    plot_type, title, _, simvars = parse_ngspice_sim_output(infile)
    fig, axes = plt.subplots(figsize=(width, height))
    axes.set_title(title)
    axes.set_xlabel(simvars[0]['type'] + " " + simvars[0]['unit'])
    axes.set_ylabel(simvars[1]['type'] + " " + simvars[1]['unit'])
    match plot_type:
        case "tran":
            for v in simvars[1:]:
                axes.plot(simvars[0]['data'], v['data'],
                          label=v['name'], color=next(clrs))
        case "ac":
            axes.set_xscale('log')
            for v in simvars[1:]:
                xdata = list(map(lambda x: x[0], simvars[0]['data']))
                ydata = list(map(lambda x: x[0], v['data']))
                axes.plot(xdata, ydata,
                          label=v['name'], color=next(clrs))
    fig.legend(bbox_to_anchor=(0.98, 0.8), title="Signals")
    fig.savefig(output + "." + filetype)
