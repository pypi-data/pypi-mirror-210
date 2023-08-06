from unittest import TestCase, skipIf

import pandas as pd
from km3net_testdata import data_path
import km3astro.toolbox as ktb
import km3astro.testing_tools as ktt
import km3astro.coord as kc
import km3astro.plot as kp

import sys


class TestPlotSkymap(TestCase):
    def test_skymap_list_deprecated(self):

        _ = kp.skymap_list(
            file0=data_path("astro/antares_coordinate_systems_benchmark.csv"),
            frame="UTM",
            detector="antares",
            plot_frame="galactic",
            detector_to="antares",
            save=True,
        )

        table_read = pd.read_csv(
            data_path("astro/antares_coordinate_systems_benchmark.csv"), comment="#"
        )
        alert_type = [
            "GRB",
            "GW",
            "Neutrino",
            "NuEM",
            "SK_SN",
            "SNEWS",
            "Transient",
            "Random",
            "GRB",
            "GW",
            "Neutrino",
            "NuEM",
            "SK_SN",
            "SNEWS",
            "Transient",
            "Random",
            "Random",
        ]

        table_read["Alert_type"] = alert_type

        _ = kp.skymap_list(
            dataframe=table_read,
            frame="UTM",
            detector="antares",
            plot_frame="equatorial",
            detector_to="antares",
            title="test_title",
            save=True,
            name="test_dataframe_input",
        )

        _ = kp.skymap_list(
            file0=data_path("astro/ORCA_coordinate_systems_benchmark.csv"),
            frame="UTM",
            detector="orca",
            plot_frame="equatorial",
            detector_to="orca",
        )

        _ = kp.skymap_list(
            file0=data_path("astro/ORCA_coordinate_systems_benchmark.csv"),
            frame="UTM",
            detector="orca",
            plot_frame="galactic",
            detector_to="orca",
        )

        _ = kp.skymap_list(
            file0=data_path("astro/ARCA_coordinate_systems_benchmark.csv"),
            frame="UTM",
            detector="arca",
            plot_frame="equatorial",
            detector_to="arca",
        )

        _ = kp.skymap_list(
            file0=data_path("astro/ARCA_coordinate_systems_benchmark.csv"),
            frame="UTM",
            detector="arca",
            plot_frame="galactic",
            detector_to="arca",
        )

    @skipIf(sys.version_info < (3, 8), "ligo.skymap requires Python 3.8+")
    def test_skymap_list(self):

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
        )

        _ = kp.skymap_list(
            dataframe=table_read,
            frame="galactic",
            frame_input="UTM",
            detector="orca",
        )

    def test_skymap_alert_deprecated(self):

        _ = kp.skymap_alert(
            file0=data_path("astro/antares_coordinate_systems_benchmark.csv"),
            frame="UTM",
            detector="antares",
            plot_frame="ParticleFrame",
            detector_to="antares",
            save=True,
        )

        _ = kp.skymap_alert(
            ra=80,
            dec=-20,
            obstime="2022-07-18T03:03:03",
            plot_frame="galactic",
            detector="orca",
            detector_to="orca",
        )

        _ = kp.skymap_alert(
            ra=80,
            dec=-20,
            obstime="2022-07-18T03:03:03",
            plot_frame="equatorial",
            detector="dummy",
            detector_to="orca",
        )

    @skipIf(sys.version_info < (3, 8), "ligo.skymap requires Python 3.8+")
    def test_skymap_alert(self):
        _ = kp.skymap_alert(
            ra=80,
            dec=-20,
            obstime="2022-07-18T03:03:03",
            frame="equatorial",
            detector="orca",
        )
        _ = kp.skymap_alert(
            ra=80,
            dec=-20,
            error_radius=5,
            obstime="2022-07-18T03:03:03",
            frame="galactic",
            detector="antares",
        )

    def test_skymap_hpx_deprecated(self):

        _ = kp.skymap_hpx(
            file0="https://gracedb.ligo.org/api/superevents/MS230522k/files/bayestar.fits.gz,1",
            save=True,
        )

    @skipIf(sys.version_info < (3, 8), "ligo.skymap requires Python 3.8+")
    def test_skymap_hpx(self):

        _ = kp.skymap_hpx(
            skymap_url="https://gracedb.ligo.org/api/superevents/MS230522k/files/bayestar.fits.gz,1",
            obstime="2022-07-18T03:03:03",
            nside=32,
            detector="antares",
        )
        _ = kp.skymap_hpx(
            skymap_url="https://gracedb.ligo.org/api/superevents/MS230522k/files/bayestar.fits.gz,1",
            obstime="2022-07-18T03:03:03",
            nside=32,
            detector="arca",
        )
