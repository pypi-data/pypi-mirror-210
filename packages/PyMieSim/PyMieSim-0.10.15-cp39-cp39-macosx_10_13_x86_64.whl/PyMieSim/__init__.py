from .tools import measure
import numpy
import os.path
from PyMieSim.tools.directories import lp_mode_path


def load_lp_mode(mode_number, type: str = 'unstructured', sampling: int = 100):

    available_modes = ["0-1", "0-2", "0-3", "1-1", "1-2", "1-3", "2-1", "2-2", "3-1", "3-2", "4-1", "5-1"]
    available_samplings = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]

    if type.lower() == 'unstructured':
        filename = f'{mode_number}/{type}{sampling}.npy'
    elif type.lower() == 'structured':
        filename = f'{mode_number}/{type}.npy'

    file_directory = lp_mode_path.joinpath(filename)

    if not os.path.exists(file_directory):
        raise ValueError(f"""\nFile: {filename} does not exists.
                  \nThis specific LP mode with specific sampling might not be available.
                  \nAvailable modes are {available_modes} \nAvailable sampling are {available_samplings}""")

    return numpy.load(file_directory).astype(complex)
