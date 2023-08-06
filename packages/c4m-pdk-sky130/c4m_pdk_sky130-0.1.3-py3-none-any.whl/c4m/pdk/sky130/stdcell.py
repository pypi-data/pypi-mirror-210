# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from typing import cast

from pdkmaster.technology import primitive as _prm
from pdkmaster.design import library as _lbry
from pdkmaster.io.klayout import merge

from c4m.flexcell import factory as _fab

from .pdkmaster import tech, cktfab, layoutfab

__all__ = ["StdCellFactory", "stdcellcanvas", "stdcelllib"]

prims = tech.primitives


class StdCellFactory(_fab.StdCellFactory):
    def __init__(self, *,
        lib: _lbry.RoutingGaugeLibrary,
        name_prefix: str = "", name_suffix: str = "",
    ):
        super().__init__(
            lib=lib, cktfab=cktfab, layoutfab=layoutfab,
            name_prefix=name_prefix, name_suffix=name_suffix,
            canvas=stdcellcanvas,
        )


stdcellcanvas = _fab.StdCellCanvas(
    tech=tech, lambda_=0.05,
    nmos=cast(_prm.MOSFET, prims.nfet_01v8), pmos=cast(_prm.MOSFET, prims.pfet_01v8),
    nimplant=cast(_prm.Implant, prims.nsdm), pimplant=cast(_prm.Implant, prims.psdm),
)
stdcelllib = _lbry.RoutingGaugeLibrary(
    name="StdCellLib", tech=tech, routinggauge=stdcellcanvas.routinggauge,
)
StdCellFactory(lib=stdcelllib).add_default()
merge(stdcelllib)
