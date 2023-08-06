# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from pdkmaster.design import library as _lbry
from pdkmaster.io import klayout as _klio
from c4m.pdk import sky130

memlib = _lbry.Library(name="ExampleSRAMs", tech=sky130.tech)
# SP
_fab = sky130.Sky130SP6TFactory(lib=memlib, cktfab=sky130.cktfab, layoutfab=sky130.layoutfab)
# WIP: generate cells
_fab.block(address_groups=(3, 4, 2), word_size=64, we_size=8, cell_name="Block_512x64_8WE").layout
# DP
_fab = sky130.Sky130DP8TFactory(lib=memlib, cktfab=sky130.cktfab, layoutfab=sky130.layoutfab)
_fab.block(address_groups=(3, 4, 2), word_size=64, we_size=8, cell_name="Block_512x64_8WE").layout

_klio.merge(memlib)

__libs__ = (*sky130.__libs__, memlib)