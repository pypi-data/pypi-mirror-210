"""
========================
Multiple exemple of how to use km3astro.plot
========================

"""

# Author: Tedjditi Hichem <htedjditi@km3net.de>


import numpy as np
import pandas as pd
import sys

import km3astro.plot as kp
from km3net_testdata import data_path


def main():

    if sys.version_info < (3, 8):
        print("ligo.skymap requires Python 3.8+")
        return

    table_read = pd.read_csv(
        data_path("astro/antares_coordinate_systems_benchmark.csv"), comment="#"
    )

    alert_type = [
        "GRB",
        "Transient",
        "Neutrino",
        "NuEM",
        "GRB",
        "GRB",
        "Transient",
        "Neutrino",
        "GRB",
        "GRB",
        "Neutrino",
        "Neutrino",
        "GRB",
        "GRB",
        "Transient",
        "GRB",
        "NuEM",
    ]
    table_read["Alert_type"] = alert_type

    _ = kp.skymap_list(
        dataframe=table_read,
        frame="equatorial",
        frame_input="UTM",
        detector="antares",
        outfile="test_plot_skymap_list_equatorial_antares.png",
    )

    _ = kp.skymap_list(
        dataframe=table_read,
        frame="galactic",
        frame_input="UTM",
        detector="orca",
        outfile="test_plot_skymap_list_galactic_orca.png",
    )

    _ = kp.skymap_alert(
        ra=80,
        dec=-20,
        obstime="2022-07-18T03:03:03",
        frame="equatorial",
        detector="orca",
        outfile="test_plot_skymap_alert_equatorial_orca.png",
    )
    _ = kp.skymap_alert(
        ra=80,
        dec=-20,
        error_radius=5,
        obstime="2022-07-18T03:03:03",
        frame="galactic",
        detector="antares",
        outfile="test_plot_skymap_alert_galactic_antares.png",
    )

    _ = kp.skymap_hpx(
        skymap_url="https://gracedb.ligo.org/api/superevents/MS230522k/files/bayestar.fits.gz,1",
        obstime="2022-07-18T03:03:03",
        nside=32,
        detector="arca",
        outfile="test_plot_skymap_hpx_arca.png",
    )


if __name__ == "__main__":
    main()
