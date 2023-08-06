#!/usr/bin/env python3


def pandas():
    """Imports and returns ``pandas``."""
    try:
        import pandas
    except ImportError:
        raise ImportError(
            "install the 'pandas' package with:\n\n"
            "    pip install pandas\n\n"
            "or\n\n"
            "    conda install pandas"
        )
    else:
        return pandas


def ligoskymap():
    """Imports and returns useful imports from ``ligo.skymap``."""
    try:
        import ligo.skymap.plot
        import ligo.skymap.io as io
        import ligo.skymap.postprocess as postprocess
    except ImportError:
        raise ImportError(
            "install the 'ligo.skymap' package with:\n\n"
            "    pip install ligo.skymap\n\n"
            "or\n\n"
            "    conda install ligo.skymap"
        )
    else:
        return io, postprocess
