# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from typing import cast

from pdkmaster.technology import primitive as _prm
from pdkmaster.design import circuit as _ckt, layout as _lay, library as _lbry
from c4m.flexmem import SP6TSpecification, SP6TFactory, DP8TSpecification, DP8TFactory

from . import pdkmaster as _pdk, stdcell as _std

__all__ = ["Sky130SP6TFactory", "Sky130DP8TFactory"]


_prims = _pdk.tech.primitives

class Sky130SP6TFactory(SP6TFactory):
    def __init__(self, *,
        lib: _lbry.Library, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        name_prefix: str="SP6T",
    ):
        spec: SP6TSpecification = SP6TSpecification(
            name_prefix=name_prefix,
            nmos=cast(_prm.MOSFET, _prims.nfet_01v8_sc), pmos=cast(_prm.MOSFET, _prims.pfet_01v8),
            stdcelllib=_std.stdcelllib,
            pu_l=0.15, pu_w=0.42, pd_l=0.15, pd_w=0.36, pg_l=0.15, pg_w=0.36,
            precharge_w=0.42, colmux_w=4.00, writedrive_w=3.90,
            wldrive_nmos_w=0.50, wldrive_pmos_w=1.00,
            prbound=cast(_prm.Auxiliary, _prims.prBoundary),
        )

        super().__init__(lib=lib, cktfab=cktfab, layoutfab=layoutfab, spec=spec)


class Sky130DP8TFactory(DP8TFactory):
    def __init__(self, *,
        lib: _lbry.Library, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        name_prefix: str="DP8T",
    ):
        spec: DP8TSpecification = DP8TSpecification(
            name_prefix=name_prefix,
            nmos=cast(_prm.MOSFET, _prims.nfet_01v8_sc), pmos=cast(_prm.MOSFET, _prims.pfet_01v8),
            stdcelllib=_std.stdcelllib,
            pu_l=0.15, pu_w=0.42, pd_l=0.15, pd_w=0.36, pg_l=0.17, pg_w=0.36,
            precharge_w=0.42, colmux_w=4.00, writedrive_w=3.90,
            wldrive_nmos_w=0.50, wldrive_pmos_w=1.00,
            prbound=cast(_prm.Auxiliary, _prims.prBoundary),
        )

        super().__init__(lib=lib, cktfab=cktfab, layoutfab=layoutfab, spec=spec)
