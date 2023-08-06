# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from typing import cast

from pdkmaster.technology import property_ as _prp, primitive as _prm
from pdkmaster.design import circuit as _ckt, layout as _lay, library as _lbry
from pdkmaster.io.klayout import merge

from c4m.flexcell import factory as _fab

from .pdkmaster import tech, cktfab, layoutfab

__all__ = [
    "stdcell3v3canvas", "StdCell3V3Factory", "stdcell3v3lib",
    "stdcell5v0canvas", "StdCell5V0Factory", "stdcell5v0lib",
]

prims = tech.primitives


class StdCell3V3Factory(_fab.StdCellFactory):
    def __init__(self, *,
        lib: _lbry.RoutingGaugeLibrary, name_prefix: str = "", name_suffix: str = "",
    ):
        super().__init__(
            lib=lib, cktfab=cktfab, layoutfab=layoutfab,
            name_prefix=name_prefix, name_suffix=name_suffix,
            canvas=stdcell3v3canvas,
        )


stdcell3v3canvas = _fab.StdCellCanvas(
    tech=tech, lambda_=0.07,
    nmos=cast(_prm.MOSFET, prims.nfet_03v3), pmos=cast(_prm.MOSFET, prims.pfet_03v3),
)
stdcell3v3lib = _lbry.RoutingGaugeLibrary(
    name="StdCell3V3Lib", tech=tech, routinggauge=stdcell3v3canvas.routinggauge,
)
StdCell3V3Factory(lib=stdcell3v3lib).add_default()
merge(stdcell3v3lib)


class StdCell5V0Factory(_fab.StdCellFactory):
    def __init__(self, *,
        lib: _lbry.RoutingGaugeLibrary, name_prefix: str = "", name_suffix: str = "",
    ):
        super().__init__(
            lib=lib, cktfab=cktfab, layoutfab=layoutfab,
            name_prefix=name_prefix, name_suffix=name_suffix,
            canvas=stdcell5v0canvas,
        )


stdcell5v0canvas = _fab.StdCellCanvas(
    tech=tech, lambda_=0.08,
    nmos=cast(_prm.MOSFET, prims.nfet_05v0), pmos=cast(_prm.MOSFET, prims.pfet_05v0),
    l=0.6,
    inside=(cast(_prm.Insulator, prims.Dualgate), cast(_prm.Marker, prims.V5_XTOR)),
    inside_enclosure=(_prp.Enclosure(0.4), _prp.Enclosure(0.005)),
)
stdcell5v0lib = _lbry.RoutingGaugeLibrary(
    name="StdCell5V0Lib", tech=tech, routinggauge=stdcell5v0canvas.routinggauge,
)
StdCell5V0Factory(lib=stdcell5v0lib).add_default()
merge(stdcell5v0lib)
