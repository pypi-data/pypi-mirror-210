# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from pathlib import Path
from typing import cast

from pdkmaster.technology import primitive as _prm
from pdkmaster.io.spice import SpicePrimsParamSpec, PySpiceFactory

from .pdkmaster import tech as _tech


__all__ = ["prims_spiceparams", "pyspicefab"]


_file = Path(__file__)
_libfile = _file.parent.joinpath("models", "all.spice")
_prims = _tech.primitives
prims_spiceparams = SpicePrimsParamSpec()
for dev_name, params in (
    ("nfet_03v3", {}),
    ("pfet_03v3", {}),
    ("nfet_05v0", dict(model="nfet_06v0")),
    ("pfet_05v0", dict(model="pfet_06v0")),
):
    prims_spiceparams.add_device_params(
        prim=cast(_prm.MOSFET, _prims[dev_name]), **params,
    )
pyspicefab = PySpiceFactory(
    libfile=str(_libfile),
    corners=(
        "init",
        "typical", "ff", "ss", "fs", "sf",
    ),
    conflicts={
        "typical": ("ff", "ss", "fs", "sf"),
        "ff": ("typical", "ss", "fs", "sf"),
        "ss": ("typical", "ff", "fs", "sf"),
        "fs": ("typical", "ff", "ss", "sf"),
        "sf": ("typical", "ff", "ss", "fs"),
    },
    prims_params=prims_spiceparams,
)
