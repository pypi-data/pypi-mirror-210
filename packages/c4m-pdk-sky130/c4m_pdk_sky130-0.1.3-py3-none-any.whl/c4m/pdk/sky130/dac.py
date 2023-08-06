# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from typing import Optional, cast

from pdkmaster.technology import geometry as _geo, primitive as _prm, technology_ as _tch
from pdkmaster.design import circuit as _ckt, layout as _lay, cell as _cell

from c4m.pdk import sky130
from c4m.pdk.sky130 import _layout as _sky130lay

_prims = sky130.tech.primitives


__all__ = ["R2R_DAC"]


class R2R_DAC(_cell.OnDemandCell):
    def __init__(self, *,
        name: Optional[str]=None,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        bits: int,
        resistor: _prm.Resistor, res_height: float, res_width: Optional[float]=None,
        inv: _cell.Cell,
    ):
        if name is None:
            name = self.__class__.__name__
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        self.bits = bits
        self.resistor = resistor
        self.res_height = res_height
        self.res_width = res_width
        self.inv = inv

    def _create_circuit(self):
        bits = self.bits
        resistor_prim = self.resistor
        res_height = self.res_height
        res_width = self.res_width
        inv_cell = self.inv

        ckt = self.new_circuit()

        vdd = ckt.new_net(name="vdd", external=True)
        vss = ckt.new_net(name="vss", external=True)

        start_ress = (
            ckt.instantiate(
                resistor_prim, name="start_res[0]",
                width=res_width, height=res_height,
            ),
            ckt.instantiate(
                resistor_prim, name="start_res[1]",
                width=res_width, height=res_height,
            ),
        )

        vss.childports += start_ress[0].ports.port1

        ckt.new_net(name="start_2rconn", external=False, childports=(
            start_ress[0].ports.port2, start_ress[1].ports.port1,
        ))

        prev_net = None
        for n in range(bits):
            r2s = (
                ckt.instantiate(
                    resistor_prim, name=f"2r[{n}][0]",
                    width=res_width, height=res_height,
                ),
                ckt.instantiate(
                    resistor_prim, name=f"2r[{n}][1]",
                    width=res_width, height=res_height,
                ),
            )

            ckt.new_net(name=f"2rconn[{n}]", external=False, childports=(
                r2s[0].ports.port2, r2s[1].ports.port1,
            ))

            net_name = "vout" if n == (bits - 1) else f"node[{n}]"
            external = (n == (bits - 1))
            if prev_net is None:
                prev_net = ckt.new_net(name=net_name, external=external, childports=(
                    start_ress[1].ports.port2, r2s[1].ports.port2,
                ))
            else:
                r = ckt.instantiate(
                    resistor_prim, name=f"r[{n}]",
                    width=res_width, height=res_height,
                )
                prev_net.childports += r.ports.port1

                prev_net = ckt.new_net(name=net_name, external=external, childports=(
                    r2s[1].ports.port2, r.ports.port2,
                ))

            inv = ckt.instantiate(inv_cell, name=f"inv[{n}]")
            vdd.childports += inv.ports.vdd
            vss.childports += inv.ports.vss

            ckt.new_net(name=f"bit_n[{n}]", external=True, childports=inv.ports.i)
            ckt.new_net(name=f"bit[{n}]", external=False, childports=(
                inv.ports.nq, r2s[0].ports.port1,
            ))

    def _create_layout(self):
        bits = self.bits

        poly = cast(_prm.GateWire, _prims.poly)
        li = cast(_prm.MetalWire, _prims.li)
        assert li.pin is not None
        lipin = li.pin
        mcon = cast(_prm.Via, _prims.mcon)
        m1 = cast(_prm.MetalWire, _prims.m1)

        ckt = self.circuit
        nets = ckt.nets

        layouter = self.new_circuitlayouter()

        rotations = {
            name: _geo.Rotation.MX
            for name in (
                "start_res[1]",
                *(f"r[{n}]" for n in range(bits)),
                *(f"2r[{n}][1]" for n in range(bits)),
            )
        }
        placer = _sky130lay.Sky130Layouter(layouter=layouter, rotations=rotations)

        placer.place_at_left(name="start_res[0]")
        placer.place_at_bottom(name="start_res[0]")

        placer.place_to_the_right(
            name="start_res[1]", ref_names="start_res[0]",
        )
        placer.align_bottom(
            name="start_res[1]", ref_name="start_res[0]", prim=poly,
        )

        placer.connect(
            name1="start_res[0]", name2="start_res[1]", prim=li, net=nets.start_2rconn,
        )

        prev_res = "start_res[1]"
        prev_res2 = None
        prev_inv = None
        for n in range(bits):
            res2_0 = f"2r[{n}][0]"
            res2_1 = f"2r[{n}][1]"
            inv = f"inv[{n}]"

            node = nets["vout" if n == (bits - 1) else f"node[{n}]"]
            r2conn = nets[f"2rconn[{n}]"]
            bit = nets[f"bit[{n}]"]

            if prev_inv is None:
                placer.place_to_the_right(
                    name=inv, ref_names=prev_res,
                )
                placer.place_below(
                    name=inv, ref_names=prev_res,
                )
            else:
                placer.place_to_the_right(
                    name=inv, ref_names=prev_inv, boundary_only=True,
                )
                placer.align_bottom(
                    name=inv, ref_name=prev_inv, prim=li, net=nets.vss,
                )

            if n > 0:
                assert prev_inv is not None

                res = f"r[{n}]"
                prev_node = f"node[{n - 1}]"

                placer.place_to_the_right(name=res, ref_names=prev_inv)
                placer.align_bottom(
                    name=res, ref_name=prev_res, prim=poly,
                )

                assert prev_res2 is not None
                placer.connect(
                    name1=prev_res2, name2=res, prim=li, net=nets[prev_node],
                )

                prev_res = res

            placer.place_to_the_right(
                name=res2_1, ref_names=prev_res,
            )
            placer.align_bottom(
                name=res2_1, ref_name=prev_res, prim=poly,
            )

            placer.place_to_the_right(
                name=res2_0, ref_names=res2_1,
            )
            placer.align_bottom(
                name=res2_0, ref_name=res2_1, prim=poly,
            )

            placer.connect(
                name1=res2_0, name2=res2_1, prim=li, net=r2conn,
            )
            placer.connect(
                name1=prev_res, name2=res2_1, prim=li, net=node,
            )

            wire1_name = f"mcon_{bit.name}_inv"
            wire2_name = f"mcon_{bit.name}_res"

            placer.wire(
                wire_name=wire1_name, net=bit, wire=mcon,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=wire1_name, ref_name=inv, ref_pin=True, prim=li, net=bit,
            )
            placer.align_top(
                name=wire1_name, ref_name=inv, ref_pin=True, prim=li, net=bit,
            )

            placer.wire(
                wire_name=wire2_name, net=bit, wire=mcon,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=wire2_name, ref_name=res2_0, prim=li, net=bit,
            )
            placer.align_bottom(
                name=wire2_name, ref_name=res2_0, prim=li, net=bit,
            )

            placer.connect(
                name1=wire1_name, name2=wire2_name, prim=m1, net=bit,
            )

            prev_res = res2_0
            prev_res2 = res2_1
            prev_inv = inv

        placer.connect(
            name1="start_res[0]", name2="inv[0]", prim=li, net=nets.vss,
        )

        if not placer.execute():
            print("R2R_DAC: not all placements completed")

        # pins
        layout = layouter.layout

        # vout
        net = nets.vout
        bb1 = placer.info_lookup[f"r[{bits - 1}]"].bb(mask=li.mask, net=net, placed=True)
        assert bb1 is not None
        bb2 = placer.info_lookup[f"2r[{bits - 1}][1]"].bb(mask=li.mask, net=net, placed=True)
        assert bb2 is not None
        shape = _geo.Rect.from_rect(rect=bb1, right=bb2.right)
        layout.add_shape(layer=lipin, net=net, shape=shape)

        # bit_n[*]
        for n in range(bits):
            net = nets[f"bit_n[{n}]"]
            inv = f"inv[{n}]"

            bb = placer.info_lookup[inv].bb(mask=lipin.mask, net=net, placed=True)
            assert bb is not None
            layout.add_shape(layer=lipin, net=net, shape=bb)

