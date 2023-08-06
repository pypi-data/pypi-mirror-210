"""

LP02 Mode detector
==================

"""


def run():
    from PyMieSim.detector import LPmode

    detector = LPmode(
        mode_number="3-1",
        rotation=0.,
        sampling=700,
        NA=0.6,
        gamma_offset=0,
        phi_offset=40,
        coupling_mode='Point'
    )

    figure = detector.plot()

    figure.show(save_directory='LP31.png', window_size=(1200, 600))


if __name__ == '__main__':
    run()

# -
