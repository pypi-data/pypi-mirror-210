Unreleased Changes
------------------

Version 0
---------
0.14.0 / 2023-05-22
~~~~~~~~~~~~~~~~~~~
* New SkyMap plots

* limits the dec coordinates of the error circle to [-90, 90]
0.13.5 / 2022-12-20
~~~~~~~~~~~~~~~~~~~
* limits the dec coordinates of the error circle to [-90, 90]

0.13.4 / 2022-12-20
~~~~~~~~~~~~~~~~~~~
* Optional error circle to skymap_alert via the ``error_radius=None``
  keyword

0.13.3 / 2022-11-23
~~~~~~~~~~~~~~~~~~~
* Inverts the visibility colours in ``plot_visibility()``

0.13.2 / 2022-11-03
~~~~~~~~~~~~~~~~~~~
* performance and cosmetics in SkyMap plots

0.13.1 / 2022-08-31
~~~~~~~~~~~~~~~~~~~
* fixes: skymap_hpx fig is empty

0.13.0 / 2022-08-30
~~~~~~~~~~~~~~~~~~~
* skymap_list : Removed default plot of colorbar (request from Damien)
* skymap_list : Added marker color palette if "Alert_type" is specified in dataframe (request from Jêrome)
* Added test for skymap_hpx with url input
* Added test for Alert_type color palette
* Added legend in skymap_list for Alert type

0.12.0 / 2022-08-19
~~~~~~~~~~~~~~~~~~~
* Added a save option for skymap
* skymap_* return fig by default now (for shiftertool website)
* added dataframe input option in skymap_*
* added option for the User to choose the title
* changed skymap alert color to darkgreen and darkred.
* Changed path + name to os.path.join in skymap_*
* applied change to tests and examples folder.


0.11.0 / 2022-08-04
~~~~~~~~~~~~~~~~~~~
* Skymap integration and lots of plotting tools made by Hichem!

0.10.0 / 2022-06-30
~~~~~~~~~~~~~~~~~~~
* Toolbox added, with lots of functionalities (``km3astro.toolbox``)

0.9.0 / 2022-05-02
~~~~~~~~~~~~~~~~~~
* Refactoring
* Coordinate transformation is now fully based on astropy.SkyCoord with
  a new frame designed for KM3NeT
* Bugfixes

0.8.4 / 2020-01-23
~~~~~~~~~~~~~~~~~~
* Cleanup and remove unnecessary requirements (scipy, km3pipe, ...)
* Bug fixes
* Preparation for API clean-up

0.8.3
~~~~~
* improve local -> equatorial example

0.8.2
~~~~~
* add fast sampling of times where sun is above/below horizon
* add new jenkins build
* more example
* bump all dependencies

0.8
~~~
* move a log of methods to km3pipe
* add a makefile

0.7.5
~~~~~
* add equat plotter

0.7.4
~~~~~
* bump km3pipe due to dataclass update
* polish examples a bit

0.7.3
~~~~~
* move minor stuff to km3pipe

0.7.1
~~~~~
* update examples
* fix builds
* streamline time handling

0.7
~~~
* COORDINATE FIX: what we call azimuth is actually co-azimuth
* add common sources

0.6
~~~
* add UTM coordinates
* derive arca coordinates from UTM grid

0.5
~~~
* fix lat-lon mixup bug
* add convenience methods for coord trafo

0.4.0
~~~~~
* move random sampling methods to `km3astro.random`

0.3.2
~~~~~
* add example gallery

0.3.0 / 2017-03-18
~~~~~~~~~~~~~~~~~~
* initial versioned release
* add package goodies
