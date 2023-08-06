# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+

# This is a temporary file with PLL support code. After completion it should be
# moved in the c4m.pdk.sky130 module.
from itertools import chain
from typing import Tuple, Optional, Any, cast

import numpy as _np

from pdkmaster.typing import MultiT, cast_MultiT
from pdkmaster.technology import geometry as _geo, primitive as _prm, technology_ as _tch
from pdkmaster.design import (
    circuit as _ckt, layout as _lay, cell as _cell,
)

# Temporary include private classes until we can upstream
# the
from c4m.flexcell.factory import _Cell as _FlexCell, StdCellFactory

from c4m.pdk import sky130
from c4m.pdk.sky130 import _layout as _sky130lay

_prims = sky130.tech.primitives


__all__ = [
    "VCOStage", "VCOChain", "VCO", "Div2", "Div2Chain", "OnPassGate", "PFD",
    "CurrentLimit", "MOSCap", "ChargePumpFilter", "PLL",
    "SimVCOStage", "SimVCO", "SimDiv2Chain", "SimPFD", "SimChargePumpFilter",
]


class VCOStage(_FlexCell):
    def __init__(self, *,
        fab: StdCellFactory, name: Optional[str]=None,
        nmos: Optional[_prm.MOSFET]=None, w_n: Optional[float]=None, l_n: Optional[float]=None,
        pmos: Optional[_prm.MOSFET]=None, w_p: float, l_p: Optional[float]=None,
    ):
        if name is None:
            name = self.__class__.__name__
        super().__init__(fab=fab, name=name)

        if nmos is None:
            nmos = fab.canvas.nmos
        if pmos is None:
            pmos = fab.canvas.pmos

        self.nmos = nmos
        self.w_n = w_n
        self.l_n = l_n
        self.pmos = pmos
        self.w_p = w_p
        self.l_p = l_p

        self._create_circuit()
        self._create_layout()

    def _create_circuit(self):
        nmos = self.nmos
        w_n = self.w_n
        l_n = self.l_n
        pmos = self.pmos
        w_p = self.w_p
        l_p = self.l_p

        ckt = self._ckt
        nets = ckt.nets

        mn1 = ckt.instantiate(nmos, name="mn1", w=w_n, l=l_n)
        mnc = ckt.instantiate(nmos, name="mnc", w=w_n, l=l_n)
        mn = ckt.instantiate(nmos, name="mn", w=w_n, l=l_n)
        ns = (mn1, mnc, mn)

        mp1 = ckt.instantiate(pmos, name="mp1", w=w_p, l=l_p)
        mpc = ckt.instantiate(pmos, name="mpc", w=w_p, l=l_p)
        mp = ckt.instantiate(pmos, name="mp", w=w_p, l=l_p)
        ps = (mp1, mpc, mp)

        nets.vdd.childports += (
            *(p.ports.bulk for p in ps),
            mp1.ports.sourcedrain1, mpc.ports.sourcedrain1,
        )
        nets.vss.childports += (
            *(n.ports.bulk for n in ns),
            mn1.ports.sourcedrain2, mnc.ports.sourcedrain2,
        )

        ckt.new_net(name="vctrl", external=True, childports=(
            mn1.ports.gate, mnc.ports.gate,
        ))
        ckt.new_net(name="vpgate", external=False, childports=(
            mp1.ports.gate, mpc.ports.gate,
            mp1.ports.sourcedrain2, mn1.ports.sourcedrain1,
        ))
        ckt.new_net(name="vin", external=True, childports=(
            mp.ports.gate, mn.ports.gate,
        ))
        ckt.new_net(name="vout", external=True, childports=(
            mp.ports.sourcedrain2, mn.ports.sourcedrain1,
        ))

        ckt.new_net(name="vpint", external=False, childports=(
            mpc.ports.sourcedrain2, mp.ports.sourcedrain1,
        ))
        ckt.new_net(name="vnint", external=False, childports=(
            mn.ports.sourcedrain2, mnc.ports.sourcedrain1,
        ))

    def _create_layout(self):
        canvas = self.canvas

        nwm = cast(_prm.Well, _prims.nwm)
        psdm = cast(_prm.Implant, _prims.psdm)
        nsdm = cast(_prm.Implant, _prims.nsdm)
        difftap = cast(_prm.WaferWire, _prims.difftap)
        poly = cast(_prm.GateWire, _prims.poly)
        licon = cast(_prm.Via, _prims.licon)
        li = cast(_prm.MetalWire, _prims.li)

        ckt = self.circuit
        nets = ckt.nets
        insts = ckt.instances

        placer = _sky130lay.Sky130Layouter(layouter=self._layouter)

        placer.wire(
            wire_name="psd_vpgate", net=nets.vpgate, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_well=nwm, bottom_implant=psdm,
            bottom_height=self.w_p,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.align_left(
            name="psd_vpgate", ref_value=0.5*psdm.min_space, prim=psdm,
        )
        placer.align_bottom(
            name="psd_vpgate", ref_value=canvas._well_edge_height, prim=nwm,
        )

        placer.place_to_the_right(
            name="mp1", ref_names="psd_vpgate", ignore_masks=(difftap.mask, nwm.mask),
        )
        placer.align_bottom(
            name="mp1", ref_name="psd_vpgate", prim=nwm,
        )

        placer.wire(
            wire_name="psd_vdd", net=nets.vdd, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_well=nwm, bottom_implant=psdm,
            bottom_height=self.w_p,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.place_to_the_right(
            name="psd_vdd", ref_names=("mp1", "psd_vpgate"),
            ignore_masks=(difftap.mask, nwm.mask),
        )
        placer.align_bottom(
            name="psd_vdd", ref_name="mp1", prim=nwm,
        )

        placer.place_to_the_right(
            name="mpc", ref_names="psd_vdd", ignore_masks=(difftap.mask, nwm.mask),
        )
        placer.align_bottom(
            name="mpc", ref_name="mp1", prim=nwm,
        )

        placer.place_to_the_right(
            name="mp", ref_names="mpc", ignore_masks=(difftap.mask, nwm.mask),
        )
        placer.align_bottom(
            name="mp", ref_name="mp1", prim=nwm,
        )

        placer.wire(
            wire_name="ppad_vin", net=nets.vin, wire=licon,
            bottom=poly, bottom_enclosure="tall",
            top_enclosure="tall", top_width=canvas._pin_width,
        )
        placer.align_left(
            name="ppad_vin", ref_name="mp", prim=poly, net=nets.vin,
        )
        placer.place_below(
            name="ppad_vin", ref_names="mp", ignore_masks=poly.mask,
        )

        placer.wire(
            wire_name="psd_vout", net=nets.vout, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_well=nwm, bottom_implant=psdm,
            bottom_height=self.w_p,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.place_to_the_right(
            name="psd_vout", ref_names="mp", ignore_masks=(difftap.mask, nwm.mask),
        )
        placer.align_bottom(
            name="psd_vout", ref_name="mp1", prim=nwm,
        )

        placer.wire(
            wire_name="ppad_vpgate", net=nets.vpgate, wire=licon,
            bottom=poly,
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.align_left(
            name="ppad_vpgate", ref_name="mp1", prim=poly,
        )
        placer.place_below(
            name="ppad_vpgate", ref_names=("mp1", "psd_vdd"), ignore_masks=poly.mask,
        )
        placer.connect(
            name1="ppad_vpgate", name2="mp1", prim=poly, net=nets.vpgate,
        )
        placer.connect(
            name1="ppad_vpgate", name2="mpc", prim=poly, net=nets.vpgate,
        )
        placer.connect(
            name1="ppad_vpgate", name2="psd_vpgate", prim=li, net=nets.vpgate,
        )

        placer.wire(
            wire_name="nsd_vpgate", net=nets.vpgate, wire=licon,
            bottom=difftap, bottom_implant=nsdm, bottom_height=self.w_n,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.align_left(
            name="nsd_vpgate", ref_value=0.5*nsdm.min_space, prim=nsdm,
        )
        placer.align_top(
            name="nsd_vpgate", ref_name="mn1", prim=difftap,
        )
        placer.connect(
            name1="nsd_vpgate", name2="psd_vpgate", prim=li, net=nets.vpgate,
        )

        placer.wire(
            wire_name="ppad_vctrl", net=nets.vctrl, wire=licon,
            bottom=poly,
            bottom_enclosure="wide", top_enclosure="wide",
            top_height=canvas._pin_width,
        )
        placer.place_to_the_right(
            name="ppad_vctrl", ref_names=("nsd_vpgate", "psd_vpgate"),
        )
        placer.place_below(
            name="ppad_vctrl", ref_names=("mp1", "ppad_vpgate"),
        )

        placer.wire(
            wire_name="poly_vctrl_l", net=nets.vctrl, wire=poly,
            ref_width="mn1", ref_height="ppad_vctrl"
        )
        placer.align_left(
            name="poly_vctrl_l", ref_name="mn1", prim=poly, net=nets.vctrl,
        )
        placer.align_top(
            name="poly_vctrl_l", ref_name="ppad_vctrl", prim=poly, net=nets.vctrl,
        )
        placer.connect(
            name1="poly_vctrl_l", name2="mn1", prim=poly, net=nets.vctrl,
        )

        placer.wire(
            wire_name="poly_vctrl_r", net=nets.vctrl, wire=poly,
            ref_width="mn1", ref_height="ppad_vctrl"
        )
        placer.align_right(
            name="poly_vctrl_r", ref_name="mnc", prim=poly, net=nets.vctrl,
        )
        placer.align_top(
            name="poly_vctrl_r", ref_name="ppad_vctrl", prim=poly, net=nets.vctrl,
        )
        placer.connect(
            name1="poly_vctrl_r", name2="mnc", prim=poly, net=nets.vctrl,
        )

        placer.place_to_the_right(
            name="mn1", ref_names="nsd_vpgate", ignore_masks=difftap.mask,
        )
        placer.place_below(
            name="mn1", ref_names="ppad_vctrl", ignore_masks=poly.mask,
        )

        placer.wire(
            wire_name="nsd_vss", net=nets.vss, wire=licon,
            bottom=difftap, bottom_implant=nsdm, bottom_height=self.w_n,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.place_to_the_right(
            name="nsd_vss", ref_names=("mn1", "nsd_vpgate"),
            ignore_masks=(difftap.mask, nwm.mask),
        )
        placer.align_bottom(
            name="nsd_vss", ref_name="mn1", prim=difftap,
        )

        placer.place_to_the_right(
            name="mnc", ref_names="nsd_vss", ignore_masks=difftap.mask,
        )
        placer.align_bottom(
            name="mnc", ref_name="mn1", prim=difftap,
        )

        placer.place_to_the_right(
            name="mn", ref_names=("mnc", "nsd_vss"), ignore_masks=difftap.mask,
        )
        placer.align_bottom(
            name="mn", ref_name="mn1", prim=difftap,
        )
        placer.connect(
            name1="mn", name2="mp", prim=poly, net=nets.vin,
        )
        placer.wire(
            wire_name="nsd_vout", net=nets.vout, wire=licon,
            bottom=difftap, bottom_implant=nsdm, bottom_height=self.w_n,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.place_to_the_right(
            name="nsd_vout", ref_names="mn", ignore_masks=difftap.mask,
        )
        placer.align_bottom(
            name="nsd_vout", ref_name="mn1", prim=difftap,
        )

        placer.wire(
            wire_name="li_vout_b", net=nets.vout, wire=li,
            ref_height="nsd_vout",
        )
        placer.place_to_the_right(
            name="li_vout_b", ref_names="ppad_vin",
        )
        placer.align_bottom(
            name="li_vout_b", ref_name="nsd_vout", prim=li, net=nets.vout,
        )
        placer.connect(
            name1="li_vout_b", name2="nsd_vout", prim=li, net=nets.vout,
        )

        placer.wire(
            wire_name="li_vout_t", net=nets.vout, wire=li,
            ref_height="psd_vout",
        )
        placer.place_to_the_right(
            name="li_vout_t", ref_names="ppad_vin",
        )
        placer.align_top(
            name="li_vout_t", ref_name="psd_vout", prim=li, net=nets.vout,
        )
        placer.connect(
            name1="li_vout_t", name2="psd_vout", prim=li, net=nets.vout,
        )
        placer.connect(
            name1="li_vout_t", name2="li_vout_b", prim=li, net=nets.vout,
        )

        placer.wire(
            wire_name="li_vss", net=nets.vss, wire=li, ref_width="nsd_vss",
        )
        placer.center_x(
            name="li_vss", ref_name="nsd_vss", prim=li, net=nets.vss,
        )
        placer.align_bottom(
            name="li_vss", ref_value=0.0, prim=li, net=nets.vss,
        )
        placer.connect(
            name1="li_vss", name2="nsd_vss", prim=li, net=nets.vss,
        )

        placer.wire(
            wire_name="li_vdd", net=nets.vdd, wire=li, ref_width="psd_vdd",
        )
        placer.center_x(
            name="li_vdd", ref_name="psd_vdd", prim=li, net=nets.vdd,
        )
        placer.align_top(
            name="li_vdd", ref_value=canvas._cell_height, prim=li, net=nets.vdd,
        )
        placer.connect(
            name1="li_vdd", name2="psd_vdd", prim=li, net=nets.vdd,
        )

        if not placer.execute():
            print("Unexecuted placements")
            # raise RuntimeError("Unexecuted placements")

        # Add pins
        # TODO: this should be able to be done by the wire, connect etc.
        layout = self._layouter.layout
        assert li.pin is not None
        lipin = li.pin

        # vctrl
        bb1 = placer.info_lookup["ppad_vctrl"].bb(mask=li.mask, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup["ppad_vpgate"].bb(mask=li.mask, placed=True)
        assert bb2 is not None
        bb3 = placer.info_lookup["ppad_vin"].bb(mask=li.mask, placed=True)
        assert bb3 is not None
        bb4 = placer.info_lookup["nsd_vss"].bb(mask=li.mask, placed=True)
        assert bb4 is not None
        shape = _geo.Rect(
            left=bb1.left, bottom=(bb4.top + li.min_space),
            right=(bb3.left - li.min_space), top=(bb2.bottom - li.min_space),
        )
        layout.add_shape(layer=li, net=nets.vctrl, shape=shape)
        layout.add_shape(layer=lipin, net=nets.vctrl, shape=shape)

        # vin
        bb1 = placer.info_lookup["ppad_vin"].bb(mask=li.mask, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup["nsd_vout"].bb(mask=li.mask, placed=True)
        assert bb2 is not None
        shape = _geo.Rect.from_rect(rect=bb1, bottom=(bb2.top + li.min_space))
        layout.add_shape(layer=li, net=nets.vin, shape=shape)
        layout.add_shape(layer=lipin, net=nets.vin, shape=shape)

        # vout
        bb1 = placer.info_lookup["li_vout_b"].bb(mask=li.mask, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup["li_vout_t"].bb(mask=li.mask, placed=True)
        assert bb2 is not None
        shape = _geo.Rect.from_rect(rect=bb1, top=bb2.top)
        layout.add_shape(layer=lipin, net=nets.vout, shape=shape)

        # Compute cell width
        right = []

        info = placer.info_lookup["psd_vout"]
        bb = info.bb(mask=psdm.mask, placed=True)
        assert bb is not None
        right.append(bb.right + 0.5*psdm.min_space)

        info = placer.info_lookup["nsd_vout"]
        bb = info.bb(mask=nsdm.mask, placed=True)
        assert bb is not None
        right.append(bb.right + 0.5*nsdm.min_space)

        info = placer.info_lookup["li_vout_b"]
        bb = info.bb(mask=li.mask, placed=True)
        assert bb is not None
        right.append(bb.right + 0.5*li.min_space)

        self.set_width(min_width=max(right))


class VCOChain(_cell.OnDemandCell):
    def __init__(self, *,
        name: Optional[str]=None,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        stage: VCOStage, n_stages: int,
    ):
        if name is None:
            name = self.__class__.__name__
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        self.stage = stage
        self.n_stages = n_stages

    def _create_circuit(self):
        stage_cell = self.stage
        n_stages = self.n_stages

        chain = self.new_circuit()

        stages = tuple(
            chain.instantiate(stage_cell, name=f"stage[{n}]")
            for n in range(n_stages)
        )

        chain.new_net(name="vdd", external=True, childports=(
            stage.ports.vdd for stage in stages
        ))
        chain.new_net(name="vss", external=True, childports=(
            stage.ports.vss for stage in stages
        ))

        chain.new_net(name="vctrl", external=True, childports=(
            stage.ports.vctrl for stage in stages
        ))

        nets = tuple(
            chain.new_net(
                name=(
                    "vin" if n == 0
                    else "vout" if n == n_stages
                    else f"node[{n}]"
                ),
                external=((n == 0) or (n == n_stages)),
            )
            for n in range(n_stages + 1)
        )
        for n, stage in enumerate(stages):
            nets[n].childports += stage.ports.vin
            nets[n+1].childports += stage.ports.vout

    def _create_layout(self):
        layouter = self.new_circuitlayouter()
        placer = _sky130lay.Sky130Layouter(layouter=layouter)

        ckt = self.circuit
        nets = ckt.nets

        li = cast(_prm.MetalWire, _prims.li)
        mcon = cast(_prm.Via, _prims.mcon)
        m1 = cast(_prm.MetalWire, _prims.m1)
        assert m1.pin is not None
        m1pin = m1.pin

        prev_vin = None
        for n in range(self.n_stages):
            inst_name = f"stage[{n}]"
            placer.place_at_bottom(name=inst_name)
            if n == 0:
                placer.place_at_left(name=inst_name)
            else:
                prev_name = f"stage[{n - 1}]"
                placer.place_to_the_right(name=inst_name, ref_names=prev_name, boundary_only=True)

            vctrl_name = f"mcon_vctrl[{n}]"
            placer.wire(
                wire_name=vctrl_name, net=nets.vctrl, wire=mcon,
                bottom_enclosure="wide", top_enclosure="wide",
            )
            placer.align_left(
                name=vctrl_name, ref_name=inst_name, ref_pin=True, prim=li, net=nets.vctrl,
            )
            placer.align_bottom(
                name=vctrl_name, ref_name=inst_name, ref_pin=True, prim=li, net=nets.vctrl,
            )

            if n == 0:
                prev_vin = vin_name = "mcon_vin"
                # Draw vin mcon
                placer.wire(
                    wire_name=vin_name, net=nets.vin, wire=mcon,
                    bottom_enclosure="wide", top_enclosure="tall",
                )
                placer.align_right(
                    name=vin_name, ref_name=inst_name, prim=li, net=nets.vin,
                )
                placer.align_top(
                    name=vin_name, ref_name=inst_name, prim=li, net=nets.vin,
                )
            elif n < (self.n_stages - 1):
                # Draw node[n + 1]
                assert prev_vin is not None
                net_name = f"node[{n + 1}]"
                net = nets[net_name]
                inst2_name = f"stage[{n + 1}]"

                vout_name = f"mcon_{net_name}_vout"
                placer.wire(
                    wire_name=vout_name, net=net, wire=mcon,
                    bottom_enclosure="wide", top_enclosure="tall",
                )
                placer.place_to_the_right(
                    name=vout_name, ref_names=prev_vin,
                )
                placer.align_top(
                    name=vout_name, ref_name=prev_vin, prim=li,
                )

                prev_vin = vin_name = f"mcon_{net_name}_vin"
                placer.wire(
                    wire_name=vin_name, net=net, wire=mcon,
                    bottom_enclosure="wide", top_enclosure="tall",
                )
                placer.align_right(
                    name=vin_name, ref_name=inst2_name, prim=li, net=net,
                )
                placer.align_top(
                    name=vin_name, ref_name=inst2_name, prim=li, net=net,
                )

                placer.connect(
                    name1=vout_name, name2=vin_name, prim=m1, net=net,
                )
            else:
                assert n == (self.n_stages - 1)
                assert prev_vin is not None

                vout_name = f"mcon_vout"
                placer.wire(
                    wire_name=vout_name, net=nets.vout, wire=mcon,
                    bottom_enclosure="wide", top_enclosure="tall",
                )
                placer.place_to_the_right(
                    name=vout_name, ref_names=prev_vin,
                )
                placer.align_top(
                    name=vout_name, ref_name=prev_vin, prim=li,
                )

        if not placer.execute():
            print("VCOChain: not all placements done")

        # pins
        layout = layouter.layout

        # vctrl
        bb1 = placer.info_lookup[
            "mcon_vctrl[0]"].bb(mask=m1.mask, net=nets.vctrl, placed=True,
        )
        assert bb1 is not None
        bb2 = placer.info_lookup[
            f"mcon_vctrl[{self.n_stages - 1}]"].bb(mask=m1.mask, net=nets.vctrl,
            placed=True,
        )
        assert bb2 is not None
        shape = _geo.Rect.from_rect(rect=bb1, right=bb2.right)
        layout.add_shape(layer=m1, net=nets.vctrl, shape=shape)
        layout.add_shape(layer=m1pin, net=nets.vctrl, shape=shape)

        # vin
        bb = placer.info_lookup["mcon_vin"].bb(
            mask=m1.mask, net=nets.vin, placed=True,
        )
        assert bb is not None
        layout.add_shape(layer=m1pin, net=nets.vin, shape=bb)

        # vout
        bb = placer.info_lookup["mcon_vout"].bb(
            mask=m1.mask, net=nets.vout, placed=True,
        )
        assert bb is not None
        layout.add_shape(layer=m1pin, net=nets.vout, shape=bb)


class VCO(_cell.OnDemandCell):
    def __init__(self, *,
        name: Optional[str]=None,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        chain: VCOChain,
    ):
        if name is None:
            name = self.__class__.__name__
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        self.chain = chain

    def _create_circuit(self):
        chain_cell = self.chain

        ckt = self.new_circuit()

        chain = ckt.instantiate(chain_cell, name="chain")

        ckt.new_net(name="vdd", external=True, childports=chain.ports.vdd)
        ckt.new_net(name="vss", external=True, childports=chain.ports.vss)

        ckt.new_net(name="vctrl", external=True, childports=chain.ports.vctrl)
        # Cnnnect chain as ring oscillator and set that as output signal
        ckt.new_net(name="vout", external=True, childports=(
            chain.ports.vin, chain.ports.vout,
        ))

    def _create_layout(self):
        layouter = self.new_circuitlayouter()
        placer = _sky130lay.Sky130Layouter(layouter=layouter)

        ckt = self.circuit
        nets = ckt.nets

        m1 = cast(_prm.MetalWire, _prims.m1)
        assert m1.pin is not None
        m1pin = m1.pin

        placer.place_at_bottom(name="chain")
        placer.place_at_left(name="chain")

        # vctrl
        placer.wire(
            wire_name="m1_vctrl", net=nets.vctrl, wire=m1,
            ref_width="chain", ref_height="chain",
        )
        placer.align_left(
            name="m1_vctrl", ref_name="chain", ref_pin=True, prim=m1, net=nets.vctrl,
        )
        placer.align_bottom(
            name="m1_vctrl", ref_name="chain", ref_pin=True, prim=m1, net=nets.vctrl,
        )

        # vout
        placer.wire(
            wire_name="m1_vout_l", net=nets.vout, wire=m1,
            ref_height="chain",
        )
        placer.align_left(
            name="m1_vout_l", ref_name="chain", ref_pin=True, prim=m1, net=nets.vout,
        )
        placer.place_above(
            name="m1_vout_l", ref_names="chain", use_boundary=False, extra_space=m1.min_space,
        )

        placer.wire(
            wire_name="m1_vout_r", net=nets.vout, wire=m1,
            ref_height="chain",
        )
        placer.align_right(
            name="m1_vout_r", ref_name="chain", ref_pin=True, prim=m1, net=nets.vout,
        )
        placer.align_top(
            name="m1_vout_r", ref_name="m1_vout_l", prim=m1, net=nets.vout,
        )

        placer.connect(
            name1="m1_vout_l", name2="chain", prim=m1, net=nets.vout
        )
        placer.connect(
            name1="m1_vout_r", name2="chain", prim=m1, net=nets.vout
        )

        if not placer.execute():
            print("VCO: not all placements executed")

        # pins
        layout = layouter.layout

        # vctrl
        bb = placer.info_lookup["m1_vctrl"].bb(mask=m1.mask, net=nets.vctrl, placed=True)
        assert bb is not None
        layout.add_shape(layer=m1pin, net=nets.vctrl, shape=bb)

        # vout
        bb1 = placer.info_lookup["m1_vout_l"].bb(mask=m1.mask, net=nets.vout, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup["m1_vout_r"].bb(mask=m1.mask, net=nets.vout, placed=True)
        assert bb2 is not None
        shape = _geo.Rect.from_rect(rect=bb1, right=bb2.right)
        layout.add_shape(layer=m1, net=nets.vout, shape=shape)
        layout.add_shape(layer=m1pin, net=nets.vout, shape=shape)


class Div2(_cell.OnDemandCell):
    def __init__(self, *,
        name: Optional[str]=None,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        ff: _cell.Cell, inv: _cell.Cell,
    ):
        if name is None:
            name = self.__class__.__name__
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        self.ff = ff
        self.inv = inv

    def _create_circuit(self):
        ff_cell = self.ff
        inv_cell = self.inv

        ckt = self.new_circuit()

        ff = ckt.instantiate(ff_cell, name="ff")
        inv = ckt.instantiate(inv_cell, name="inv")

        ckt.new_net(name="vdd", external=True, childports=(
            ff.ports.vdd, inv.ports.vdd,
        ))
        ckt.new_net(name="vss", external=True, childports=(
            ff.ports.vss, inv.ports.vss,
        ))

        ckt.new_net(name="sig", external=True, childports=ff.ports.ck)
        ckt.new_net(name="div2", external=True, childports=(
            ff.ports.q, inv.ports.i,
        ))

        ckt.new_net(name="n", external=False, childports=(
            inv.ports.nq, ff.ports.i,
        ))

    def _create_layout(self):
        layouter = self.new_circuitlayouter()
        placer = _sky130lay.Sky130Layouter(layouter=layouter)

        ckt = self.circuit
        nets = ckt.nets

        li = cast(_prm.MetalWire, _prims.li)
        assert li.pin is not None
        lipin = li.pin
        mcon = cast(_prm.Via, _prims.mcon)
        m1 = cast(_prm.MetalWire, _prims.m1)
        assert m1.pin is not None
        m1pin = m1.pin

        lipin_width = self.tech.computed.min_width(
            primitive=li, up=True, down=True, min_enclosure=True,
        )

        placer.place_at_bottom(name="ff")
        placer.place_at_left(name="ff")

        placer.place_at_bottom(name="inv")
        placer.place_to_the_right(
            name="inv", ref_names="ff", boundary_only=True,
        )

        placer.wire(
            wire_name="li_sig", net=nets.sig, wire=li,
            width=lipin_width, ref_height="ff",
        )
        placer.align_right(
            name="li_sig", ref_name="ff", ref_pin=True, prim=li, net=nets.sig,
        )
        placer.align_top(
            name="li_sig", ref_name="ff", ref_pin=True, prim=li, net=nets.sig,
        )

        placer.wire(
            wire_name="mcon_div2_ff", net=nets.div2, wire=mcon,
        )
        placer.align_right(
            name="mcon_div2_ff", ref_name="ff", ref_pin=True, prim=li, net=nets.div2,
        )
        placer.center_y(
            name="mcon_div2_ff", ref_name="ff", ref_pin=True, prim=li, net=nets.div2,
        )

        placer.wire(
            wire_name="mcon_div2_inv", net=nets.div2, wire=mcon,
        )
        placer.align_left(
            name="mcon_div2_inv", ref_name="inv", ref_pin=True, prim=li, net=nets.div2,
        )
        placer.center_y(
            name="mcon_div2_inv", ref_name="mcon_div2_ff", prim=li, net=nets.div2,
        )

        placer.wire(
            wire_name="mcon_n_ff", net=nets.n, wire=mcon,
        )
        placer.align_right(
            name="mcon_n_ff", ref_name="ff", ref_pin=True, prim=li, net=nets.n,
        )
        placer.place_above(
            name="mcon_n_ff", ref_names="mcon_div2_ff", extra_space=m1.min_space,
        )

        placer.wire(
            wire_name="mcon_n_inv", net=nets.n, wire=mcon,
        )
        placer.align_left(
            name="mcon_n_inv", ref_name="inv", ref_pin=True, prim=li, net=nets.n,
        )
        placer.align_bottom(
            name="mcon_n_inv", ref_name="mcon_n_ff", prim=li, net=nets.n,
        )

        placer.connect(
            name1="mcon_n_ff", name2="mcon_n_inv", prim=m1, net=nets.n,
        )

        if not placer.execute():
            print("Div2: Not all placements executed")

        # pins
        layout = layouter.layout

        # sig
        bb = placer.info_lookup["li_sig"].bb(mask=li.mask, net=nets.sig, placed=True)
        assert bb is not None
        layout.add_shape(layer=lipin, net=nets.sig, shape=bb)

        # div2
        bb1 = placer.info_lookup["mcon_div2_ff"].bb(
            mask=m1.mask, net=nets.div2, placed=True,
        )
        assert bb1 is not None
        bb2 = placer.info_lookup["mcon_div2_inv"].bb(
            mask=m1.mask, net=nets.div2, placed=True,
        )
        assert bb2 is not None
        shape = _geo.Rect.from_rect(rect=bb1, right=bb2.right)
        layout.add_shape(layer=m1, net=nets.div2, shape=shape)
        layout.add_shape(layer=m1pin, net=nets.div2, shape=shape)


class Div2Chain(_cell.OnDemandCell):
    def __init__(self, *,
        name: Optional[str]=None,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        div: Div2, n_stages: int,
    ):
        assert n_stages > 0
        if name is None:
            name = f"{div.name}Chain"
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        self.div = div
        self.n_stages = n_stages

    def _create_circuit(self):
        div_cell = self.div
        n_stages = self.n_stages

        ckt = self.new_circuit()

        stages = tuple(
            ckt.instantiate(div_cell, name=f"stage[{n}]")
            for n in range(n_stages)
        )

        ckt.new_net(name="vdd", external=True, childports=(
            stage.ports.vdd for stage in stages
        ))
        ckt.new_net(name="vss", external=True, childports=(
            stage.ports.vss for stage in stages
        ))

        ckt.new_net(name="sig", external=True, childports=stages[0].ports.sig)
        div_nets = tuple(
            ckt.new_net(
                name=f"div{2**(n + 1)}", external=True,
                childports=stages[n].ports.div2,
            ) for n in range(n_stages)
        )
        # Connect net to sig input of the stages
        for n in range(n_stages - 1):
            div_nets[n].childports += stages[n + 1].ports.sig

    def _create_layout(self):
        layouter = self.new_circuitlayouter()
        placer = _sky130lay.Sky130Layouter(layouter=layouter)

        ckt = self.circuit
        nets = ckt.nets

        li = cast(_prm.MetalWire, _prims.li)
        assert li.pin is not None
        lipin = li.pin
        mcon = cast(_prm.Via, _prims.mcon)
        m1 = cast(_prm.MetalWire, _prims.m1)
        assert m1.pin is not None
        m1pin = m1.pin

        lipin_width = self.tech.computed.min_width(
            primitive=li, up=True, down=True, min_enclosure=True,
        )

        for n in range(self.n_stages):
            inst_name = f"stage[{n}]"
            placer.place_at_bottom(name=inst_name)
            if n == 0:
                placer.place_at_left(name=inst_name)
            else:
                previnst_name = f"stage[{n - 1}]"
                placer.place_to_the_right(
                    name=inst_name, ref_names=previnst_name, boundary_only=True,
                )

            if n == 0:
                placer.wire(
                    wire_name="li_sig", net=nets.sig, wire=li,
                    width=lipin_width, ref_height=inst_name,
                )
                placer.align_right(
                    name="li_sig", ref_name=inst_name, ref_pin=True,
                    prim=li, net=nets.sig,
                )
                placer.center_y(
                    name="li_sig", ref_name=inst_name, ref_pin=True,
                    prim=li, net=nets.sig,
                )

            if n < (self.n_stages - 1):
                net_name = f"div{2**(n + 1)}"
                net = nets[net_name]

                nextinst_name = f"stage[{n + 1}]"

                wire_name = f"mcon_{net_name}_{nextinst_name}"
                placer.wire(
                    wire_name=wire_name, net=net, wire=mcon,
                    bottom_enclosure="tall", top_enclosure="wide",
                )
                placer.align_right(
                    name=wire_name, ref_name=nextinst_name, ref_pin=True,
                    prim=li, net=net,
                )
                placer.center_y(
                    name=wire_name, ref_name=inst_name, ref_pin=True,
                    prim=m1, net=net,
                )

                placer.connect(
                    name1=wire_name, name2=inst_name, prim=m1, net=net,
                )

        if not placer.execute():
            print("Div2Chain: not all placements completed")

        # pins
        layout = layouter.layout

        # sig
        bb = placer.info_lookup["li_sig"].bb(mask=li.mask, net=nets.sig, placed=True)
        assert bb is not None
        layout.add_shape(layer=lipin, net=nets.sig, shape=bb)

        # div*
        for n in range(self.n_stages):
            net = nets[f"div{2**(n + 1)}"]
            inst_name = f"stage[{n}]"

            bb = placer.info_lookup[inst_name].bb(mask=m1pin.mask, net=net, placed=True)
            assert bb is not None
            layout.add_shape(layer=m1pin, net=net, shape=bb)


class OnPassGate(_FlexCell):
    """Always on pass gate used for internal delay"""
    def __init__(self, *,
        fab: StdCellFactory, name: Optional[str]=None,
        npass: Optional[_prm.MOSFET]=None, w_npass: float,
        ppass: Optional[_prm.MOSFET]=None, w_ppass: float,
    ):
        if name is None:
            name = self.__class__.__name__
        super().__init__(fab=fab, name=name)

        if npass is None:
            npass = fab.canvas.nmos
        if ppass is None:
            ppass = fab.canvas.pmos

        self.npass = npass
        self.w_npass = w_npass
        self.ppass = ppass
        self.w_ppass = w_ppass

        self._create_circuit()
        self._create_layout()

    def _create_circuit(self):
        npass_trans = self.npass
        w_npass = self.w_npass
        ppass_trans = self.ppass
        w_ppass = self.w_ppass

        ckt = self.circuit
        nets = ckt.nets

        npass = ckt.instantiate(npass_trans, name="npass", w=w_npass)
        ppass = ckt.instantiate(ppass_trans, name="ppass", w=w_ppass)

        nets.vdd.childports += (ppass.ports.bulk, npass.ports.gate)
        nets.vss.childports += (npass.ports.bulk, ppass.ports.gate)

        ckt.new_net(name="i", external=True, childports=(
            npass.ports.sourcedrain1, ppass.ports.sourcedrain1,
        ))
        ckt.new_net(name="o", external=True, childports=(
            npass.ports.sourcedrain2, ppass.ports.sourcedrain2,
        ))

    def _create_layout(self):
        layouter = self._layouter
        placer = _sky130lay.Sky130Layouter(layouter=layouter)

        canvas = self.canvas

        ckt = self.circuit
        nets = ckt.nets

        nwm = cast(_prm.Well, _prims.nwm)
        nsdm = cast(_prm.Implant, _prims.nsdm)
        psdm = cast(_prm.Implant, _prims.psdm)
        difftap = cast(_prm.WaferWire, _prims.difftap)
        poly = cast(_prm.GateWire, _prims.poly)
        licon = cast(_prm.Via, _prims.licon)
        li = cast(_prm.MetalWire, _prims.li)
        assert li.pin is not None
        lipin = li.pin

        # Create the wires
        placer.wire(
            wire_name="nsd_i", net=nets.i, wire=licon,
            bottom=difftap, bottom_implant=nsdm,
            bottom_height=self.w_npass,
        )
        placer.wire(
            wire_name="ppad_n", net=nets.vdd, wire=licon,
            bottom=poly,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.wire(
            wire_name="polyconn_n", net=nets.vdd, wire=poly,
            ref_height="ppad_n",
        )
        placer.wire(
            wire_name="li_vdd", net=nets.vdd, wire=li,
            ref_width="ppad_n",
        )
        placer.wire(
            wire_name="nsd_o", net=nets.o, wire=licon,
            bottom=difftap, bottom_implant=nsdm,
            bottom_height=self.w_npass,
        )

        placer.wire(
            wire_name="psd_i", net=nets.i, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_implant=psdm, bottom_well=nwm,
            bottom_height=self.w_ppass, bottom_enclosure="tall",
            top_enclosure="tall",
        )
        placer.wire(
            wire_name="ppad_p", net=nets.vss, wire=licon,
            bottom=poly,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.wire(
            wire_name="polyconn_p", net=nets.vss, wire=poly,
            ref_height="ppad_p",
        )
        placer.wire(
            wire_name="li_vss", net=nets.vss, wire=li,
            ref_width="ppad_p"
        )
        placer.wire(
            wire_name="psd_o", net=nets.o, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_implant=psdm, bottom_well=nwm,
            bottom_height=self.w_ppass, bottom_enclosure="tall",
            top_enclosure="tall",
        )

        placer.align_left(
            name="psd_i", ref_value=0.5*psdm.min_space, prim=psdm,
        )
        placer.align_bottom(
            name="psd_i", ref_value=canvas._well_edge_height, prim=nwm,
        )

        placer.place_to_the_right(
            name="ppass", ref_names="psd_i", ignore_masks=(difftap.mask, nwm.mask),
        )
        placer.align_bottom(
            name="ppass", ref_name="psd_i", prim=difftap,
        )

        placer.place_to_the_right(
            name="ppad_p", ref_names="psd_i", ignore_masks=(poly.mask, licon.mask),
        )
        placer.place_below(
            name="ppad_p", ref_names="ppass", ignore_masks=poly.mask,
        )

        placer.align_left(
            name="li_vss", ref_name="ppad_p", prim=li, net=nets.vss,
        )
        placer.align_bottom(
            name="li_vss", ref_value=0.0, prim=li, net=nets.vss,
        )

        placer.connect(
            name1="li_vss", name2="ppad_p", prim=li, net=nets.vss,
        )

        placer.align_left(
            name="polyconn_p", ref_name="ppass", prim=poly, net=nets.vss,
        )
        placer.center_y(
            name="polyconn_p", ref_name="ppad_p", prim=poly, net=nets.vss,
        )

        placer.connect(
            name1="polyconn_p", name2="ppass", prim=poly, net=nets.vss,
        )
        placer.connect(
            name1="polyconn_p", name2="ppad_p", prim=poly, net=nets.vss,
        )

        placer.place_to_the_right(
            name="ppad_n", ref_names="ppad_p", ignore_masks=poly.mask,
        )
        placer.place_below(
            name="ppad_n", ref_names="ppad_p", ignore_masks=li.mask,
        )

        placer.align_left(
            name="li_vdd", ref_name="ppad_n", prim=li, net=nets.vdd,
        )
        placer.align_top(
            name="li_vdd", ref_value=canvas._cell_height, prim=li, net=nets.vdd,
        )

        placer.connect(
            name1="li_vdd", name2="ppad_n", prim=li, net=nets.vdd,
        )

        placer.align_left(
            name="polyconn_n", ref_name="npass", prim=poly, net=nets.vdd,
        )
        placer.center_y(
            name="polyconn_n", ref_name="ppad_n", prim=poly, net=nets.vdd,
        )

        placer.connect(
            name1="polyconn_n", name2="npass", prim=poly, net=nets.vdd,
        )
        placer.connect(
            name1="polyconn_n", name2="ppad_n", prim=poly, net=nets.vdd,
        )

        placer.align_left(
            name="nsd_i", ref_value=0.5*nsdm.min_space, prim=nsdm,
        )
        placer.align_top(
            name="nsd_i", ref_name="npass", prim=difftap,
        )

        placer.place_to_the_right(
            name="npass", ref_names="nsd_i", ignore_masks=difftap.mask,
        )
        placer.place_below(
            name="npass", ref_names="ppad_n", ignore_masks=poly.mask,
        )

        placer.place_to_the_right(
            name="nsd_o", ref_names="ppad_n", ignore_masks=(poly.mask, licon.mask),
        )
        placer.align_top(
            name="nsd_o", ref_name="npass", prim=difftap,
        )

        placer.place_to_the_right(
            name="psd_o", ref_names="ppad_n", ignore_masks=(poly.mask, licon.mask),
        )
        placer.align_bottom(
            name="psd_o", ref_name="ppass", prim=difftap,
        )

        placer.fill(
            names=("nsd_i", "nsd_o"), prim=nsdm,
        )
        placer.fill(
            names=("psd_i", "psd_o"), prim=psdm,
        )
        placer.fill(
            names=("psd_i", "psd_o"), prim=nwm, net=nets.vdd,
        )

        if not placer.execute():
            print("OnPassGate: not all placements completed")
            for instr in placer.constraint_stack:
                print(instr)

        # pins
        layout = layouter.layout

        # i
        bb1 = placer.info_lookup["nsd_i"].bb(mask=li.mask, net=nets.i, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup["psd_i"].bb(mask=li.mask, net=nets.i, placed=True)
        assert bb2 is not None
        shape = _geo.Rect.from_rect(rect=bb1, top=bb2.top)
        layout.add_shape(layer=li, net=nets.i, shape=shape)
        layout.add_shape(layer=lipin, net=nets.i, shape=shape)

        # o
        bb1 = placer.info_lookup["nsd_o"].bb(mask=li.mask, net=nets.o, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup["psd_o"].bb(mask=li.mask, net=nets.o, placed=True)
        assert bb2 is not None
        shape = _geo.Rect.from_rect(rect=bb1, top=bb2.top)
        layout.add_shape(layer=li, net=nets.o, shape=shape)
        layout.add_shape(layer=lipin, net=nets.o, shape=shape)

        # hack connection of [np]sd_o
        bb1 = placer.info_lookup["nsd_o"].bb(mask=difftap.mask, net=nets.o, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup["npass"].bb(mask=difftap.mask, placed=True)
        assert bb2 is not None
        assert bb1.left > bb2.right
        shape = _geo.Rect.from_rect(rect=bb1, left=bb2.right)
        layout.add_shape(layer=difftap, net=nets.o, shape=shape)

        bb1 = placer.info_lookup["psd_o"].bb(mask=difftap.mask, net=nets.o, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup["ppass"].bb(mask=difftap.mask, placed=True)
        assert bb2 is not None
        assert bb1.left > bb2.right
        shape = _geo.Rect.from_rect(rect=bb1, left=bb2.right)
        layout.add_shape(layer=difftap, net=nets.o, shape=shape)

        # cell width
        width = []

        info = placer.info_lookup["nsd_o"]
        bb = info.bb(mask=nsdm.mask, placed=True)
        assert bb is not None
        width.append(bb.right + 0.5*nsdm.min_space)
        bb = info.bb(mask=li.mask, placed=True)
        assert bb is not None
        width.append(bb.right + 0.5*li.min_space)

        info = placer.info_lookup["psd_o"]
        bb = info.bb(mask=psdm.mask, placed=True)
        assert bb is not None
        width.append(bb.right + 0.5*psdm.min_space)
        bb = info.bb(mask=li.mask, placed=True)
        assert bb is not None
        width.append(bb.right + 0.5*li.min_space)

        self.set_width(min_width=max(width))


class PFD(_cell.OnDemandCell):
    """Phase-frequency Detector"""
    def __init__(self, *,
        name: Optional[str]=None,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        one: _cell.Cell, ffr: _cell.Cell,
        rstnand: _cell.Cell, rstbuf: _cell.Cell,
        refl_pass: OnPassGate, divl_inv: _cell.Cell,
        down_nor2: _cell.Cell, up_nand2: _cell.Cell,
    ):
        if name is None:
            name = "PFD"
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        self.one = one
        self.ffr = ffr
        self.rstnand = rstnand
        self.rstbuf = rstbuf
        self.refl_pass = refl_pass
        self.divl_inv = divl_inv
        self.down_nor2 = down_nor2
        self.up_nand2 = up_nand2

    def _create_circuit(self):
        one_cell = self.one
        ffr_cell = self.ffr
        rstnand_cell = self.rstnand
        rstbuf_cell = self.rstbuf
        refl_pass_cell = self.refl_pass
        divl_inv_cell = self.divl_inv
        down_nor2_cell = self.down_nor2
        up_nand2_cell = self.up_nand2

        ckt =  self.new_circuit()

        cells = []

        one = ckt.instantiate(one_cell, name="one")
        ffr_ref = ckt.instantiate(ffr_cell, name="ff_ref")
        ffr_div = ckt.instantiate(ffr_cell, name="ff_div")
        cells.extend((one, ffr_ref, ffr_div))

        ckt.new_net(name="ref", external=True, childports=ffr_ref.ports.ck)
        ckt.new_net(name="div", external=True, childports=ffr_div.ports.ck)

        rstnand = ckt.instantiate(rstnand_cell, name="rstnand")
        rstbuf = ckt.instantiate(rstbuf_cell, name="rstbuf")
        cells.extend((rstnand, rstbuf))

        ckt.new_net(name="rst_n", external=False, childports=(
            rstnand.ports.nq, rstbuf.ports.i,
        ))
        ckt.new_net(name="rst_n_buf", external=False, childports=(
            rstbuf.ports.q, ffr_ref.ports.nrst, ffr_div.ports.nrst,
        ))

        refl_pass = ckt.instantiate(refl_pass_cell, name="refl_pass")
        cells.append(refl_pass)

        ckt.new_net(name="refl", external=False, childports=(
            ffr_ref.ports.q, rstnand.ports.i0,
            refl_pass.ports.i,
        ))

        divl_inv = ckt.instantiate(divl_inv_cell, name="divl_inv")
        cells.append(divl_inv)

        ckt.new_net(name="divl", external=False, childports=(
            ffr_div.ports.q, rstnand.ports.i1, divl_inv.ports.i,
        ))

        down_nor2 = ckt.instantiate(down_nor2_cell, name="down_nor2")
        up_nand2 = ckt.instantiate(up_nand2_cell, name="up_nand2")
        cells.extend((down_nor2, up_nand2))

        ckt.new_net(name="refl_pass", external=False, childports=(
            refl_pass.ports.o,
            down_nor2.ports.i0, up_nand2.ports.i0,
        ))
        ckt.new_net(name="divl_n", external=False, childports=(
            divl_inv.ports.nq,
            down_nor2.ports.i1, up_nand2.ports.i1,
        ))

        ckt.new_net(name="down", external=True, childports=down_nor2.ports.nq)
        ckt.new_net(name="up_n", external=True, childports=up_nand2.ports.nq)

        ckt.new_net(name="one", external=False, childports=(
            one.ports.one,
            ffr_ref.ports.i, ffr_div.ports.i,
        ))

        ckt.new_net(name="vdd", external=True, childports=(
            *(cell.ports.vdd for cell in cells),
        ))
        ckt.new_net(name="vss", external=True, childports=(
            *(cell.ports.vss for cell in cells),
        ))

    def _create_layout(self):
        layouter = self.new_circuitlayouter()
        placer = _sky130lay.Sky130Layouter(layouter=layouter)

        ckt = self.circuit
        nets = ckt.nets

        li = cast(_prm.MetalWire, _prims.li)
        assert li.pin is not None
        lipin = li.pin
        mcon = cast(_prm.Via, _prims.mcon)
        m1 = cast(_prm.MetalWire, _prims.m1)
        assert m1.pin is not None
        m1pin = m1.pin

        # Place the cells in a row
        prev_wire = None
        for name in (
            "one", "ff_ref", "ff_div", "rstnand", "rstbuf",
            "refl_pass", "divl_inv", "down_nor2", "up_nand2",
        ):
            placer.place_at_bottom(name=name)
            if prev_wire is None:
                placer.place_at_left(name=name)
            else:
                assert prev_wire is not None, "Internal error"
                placer.place_to_the_right(
                    name=name, ref_names=prev_wire, boundary_only=True,
                )
            prev_wire = name

        #
        ## Create interconnects of mcon
        #

        # one
        net = nets.one
        placer.wire(
            wire_name="mcon_one_one", net=net, wire=mcon,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_right(
            name="mcon_one_one", ref_name="one", ref_pin=True, prim=li, net=net,
        )
        placer.align_top(
            name="mcon_one_one", ref_name="one", ref_pin=True, prim=li, net=net,
        )

        placer.wire(
            wire_name="mcon_one_ff_ref", net=net, wire=mcon,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_right(
            name="mcon_one_ff_ref", ref_name="ff_ref", ref_pin=True, prim=li, net=net,
        )
        placer.align_top(
            name="mcon_one_ff_ref", ref_name="ff_ref", ref_pin=True, prim=li, net=net,
        )

        placer.wire(
            wire_name="mcon_one_ff_div", net=net, wire=mcon,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_right(
            name="mcon_one_ff_div", ref_name="ff_div", ref_pin=True, prim=li, net=net,
        )
        placer.align_top(
            name="mcon_one_ff_div", ref_name="ff_div", ref_pin=True, prim=li, net=net,
        )

        placer.connect(
            name1="mcon_one_one", name2="mcon_one_ff_div", prim=m1, net=nets.one,
        )

        # rts_n_buf
        net_name = "rst_n_buf"
        net = nets[net_name]

        cell_name = "ff_ref"
        first_wire = wire_name = f"mcon_{net_name}_{cell_name}"
        placer.wire(
            wire_name=wire_name, net=net, wire=mcon,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_right(
            name=wire_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
        )
        placer.align_top(
            name=wire_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
        )

        cell_name = "ff_div"
        wire_name = f"mcon_{net_name}_{cell_name}"
        placer.wire(
            wire_name=wire_name, net=net, wire=mcon,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_right(
            name=wire_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
        )
        placer.align_top(
            name=wire_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
        )

        cell_name = "rstbuf"
        wire_name = f"mcon_{net_name}_{cell_name}"
        placer.wire(
            wire_name=wire_name, net=net, wire=mcon,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_right(
            name=wire_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
        )
        placer.align_top(
            name=wire_name, ref_name=first_wire, prim=li, net=net,
        )

        placer.connect(
            name1=first_wire, name2=wire_name, prim=m1, net=net,
        )

        prev_wires = (first_wire, wire_name)


        # rst_n
        net_name = "rst_n"
        net = nets[net_name]

        first_wire = None
        for cell_name in ("rstnand", "rstbuf"):
            wire_name = f"mcon_{net_name}_{cell_name}"
            if first_wire is None:
                first_wire = wire_name

            placer.wire(
                wire_name=wire_name, net=net, wire=mcon,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.align_right(
                name=wire_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
            )
            placer.place_above(
                name=wire_name, ref_names=prev_wires,
            )
        assert first_wire is not None

        placer.connect(
            name1=first_wire, name2=wire_name, prim=m1, net=net,
        )

        # keep prev_wires as it will now be placed below it

        # refl
        net_name = "refl"
        net = nets[net_name]

        first_wire = None
        for cell_name in ("ff_ref", "rstnand", "refl_pass"):
            wire_name = f"mcon_{net_name}_{cell_name}"
            if first_wire is None:
                first_wire = wire_name

            placer.wire(
                wire_name=wire_name, net=net, wire=mcon,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.align_right(
                name=wire_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
            )
            placer.place_below(
                name=wire_name, ref_names=prev_wires,
            )
        assert first_wire is not None

        placer.connect(
            name1=first_wire, name2=wire_name, prim=m1, net=net,
        )

        prev_wires = (first_wire, wire_name)

        # divl
        net_name = "divl"
        net = nets[net_name]

        first_wire = None
        for cell_name in ("ff_div", "rstnand", "divl_inv"):
            wire_name = f"mcon_{net_name}_{cell_name}"
            if first_wire is None:
                first_wire = wire_name

            placer.wire(
                wire_name=wire_name, net=net, wire=mcon,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.align_right(
                name=wire_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
            )
            placer.place_below(
                name=wire_name, ref_names=prev_wires,
            )
        assert first_wire is not None

        placer.connect(
            name1=first_wire, name2=wire_name, prim=m1, net=net,
        )

        prev_wires = (first_wire, wire_name)

        # refl_pass
        net_name = "refl_pass"
        net = nets[net_name]

        first_wire = None
        for cell_name in ("refl_pass", "down_nor2", "up_nand2"):
            wire_name = f"mcon_{net_name}_{cell_name}"

            placer.wire(
                wire_name=wire_name, net=net, wire=mcon,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.align_right(
                name=wire_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
            )
            if first_wire is None:
                first_wire = wire_name
                placer.align_top(
                    name=wire_name, ref_name=cell_name, prim=li, net=net,
                )
            else:
                placer.center_y(
                    name=wire_name, ref_name=first_wire, prim=li, net=net,
                )
        assert first_wire is not None

        placer.connect(
            name1=first_wire, name2=wire_name, prim=m1, net=net,
        )

        prev_wires = (first_wire, wire_name)

        # divl_n
        net_name = "divl_n"
        net = nets[net_name]

        first_wire = None
        for cell_name in ("divl_inv", "down_nor2", "up_nand2"):
            wire_name = f"mcon_{net_name}_{cell_name}"
            if first_wire is None:
                first_wire = wire_name

            placer.wire(
                wire_name=wire_name, net=net, wire=mcon,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.align_right(
                name=wire_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
            )
            placer.place_below(
                name=wire_name, ref_names=prev_wires,
            )
        assert first_wire is not None

        placer.connect(
            name1=first_wire, name2=wire_name, prim=m1, net=net,
        )

        prev_wires = (first_wire, wire_name)

        if not placer.execute():
            print("PFD: not all placements completed")

        # pins
        layout = layouter.layout

        for net, cell_name in (
            (nets.ref, "ff_ref"),
            (nets.div, "ff_div"),
            (nets.down, "down_nor2"),
            (nets.up_n, "up_nand2"),
        ):
            bb = placer.info_lookup[cell_name].bb(
                mask=lipin.mask, net=net, placed=True,
            )
            assert bb is not None
            layout.add_shape(layer=lipin, net=net, shape=bb)


class CurrentLimit(_FlexCell):
    def __init__(self, *,
        fab: StdCellFactory, name: Optional[str]=None,
        nmos: Optional[_prm.MOSFET]=None,
        nmos_w: Optional[float]=None, nmos_l: float, nmos_mult: int=1,
        pmos: Optional[_prm.MOSFET]=None,
        pmos_w: Optional[float]=None, pmos_l: float, pmos_mult: int=1,
    ):
        if name is None:
            name = self.__class__.__name__
        super().__init__(fab=fab, name=name)

        if nmos is None:
            nmos = fab.canvas.nmos
        if pmos is None:
            pmos = fab.canvas.pmos

        self.nmos = nmos
        self.nmos_w = nmos_w
        self.nmos_l = nmos_l
        self.nmos_mult = nmos_mult
        self.pmos = pmos
        self.pmos_w = pmos_w
        self.pmos_l = pmos_l
        self.pmos_mult = pmos_mult

        self._create_circuit()
        self._create_layout()

    def _create_circuit(self):
        nmos_trans = self.nmos
        nmos_w = self.nmos_w
        nmos_l = self.nmos_l
        nmos_mult = self.nmos_mult
        pmos_trans = self.pmos
        pmos_w = self.pmos_w
        pmos_l = self.pmos_l
        pmos_mult = self.pmos_mult

        ckt = self.circuit
        nets = ckt.nets

        nmoss = tuple(
            ckt.instantiate(nmos_trans, name=f"nmos[{n}]", w=nmos_w, l=nmos_l)
            for n in range(nmos_mult)
        )
        pmoss = tuple(
            ckt.instantiate(pmos_trans, name=f"pmos[{n}]", w=pmos_w, l=pmos_l)
            for n in range(pmos_mult)
        )

        nets.vdd.childports += (pmos.ports.bulk for pmos in pmoss)
        nets.vss.childports += (nmos.ports.bulk for nmos in nmoss)

        ckt.new_net(name="vhigh", external=True, childports=pmoss[0].ports.sourcedrain1)
        ckt.new_net(name="vlow", external=True, childports=nmoss[0].ports.sourcedrain1)

        ckt.new_net(name="low_en", external=True, childports=(
            nmos.ports.gate for nmos in nmoss
        ))
        ckt.new_net(name="high_en_n", external=True, childports=(
            pmos.ports.gate for pmos in pmoss
        ))

        ckt.new_net(name="drive", external=True, childports=(
            nmoss[-1].ports.sourcedrain2, pmoss[-1].ports.sourcedrain2,
        ))

        for n in range(nmos_mult - 1):
            ckt.new_net(name=f"nnode[{n}]", external=False, childports=(
                nmoss[n].ports.sourcedrain2, nmoss[n + 1].ports.sourcedrain1,
            ))

        for n in range(pmos_mult - 1):
            ckt.new_net(name=f"pnode[{n}]", external=False, childports=(
                pmoss[n].ports.sourcedrain2, pmoss[n + 1].ports.sourcedrain1,
            ))


    def _create_layout(self):
        nmos_mult = self.nmos_mult
        pmos_mult = self.pmos_mult

        canvas = self.canvas

        nwm = cast(_prm.Well, _prims.nwm)
        psdm = cast(_prm.Implant, _prims.psdm)
        nsdm = cast(_prm.Implant, _prims.nsdm)
        difftap = cast(_prm.WaferWire, _prims.difftap)
        poly = cast(_prm.GateWire, _prims.poly)
        licon = cast(_prm.Via, _prims.licon)
        li = cast(_prm.MetalWire, _prims.li)
        assert li.pin is not None
        lipin = li.pin

        ckt = self.circuit
        nets = ckt.nets

        rotations = {
            name: _geo.Rotation.MY
            for name in (
                *(f"nmos[{n}]" for n in range(1, nmos_mult, 2)),
                *(f"pmos[{n}]" for n in range(1, pmos_mult, 2)),
            )
        }
        placer = _sky130lay.Sky130Layouter(layouter=self._layouter, rotations=rotations)

        # Create wires
        placer.wire(
            wire_name="nsd_vlow", net=nets.vlow, wire=licon,
            bottom=difftap, bottom_implant=nsdm,
            ref_bottom_height="nmos[0]",
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.wire(
            wire_name="nsd_drive", net=nets.drive, wire=licon,
            bottom=difftap, bottom_implant=nsdm,
            ref_bottom_height=f"nmos[{nmos_mult - 1}]",
            bottom_enclosure="wide", top_enclosure="tall",
        )
        placer.wire(
            wire_name="ppad_low_en", net=nets.low_en, wire=licon,
            bottom=poly, ref_bottom_width="nmos[0]",
            bottom_enclosure="wide", top_enclosure="tall",
        )
        placer.wire(
            wire_name="psd_vhigh", net=nets.vhigh, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_implant=psdm, bottom_well=nwm,
            ref_bottom_height="pmos[0]",
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.wire(
            wire_name="psd_drive", net=nets.drive, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_implant=psdm, bottom_well=nwm,
            ref_bottom_height=f"pmos[{pmos_mult - 1}]",
            bottom_enclosure="wide", top_enclosure="tall",
        )
        placer.wire(
            wire_name="ppad_high_en_n", net=nets.high_en_n, wire=licon,
            bottom=poly, ref_bottom_width="pmos[0]",
            bottom_enclosure="wide", top_enclosure="tall",
        )

        placer.align_left(
            name="psd_vhigh", ref_value=0.5*psdm.min_space, prim=psdm,
        )
        placer.align_bottom(
            name="psd_vhigh", ref_value=canvas._well_edge_height, prim=nwm,
        )

        for n in range(pmos_mult):
            name = f"pmos[{n}]"
            if n == 0:
                placer.place_to_the_right(
                    name=name, ref_names="psd_vhigh", ignore_masks=(difftap.mask, nwm.mask),
                )
                placer.align_bottom(
                    name=name, ref_name="psd_vhigh", prim=difftap,
                )
            else:
                prev_name = f"pmos[{n - 1}]"

                placer.align_left(
                    name=name, ref_name=prev_name, prim=poly, net=nets.high_en_n,
                )
                placer.place_above(
                    name=name, ref_names=prev_name, ignore_masks=(poly.mask, nwm.mask),
                )

                placer.connect(
                    name1=name, name2=prev_name, prim=poly, net=nets.high_en_n,
                )

        placer.center_x(
            name="ppad_high_en_n", ref_name="pmos[0]", prim=poly, net=nets.high_en_n,
        )
        placer.place_below(
            name="ppad_high_en_n", ref_names="pmos[0]", ignore_masks=poly.mask,
        )

        placer.connect(
            name1="pmos[0]", name2="ppad_high_en_n", prim=poly, net=nets.high_en_n,
        )

        ref_name = f"pmos[{pmos_mult - 1}]"
        psd_name = "psd_drive"
        if (pmos_mult%2) == 0:
            placer.place_to_the_left(
                name=psd_name, ref_names=ref_name, ignore_masks=(difftap.mask, nwm.mask),
            )

            wire_name = "liconn_drive_pmos"
            placer.wire(
                wire_name=wire_name, net=nets.drive, wire=li,
                ref_height=psd_name,
            )
            placer.place_to_the_right(
                name=wire_name, ref_names="ppad_high_en_n",
            )
            placer.center_y(
                name=wire_name, ref_name=psd_name, prim=li, net=nets.drive,
            )

            placer.connect(
                name1=wire_name, name2=psd_name, prim=li, net=nets.drive,
            )

            drivepin_p = wire_name
        else:
            placer.place_to_the_right(
                name="psd_drive", ref_names=ref_name, ignore_masks=(difftap.mask, nwm.mask),
            )

            drivepin_p = "psd_drive"

        placer.align_bottom(
            name="psd_drive", ref_name=ref_name, prim=difftap,
        )

        placer.center_x(
            name="ppad_low_en", ref_name="nmos[0]", prim=poly, net=nets.low_en,
        )
        placer.place_below(
            name="ppad_low_en", ref_names="ppad_high_en_n",
        )

        placer.connect(
            name1="ppad_low_en", name2="nmos[0]", prim=poly, net=nets.low_en,
        )

        for n in range(nmos_mult):
            name = f"nmos[{n}]"
            if n == 0:
                placer.place_to_the_right(
                    name=name, ref_names="nsd_vlow", ignore_masks=difftap.mask,
                )
                placer.place_below(
                    name=name, ref_names="ppad_low_en", ignore_masks=poly.mask,
                )
            else:
                prev_name = f"nmos[{n - 1}]"

                placer.align_left(
                    name=name, ref_name=prev_name, prim=poly, net=nets.low_en,
                )
                placer.place_below(
                    name=name, ref_names=prev_name, ignore_masks=poly.mask,
                )

                placer.connect(
                    name1=name, name2=prev_name, prim=poly, net=nets.low_en,
                )

        placer.align_left(
            name="nsd_vlow", ref_value=0.5*nsdm.min_space, prim=nsdm,
        )
        placer.align_top(
            name="nsd_vlow", ref_name="nmos[0]", prim=difftap,
        )

        ref_name = f"nmos[{nmos_mult - 1}]"
        nsd_name = "nsd_drive"
        if (nmos_mult%2) == 0:
            placer.place_to_the_left(
                name=nsd_name, ref_names=ref_name, ignore_masks=difftap.mask,
            )

            wire_name = "liconn_drive_nmos"
            placer.wire(
                wire_name=wire_name, net=nets.drive, wire=li,
                ref_height=nsd_name,
            )
            placer.place_to_the_right(
                name=wire_name, ref_names="ppad_low_en",
            )
            placer.center_y(
                name=wire_name, ref_name=nsd_name, prim=li, net=nets.drive,
            )

            placer.connect(
                name1=wire_name, name2=nsd_name, prim=li, net=nets.drive,
            )

            drivepin_n = wire_name
        else:
            placer.place_to_the_right(
                name=nsd_name, ref_names=ref_name, ignore_masks=difftap.mask,
            )

            drivepin_n = nsd_name
        placer.align_top(
            name=nsd_name, ref_name=ref_name, prim=difftap,
        )

        placer.fill(
            names=(
                *(f"nmos[{n}]" for n in range(nmos_mult)),
                "nsd_drive", "nsd_vlow"
            ), prim=nsdm,
        )

        placer.fill(
            names=(
                *(f"pmos[{n}]" for n in range(pmos_mult)),
                "psd_drive", "psd_vhigh"
            ), prim=psdm,
        )

        ## execute the placements
        if not placer.execute():
            print("CharePump: not all placements completed")

        ## Manual connections

        layout = self._layouter.layout
        min_actpoly_space = self.tech.computed.min_space(
            primitive1=difftap, primitive2=poly,
        )

        # connect pmos pnode[*]
        for n in range(pmos_mult - 1):
            net_name = f"pnode[{n}]"
            net = nets[net_name]
            pmos1_name = f"pmos[{n}]"
            pmos2_name = f"pmos[{n + 1}]"

            info1 = placer.info_lookup[pmos1_name]
            info2 = placer.info_lookup[pmos2_name]

            polybb = info1.bb(mask=poly.mask, placed=True)
            assert polybb is not None
            actbb1 = info1.bb(mask=difftap.mask, placed=True)
            assert actbb1 is not None
            actbb2 = info2.bb(mask=difftap.mask, placed=True)
            assert actbb2 is not None

            bottom = actbb1.bottom
            top = actbb2.top
            if (n%2) == 0:
                left = polybb.right + min_actpoly_space
                right = max(
                    left + difftap.min_width,
                    actbb1.right, actbb2.right,
                )
            else:
                right = polybb.left - min_actpoly_space
                left = min(
                    right - difftap.min_width,
                    actbb1.left, actbb2.left,
                )
            shape = _geo.Rect(left=left, bottom=bottom, right=right, top=top)

            self._layouter.add_wire(
                net=net, wire=difftap, shape=shape, implant=psdm,
            )

        # connect nmos nnode[*]
        for n in range(nmos_mult - 1):
            net_name = f"nnode[{n}]"
            net = nets[net_name]
            nmos1_name = f"nmos[{n}]"
            nmos2_name = f"nmos[{n + 1}]"

            info1 = placer.info_lookup[nmos1_name]
            info2 = placer.info_lookup[nmos2_name]

            polybb = info1.bb(mask=poly.mask, placed=True)
            assert polybb is not None
            actbb1 = info1.bb(mask=difftap.mask, placed=True)
            assert actbb1 is not None
            actbb2 = info2.bb(mask=difftap.mask, placed=True)
            assert actbb2 is not None

            bottom = actbb2.bottom
            top = actbb1.top
            if (n%2) == 0:
                left = polybb.right + min_actpoly_space
                right = max(
                    left + difftap.min_width,
                    actbb1.right, actbb2.right,
                )
            else:
                right = polybb.left - min_actpoly_space
                left = min(
                    right - difftap.min_width,
                    actbb1.left, actbb2.left,
                )
            shape = _geo.Rect(left=left, bottom=bottom, right=right, top=top)

            self._layouter.add_wire(
                net=net, wire=difftap, shape=shape, implant=nsdm,
            )

        ## pins

        # vlow, vhigh, low_en, high_en_n
        for net, inst_name in (
            (nets.vlow, "nsd_vlow"),
            (nets.vhigh, "psd_vhigh"),
            (nets.low_en, "ppad_low_en"),
            (nets.high_en_n, "ppad_high_en_n"),
        ):
            bb = placer.info_lookup[inst_name].bb(mask=li.mask, net=net, placed=True)
            assert bb is not None
            layout.add_shape(layer=lipin, net=net, shape=bb)

        # drive
        bb1 = placer.info_lookup[drivepin_n].bb(mask=li.mask, net=nets.drive, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup[drivepin_p].bb(mask=li.mask, net=nets.drive, placed=True)
        assert bb2 is not None
        if (nmos_mult%2) == 1: # Try to use
            shape = _geo.Rect.from_rect(rect=bb1, top=bb2.top)
        else:
            shape = _geo.Rect.from_rect(rect=bb2, bottom=bb1.bottom)
        layout.add_shape(layer=li, net=nets.drive, shape=shape)
        layout.add_shape(layer=lipin, net=nets.drive, shape=shape)

        # cell width
        width = []

        for ref, prim, net in (
            ("nsd_drive", nsdm, None),
            ("nmos[0]", nsdm, None),
            ("psd_drive", psdm, None),
            ("pmos[0]", psdm, None),
            (drivepin_n, li, nets.drive),
            (drivepin_p, li, nets.drive),
        ):
            info = placer.info_lookup[ref]

            bb = info.bb(mask=prim.mask, net=net, placed=True)
            assert bb is not None
            width.append(bb.right + 0.5*prim.min_space)

        self.set_width(min_width=max(width))


class MOSCap(_FlexCell):
    def __init__(self, *,
        fab: StdCellFactory, name: Optional[str]=None,
        load_n: int, load_mos_l: float,
        load_nmos: Optional[_prm.MOSFET]=None, load_nmos_w: float,
        load_pmos: Optional[_prm.MOSFET]=None, load_pmos_w: float,
    ):
        if name is None:
            name = self.__class__.__name__
        super().__init__(fab=fab, name=name)

        self.load_n = load_n
        self.load_mos_l = load_mos_l

        if load_nmos is None:
            load_nmos = fab.canvas.nmos
        self.load_nmos = load_nmos
        self.load_nmos_w = load_nmos_w

        if load_pmos is None:
            load_pmos = fab.canvas.pmos
        self.load_pmos = load_pmos
        self.load_pmos_w = load_pmos_w

        self._create_circuit()
        self._create_layout()

    def _create_circuit(self):
        load_n = self.load_n
        mos_l = self.load_mos_l

        nmos_trans = self.load_nmos
        nmos_w = self.load_nmos_w

        pmos_trans = self.load_pmos
        pmos_w = self.load_pmos_w

        ckt = self.circuit
        nets = ckt.nets

        nmoses = tuple(
            ckt.instantiate(nmos_trans, name=f"nmos[{n}]", w=nmos_w, l=mos_l)
            for n in range(load_n)
        )
        pmoses = tuple(
            ckt.instantiate(pmos_trans, name=f"pmos[{n}]", w=pmos_w, l=mos_l)
            for n in range(load_n)
        )

        nets.vdd.childports +=(
            *chain(*(
                (pmos.ports.bulk, pmos.ports.sourcedrain1, pmos.ports.sourcedrain2)
                for pmos in pmoses
            )),
        )
        nets.vss.childports += (
            *chain(*(
                (nmos.ports.bulk, nmos.ports.sourcedrain1, nmos.ports.sourcedrain2)
                for nmos in nmoses
            )),
        )

        ckt.new_net(name="vin", external=True, childports=(
            mos.ports.gate for mos in (*nmoses, *pmoses)
        ))

    def _create_layout(self):
        load_n = self.load_n
        mos_l = self.load_mos_l

        nmos_w = self.load_nmos_w
        pmos_w = self.load_pmos_w

        canvas = self.canvas

        circuit = self.circuit
        nets = circuit.nets

        layouter = self._layouter
        placer = _sky130lay.Sky130Layouter(layouter=layouter)

        nwm = cast(_prm.Well, _prims.nwm)
        psdm = cast(_prm.Implant, _prims.psdm)
        nsdm = cast(_prm.Implant, _prims.nsdm)
        difftap = cast(_prm.WaferWire, _prims.difftap)
        poly = cast(_prm.GateWire, _prims.poly)
        licon = cast(_prm.Via, _prims.licon)
        li = cast(_prm.MetalWire, _prims.li)
        assert li.pin is not None
        lipin = li.pin

        placer.wire(
            wire_name="psd_vdd[0]", net=nets.vdd, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_implant=psdm, bottom_well=nwm,
            bottom_height=pmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_left(
            name="psd_vdd[0]", ref_value=0.5*psdm.min_space, prim=psdm,
        )
        placer.align_bottom(
            name="psd_vdd[0]", ref_value=canvas._well_edge_height, prim=nwm,
        )

        placer.wire(
            wire_name="vddtap[0]", net=nets.vdd, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_implant=nsdm, bottom_well=nwm,
            rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_left(
            name="vddtap[0]", ref_value=0.5*nsdm.min_space, prim=nsdm,
        )
        placer.align_top(
            name="vddtap[0]", ref_value=(canvas._cell_height - 0.5*nsdm.min_space),
            prim=nsdm,
        )

        placer.connect(
            name1="psd_vdd[0]", name2="vddtap[0]", prim=li, net=nets.vdd,
        )

        placer.wire(
            wire_name="nsd_vss[0]", net=nets.vss, wire=licon,
            bottom=difftap, bottom_implant=nsdm,
            bottom_height=nmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_left(
            name="nsd_vss[0]", ref_value=0.5*nsdm.min_space, prim=nsdm,
        )
        placer.align_top(
            name="nsd_vss[0]", ref_name="nmos[0]", prim=difftap,
        )

        placer.wire(
            wire_name="vsstap[0]", net=nets.vss, wire=licon,
            bottom=difftap, bottom_implant=psdm,
            rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_left(
            name="vsstap[0]", ref_value=0.5*psdm.min_space, prim=psdm,
        )
        placer.align_bottom(
            name="vsstap[0]", ref_value=0.5*psdm.min_space, prim=psdm,
        )

        placer.connect(
            name1="nsd_vss[0]", name2="vsstap[0]", prim=li, net=nets.vss,
        )

        prev_n_wire = "nsd_vss[0]"
        prev_p_wire = "psd_vdd[0]"
        for n in range(load_n):
            nmos_name = f"nmos[{n}]"
            pmos_name = f"pmos[{n}]"
            ppad_name = f"ppad[{n}]"
            nsd_name = f"nsd_vss[{n + 1}]"
            psd_name = f"psd_vdd[{n + 1}]"
            vddtap_name = f"vddtap[{n + 1}]"
            vsstap_name = f"vsstap[{n + 1}]"

            placer.place_to_the_right(
                name=pmos_name, ref_names=(prev_p_wire, prev_n_wire), ignore_masks=(
                    difftap.mask, nwm.mask,
                ),
            )
            placer.align_bottom(
                name=pmos_name, ref_name=prev_p_wire, prim=difftap,
            )

            placer.wire(
                wire_name=psd_name, net=nets.vdd, well_net=nets.vdd, wire=licon,
                bottom=difftap, bottom_implant=psdm, bottom_well=nwm,
                bottom_height=pmos_w,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.place_to_the_right(
                name=psd_name, ref_names=pmos_name, ignore_masks=(difftap.mask, nwm.mask),
            )
            placer.align_bottom(
                name=psd_name, ref_value=canvas._well_edge_height, prim=nwm,
            )

            placer.wire(
                wire_name=vddtap_name, net=nets.vdd, well_net=nets.vdd, wire=licon,
                bottom=difftap, bottom_implant=nsdm, bottom_well=nwm,
                rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=vddtap_name, ref_name=psd_name, prim=difftap, net=nets.vdd,
            )
            placer.align_top(
                name=vddtap_name, ref_value=(canvas._cell_height - 0.5*nsdm.min_space),
                prim=nsdm,
            )

            placer.connect(
                name1=psd_name, name2=vddtap_name, prim=li, net=nets.vdd,
            )

            placer.wire(
                wire_name=ppad_name, net=nets.vin, wire=licon,
                bottom=poly, ref_bottom_width=pmos_name,
                bottom_enclosure="wide", top_enclosure="wide",
            )
            placer.center_x(
                name=ppad_name, ref_name=pmos_name, prim=poly, net=nets.vin,
            )
            placer.place_below(
                name=ppad_name, ref_names=(pmos_name, prev_p_wire),
                ignore_masks=poly.mask,
            )

            placer.place_to_the_right(
                name=nmos_name, ref_names=(prev_p_wire, prev_n_wire), ignore_masks=(
                    difftap.mask, nwm.mask,
                ),
            )
            placer.place_below(
                name=nmos_name, ref_names=ppad_name, ignore_masks=poly.mask,
            )

            placer.wire(
                wire_name=nsd_name, net=nets.vss, wire=licon,
                bottom=difftap, bottom_implant=nsdm,
                bottom_height=nmos_w,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.place_to_the_right(
                name=nsd_name, ref_names=nmos_name, ignore_masks=difftap.mask,
            )
            placer.align_top(
                name=nsd_name, ref_name=nmos_name, prim=difftap,
            )

            placer.wire(
                wire_name=vsstap_name, net=nets.vss, wire=licon,
                bottom=difftap, bottom_implant=psdm,
                rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=vsstap_name, ref_name=nsd_name, prim=difftap, net=nets.vss,
            )
            placer.align_bottom(
                name=vsstap_name, ref_value=0.5*psdm.min_space, prim=psdm,
            )

            placer.connect(
                name1=nsd_name, name2=vsstap_name, prim=li, net=nets.vss,
            )

            prev_n_wire = nsd_name
            prev_p_wire = psd_name

        if not placer.execute():
            print("MOSCap: not all placements completed")

        # pins
        layout = layouter.layout

        # vin
        name = "ppad[0]"
        bb1 = placer.info_lookup[name].bb(mask=li.mask, net=nets.vin, placed=True)
        assert bb1 is not None
        name = f"ppad[{load_n - 1}]"
        bb2 = placer.info_lookup[name].bb(mask=li.mask, net=nets.vin, placed=True)
        assert bb2 is not None
        shape = _geo.Rect.from_rect(rect=bb1, right=bb2.right)
        layout.add_shape(layer=li, net=nets.vin, shape=shape)
        layout.add_shape(layer=lipin, net=nets.vin, shape=shape)

        # cell width
        width = []

        for sd, impl in (
            (f"nsd_vss[{load_n}]", nsdm),
            (f"vsstap[{load_n}]", psdm),
            (f"psd_vdd[{load_n}]", psdm),
            (f"vddtap[{load_n}]", nsdm),
        ):
            info = placer.info_lookup[sd]
            bb = info.bb(mask=impl.mask, placed=True)
            assert bb is not None
            width.append(bb.right + 0.5*impl.min_space)
            bb = info.bb(mask=li.mask, placed=True)
            assert bb is not None
            width.append(bb.right + 0.5*li.min_space)

        self.set_width(min_width=max(width))


class ChargePumpFilter(_cell.OnDemandCell):
    def __init__(self, *,
        name: Optional[str]=None,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        chargepump: CurrentLimit,
        cap1_currentlimit: CurrentLimit,
        cap1: MOSCap,
        cap2: Optional[MOSCap]=None,
    ):
        if name is None:
            name = self.__class__.__name__
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        self.cp = chargepump
        self.cap1_cl = cap1_currentlimit
        self.cap1 = cap1
        self.cap2 = cap2

    def _create_circuit(self):
        cp_cell = self.cp
        cl_cell = self.cap1_cl
        cap1_cell = self.cap1
        cap2_cell = self.cap2

        ckt = self.new_circuit()

        cp = ckt.instantiate(cp_cell, name="cp")
        cl = ckt.instantiate(cl_cell, name="cl")
        cap1 = ckt.instantiate(cap1_cell, name="cap1")
        cells = [cp, cl, cap1]
        if cap2_cell is None:
            cap2 = None
        else:
            cap2 = ckt.instantiate(cap2_cell, name="cap2")
            cells.append(cap2)

        ckt.new_net(name="vdd", external=True, childports=(
            *(cell.ports.vdd for cell in cells),
            cl.ports.low_en,
        ))
        ckt.new_net(name="vss", external=True, childports=(
            *(cell.ports.vss for cell in cells),
            cl.ports.high_en_n,
        ))

        ckt.new_net(name="vhigh", external=True, childports=cp.ports.vhigh)
        ckt.new_net(name="vlow", external=True, childports=cp.ports.vlow)

        ckt.new_net(name="down", external=True, childports=cp.ports.low_en)
        ckt.new_net(name="up_n", external=True, childports=cp.ports.high_en_n)

        vctrl = ckt.new_net(name="vctrl", external=True, childports=(
            cp.ports.drive, cl.ports.vhigh, cl.ports.vlow,
        ))
        if cap2 is not None:
            vctrl.childports += cap2.ports.vin

        ckt.new_net(name="node1", external=False, childports=(
            cl.ports.drive, cap1.ports.vin,
        ))

    def _create_layout(self):
        ckt = self.circuit
        nets = ckt.nets

        layouter = self.new_circuitlayouter()
        placer = _sky130lay.Sky130Layouter(layouter=layouter)

        li = cast(_prm.MetalWire, _prims.li)
        assert li.pin is not None
        lipin = li.pin
        mcon = cast(_prm.Via, _prims.mcon)
        m1 = cast(_prm.MetalWire, _prims.m1)
        via = cast(_prm.Via, _prims.via)
        m2 = cast(_prm.MetalWire, _prims.m2)

        ## Place the cells in a row
        prev_wire = None
        for name in (
            "cp",
            *([] if self.cap2 is None else ("cap2",)),
            "cl", "cap1",
        ):
            placer.place_at_bottom(name=name)
            if prev_wire is None:
                placer.place_at_left(name=name)
            else:
                assert prev_wire is not None, "Internal error"
                placer.place_to_the_right(
                    name=name, ref_names=prev_wire, boundary_only=True,
                )
            prev_wire = name

        # vctrl
        net = nets.vctrl
        wire_name = "liconn_vctrl_cl"
        placer.wire(
            wire_name=wire_name, net=net, wire=li,
            ref_height="cl",
        )
        placer.align_left(
            name=wire_name, ref_name="cl",  prim=li, net=net,
        )
        placer.center_y(
            name=wire_name, ref_name="cl",  prim=li, net=net,
        )

        if self.cap2 is None:
            placer.connect(
                name1="cp", name2="cl", prim=li, net=net,
            )
        else:
            placer.connect(
                name1="cap2", name2="cp", prim=li, net=nets.vctrl,
            )
            placer.connect(
                name1="cap2", name2="liconn_vctrl_cl", prim=li, net=nets.vctrl,
            )

        # node1
        net = nets.node1
        placer.connect(
            name1="cl", name2="cap1", prim=li, net=net,
        )

        if not placer.execute():
            print("ChargePumpFilter: not all placements completed")

        ## Manual connection

        layout = layouter.layout

        # high_en_n and low_en for cl
        # they are connected to vss/vdd
        # we will add new placements

        info = placer.info_lookup["cl"]
        assert info.x is not None
        assert info.y is not None
        orig = _geo.Point(x=info.x, y=info.y)

        ms1, ms2 = info.layout.filter_polygons(
            net=nets.vdd, mask=lipin.mask, depth=1,
        )
        bb1 = ms1.shape + orig
        assert isinstance(bb1, _geo.Rect)
        bb2 = ms2.shape + orig
        assert isinstance(bb2, _geo.Rect)
        if bb1.bottom > bb2.top:
            bbvdd_pin = bb2
            bbvdd_rail = bb1
        else:
            bbvdd_pin = bb1
            bbvdd_rail = bb2

        ms1, ms2 = info.layout.filter_polygons(
            net=nets.vss, mask=lipin.mask, depth=1,
        )
        bb1 = ms1.shape + orig
        assert isinstance(bb1, _geo.Rect)
        bb2 = ms2.shape + orig
        assert isinstance(bb2, _geo.Rect)
        if bb1.bottom > bb2.top:
            bbvss_pin = bb1
            bbvss_rail = bb2
        else:
            bbvss_pin = bb2
            bbvss_rail = bb1

        mcon1_name = "mcon1_vdd_cl"
        mcon2_name = "mcon2_vdd_cl"

        placer.wire(
            wire_name=mcon1_name, net=nets.vdd, wire=mcon,
        )
        placer.align_right(
            name=mcon1_name, ref_value=bbvdd_pin.right, prim=li, net=nets.vdd,
        )
        placer.align_top(
            name=mcon1_name, ref_value=bbvdd_pin.top, prim=li, net=nets.vdd,
        )

        placer.wire(
            wire_name=mcon2_name, net=nets.vdd, wire=mcon,
        )
        placer.align_right(
            name=mcon2_name, ref_value=bbvdd_pin.right, prim=li, net=nets.vdd,
        )
        placer.align_bottom(
            name=mcon2_name, ref_value=bbvdd_rail.bottom,
            prim=li, net=nets.vdd,
        )

        placer.connect(
            name1=mcon1_name, name2=mcon2_name, prim=m1, net=nets.vdd,
        )

        mcon1_name = "mcon1_vss_cl"
        via1_name = "via1_vss_cl"
        mcon2_name = "mcon2_vss_cl"
        via2_name = "via2_vss_cl"

        placer.wire(
            wire_name=mcon1_name, net=nets.vss, wire=mcon,
        )
        placer.align_left(
            name=mcon1_name, ref_value=bbvss_pin.left, prim=li, net=nets.vss,
        )
        placer.align_bottom(
            name=mcon1_name, ref_value=bbvss_pin.bottom, prim=li, net=nets.vss,
        )

        placer.wire(
            wire_name=via1_name, net=nets.vss, wire=via,
        )
        placer.center_x(
            name=via1_name, ref_name=mcon1_name, prim=m1, net=nets.vss,
        )
        placer.align_bottom(
            name=via1_name, ref_name=mcon1_name, prim=m1, net=nets.vss,
        )

        placer.wire(
            wire_name=mcon2_name, net=nets.vss, wire=mcon,
        )
        placer.center_x(
            name=mcon2_name, ref_name=mcon1_name, prim=li, net=nets.vss,
        )
        placer.center_y(
            name=mcon2_name, ref_value=bbvss_rail.center.y, prim=li,
        )

        placer.wire(
            wire_name=via2_name, net=nets.vss, wire=via,
        )
        placer.center_x(
            name=via2_name, ref_name=mcon2_name, prim=m1, net=nets.vss,
        )
        placer.align_top(
            name=via2_name, ref_name=mcon2_name, prim=m1, net=nets.vss,
        )

        placer.connect(
            name1=via1_name, name2=via2_name, prim=m2, net=nets.vss,
        )

        if not placer.execute():
            print("ChargePumpFilter: not all second placements completed")

        ## pins

        # vhigh, vlow, down, up_n
        info = placer.info_lookup["cp"]
        for name in ("vhigh", "vlow", "down", "up_n", "vctrl"):
            net = nets[name]
            bb = info.bb(mask=lipin.mask, net=net, placed=True)
            assert bb is not None
            layout.add_shape(layer=lipin, net=net, shape=bb)


class PLL(_cell.OnDemandCell):
    def __init__(self, *,
        name: Optional[str]=None,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        vco: VCO, divchain: Div2Chain, pfd: PFD, cpf: ChargePumpFilter,
    ):
        if name is None:
            name = self.__class__.__name__
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        self.vco = vco
        self.divchain = divchain
        self.pfd = pfd
        self.cpf = cpf

    def _create_circuit(self):
        vco_cell = self.vco
        divchain_cell = self.divchain
        pfd_cell = self.pfd
        cpf_cell = self.cpf

        ckt = self.new_circuit()

        vco = ckt.instantiate(vco_cell, name="vco")
        divchain = ckt.instantiate(divchain_cell, name="divchain")
        pfd = ckt.instantiate(pfd_cell, name="pfd")
        cpf = ckt.instantiate(cpf_cell, name="cpf")
        cells = (vco, pfd, cpf, divchain)

        vdd = ckt.new_net(name="vdd", external=True, childports=(
            *(cell.ports.vdd for cell in cells),
            cpf.ports.vhigh,
        ))
        vss = ckt.new_net(name="vss", external=True, childports=(
            *(cell.ports.vss for cell in cells),
            cpf.ports.vlow,
        ))

        ckt.new_net(name="ref", external=True, childports=pfd.ports.ref)
        net_name = f"fvco_div{2**divchain_cell.n_stages}"
        chaindiv_name = f"div{2**divchain_cell.n_stages}"
        ckt.new_net(name=net_name, external=False, childports=(
            pfd.ports.div, divchain.ports[chaindiv_name],
        ))

        ckt.new_net(name="down", external=False, childports=(
            pfd.ports.down, cpf.ports.down,
        ))
        ckt.new_net(name="up_n", external=False, childports=(
            pfd.ports.up_n, cpf.ports.up_n,
        ))

        vctrl = ckt.new_net(name="vctrl", external=False, childports=(
            cpf.ports.vctrl, vco.ports.vctrl,
        ))
        ckt.new_net(name="fvco", external=False, childports=(
            vco.ports.vout, divchain.ports.sig,
        ))

        # Divided fvco nets
        for n in range(divchain_cell.n_stages - 1):
            net_name = f"fvco_div{2**(n + 1)}"
            div_name = f"div{2**(n + 1)}"
            ckt.new_net(name=net_name, external=True, childports=divchain.ports[div_name])

    def _create_layout(self):
        ckt = self.circuit
        nets = ckt.nets

        layouter = self.new_circuitlayouter()
        placer = _sky130lay.Sky130Layouter(layouter=layouter)

        li = cast(_prm.MetalWire, _prims.li)
        assert li.pin is not None
        lipin = li.pin
        mcon = cast(_prm.Via, _prims.mcon)
        m1 = cast(_prm.MetalWire, _prims.m1)
        assert m1.pin is not None
        m1pin = m1.pin

        ## Place the cells in a row
        prev_wire = None
        for name in (
            "pfd", "cpf", "vco", "divchain",
        ):
            placer.place_at_bottom(name=name)
            if prev_wire is None:
                placer.place_at_left(name=name)
            else:
                assert prev_wire is not None, "Internal error"
                placer.place_to_the_right(
                    name=name, ref_names=prev_wire, boundary_only=True,
                )
            prev_wire = name

        ## interconnects

        # down
        net = nets.down

        placer.wire(
            wire_name="mcon_down_pfd", net=net, wire=mcon,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.wire(
            wire_name="mcon_down_cpf", net=net, wire=mcon,
            bottom_enclosure="wide", top_enclosure="wide",
        )

        placer.align_right(
            name="mcon_down_pfd", ref_name="pfd", ref_pin=True, prim=li, net=net,
        )
        placer.center_y(
            name="mcon_down_pfd", ref_name="mcon_down_cpf", prim=m1, net=net,
        )

        placer.align_left(
            name="mcon_down_cpf", ref_name="cpf", ref_pin=True, prim=li, net=net,
        )
        placer.center_y(
            name="mcon_down_cpf", ref_name="cpf", ref_pin=True, prim=li, net=net,
        )

        placer.connect(
            name1="mcon_down_pfd", name2="mcon_down_cpf", prim=m1, net=nets.down,
        )

        # fvco_div
        net_name = f"fvco_div{2**self.divchain.n_stages}"
        net = nets[net_name]

        fvcoconn_name = wire_name = f"mcon_{net_name}_pfd"
        placer.wire(
            wire_name=wire_name, net=net, wire=mcon,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.center_x(
            name=wire_name, ref_name="pfd", ref_pin=True, prim=li, net=net,
        )
        placer.align_bottom(
            name=wire_name, ref_name="pfd", ref_pin=True, prim=li, net=net,
        )

        conn_name = f"m1conn_{net_name}"
        placer.wire(
            wire_name=conn_name, net=net, wire=m1,
            ref_width="divchain", ref_height=wire_name,
        )
        placer.center_x(
            name=conn_name, ref_name="divchain", prim=m1, net=net,
        )
        placer.center_y(
            name=conn_name, ref_name=wire_name, prim=m1, net=net,
        )

        placer.connect(
            name1=wire_name, name2=conn_name, prim=m1, net=net,
        )
        placer.connect(
            name1="divchain", name2=conn_name, prim=m1, net=net,
        )

        # vctrl
        net = nets.vctrl
        placer.wire(
            wire_name="mcon_vctrl_src", net=net, wire=mcon,
            bottom_enclosure="tall", top_enclosure="wide",
        )

        placer.align_right(
            name="mcon_vctrl_src", ref_name="cpf", ref_pin=True, prim=li, net=net,
        )
        placer.place_above(
            name="mcon_vctrl_src", ref_names=fvcoconn_name,
        )

        placer.connect(
            name1="mcon_vctrl_src", name2="vco", prim=m1, net=net,
        )

        if not placer.execute():
            print("PLL: not all placements completed")

        ## Manual connection
        layout = layouter.layout

        # up_n
        bb1 = placer.info_lookup["pfd"].bb(mask=lipin.mask, net=nets.up_n, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup["cpf"].bb(mask=lipin.mask, net=nets.up_n, placed=True)
        assert bb2 is not None
        shape = _geo.Rect.from_rect(rect=bb2, left=bb1.left)
        layout.add_shape(layer=li, net=nets.up_n, shape=shape)

        # chargepump vhigh/vlow
        info = placer.info_lookup["cpf"]
        assert (info.x is not None) and (info.y is not None)
        cpf_orig = _geo.Point(x=info.x, y=info.y)

        cpf_cell = self.cpf
        cell_height = cpf_cell.cp.canvas._cell_height
        cpf_nets = cpf_cell.circuit.nets
        cpf_lay = cpf_cell.layout

        bb = cpf_lay.bounds(mask=lipin.mask, net=cpf_nets.vhigh, depth=1) + cpf_orig
        shape = _geo.Rect.from_rect(rect=bb, top=cell_height)
        layout.add_shape(layer=li, net=nets.vdd, shape=shape)

        bb = cpf_lay.bounds(mask=lipin.mask, net=cpf_nets.vlow, depth=1) + cpf_orig
        shape = _geo.Rect.from_rect(rect=bb, bottom=0.0)
        layout.add_shape(layer=li, net=nets.vss, shape=shape)

        ## pins

        # ref
        net = nets.ref
        bb = placer.info_lookup["pfd"].bb(mask=lipin.mask, net=net)
        assert bb is not None
        layout.add_shape(layer=lipin, net=net, shape=bb)

        # fvco*
        for n in range(self.divchain.n_stages + 1):
            if n == 0:
                net = nets.fvco
                cell_name = "vco"
            else:
                net = nets[f"fvco_div{2**n}"]
                cell_name = "divchain"
            bb = placer.info_lookup[cell_name].bb(mask=m1pin.mask, net=net, placed=True)
            assert bb is not None
            layout.add_shape(layer=m1pin, net=net, shape=bb)


class SimVCOStage:
    def __init__(self, *, stage: VCOStage) -> None:
        self.stage = stage
        self.last_sim = None
        self.last_trans = None

    def sim_delay(self, *,
        vctrl: float, tr_in: float,
        vdd: float, corner: MultiT[str], temperature: float=25.0,
        sim_end: float=10e-9,
        _second: bool=False,
    ) -> Tuple[float, float, float]:
        """Returns (td, tr, tf)
            td: average single stage delay
            tr: rise time
            tf: fall time
        """
        corner = cast_MultiT(corner)

        stage = self.stage

        chain = VCOChain(
            tech=stage.tech, cktfab=stage.cktfab, layoutfab=stage.layoutfab,
            stage=stage, n_stages=13,
        )
        tb = sky130.pyspicefab.new_pyspicecircuit(
            corner=corner, top=chain.circuit, title="stage delay",
        )
        tb.V("vdd", "vdd", "vss", vdd)
        tb.V("vss", "vss", tb.gnd, 0.0)
        tb.V("vctrl", "vctrl", "vss", vctrl)

        tb.PieceWiseLinearVoltageSource("vin", "vin", "vss", dc=0.0, values=(
            (0.0, 0.0),
            (tr_in, 0.0),
            (2*tr_in, vdd),
        ))

        self.last_sim = sim = tb.simulator(temperature=temperature)
        self.last_trans = trans = sim.transient(step_time=tr_in/10, end_time=sim_end)

        time = 1e12*_np.array(trans.time)
        nr1 = _np.array(trans.nodes["xtop.node[8]"])
        nr2 = _np.array(trans.nodes["xtop.node[10]"])
        nr3 = _np.array(trans.nodes["xtop.node[12]"])
        nf1 = _np.array(trans.nodes["xtop.node[11]"])
        if nr3[-1] < 0.9*vdd:
            return _np.nan, _np.nan, _np.nan

        tcr1 = _np.interp(0.5*vdd, nr1, time)
        tcr2 = _np.interp(0.5*vdd, nr2, time)
        tcr3 = _np.interp(0.5*vdd, nr3, time)
        td = 0.25*(tcr3-tcr1)
        td2 = 0.5*(tcr3-tcr2)

        tlr3 = _np.interp(0.1*vdd, nr3, time)
        thr3 = _np.interp(0.9*vdd, nr3, time)
        tr = thr3 - tlr3

        tlf1 = _np.interp(-0.1*vdd, -1.0*nf1, time)
        thf1 = _np.interp(-0.9*vdd, -1.0*nf1, time)
        tf = tlf1 - thf1

        reldiff = abs(td/td2 - 1)
        if (reldiff > 5e-3):
            if (not _second):
                print(f"second try with tr_in={tr:.2f}")
                return self.sim_delay(
                    vctrl=vctrl, tr_in=1e-12*tr, vdd=vdd, corner=corner, temperature=temperature,
                    sim_end=sim_end, _second=True,
                )
            else:
                print(f"second big reldiff {reldiff:.4f}")

        return (td, tr, tf)


class SimVCO:
    def __init__(self, *, vco: VCO) -> None:
        self.vco = vco

        self.last_sim = None
        self.last_trans = None

    def sim_vdd_ramp(self, *,
        vctrl: float, t_vddramp: float=10e-9,
        vdd: float, corner: MultiT[str], temperature: float=25.0,
        sim_end: Optional[float]=None, # default 6*t_vddramp
        sim_step: float=5e-12,
    ):
        corner = cast_MultiT(corner)
        if sim_end is None:
            sim_end = 6*t_vddramp

        vco = self.vco

        tb = sky130.pyspicefab.new_pyspicecircuit(
            corner=corner, top=vco.circuit, title="VCO vdd ramp",
        )
        tb.PieceWiseLinearVoltageSource("vdd", "vdd", "vss", dc=0.0, values=(
            (0.0, 0.0),
            (t_vddramp, vdd),
            (6*t_vddramp, vdd),
        ))
        tb.V("vss", "vss", tb.gnd, 0.0)
        tb.V("vctrl", "vctrl", "vss", vctrl)

        self.last_sim = sim = tb.simulator(temperature=temperature)
        self.last_trans = trans = sim.transient(step_time=sim_step, end_time=sim_end)

        return trans


class SimDiv2Chain:
    def __init__(self, *, chain: Div2Chain) -> None:
        self.chain = chain

        self.last_sim = None
        self.last_trans = None

    def sim_freq(self, *,
        freq: float, tr: float,
        vdd: float, corner: MultiT[str], temperature: float=25.0,
        sim_end: Optional[float]=None, # default to 50 periods of original frequency
        sim_step: Optional[float]=None, # default tr/10
    ):
        corner = cast_MultiT(corner)
        period = 1/freq
        if sim_end is None:
            sim_end = 50*period
        if sim_step is None:
            sim_step = tr/10

        chain = self.chain

        tb = sky130.pyspicefab.new_pyspicecircuit(
            corner=corner, top=chain.circuit, title="Div2Chain verification",
        )
        tb.V("vdd", "vdd", "vss", vdd)
        tb.V("vss", "vss", tb.gnd, 0.0)
        tb.PulseVoltageSource(
            "sig", "sig", "vss",
            delay_time=0.25*period, period=period, pulse_width=(0.5*period - tr),
            rise_time=tr, fall_time=tr, initial_value=0.0, pulsed_value=vdd,
        )

        self.last_sim = sim = tb.simulator(temperature=temperature)
        self.last_trans = trans = sim.transient(step_time=sim_step, end_time=sim_end)

        return trans


class SimPFD:
    def __init__(self, *, pfd: PFD) -> None:
        self.pfd = pfd

        self.last_sim = None
        self.last_trans = None

    def sim_delay(self, *,
        freq: float, tr: float,
        td: float, # delay of div to ref can be positive or negative
        vdd: float, corner: MultiT[str], temperature: float=25.0,
        sim_end: Optional[float]=None, # default 5*period
        sim_step: Optional[float]=None, # default tr/10
        c_out: float=50e-15,
    ) -> Any:
        corner = cast_MultiT(corner)
        period = 1/freq
        if sim_end is None:
            sim_end = 5*period
        if sim_step is None:
            sim_step = tr/10

        pfd = self.pfd

        tb = sky130.pyspicefab.new_pyspicecircuit(
            corner=corner, top=pfd.circuit, title="PFD ref-div delay",
        )
        tb.V("vdd", "vdd", "vss", vdd)
        tb.V("vss", "vss", tb.gnd, 0.0)
        tb.PulseVoltageSource(
            "ref", "ref", "vss",
            delay_time=0.25*period, period=period, pulse_width=(0.5*period - tr),
            rise_time=tr, fall_time=tr, initial_value=0.0, pulsed_value=vdd,
        )
        tb.PulseVoltageSource(
            "div", "div", "vss",
            delay_time=(0.25*period + td), period=period, pulse_width=(0.5*period - tr),
            rise_time=tr, fall_time=tr, initial_value=0.0, pulsed_value=vdd,
        )

        tb.C("down", "down", "vss", c_out)
        tb.C("up_n", "up_n", "vss", c_out)

        self.last_sim = sim = tb.simulator(temperature=temperature)
        self.last_trans = trans = sim.transient(step_time=sim_step, end_time=sim_end)

        return trans

    def sim_pulsewidth(self, *,
        freq: float, tr: float,
        td: float, # delay of div to ref can be positive or negative
        vdd: float, corner: MultiT[str], temperature: float=25.0,
        sim_step: Optional[float]=None, # default tr/10
        c_out: float=50e-15,
    ) -> Tuple[float, float]:
        period = 1/freq
        sim_end = 2.1*period

        trans = self.sim_delay(
            freq=freq, tr=tr, td=td, vdd=vdd, corner=corner,
            temperature=temperature, sim_end=sim_end, sim_step=sim_step, c_out=c_out,
        )

        time = _np.array(trans.time)
        idcs_period1 = _np.nonzero(((time >= period) & (time <= 2*period)))[0]

        time = time[idcs_period1]
        down = _np.array(trans.down[idcs_period1])
        up_n = _np.array(trans.up_n[idcs_period1])

        if max(down) < 0.55*vdd:
            pw_down = 0.0
        else:
            idcs_high = _np.nonzero(down >= 0.55*vdd)[0]
            # Check if there is a glitch
            if not all((idcs_high[1:] - idcs_high[:-1]) == 1):
                print("glitch")
                pw_down = _np.nan
            else:
                idx = idcs_high[0]
                crossr = cast(float, _np.interp(0.5*vdd, down[:idx], time[:idx]))
                idx = idcs_high[-1]
                crossf = cast(float, _np.interp(-0.5*vdd, -down[idx:], time[idx:]))
                assert crossf > crossr, "Internal error"
                pw_down = crossf - crossr

        if min(up_n) > 0.45*vdd:
            pw_up_n = 0.0
        else:
            idcs_low = _np.nonzero(up_n <= 0.45*vdd)[0]
            # Check if there is a glitch
            if not all((idcs_low[1:] - idcs_low[:-1]) == 1):
                print("glitch")
                pw_up_n = _np.nan
            else:
                idx = idcs_low[0]
                crossf = cast(float, _np.interp(-0.5*vdd, -up_n[:idx], time[:idx]))
                idx = idcs_low[-1]
                crossr = cast(float, _np.interp(0.5*vdd, up_n[idx:], time[idx:]))
                assert crossr > crossf, "Internal error"
                pw_up_n = crossr - crossf

        return pw_down, pw_up_n


class SimChargePumpFilter:
    def __init__(self, *, cpf: ChargePumpFilter) -> None:
        self.cpf = cpf

        self.last_sim = None
        self.last_ac = None

    def sim_transfer(self, *,
        load: Optional[VCO]=None, load_pin_name: Optional[str]=None,
        vdd: float, corner: MultiT[str], temperature: float=25.0,
        start_frequency: float=1e4, stop_frequency: float=1e10,
    ):
        if load_pin_name is None:
            load_pin_name = "vctrl"

        cpf_cell = self.cpf

        ckt = sky130.cktfab.new_circuit(name="cp_transfer")

        cpf1 = ckt.instantiate(cpf_cell, name="cpf1")
        cpf2 = ckt.instantiate(cpf_cell, name="cp2")
        cells = [cpf1, cpf2]

        load1 = load2 = None
        if load is not None:
            load1 = ckt.instantiate(load, name="load1")
            load2 = ckt.instantiate(load, name="load2")
            cells.extend((load1, load2))

            for port in load1.ports:
                if port.name not in ("vdd", "vss", load_pin_name):
                    ckt.new_net(name=f"load1_{port.name}", external=False, childports=port)
            for port in load2.ports:
                if port.name not in ("vdd", "vss", load_pin_name):
                    ckt.new_net(name=f"load2_{port.name}", external=False, childports=port)

        ckt.new_net(name="vdd", external=True, childports=(
            cell.ports.vdd for cell in cells
        ))
        ckt.new_net(name="vss", external=True, childports=(
            cell.ports.vss for cell in cells
        ))

        ckt.new_net(name="vhigh1", external=True, childports=cpf1.ports.vhigh)
        ckt.new_net(name="vhigh2", external=True, childports=cpf2.ports.vhigh)

        ckt.new_net(name="vlow1", external=True, childports=cpf1.ports.vlow)
        ckt.new_net(name="vlow2", external=True, childports=cpf2.ports.vlow)

        ckt.new_net(name="down1", external=True, childports=cpf1.ports.down)
        ckt.new_net(name="down2", external=True, childports=cpf2.ports.down)

        ckt.new_net(name="up_n1", external=True, childports=cpf1.ports.up_n)
        ckt.new_net(name="up_n2", external=True, childports=cpf2.ports.up_n)

        vctrl1 = ckt.new_net(name="vctrl1", external=True, childports=cpf1.ports.vctrl)
        vctrl2 = ckt.new_net(name="vctrl2", external=True, childports=cpf2.ports.vctrl)
        if load is not None:
            assert load1 is not None
            assert load2 is not None
            vctrl1.childports += load1.ports[load_pin_name]
            vctrl2.childports += load2.ports[load_pin_name]

        tb = sky130.pyspicefab.new_pyspicecircuit(corner=corner, top=ckt, title="cp tb")

        tb.V("vdd", "vdd", "vss", vdd)
        tb.V("vss", "vss", tb.gnd, 0.0)

        tb.SinusoidalVoltageSource("vhigh1", "vdd", "vhigh1", offset=-1.8, amplitude=1.0)
        tb.V("vlow1", "vdd", "vlow1", 0.0)

        tb.V("down1", "down1", "vss", 0.0)
        tb.V("up_n1", "up_n1", "vss", 0.0)

        tb.V("vhigh2", "vdd", "vhigh2", 0.0)
        tb.SinusoidalVoltageSource("vlow2", "vss", "vlow2", offset=vdd, amplitude=1.0)

        tb.V("down2", "down2", "vss", 1.8)
        tb.V("up_n2", "up_n2", "vss", 1.8)

        self.last_sim = sim = tb.simulator(temperature=temperature)
        self.last_ac = ac = sim.ac(
            start_frequency=start_frequency, stop_frequency=stop_frequency,
            number_of_points=5, variation="dec",
        )

        return ac

    def plot_transfer(self, *, ac: Any, axes):
        ax1 = axes[0]
        ax2 = axes[1]

        ax1.plot(
            _np.array(ac.frequency), 20*_np.log10(_np.absolute(_np.array(ac.vctrl1))),
            label="high",
        )
        ax1.plot(
            _np.array(ac.frequency), 20*_np.log10(_np.absolute(_np.array(ac.vctrl2))),
            label="low",
        )
        ax1.set_xscale("log")
        ax1.grid(True)
        ax1.legend()

        if ax2 is not None:
            ax2.plot(
                _np.array(ac.frequency), _np.angle(_np.array(ac.vctrl1), deg=True) - 180.0,
                label="high",
            )
            ax2.plot(
                _np.array(ac.frequency), _np.angle(_np.array(ac.vctrl2), deg=True) - 180.0,
                label="low",
            )
            ax2.set_xscale("log")
            ax2.grid(True)
            ax2.legend()

