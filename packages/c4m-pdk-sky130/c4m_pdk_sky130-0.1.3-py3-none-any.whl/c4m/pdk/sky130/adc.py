# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+

# This is a temporary file with ADC support code. After completion it should be
# moved in the c4m.pdk.sky130 module
from typing import Optional, cast
from itertools import chain

from pdkmaster.technology import geometry as _geo, primitive as _prm, technology_ as _tch
from pdkmaster.design import (
    circuit as _ckt, layout as _lay, cell as _cell, library as _lbry,
)

from c4m.pdk import sky130
from c4m.pdk.sky130 import _layout as _sky130lay

_prims = sky130.tech.primitives


__all__ = ["ADC"]


class ADC(_cell.OnDemandCell):
    def __init__(self, *,
        name: str,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        bits: int,
        nmos: _prm.MOSFET, nmos_nom_w: float, nmos_nom_l: Optional[float]=None,
        pmos: _prm.MOSFET,
        pmos_nom_w: float, pmos_nom_l: Optional[float]=None,
        pmos_amppair: Optional[_prm.MOSFET]=None,
        pmos_amppair_w: float, pmos_amppair_l: float,
        pmos_holdpasstrans: Optional[_prm.MOSFET]=None,
        pmos_holdpasstrans_w: float, pmos_holdpasstrans_l: Optional[float]=None,
        stdcelllib: _lbry.Library,
        cap: _prm.CapacitorT, cap_unit_args: dict,
    ):
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)

        nmos_nom_args = {"w": nmos_nom_w}
        if nmos_nom_l is not None:
            nmos_nom_args["l"] = nmos_nom_l
        pmos_nom_args = {"w": pmos_nom_w}
        if pmos_nom_l is not None:
            pmos_nom_args["l"] = pmos_nom_l

        if pmos_amppair is None:
            pmos_amppair = pmos
        pmos_amppair_args = {"w": pmos_amppair_w, "l": pmos_amppair_l}

        if pmos_holdpasstrans is None:
            pmos_holdpasstrans = pmos
        pmos_holdpasstrans_args = {"w": pmos_holdpasstrans_w}
        if pmos_holdpasstrans_l is not None:
            pmos_holdpasstrans_args["l"] = pmos_holdpasstrans_l

        self.bits = bits
        self.nmos = nmos
        self.nmos_nom_args = nmos_nom_args
        self.pmos = pmos
        self.pmos_nom_args = pmos_nom_args
        self.pmos_amppair = pmos_amppair
        self.pmos_amppair_args = pmos_amppair_args
        self.pmos_holdpasstrans = pmos_holdpasstrans
        self.pmos_holdpasstrans_args = pmos_holdpasstrans_args
        self.cap = cap
        self.cap_unit_args = cap_unit_args

        self.stdcells = stdcelllib.cells

    def _create_circuit(self):
        bits = self.bits
        nmos = self.nmos
        nmos_nom_args = self.nmos_nom_args
        pmos = self.pmos
        pmos_nom_args = self.pmos_nom_args
        pmos_amppair = self.pmos_amppair
        pmos_amppair_args = self.pmos_amppair_args
        pmos_holdpasstrans = self.pmos_holdpasstrans
        pmos_holdpasstrans_args = self.pmos_holdpasstrans_args
        cap = self.cap
        cap_unit_args = self.cap_unit_args

        stdcells = self.stdcells

        invd1 = stdcells.inv_x1
        invd2 = stdcells.inv_x2
        nor2 = stdcells.nor2_x0
        nand2 = stdcells.nand2_x0
        ff = stdcells.sff1_x4
        fill = stdcells.fill_w4
        latch = stdcells.nsnrlatch_x1

        # ======================
        # Instantiate primitives
        # ======================

        # sequencer primitives
        # --------------------

        qs = bits + 1
        ckt = self.new_circuit()

        # The start signal is going through a shift register.
        # It may only be high for one clock cycle and not
        # become again before the end signal is high.
        inst_seq_capt = ckt.instantiate(ff, name="seq_capt")
        inst_seq_qffs = tuple(
            ckt.instantiate(ff, name=f"seq_qff[{n}]") for n in range(qs)
        )
        # Add filler cell next to seq_qff
        inst_seq_qffills = tuple(
            ckt.instantiate(fill, name=f"seq_qfffill[{n}]") for n in range(bits)
        )

        # For each bit we use a nsnrlatch.
        # When start is high the latch is reset.
        # The latch is first set for comparison and then the
        # cmp value is put in the latch. So it needs to be
        # reset if cmp is 0. Only reset it during the first half of the clock cycle
        # nrst = (start + q[n+1]*cmp_rst)'
        #      = (start + (q[n+1]*cmp_rst)'')'
        # q[n+1]--\
        # cmp_rst--nand2--inv--nor2==nrst
        # start --------------/
        #
        # nset = (q[n] + q[n+1]*cmp_set)'
        # nset = (q[n] + (q[n+1]*cmp_set)'')'
        # q[n+1]--\
        # cmp_set--nand2--inv--nor2--nset
        # q[n]----------------/

        inst_seq_latch_bits = tuple(
            ckt.instantiate(latch, name=f"seq_latch_bit[{n}]")
            for n in range(bits)
        )
        inst_seq_nand2_nrstbits = tuple(
            ckt.instantiate(nand2, name=f"seq_nand2_nrstbit[{n}]")
            for n in range(bits)
        )
        inst_seq_inv_nrstbits = tuple(
            ckt.instantiate(invd1, name=f"seq_inv_nrstbit[{n}]")
            for n in range(bits)
        )
        inst_seq_nor2_nrstbits = tuple(
            ckt.instantiate(nor2, name=f"seq_nor2_nrstbit[{n}]")
            for n in range(bits)
        )
        inst_seq_nand2_nsetbits = tuple(
            ckt.instantiate(nand2, name=f"seq_nand2_nsetbit[{n}]")
            for n in range(bits)
        )
        inst_seq_inv_nsetbits = tuple(
            ckt.instantiate(invd1, name=f"seq_inv_nsetbit[{n}]")
            for n in range(bits)
        )
        inst_seq_nor2_nsetbits = tuple(
            ckt.instantiate(nor2, name=f"seq_nor2_nsetbit[{n}]")
            for n in range(bits)
        )

        # DAC
        # ---

        inst_dac_refcap = ckt.instantiate(cap, name="dac_refcap", **cap_unit_args)
        inst_dac_pmosholdpass = ckt.instantiate(
            pmos_holdpasstrans, name="dac_pmosholdpass", **pmos_holdpasstrans_args,
        )

        dac_caps = []
        dac_switches = []
        for bit in range(bits):
            n_caps = 2**(bits - bit - 1)
            sub_caps = tuple(
                ckt.instantiate(cap, name=f"daccap[{bit}][{n}]", **cap_unit_args)
                for n in range(n_caps)
            )
            dac_caps.append(sub_caps)

            invswitch = ckt.instantiate(invd2, name=f"invswitch[{bit}]")
            dac_switches.append(invswitch)

        # Comparator
        # ----------

        # Run comparator with inverted clock
        clk_inv = ckt.instantiate(invd1, name="clk_inv")
        clk_inv2 = ckt.instantiate(invd1, name="clk_inv2")

        # The hold pass gate needs inverted signal for pmos
        start_latch_inv = ckt.instantiate(invd1, name="start_latch_inv")

        # Amplifier
        amp_en = ckt.instantiate(pmos, name="amp_en", **pmos_nom_args)
        amp_cmp1 = ckt.instantiate(
            pmos_amppair, name="amp_cmp1", **pmos_amppair_args,
        )
        amp_cmp2 = ckt.instantiate(
            pmos_amppair, name="amp_cmp2", **pmos_amppair_args,
        )

        amp_unlen = ckt.instantiate(nmos, name="amp_unlen", **nmos_nom_args)
        amp_unl1 = ckt.instantiate(nmos, name="amp_unl1", **nmos_nom_args)
        amp_unl2 = ckt.instantiate(nmos, name="amp_unl2", **nmos_nom_args)

        # Inverters
        amp_inv1 = ckt.instantiate(invd1, name="amp_inv1")
        amp_inv2 = ckt.instantiate(invd1, name="amp_inv2")

        # Lewis and Gray latch
        lg_leftenvdd = ckt.instantiate(pmos, name="lg_leftenvdd", **pmos_nom_args)
        lg_leftunltop = ckt.instantiate(nmos, name="lg_leftunltop", **nmos_nom_args)
        lg_leftenbottom = ckt.instantiate(nmos, name="lg_leftenbottom", **nmos_nom_args)
        lg_leftlatchtop = ckt.instantiate(pmos, name="lg_leftlatchtop", **pmos_nom_args)
        lg_leftlatchbottom = ckt.instantiate(nmos, name="lg_leftlatchbottom", **nmos_nom_args)

        lg_rightenvdd = ckt.instantiate(pmos, name="lg_rightenvdd", **pmos_nom_args)
        lg_rightunltop = ckt.instantiate(nmos, name="lg_rightunltop", **nmos_nom_args)
        lg_rightenbottom = ckt.instantiate(nmos, name="lg_rightenbottom", **nmos_nom_args)
        lg_rightlatchtop = ckt.instantiate(pmos, name="lg_rightlatchtop", **pmos_nom_args)
        lg_rightlatchbottom = ckt.instantiate(nmos, name="lg_rightlatchbottom", **nmos_nom_args)

        #
        # Create nets
        #

        # collections
        # -----------

        inst_allcells = (
            inst_seq_capt, *inst_seq_qffs, *inst_seq_qffills,
            *inst_seq_latch_bits,
            *inst_seq_nand2_nrstbits, *inst_seq_inv_nrstbits, *inst_seq_nor2_nrstbits,
            *inst_seq_nand2_nsetbits, *inst_seq_inv_nsetbits, *inst_seq_nor2_nsetbits,
            start_latch_inv, *dac_switches,
            clk_inv, clk_inv2,
            amp_inv1, amp_inv2,
        )
        amp_pmoss = (
            amp_en, amp_cmp1, amp_cmp2,
            lg_leftenvdd, lg_leftlatchtop, lg_rightenvdd, lg_rightlatchtop,
        )
        amp_nmoss = (
            amp_unlen, amp_unl1, amp_unl2,
            lg_leftunltop, lg_leftenbottom, lg_leftlatchbottom,
            lg_rightunltop, lg_rightenbottom, lg_rightlatchbottom,
        )

        # ===============
        # Create the nets
        # ===============

        # DC
        # --

        ckt.new_net(name="vdd", external=True, childports=(
            *(inst.ports.vdd for inst in inst_allcells),
            inst_dac_refcap.ports.bottom,
            inst_dac_pmosholdpass.ports.bulk,
            *(mp.ports.bulk for mp in amp_pmoss), amp_en.ports.sourcedrain1,
            lg_leftenvdd.ports.sourcedrain1, lg_rightenvdd.ports.sourcedrain1,
        ))
        ckt.new_net(name="vss", external=True, childports=(
            *(inst.ports.vss for inst in inst_allcells),
            *(mn.ports.bulk for mn in amp_nmoss), *(mn.ports.sourcedrain2 for mn in amp_nmoss),
            # '-' input of comparator is connected to vss
            amp_cmp2.ports.gate,
        ))

        # pins
        # ----

        ckt.new_net(name="clk", external=True, childports=(
            inst_seq_capt.ports.ck, clk_inv.ports.i,
        ))
        ckt.new_net(name="vin", external=True, childports=(
            inst_dac_pmosholdpass.ports.sourcedrain1,
        ))
        ckt.new_net(name="start", external=True, childports=(
            inst_seq_capt.ports.i, *(inst.ports.i1 for inst in inst_seq_nor2_nrstbits),
        ))
        # Connect the last qff to the output
        ckt.new_net(name="end", external=True, childports=(
            inst_seq_qffs[-1].ports.q,
            inst_seq_nand2_nrstbits[-1].ports.i0, inst_seq_nand2_nsetbits[-1].ports.i0,
        ))
        for n, inst_latch in enumerate(inst_seq_latch_bits):
            invswitch = dac_switches[n]
            ckt.new_net(name=f"bit[{n}]", external=True, childports=(
                    inst_latch.ports.q, invswitch.ports.i,
            ))
            ckt.new_net(
                name=f"bit_n[{n}]", external=True, childports=inst_latch.ports.nq,
            )

        # internal
        # --------
        ckt.new_net(name="clk_n", external=False, childports=(
            clk_inv.ports.nq,
            *(inst.ports.gate for inst in (amp_en, amp_unlen, amp_unl1, amp_unl2)),
            clk_inv2.ports.i,
        ))
        ckt.new_net(name="clk2", external=False, childports=(
            clk_inv2.ports.nq,
            *(inst.ports.ck for inst in inst_seq_qffs),
        ))
        ckt.new_net(name="start_latch", external=False, childports=(
            inst_seq_capt.ports.q, inst_seq_qffs[0].ports.i,
            start_latch_inv.ports.i,
        ))
        ckt.new_net(name="start_latch_n", external=False, childports=(
            start_latch_inv.ports.nq, inst_dac_pmosholdpass.ports.gate,
        ))

        for n in range(bits):
            inst_qff = inst_seq_qffs[n]
            inst_qff_next = inst_seq_qffs[n + 1]
            inst_latch = inst_seq_latch_bits[n]
            inst_nand2_nrstbit = inst_seq_nand2_nrstbits[n]
            inst_inv_nrstbit = inst_seq_inv_nrstbits[n]
            inst_nor2_nrstbit = inst_seq_nor2_nrstbits[n]
            inst_nand2_nsetbit = inst_seq_nand2_nsetbits[n]
            inst_inv_nsetbit = inst_seq_inv_nsetbits[n]
            inst_nor2_nsetbit = inst_seq_nor2_nsetbits[n]

            ports = [inst_qff.ports.q, inst_qff_next.ports.i, inst_nor2_nsetbit.ports.i1]
            if n > 0:
                inst_nand2_nrstbit2 = inst_seq_nand2_nrstbits[n - 1]
                inst_nand2_nsetbit2 = inst_seq_nand2_nsetbits[n - 1]
                ports.extend((inst_nand2_nrstbit2.ports.i0, inst_nand2_nsetbit2.ports.i0))
            ckt.new_net(name=f"q[{n}]", external=False, childports=ports)

            ckt.new_net(name=f"nrstbit[{n}]_nand2", external=False, childports=(
                inst_nand2_nrstbit.ports.nq, inst_inv_nrstbit.ports.i,
            ))
            ckt.new_net(name=f"nrstbit[{n}]_inv", external=False, childports=(
                inst_inv_nrstbit.ports.nq, inst_nor2_nrstbit.ports.i0,
            ))
            ckt.new_net(name=f"nrst_bit[{n}]", external=False, childports=(
                inst_nor2_nrstbit.ports.nq, inst_latch.ports.nrst),
            )
            ckt.new_net(name=f"nsetbit[{n}]_nand2", external=False, childports=(
                inst_nand2_nsetbit.ports.nq, inst_inv_nsetbit.ports.i,
            ))
            ckt.new_net(name=f"nsetbit[{n}]_inv", external=False, childports=(
                inst_inv_nsetbit.ports.nq, inst_nor2_nsetbit.ports.i0,
            ))
            ckt.new_net(name=f"nset_bit[{n}]", external=False, childports=(
                inst_nor2_nsetbit.ports.nq, inst_latch.ports.nset),
            )

        for bit, sub_caps in enumerate(dac_caps):
            invswitch = dac_switches[bit]
            ckt.new_net(name=f"dac_cap_bit[{bit}]", external=False, childports=(
                *(cap.ports.bottom for cap in sub_caps), invswitch.ports.nq,
            ))

        ckt.new_net(name="dac_caps_common", external=False, childports=(
            inst_dac_pmosholdpass.ports.sourcedrain2,
            *(cap.ports.top for cap in (*chain(*dac_caps), inst_dac_refcap)),
            amp_cmp1.ports.gate,
        ))

        ckt.new_net(name="amp_outn", external=False, childports=(
            amp_cmp1.ports.sourcedrain2, amp_unl1.ports.sourcedrain1, amp_inv1.ports.i,
        ))
        ckt.new_net(name="amp_outp", external=False, childports=(
            amp_cmp2.ports.sourcedrain2, amp_unl2.ports.sourcedrain1, amp_inv2.ports.i,
        ))
        ckt.new_net(name="amp_vdden", external=False, childports=(
            amp_en.ports.sourcedrain2, amp_cmp1.ports.sourcedrain1, amp_cmp2.ports.sourcedrain1, amp_unlen.ports.sourcedrain1,
        ))

        ckt.new_net(name="amp_bufp", external=False, childports=(
            amp_inv1.ports.nq, lg_leftenvdd.ports.gate, lg_leftunltop.ports.gate, lg_leftenbottom.ports.gate,
        ))
        ckt.new_net(name="amp_bufn", external=False, childports=(
            amp_inv2.ports.nq, lg_rightenvdd.ports.gate, lg_rightunltop.ports.gate, lg_rightenbottom.ports.gate,
        ))

        ckt.new_net(name="lg_leftvdden", external=False, childports=(
            lg_leftenvdd.ports.sourcedrain2, lg_leftunltop.ports.sourcedrain1, lg_leftlatchtop.ports.sourcedrain1,
        ))
        ckt.new_net(name="lg_rightvdden", external=False, childports=(
            lg_rightenvdd.ports.sourcedrain2, lg_rightunltop.ports.sourcedrain1, lg_rightlatchtop.ports.sourcedrain1,
        ))

        ckt.new_net(name="cmp_set", external=False, childports=(
            lg_leftlatchtop.ports.gate, lg_leftlatchbottom.ports.gate,
            lg_rightlatchtop.ports.sourcedrain2, lg_rightenbottom.ports.sourcedrain1,
            lg_rightlatchbottom.ports.sourcedrain1,
            *(nand2.ports.i1 for nand2 in inst_seq_nand2_nsetbits),
        ))
        ckt.new_net(name="cmp_rst", external=False, childports=(
            lg_rightlatchtop.ports.gate, lg_rightlatchbottom.ports.gate,
            lg_leftlatchtop.ports.sourcedrain2, lg_leftenbottom.ports.sourcedrain1,
            lg_leftlatchbottom.ports.sourcedrain1,
            *(nand2.ports.i1 for nand2 in inst_seq_nand2_nrstbits),
        ))

    def _create_layout(self):
        difftap = cast(_prm.WaferWire, _prims.difftap)
        nsdm = cast(_prm.Implant, _prims.nsdm)
        psdm = cast(_prm.Implant, _prims.psdm)
        nwell = self.pmos.well
        assert nwell is not None
        assert nwell == self.pmos_amppair.well
        assert nwell == self.pmos_holdpasstrans.well
        pwell = self.nmos.well
        assert pwell is None
        poly = cast(_prm.GateWire, _prims.poly)
        licon = cast(_prm.Via, _prims.licon)
        li = cast(_prm.MetalWire, _prims.li)
        mcon = cast(_prm.Via, _prims.mcon)
        m1 = cast(_prm.MetalWire, _prims.m1)
        via = cast(_prm.Via, _prims.via)
        m2 = cast(_prm.MetalWire, _prims.m2)
        via2 = cast(_prm.Via, _prims.via2)
        m3 = cast(_prm.MetalWire, _prims.m3)
        via3 = cast(_prm.Via, _prims.via3)
        m4 = cast(_prm.MetalWire, _prims.m4)

        bits = self.bits
        qs = bits + 1

        ckt = self.circuit
        nets = ckt.nets

        rotations = {
            "seq_capt": _geo.Rotation.MY,
            "start_latch_inv": _geo.Rotation.MY,
            "lg_rightenvdd": _geo.Rotation.MY,
            "lg_rightlatchtop": _geo.Rotation.MY,
            "lg_rightlatchbottom": _geo.Rotation.MY,
            "amp_inv1": _geo.Rotation.MX,
            "amp_inv2": _geo.Rotation.MX,
        }
        for n in range(bits):
            rotations.update({
                name: _geo.Rotation.MX
                for name in (
                    f"seq_nand2_nsetbit[{n}]", f"seq_nand2_nrstbit[{n}]",
                    f"seq_inv_nsetbit[{n}]", f"seq_inv_nrstbit[{n}]",
                    f"seq_nor2_nsetbit[{n}]", f"seq_nor2_nrstbit[{n}]",
                    f"seq_latch_bit[{n}]", f"invswitch[{n}]",
                )
            })
        layouter = self.new_circuitlayouter()
        placer = _sky130lay.Sky130Layouter(layouter=layouter, rotations=rotations)

        # Hacking
        # =======
        
        # Add boundary to the MIM caps; so abutment works.
        # TODO: should be handled by regular placement rules
        all_caps = ["dac_refcap"]
        for bit in range(bits):
            for cap in range(2**bit):
                all_caps.append(f"daccap[{bits - bit - 1}][{cap}]")
        for cap_name in all_caps:
            info = placer.info_lookup[cap_name]
            shape = info.layout.boundary
            assert shape is not None
            info.layout.add_shape(layer=m4, net=nets.dac_caps_common, shape=shape)

        # Place instances & sd contacts
        # =============================

        placer.place_at_bottom(name="start_latch_inv")
        placer.place_at_left(name="start_latch_inv")
        left_cell = "start_latch_inv"

        placer.place_at_bottom(name="seq_capt")
        placer.place_to_the_right(
            name="seq_capt", ref_names="start_latch_inv", boundary_only=True,
        )

        placer.place_at_bottom(name="clk_inv")
        placer.place_to_the_right(
            name="clk_inv", ref_names="seq_capt", boundary_only=True,
        )

        placer.place_at_bottom(name="clk_inv2")
        placer.place_to_the_right(
            name="clk_inv2", ref_names="clk_inv", boundary_only=True,
        )

        # for n in range(bits):
        prev_names = "clk_inv2"
        for n in range(bits):
            qff_name = f"seq_qff[{n}]"
            fill_name = f"seq_qfffill[{n}]"
            cell_names = (
                f"seq_nand2_nsetbit[{n}]",
                f"seq_inv_nsetbit[{n}]",
                f"seq_nor2_nsetbit[{n}]",
                f"seq_latch_bit[{n}]",
                f"invswitch[{n}]",
                f"seq_nor2_nrstbit[{n}]",
                f"seq_inv_nrstbit[{n}]",
                f"seq_nand2_nrstbit[{n}]",
            )

            placer.place_at_bottom(name=qff_name)
            placer.place_to_the_right(
                name=qff_name, ref_names=prev_names, boundary_only=True,
            )

            placer.place_at_bottom(name=fill_name)
            placer.place_to_the_right(
                name=fill_name, ref_names=qff_name, boundary_only=True,
            )

            for i, name in enumerate(cell_names):
                placer.place_above(name=name, ref_names=qff_name, boundary_only=True)
                ref_name = cell_names[i - 1] if i > 0 else prev_names
                placer.place_to_the_right(
                    name=name, ref_names=ref_name, boundary_only=True,
                )

            prev_names = (qff_name, cell_names[-1])
        # Place last qff
        qff_name = f"seq_qff[{bits}]"
        placer.place_at_bottom(name=qff_name)
        placer.place_to_the_right(
            name=qff_name, ref_names=prev_names, boundary_only=True,
        )

        # Lewis and Gray latch
        lg_ptrans1_name = "lg_rightenvdd"
        lg_ptrans2_name = "lg_rightlatchtop"
        lg_ptrans3_name = "lg_leftlatchtop"
        lg_ptrans4_name = "lg_leftenvdd"

        lg_ptrans1sd2_name = f"{lg_ptrans1_name}__sd2" # vdd
        lg_ptrans12sd_name = f"{lg_ptrans1_name}__{lg_ptrans2_name}__sd" # lg_rightvdden
        lg_ptrans2sd1_name = f"{lg_ptrans2_name}__sd1" # cmp_set
        lg_ptrans3sd2_name = f"{lg_ptrans3_name}__sd2" # cmp_rst
        lg_ptrans34sd_name = f"{lg_ptrans3_name}__{lg_ptrans4_name}__sd" # lg_leftvdden
        lg_ptrans4sd1_name = f"{lg_ptrans4_name}__sd1" # vdd

        lg_ntrans1_name = "lg_rightunltop"
        lg_ntrans2_name = "lg_rightlatchbottom"
        lg_ntrans3_name = "lg_rightenbottom"
        lg_ntrans4_name = "lg_leftenbottom"
        lg_ntrans5_name = "lg_leftlatchbottom"
        lg_ntrans6_name = "lg_leftunltop"

        lg_ntrans1sd2_name = f"{lg_ntrans1_name}__sd2" # lg_rightvdden
        lg_ntrans12sd_name = f"{lg_ntrans1_name}__{lg_ntrans2_name}__sd" # vss
        lg_ntrans23sd_name = f"{lg_ntrans2_name}__{lg_ntrans3_name}__sd" # cmp_set
        lg_ntrans34sd_name = f"{lg_ntrans3_name}__{lg_ntrans4_name}__sd" # vss
        lg_ntrans45sd_name = f"{lg_ntrans4_name}__{lg_ntrans5_name}__sd" # cmp_rst
        lg_ntrans56sd_name = f"{lg_ntrans5_name}__{lg_ntrans6_name}__sd" # vss
        lg_ntrans6sd1_name = f"{lg_ntrans6_name}__sd1" # lg_leftvdden

        lg_pad1_name = "polypad_amp_bufn"
        lg_pad2_name = "polypad_cmp_rst"
        lg_pad3_name = "polypad_amp_bufn2"
        lg_pad4_name = "polypad_amp_bufp2"
        lg_pad5_name = "polypad_cmp_set"
        lg_pad6_name = "polypad_amp_bufp"

        for psd_name, net in (
            (lg_ptrans1sd2_name, nets.vdd),
            (lg_ptrans12sd_name, nets.lg_rightvdden),
            (lg_ptrans2sd1_name, nets.cmp_set),
            (lg_ptrans3sd2_name, nets.cmp_rst),
            (lg_ptrans34sd_name, nets.lg_leftvdden),
            (lg_ptrans4sd1_name, nets.vdd),
        ):
            placer.wire(
                wire_name=psd_name, net=net, well_net=nets.vdd, wire=licon,
                bottom=difftap, bottom_well=nwell, bottom_implant=psdm,
                bottom_height=self.pmos_nom_args["w"],
                bottom_enclosure="tall", top_enclosure="tall",
            )

        for nsd_name, net in (
            (lg_ntrans1sd2_name, nets.lg_rightvdden),
            (lg_ntrans12sd_name, nets.vss),
            (lg_ntrans23sd_name, nets.cmp_set),
            (lg_ntrans34sd_name, nets.vss),
            (lg_ntrans45sd_name, nets.cmp_rst),
            (lg_ntrans56sd_name, nets.vss),
            (lg_ntrans6sd1_name, nets.lg_leftvdden),
        ):
            placer.wire(
                wire_name=nsd_name, net=net, wire=licon,
                bottom=difftap, bottom_implant=nsdm,
                bottom_height=self.nmos_nom_args["w"],
                bottom_enclosure="tall", top_enclosure="tall",
            )

        for pad_name, net in (
            (lg_pad1_name, nets.amp_bufn),
            (lg_pad2_name, nets.cmp_rst),
            (lg_pad3_name, nets.amp_bufn),
            (lg_pad4_name, nets.amp_bufp),
            (lg_pad5_name, nets.cmp_set),
            (lg_pad6_name, nets.amp_bufp),
        ):
            placer.wire(
                wire_name=pad_name, net=net, wire=licon,
                bottom=poly, bottom_enclosure="tall", top_enclosure="wide",
            )
        # Add psdm on pmos pad
        # TODO: should be able to be done by adding bottom implamt layer to the
        # wire
        for pad_name in (lg_pad1_name, lg_pad3_name, lg_pad5_name):
            info = placer.info_lookup[pad_name]
            bb = info.bb(mask=poly.mask)
            assert bb is not None
            info.layout.add_shape(layer=psdm, net=None, shape=bb)

        placer.place_to_the_left(
            name=lg_ptrans1sd2_name, ref_names="seq_nand2_nsetbit[0]",
            ignore_masks=nwell.mask,
        )
        prev_name = lg_ptrans1sd2_name
        for place_name in (
            lg_ptrans1_name, lg_ptrans12sd_name,
            lg_ptrans2_name, lg_ptrans2sd1_name,
        ):
            placer.place_to_the_left(
                name=place_name, ref_names=prev_name,
                ignore_masks=(difftap.mask, psdm.mask, nwell.mask),
            )
            prev_name = place_name

        placer.align_top(
            name=lg_ptrans1_name, ref_name="seq_nand2_nsetbit[0]", prim=nwell,
        )

        for align_name in (
            lg_ptrans1sd2_name, lg_ptrans12sd_name,
            lg_ptrans2_name, lg_ptrans2sd1_name,
            lg_ptrans3sd2_name,
            lg_ptrans3_name, lg_ptrans34sd_name,
            lg_ptrans4_name, lg_ptrans4sd1_name,
        ):
            placer.align_top(
                name=align_name, ref_name=lg_ptrans1_name, prim=difftap,
            )

        placer.center_x(
            name=lg_pad1_name, ref_name=lg_ptrans1_name, prim=poly, net=nets.amp_bufn,
        )
        placer.place_above(
            name=lg_pad1_name, ref_names=lg_ptrans1_name,
            ignore_masks=(poly.mask, psdm.mask),
        )

        placer.center_x(
            name=lg_pad2_name, ref_name=lg_ptrans2_name, prim=poly, net=nets.cmp_rst,
        )
        placer.place_above(name=lg_pad2_name, ref_names=lg_pad1_name)

        placer.center_x(
            name=lg_pad3_name, ref_name=lg_ntrans3_name, prim=poly, net=nets.amp_bufn,
        )
        placer.align_top(name=lg_pad3_name, ref_name=lg_pad1_name, prim=poly)

        placer.align_right(
            name=lg_ntrans1_name, ref_name=lg_ptrans1_name, prim=poly,
        )
        placer.place_to_the_right(
            name=lg_ntrans1sd2_name, ref_names=lg_ntrans1_name,
            ignore_masks=(difftap.mask, nsdm.mask),
        )
        prev_name = lg_ntrans1_name
        for place_name in (
            lg_ntrans12sd_name,
            lg_ntrans2_name, lg_ntrans23sd_name,
            lg_ntrans3_name, lg_ntrans34sd_name,
            lg_ntrans4_name, lg_ntrans45sd_name,
            lg_ntrans5_name, lg_ntrans56sd_name,
            lg_ntrans6_name, lg_ntrans6sd1_name,
        ):
            placer.place_to_the_left(
                name=place_name, ref_names=prev_name,
                ignore_masks=(difftap.mask, nsdm.mask),
            )
            prev_name = place_name

        placer.place_above(
            name=lg_ntrans1_name, ref_names=(lg_pad1_name, lg_pad2_name),
            ignore_masks=poly.mask,
        )
        for align_name in (
            lg_ntrans1sd2_name, lg_ntrans12sd_name,
            lg_ntrans2_name, lg_ntrans23sd_name,
            lg_ntrans3_name, lg_ntrans34sd_name,
            lg_ntrans4_name, lg_ntrans45sd_name,
            lg_ntrans5_name, lg_ntrans56sd_name,
            lg_ntrans6_name, lg_ntrans6sd1_name,
        ):
            placer.align_bottom(
                name=align_name, ref_name=lg_ntrans1_name, prim=difftap,
            )

        placer.center_x(
            name=lg_pad4_name, ref_name=lg_ntrans4_name, prim=poly, net=nets.amp_bufp,
        )
        placer.place_below(
            name=lg_pad4_name, ref_names=lg_ntrans4_name, ignore_masks=poly.mask,
        )

        placer.center_x(
            name=lg_pad5_name, ref_name=lg_ntrans5_name, prim=poly, net=nets.cmp_set,
        )
        placer.place_below(
            name=lg_pad5_name, ref_names=lg_pad4_name,
        )

        placer.center_x(
            name=lg_pad6_name, ref_name=lg_ntrans6_name, prim=poly, net=nets.amp_bufp,
        )
        placer.place_below(
            name=lg_pad6_name, ref_names=lg_ntrans6_name, ignore_masks=poly.mask,
        )

        placer.align_right(
            name=lg_ptrans3_name, ref_name=lg_ntrans5_name, prim=poly, net=nets.cmp_set,
        )
        placer.place_to_the_right(
            name=lg_ptrans3sd2_name, ref_names=lg_ptrans3_name,
            ignore_masks=(difftap.mask, psdm.mask, nwell.mask),
        )
        prev_name = lg_ptrans3_name
        for place_name in (lg_ptrans34sd_name, lg_ptrans4_name, lg_ptrans4sd1_name):
            placer.place_to_the_left(
                name=place_name, ref_names=prev_name,
                ignore_masks=(difftap.mask, psdm.mask, nwell.mask),
            )
            prev_name = place_name

        placer.connect(
            name1=lg_ntrans1_name, name2=lg_ptrans1_name, net=nets.amp_bufn, prim=poly,
        )
        placer.connect(
            name1=lg_ntrans2_name, name2=lg_ptrans2_name, net=nets.cmp_rst, prim=poly,
        )
        placer.connect(
            name1=lg_ntrans3_name, name2=lg_pad3_name, net=nets.amp_bufn, prim=poly,
        )
        placer.connect(
            name1=lg_ntrans4_name, name2=lg_pad4_name, net=nets.amp_bufp, prim=poly,
        )
        placer.connect(
            name1=lg_ntrans5_name, name2=lg_ptrans3_name, net=nets.cmp_set, prim=poly,
        )
        placer.connect(
            name1=lg_ntrans6_name, name2=lg_ptrans4_name, net=nets.amp_bufp, prim=poly,
        )

        placer.connect(
            name1=lg_pad1_name, name2=lg_pad3_name, net=nets.amp_bufn, prim=li,
        )
        placer.connect(
            name1=lg_pad4_name, name2=lg_pad6_name, net=nets.amp_bufp, prim=li,
        )

        placer.fill(
            names=(lg_ptrans1sd2_name, left_cell), prim=nwell, net=nets.vdd,
        )

        # dac_caps
        #
        # Help typing
        # Make it so that error will be generated when default value is used
        prev_top_via: str = ""
        prev_left_via: str = ""
        prev_right_via: str = ""
        cap_group: Optional[list[str]] = None
        cap_group1: Optional[list[str]] = None
        cap_group2: Optional[list[str]] = None


        # Build up array, always keep reference for left, bottom, right and top cell
        # left and bottom cell will be place at the end relative to other cells
        # This allows to support different #bits

        cap_net = nets.vdd
        cap_name = "dac_refcap"
        via_name = f"via2_{cap_name}"
        left_cap = cap_name
        right_cap = cap_name
        bottom_cap = cap_name
        top_cap = cap_name
        placer.wire(
            wire_name=via_name, net=cap_net, wire=via2,
            ref_top_height=cap_name,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.align_right(
            name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
        )
        placer.center_y(
            name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
        )
        prev_via = via_name

        cap_net = nets[f"dac_cap_bit[{bits - 1}]"]
        cap_name = f"daccap[{bits - 1}][0]"
        via_name = f"via2_{cap_name}"
        placer.center_x(
            name=cap_name, ref_name=left_cap, prim=m3,
        )
        placer.place_above(
            name=cap_name, ref_names=bottom_cap, ignore_masks=m4.mask,
        )
        top_cap = cap_name
        placer.wire(
            wire_name=via_name, net=cap_net, wire=via2,
            ref_top_height=cap_name,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.place_to_the_left(name=via_name, ref_names=prev_via)
        placer.center_y(
            name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
        )
        prev_via = via_name
        cap_bit_via2s = [via_name]

        if bits > 8:
            raise NotImplementedError("Capacitance layout for #bits > 8")

        if bits > 1:
            cap_net = nets[f"dac_cap_bit[{bits - 2}]"]

            cap_name = f"daccap[{bits - 2}][0]"
            via_name = f"via2_{cap_name}"
            placer.center_x(
                name=cap_name, ref_name=left_cap, prim=m3,
            )
            placer.place_above(
                name=bottom_cap, ref_names=cap_name, ignore_masks=m4.mask,
            )
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_height=cap_name,
                top_enclosure="tall", bottom_enclosure="tall",
            )
            placer.place_to_the_left(name=via_name, ref_names=prev_via)
            placer.center_y(name=via_name, ref_name=cap_name, prim=m3, net=cap_net)
            bottom_cap = cap_name
            prev_top_via = prev_via = via_name
            cap_bit_via2s.insert(0, via_name)

            cap_name = f"daccap[{bits - 2}][1]"
            via_name = f"via2_{cap_name}"
            placer.center_x(
                name=cap_name, ref_name=right_cap, prim=m3,
            )
            placer.place_above(
                name=cap_name, ref_names=top_cap, ignore_masks=m4.mask,
            )
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_height=cap_name,
                top_enclosure="tall", bottom_enclosure="tall",
            )
            placer.center_x(name=via_name, ref_name=prev_via, prim=m3, net=cap_net)
            placer.center_y(name=via_name, ref_name=cap_name, prim=m3, net=cap_net)
            top_cap = cap_name
            prev_top_via = via_name

            placer.connect(
                name1=prev_via, name2=via_name, prim=m2, net=cap_net,
            )

        if bits > 2:
            cap_net = nets[f"dac_cap_bit[{bits - 3}]"]
            cap_names = (f"daccap[{bits - 3}][{n}]" for n in range(2**2))

            # column of 2 on the left
            cap_group = []

            cap_name = next(cap_names)
            via_name = f"via2_{cap_name}"
            placer.place_to_the_right(
                name=left_cap, ref_names=cap_name, ignore_masks=m4.mask,
            )
            placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_height=cap_name,
                top_enclosure="tall", bottom_enclosure="tall",
            )
            placer.align_right(name=via_name, ref_name=cap_name, prim=m3, net=cap_net)
            placer.center_y(name=via_name, ref_name=cap_name, prim=m3, net=cap_net)
            left_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)
            prev_via = via_name
            prev_left_via = via_name
            cap_bit_via2s.insert(0, via_name)

            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
            placer.place_above(
                name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
            )
            cap_group.append(cap_name)

            placer.fill(names=cap_group, prim=m3, net=cap_net)
            cap_group = []

            # column of 2 on the right
            cap_name = next(cap_names)
            via_name = f"via2_{cap_name}"
            placer.place_to_the_right(
                name=cap_name, ref_names=right_cap, ignore_masks=m4.mask,
            )
            placer.center_y(name=cap_name, ref_name=top_cap, prim=m3)
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_height=cap_name,
                top_enclosure="tall", bottom_enclosure="tall",
            )
            placer.align_left(name=via_name, ref_name=cap_name, prim=m3, net=cap_net)
            placer.center_y(name=via_name, ref_name=cap_name, prim=m3, net=cap_net)
            right_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)
            prev_right_via = via_name

            conn_name = f"m2_{cap_net.name}_conn"
            placer.wire(
                wire_name=conn_name, net=cap_net, wire=m2,
                width=3*m2.min_width, height=2*m2.min_width,
            )
            placer.center_x(name=conn_name, ref_name=prev_top_via, prim=m2)
            placer.place_above(name=conn_name, ref_names=prev_top_via)
            placer.connect(
                name1=conn_name, name2=prev_via, prim=m2, net=cap_net,
            )
            placer.connect(
                name1=conn_name, name2=via_name, prim=m2, net=cap_net,
            )
            prev_top_via = conn_name

            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
            placer.place_below(
                name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
            )
            cap_group.append(cap_name)

            placer.fill(names=cap_group, prim=m3, net=cap_net)
            cap_group = None

            try:
                next(cap_names)
            except StopIteration:
                pass
            else:
                raise RuntimeError("Internal error")

        if bits > 3:
            cap_net = nets[f"dac_cap_bit[{bits - 4}]"]
            cap_names = (f"daccap[{bits - 4}][{n}]" for n in range(2**3))

            # 2X2 caps on the left
            cap_group = []

            cap_name = next(cap_names)
            via_name = f"via2_{cap_name}"
            placer.center_x(name=cap_name, ref_name=left_cap, prim=m3)
            placer.center_y(name=cap_name, ref_name=top_cap, prim=m3)
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_height=cap_name,
                bottom_enclosure="tall", top_enclosure="tall",
            )
            placer.place_to_the_left(name=via_name, ref_names=prev_left_via)
            placer.center_y(name=via_name, ref_name=cap_name, prim=m3, net=cap_net)
            prev_via = via_name
            prev_cap = cap_name
            cap_bit_via2s.insert(0, via_name)
            cap_group.append(cap_name)

            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=left_cap, prim=m3)
            placer.place_below(
                name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
            )
            cap_group.append(cap_name)

            cap_name = next(cap_names)
            placer.place_to_the_right(
                name=left_cap, ref_names=cap_name, ignore_masks=m4.mask,
            )
            placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
            left_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)

            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=left_cap, prim=m3)
            placer.place_below(
                name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
            )
            cap_group.append(cap_name)

            placer.fill(names=cap_group, prim=m3, net=cap_net)

            # 2X2 caps on the right
            cap_group = []

            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=right_cap, prim=m3)
            placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
            prev_cap = cap_name
            cap_group.append(cap_name)

            cap_name = next(cap_names)
            via_name = f"via2_{cap_name}"
            placer.center_x(name=cap_name, ref_name=right_cap, prim=m3)
            placer.place_above(
                name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
            )
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_height=cap_name,
                bottom_enclosure="tall", top_enclosure="tall",
            )
            placer.place_to_the_right(name=via_name, ref_names=prev_right_via)
            placer.center_y(name=via_name, ref_name=cap_name, prim=m3, net=cap_net)
            cap_group.append(cap_name)

            conn_name = f"m3_{cap_net.name}_conn"
            placer.wire(
                wire_name=conn_name, net=cap_net, wire=m2,
                width=3*m2.min_width, height=2*m2.min_width,
            )
            placer.center_x(name=conn_name, ref_name=prev_top_via, prim=m2)
            placer.place_above(name=conn_name, ref_names=prev_top_via)
            placer.connect(
                name1=conn_name, name2=prev_via, prim=m2, net=cap_net,
            )
            placer.connect(
                name1=conn_name, name2=via_name, prim=m2, net=cap_net,
            )
            prev_top_via = conn_name

            cap_name = next(cap_names)
            placer.place_to_the_right(
                name=cap_name, ref_names=right_cap, ignore_masks=m4.mask,
            )
            placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
            right_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)

            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=right_cap, prim=m3)
            placer.place_above(
                name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
            )
            cap_group.append(cap_name)

            placer.fill(names=cap_group, prim=m3, net=cap_net)

            # Clean up
            cap_group = None

            try:
                next(cap_names)
            except StopIteration:
                pass
            else:
                raise RuntimeError("Internal error")

        if bits > 4:
            cap_net = nets[f"dac_cap_bit[{bits - 5}]"]
            cap_names = (f"daccap[{bits - 5}][{n}]" for n in range(2**4))

            # Column of 3 on left
            cap_group = []

            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=left_cap, prim=m3)
            placer.place_above(
                name=bottom_cap, ref_names=cap_name, ignore_masks=m4.mask,
            )
            bottom_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)

            for _ in range(2):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                placer.place_above(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                prev_cap = cap_name
                cap_group.append(cap_name)
            # via2 on top of the column
            via_name = f"via2_{cap_name}"
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_height=cap_name,
                bottom_enclosure="tall", top_enclosure="tall",
            )
            placer.align_right(
                name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
            )
            placer.center_y(name=via_name, ref_name=cap_name, prim=m3, net=cap_net)
            prev_via = via_name
            prev_left_via = via_name
            cap_bit_via2s.insert(0, via_name)

            # Column of 5 on left
            cap_name = next(cap_names)
            placer.place_to_the_right(
                name=left_cap, ref_names=cap_name, ignore_masks=m4.mask,
            )
            placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
            left_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)

            for i in range(4):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                placer.place_above(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                prev_cap = cap_name
                cap_group.append(cap_name)

                if i == 1:
                    # Connect 3X3 bottom plates
                    placer.fill(names=cap_group, prim=m3, net=cap_net)
                    # Keep left ones in group
                    cap_group = [cap_group[-1]]

            placer.fill(names=cap_group, prim=m3, net=cap_net)

            # Column of 3 on right
            cap_group = []

            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=right_cap, prim=m3)
            placer.place_above(
                name=cap_name, ref_names=top_cap, ignore_masks=m4.mask,
            )
            top_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)
            # via2 on top of the column
            via_name = f"via2_{cap_name}"
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_width=cap_name,
                bottom_enclosure="tall", top_enclosure="tall",
            )
            placer.center_x(
                name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
            )
            placer.align_bottom(
                name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
            )
            prev_top_via = via_name
            prev_right_via = via_name

            placer.connect(
                name1=prev_via, name2=via_name, prim=m2, net=cap_net,
            )

            for _ in range(2):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                placer.place_below(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                prev_cap = cap_name
                cap_group.append(cap_name)

            # Column of 5 on right
            cap_name=next(cap_names)
            placer.place_to_the_right(
                name=cap_name, ref_names=right_cap, ignore_masks=m4.mask,
            )
            placer.center_y(name=cap_name, ref_name=top_cap, prim=m3)
            right_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)

            for i in range(4):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                placer.place_below(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                prev_cap = cap_name
                cap_group.append(cap_name)

                if i == 1:
                    # Connect 3X3 bottom plates
                    placer.fill(names=cap_group, prim=m3, net=cap_net)
                    # Keep left ones in group
                    cap_group = [cap_group[-1]]

            placer.fill(names=cap_group, prim=m3, net=cap_net)

            # Clean up
            cap_group = None

            try:
                next(cap_names)
            except StopIteration:
                pass
            else:
                raise RuntimeError("Internal error")

        if bits > 5:
            cap_net = nets[f"dac_cap_bit[{bits - 6}]"]
            cap_names = (f"daccap[{bits - 6}][{n}]" for n in range(2**5))

            # Column of 6 on the left
            cap_group = []

            cap_name = next(cap_names)
            placer.place_to_the_right(
                name=left_cap, ref_names=cap_name, ignore_masks=m4.mask,
            )
            placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
            left_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)
            # via2 on bottom of column
            via_name = f"via2_{cap_name}"
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_height=cap_name,
                bottom_enclosure="tall", top_enclosure="tall",
            )
            placer.align_right(
                name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
            )
            placer.center_y(
                name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
            )
            prev_via = via_name
            prev_left_via = via_name
            cap_bit_via2s.insert(0, via_name)

            for _ in range(5):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                placer.place_above(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                prev_cap = cap_name
                cap_group.append(cap_name)

            # Row of 4 top left
            cap_group2 = [cap_group[-1]]
            for _ in range(4):
                cap_name = next(cap_names)
                placer.place_to_the_right(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
                prev_cap = cap_name
                cap_group2.append(cap_name)

            placer.fill(names=cap_group2, prim=m3, net=cap_net)
            cap_group2 = None

            # Column of 6 on the left
            cap_name = next(cap_names)
            placer.place_to_the_right(
                name=left_cap, ref_names=cap_name, ignore_masks=m4.mask,
            )
            placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
            left_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)

            for _ in range(5):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                placer.place_above(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                prev_cap = cap_name
                cap_group.append(cap_name)

            placer.fill(names=cap_group, prim=m3, net=cap_net)

            # Column of 6 on the right
            cap_group = []

            cap_name = next(cap_names)
            placer.place_to_the_right(
                name=cap_name, ref_names=right_cap, ignore_masks=m4.mask,
            )
            placer.center_y(name=cap_name, ref_name=top_cap, prim=m3)
            right_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)
            # via2 on top of the column
            via_name = f"via2_{cap_name}"
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_width=cap_name,
                bottom_enclosure="tall", top_enclosure="tall",
            )
            placer.center_x(
                name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
            )
            placer.place_above(name=via_name, ref_names=prev_top_via)
            prev_top_via = via_name
            prev_right_via = via_name

            placer.connect(
                name1=prev_via, name2=via_name, prim=m2, net=cap_net,
            )

            for _ in range(5):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                placer.place_below(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                prev_cap = cap_name
                cap_group.append(cap_name)

            # Row of 4 bottom right
            cap_group2 = [cap_group[-1]]
            for _ in range(4):
                cap_name = next(cap_names)
                placer.place_to_the_left(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
                prev_cap = cap_name
                cap_group2.append(cap_name)

            placer.fill(names=cap_group2, prim=m3, net=cap_net)
            cap_group2 = None

            # Column of 6 on the right
            cap_name = next(cap_names)
            placer.place_to_the_right(
                name=cap_name, ref_names=right_cap, ignore_masks=m4.mask,
            )
            placer.center_y(name=cap_name, ref_name=top_cap, prim=m3)
            right_cap = cap_name
            prev_cap = cap_name
            cap_group.append(cap_name)

            for _ in range(5):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                placer.place_below(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                prev_cap = cap_name
                cap_group.append(cap_name)

            placer.fill(names=cap_group, prim=m3, net=cap_net)

            # Clean-up
            cap_group = None

            try:
                next(cap_names)
            except StopIteration:
                pass
            else:
                raise RuntimeError("Internal error")

        if bits > 6:
            cap_net = nets[f"dac_cap_bit[{bits - 7}]"]
            cap_names = (f"daccap[{bits - 7}][{n}]" for n in range(2**6))

            cap_group1 = [] # group for bottom rows
            cap_group2 = [] # group for top rows

            # one row of 4 bottom left
            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=left_cap, prim=m3)
            placer.place_above(
                name=bottom_cap, ref_names=cap_name, ignore_masks=m4.mask,
            )
            bottom_cap = cap_name
            prev_cap = cap_name
            cap_group1.append(cap_name)
            # Add via vertically aligned with cap but left of prev_left_cap
            via_name = f"via2_{cap_name}"
            placer.wire(
                wire_name=via_name, net=cap_net, wire=via2,
                ref_top_height=cap_name,
                bottom_enclosure="tall", top_enclosure="tall",
            )
            placer.place_to_the_left(name=via_name, ref_names=prev_left_via)
            placer.center_y(
                name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
            )
            prev_left_via = via_name
            cap_bit_via2s.insert(0, via_name)

            for _ in range(3):
                cap_name = next(cap_names)
                placer.place_to_the_right(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
                prev_cap = cap_name
                cap_group1.append(cap_name)

            # one row of 4 top left
            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=left_cap, prim=m3)
            placer.place_above(
                name=cap_name, ref_names=top_cap, ignore_masks=m4.mask,
            )
            top_cap = cap_name
            prev_cap = cap_name
            cap_group2.append(cap_name)

            for _ in range(3):
                cap_name = next(cap_names)
                placer.place_to_the_right(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
                prev_cap = cap_name
                cap_group2.append(cap_name)

            # 3 columns of 8 on left
            cap_group = []

            for _ in range(3):
                cap_name = next(cap_names)
                placer.place_to_the_right(
                    name=left_cap, ref_names=cap_name, ignore_masks=m4.mask,
                )
                placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
                left_cap = cap_name
                prev_cap = cap_name
                cap_group.append(cap_name)
                # Add bottom also to bottom row
                cap_group1.append(cap_name)

                for _ in range(7):
                    cap_name = next(cap_names)
                    placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                    placer.place_above(
                        name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                    )
                    prev_cap = cap_name
                    cap_group.append(cap_name)
                # Add top also to top row
                cap_group2.append(cap_name)

            placer.fill(names=cap_group, prim=m3, net=cap_net)
            cap_group = None

            # one row of 4 bottom right
            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=right_cap, prim=m3)
            placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
            prev_cap = cap_name
            cap_group1.append(cap_name)

            for _ in range(3):
                cap_name = next(cap_names)
                placer.place_to_the_left(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
                prev_cap = cap_name
                cap_group1.append(cap_name)

            # one row of 4 top right
            cap_name = next(cap_names)
            placer.center_x(name=cap_name, ref_name=right_cap, prim=m3)
            placer.center_y(name=cap_name, ref_name=top_cap, prim=m3)
            prev_cap = cap_name
            cap_group2.append(cap_name)

            for _ in range(3):
                cap_name = next(cap_names)
                placer.place_to_the_left(
                    name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                )
                placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
                prev_cap = cap_name
                cap_group2.append(cap_name)

            # 3 columns of 8 on right
            cap_group = []

            for _ in range(3):
                cap_name = next(cap_names)
                placer.place_to_the_right(
                    name=cap_name, ref_names=right_cap, ignore_masks=m4.mask,
                )
                placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
                right_cap = cap_name
                prev_cap = cap_name
                cap_group.append(cap_name)
                # Add bottom also to bottom row
                cap_group1.append(cap_name)

                for _ in range(7):
                    cap_name = next(cap_names)
                    placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                    placer.place_above(
                        name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                    )
                    prev_cap = cap_name
                    cap_group.append(cap_name)
                # Add top also to top row
                cap_group2.append(cap_name)

            placer.fill(names=cap_group1, prim=m3, net=cap_net)
            cap_group1 = None
            placer.fill(names=cap_group2, prim=m3, net=cap_net)
            cap_group2 = None
            placer.fill(names=cap_group, prim=m3, net=cap_net)
            cap_group = None

            # Clean-up
            try:
                next(cap_names)
            except StopIteration:
                pass
            else:
                raise RuntimeError("Internal error")

        if bits > 7:
            cap_net = nets[f"dac_cap_bit[{bits - 8}]"]
            cap_names = (f"daccap[{bits - 8}][{n}]" for n in range(2**7))

            cap_group1 = [] # group for bottom rows
            cap_group2 = [] # group for top rows

            # two rows of 4 bottom left
            for i in range(2):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=left_cap, prim=m3)
                placer.place_above(
                    name=bottom_cap, ref_names=cap_name, ignore_masks=m4.mask,
                )
                bottom_cap = cap_name
                prev_cap = cap_name
                cap_group1.append(cap_name)

                for _ in range(3):
                    cap_name = next(cap_names)
                    placer.place_to_the_right(
                        name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                    )
                    placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
                    prev_cap = cap_name
                    cap_group1.append(cap_name)
                
                if i == 0:
                    # Add via vertically aligned with cap but left of prev_left_cap
                    via_name = f"via2_{cap_name}"
                    placer.wire(
                        wire_name=via_name, net=cap_net, wire=via2,
                        ref_top_height=cap_name,
                        bottom_enclosure="tall", top_enclosure="tall",
                    )
                    placer.place_to_the_left(name=via_name, ref_names=prev_left_via)
                    placer.center_y(
                        name=via_name, ref_name=cap_name, prim=m3, net=cap_net,
                    )
                    prev_left_via = via_name
                    cap_bit_via2s.insert(0, via_name)

            # two row2 of 4 top left
            for _ in range(2):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=left_cap, prim=m3)
                placer.place_above(
                    name=cap_name, ref_names=top_cap, ignore_masks=m4.mask,
                )
                top_cap = cap_name
                prev_cap = cap_name
                cap_group2.append(cap_name)

                for _ in range(3):
                    cap_name = next(cap_names)
                    placer.place_to_the_right(
                        name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                    )
                    placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
                    prev_cap = cap_name
                    cap_group2.append(cap_name)

            # 4 columns of 12 on left
            cap_group = [] # Group for left columns

            for _ in range(4):
                cap_name = next(cap_names)
                placer.place_to_the_right(
                    name=left_cap, ref_names=cap_name, ignore_masks=m4.mask,
                )
                placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
                left_cap = cap_name
                prev_cap = cap_name
                cap_group.append(cap_name)
                # Add bottom also to bottom row
                cap_group1.append(cap_name)

                for _ in range(11):
                    cap_name = next(cap_names)
                    placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                    placer.place_above(
                        name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                    )
                    prev_cap = cap_name
                    cap_group.append(cap_name)
                # Add top also to top row
                cap_group2.append(cap_name)

            placer.fill(names=cap_group, prim=m3, net=cap_net)
            cap_group = None

            # two rows of 4 bottom right
            for i in range(2):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=right_cap, prim=m3)
                if i == 0:
                    placer.place_above(
                        name=cap_name, ref_names=bottom_cap, ignore_masks=m4.mask,
                    )
                else:
                    placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
                prev_cap = cap_name
                cap_group1.append(cap_name)

                for _ in range(3):
                    cap_name = next(cap_names)
                    placer.place_to_the_left(
                        name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                    )
                    placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
                    prev_cap = cap_name
                    cap_group1.append(cap_name)

            # two rows of 4 top right
            for i in range(2):
                cap_name = next(cap_names)
                placer.center_x(name=cap_name, ref_name=right_cap, prim=m3)
                if i == 0:
                    placer.place_below(
                        name=cap_name, ref_names=top_cap, ignore_masks=m4.mask,
                    )
                else:
                    placer.center_y(name=cap_name, ref_name=top_cap, prim=m3)
                prev_cap = cap_name
                cap_group2.append(cap_name)

                for _ in range(3):
                    cap_name = next(cap_names)
                    placer.place_to_the_left(
                        name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                    )
                    placer.center_y(name=cap_name, ref_name=prev_cap, prim=m3)
                    prev_cap = cap_name
                    cap_group2.append(cap_name)

            # 4 columns of 12 on right
            cap_group = [] # group for right columns

            for _ in range(4):
                cap_name = next(cap_names)
                placer.place_to_the_right(
                    name=cap_name, ref_names=right_cap, ignore_masks=m4.mask,
                )
                placer.center_y(name=cap_name, ref_name=bottom_cap, prim=m3)
                right_cap = cap_name
                prev_cap = cap_name
                cap_group.append(cap_name)
                # Add bottom also to bottom row
                cap_group1.append(cap_name)

                for _ in range(11):
                    cap_name = next(cap_names)
                    placer.center_x(name=cap_name, ref_name=prev_cap, prim=m3)
                    placer.place_above(
                        name=cap_name, ref_names=prev_cap, ignore_masks=m4.mask,
                    )
                    prev_cap = cap_name
                    cap_group.append(cap_name)
                # Add top also to top row
                cap_group2.append(cap_name)

            placer.fill(names=cap_group1, prim=m3, net=cap_net)
            cap_group1 = None
            placer.fill(names=cap_group2, prim=m3, net=cap_net)
            cap_group2 = None
            placer.fill(names=cap_group, prim=m3, net=cap_net)
            cap_group = None

            # Clean-up
            try:
                next(cap_names)
            except StopIteration:
                pass
            else:
                raise RuntimeError("Internal error")

        assert len(cap_bit_via2s) == bits, "Internal error"

        placer.place_to_the_right(
            name=left_cap, ref_names="clk_inv2", boundary_only=True,
        )
        placer.place_above(
            name=bottom_cap, ref_names="amp_inv1", extra_space=1.0,
        )

        # dac_pmosholdpass
        hold_ptrans_name = "dac_pmosholdpass"
        hold_passtrans_w = self.pmos_holdpasstrans_args["w"]

        gate_net = nets.start_latch_n
        hold_ptranspad_name = f"{hold_ptrans_name}__pad"
        hold_ptransmcongate_name = f"mcon__{hold_ptrans_name}__gate"

        sd1_net = nets.vin
        hold_ptranssd1_name = f"{hold_ptrans_name}__sd1" # net: vin

        sd2_net = nets.dac_caps_common
        hold_ptranssd2_name = f"{hold_ptrans_name}__sd2" # net: dac_caps_common
        sd2_via3_name = f"via3__{hold_ptranssd2_name}"
        sd2_via2_name = f"via2__{hold_ptranssd2_name}"
        sd2_via_name = f"via__{hold_ptranssd2_name}"
        sd2_mcon_name = f"mcon__{hold_ptranssd2_name}"

        hold_tap_name = f"tap_vdd_{hold_ptrans_name}"

        placer.wire(
            wire_name=sd2_via3_name, net=sd2_net, wire=via3,
            bottom_height=hold_passtrans_w, top_height=hold_passtrans_w,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        # Do alignment of the via to the caps
        placer.place_to_the_left(name=sd2_via3_name, ref_names=left_cap)
        placer.align_top(name=sd2_via3_name, ref_name=top_cap, prim=m4)

        placer.fill(names=(sd2_via3_name, top_cap), prim=m4, net=sd2_net)

        placer.wire(
            wire_name=sd2_via2_name, net=sd2_net, wire=via2,
            bottom_height=hold_passtrans_w, top_height=hold_passtrans_w,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.align_left(
            name=sd2_via2_name, ref_name=sd2_via3_name, prim=m3, net=sd2_net,
        )
        placer.center_y(name=sd2_via2_name, ref_name=sd2_via3_name, prim=m3)

        placer.wire(
            wire_name=sd2_via_name, net=sd2_net, wire=via,
            bottom_height=hold_passtrans_w, top_height=hold_passtrans_w,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.align_left(
            name=sd2_via_name, ref_name=sd2_via2_name, prim=m2, net=sd2_net,
        )
        placer.center_y(name=sd2_via_name, ref_name=sd2_via2_name, prim=m2)

        placer.wire(
            wire_name=sd2_mcon_name, net=sd2_net, wire=mcon,
            bottom_height=hold_passtrans_w, top_height=hold_passtrans_w,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.align_left(
            name=sd2_mcon_name, ref_name=sd2_via_name, prim=m1, net=sd2_net,
        )
        placer.center_y(name=sd2_mcon_name, ref_name=sd2_via_name, prim=m1)

        placer.wire(
            wire_name=hold_ptranssd2_name, net=sd2_net, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_implant=psdm, bottom_well=nwell,
            bottom_height=hold_passtrans_w, top_height=hold_passtrans_w,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.align_left(
            name=hold_ptranssd2_name, ref_name=sd2_mcon_name, prim=li, net=sd2_net,
        )
        placer.center_y(name=hold_ptranssd2_name, ref_name=sd2_mcon_name, prim=li)

        placer.place_to_the_left(
            name=hold_ptrans_name, ref_names=hold_ptranssd2_name,
            ignore_masks=(nwell.mask, difftap.mask),
        )
        placer.center_y(
            name=hold_ptrans_name, ref_name=hold_ptranssd2_name, prim=difftap,
        )

        placer.wire(
            wire_name=hold_ptranssd1_name, net=sd1_net, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_implant=psdm, bottom_well=nwell,
            bottom_height=hold_passtrans_w, top_height=hold_passtrans_w,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.place_to_the_left(
            name=hold_ptranssd1_name, ref_names=hold_ptrans_name,
            ignore_masks=(nwell.mask, difftap.mask),
        )
        placer.center_y(
            name=hold_ptranssd1_name, ref_name=hold_ptranssd2_name, prim=difftap,
        )

        placer.wire(
            wire_name=hold_tap_name, net=nets.vdd, well_net=nets.vdd, wire=licon,
            bottom=difftap, bottom_implant=psdm, bottom_well=nwell,
            bottom_height=hold_passtrans_w, top_height=hold_passtrans_w,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.place_to_the_left(
            name=hold_tap_name, ref_names=hold_ptranssd1_name,
            ignore_masks=nwell.mask,
        )
        placer.center_y(
            name=hold_tap_name, ref_name=hold_ptranssd2_name, prim=difftap,
        )

        placer.wire(
            wire_name=hold_ptranspad_name, net=gate_net, wire=licon,
            bottom=poly, bottom_enclosure="wide", top_enclosure="wide",
        )
        # Hack psdm
        info = placer.info_lookup[hold_ptranspad_name]
        bb = info.bb(mask=poly.mask)
        assert bb is not None
        info.layout.add_shape(layer=psdm, net=None, shape=bb)
        placer.center_x(
            name=hold_ptranspad_name, ref_name=hold_ptrans_name,
            prim=poly, net=gate_net,
        )
        placer.place_below(
            name=hold_ptranspad_name, ref_names=hold_ptrans_name,
            ignore_masks=poly.mask,
        )

        placer.connect(
            name1=hold_ptranspad_name, name2=hold_ptrans_name,
            prim=poly, net=gate_net,
        )

        placer.wire(
            wire_name=hold_ptransmcongate_name, net=gate_net, wire=mcon,
            columns=2, bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.align_right(
            name=hold_ptransmcongate_name, ref_name=hold_ptranspad_name,
            prim=li, net=gate_net,
        )
        placer.align_top(
            name=hold_ptransmcongate_name, ref_name=hold_ptranspad_name,
            prim=li, net=gate_net,
        )

        placer.fill(
            names=(hold_tap_name, hold_ptranssd2_name, hold_ptranspad_name),
            prim=psdm,
        )

        # Connect with wires
        # ==================

        # clk
        net = nets.clk
        placer.wire(
            wire_name="mcon_clk_clk_inv", net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.wire(
            wire_name="mcon_clk_seq_capt", net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_left(
            name="mcon_clk_clk_inv", ref_name="clk_inv", prim=li, net=net,
        )
        placer.align_bottom(
            name="mcon_clk_clk_inv", ref_name="clk_inv", prim=li, net=net,
        )
        placer.align_right(
            name="mcon_clk_seq_capt", ref_name="seq_capt", prim=li, net=net,
        )
        placer.align_bottom(
            name="mcon_clk_seq_capt", ref_name="seq_capt", prim=li, net=net,
        )
        placer.connect(
            name1="mcon_clk_clk_inv", name2="mcon_clk_seq_capt", prim=m1, net=net,
        )

        # clk_n
        net = nets.clk_n
        placer.wire(
            wire_name="mcon_clkn_clk_inv", net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.wire(
            wire_name="mcon_clkn_clk_inv2", net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_left(
            name="mcon_clkn_clk_inv", ref_name="clk_inv", prim=li, net=net,
        )
        placer.align_bottom(
            name="mcon_clkn_clk_inv", ref_name="clk_inv", prim=li, net=net,
        )
        placer.align_left(
            name="mcon_clkn_clk_inv2", ref_name="clk_inv2", prim=li, net=net,
        )
        placer.align_bottom(
            name="mcon_clkn_clk_inv2", ref_name="clk_inv2", prim=li, net=net,
        )
        placer.connect(
            name1="mcon_clkn_clk_inv", name2="mcon_clkn_clk_inv2", prim=m1, net=net,
        )

        # clk2
        net = nets.clk2
        placer.wire(
            wire_name="mcon_clk2_clk_inv2", net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_left(
            name="mcon_clk2_clk_inv2", ref_name="clk_inv2", prim=li, net=net,
        )
        placer.align_bottom(
            name="mcon_clk2_clk_inv2", ref_name="clk_inv2", prim=li, net=net,
        )
        wire_name = None
        for n in range(qs):
            ref_name = f"seq_qff[{n}]"
            wire_name = f"mcon_clk2_{ref_name}"
            placer.wire(
                wire_name=wire_name, net=net, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )

            placer.align_right(
                name=wire_name, ref_name=ref_name, prim=li, net=net,
            )
            placer.align_bottom(
                name=wire_name, ref_name=ref_name, prim=li, net=net,
            )
        assert wire_name is not None
        placer.connect(
            name1="mcon_clk2_clk_inv2", name2=wire_name, prim=m1, net=net,
        )

        # start_latch
        net = nets.start_latch

        cell1_name = "seq_capt"
        cell2_name = "start_latch_inv"
        cell3_name = "seq_qff[0]"

        mcon1_name = f"mcon__{net.name}__{cell1_name}"
        mcon2_name = f"mcon__{net.name}__{cell2_name}"
        mcon3_name = f"mcon__{net.name}__{cell3_name}"

        placer.wire(
            wire_name=mcon1_name, net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=mcon1_name, ref_name=cell1_name, ref_pin=True, prim=li, net=net,
        )
        placer.center_y(
            name=mcon1_name, ref_name=cell1_name, ref_pin=True, prim=li, net=net,
        )

        placer.wire(
            wire_name=mcon2_name, net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=mcon2_name, ref_name=cell2_name, ref_pin=True, prim=li, net=net,
        )
        placer.center_y(
            name=mcon2_name, ref_name=mcon1_name, prim=li, net=net,
        )

        placer.wire(
            wire_name=mcon3_name, net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=mcon3_name, ref_name=cell3_name, ref_pin=True, prim=li, net=net,
        )
        placer.center_y(
            name=mcon3_name, ref_name=mcon1_name, prim=li, net=net,
        )

        placer.connect(
            name1=mcon2_name, name2=mcon3_name, prim=m1, net=net,
        )

        # start_latch_n
        net = nets.start_latch_n

        cell_name = "start_latch_inv"
        mcon_name = f"mcon__{net.name}__{cell_name}"

        placer.wire(
            wire_name=mcon_name, net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.center_x(
            name=mcon_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
        )
        placer.align_top(
            name=mcon_name, ref_name=cell_name, ref_pin=True, prim=li, net=net,
        )

        placer.connect(
            name1=mcon_name, name2=hold_ptransmcongate_name, prim=m1, net=net,
        )

        # q[n]
        for bit in range(bits):
            net = nets[f"q[{bit}]"]

            cell1_name = f"seq_qff[{bit}]"
            mcon1_name = f"mcon__{net.name}__{cell1_name}"

            placer.wire(
                wire_name=mcon1_name, net=net, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=mcon1_name, ref_name=cell1_name, ref_pin=True,
                prim=li, net=net,
            )
            placer.center_y(
                name=mcon1_name, ref_name=cell1_name, ref_pin=True,
                prim=li, net=net,
            )

            cell2_name = f"seq_qff[{bit + 1}]"
            mcon2_name = f"mcon__{net.name}__{cell2_name}"

            placer.wire(
                wire_name=mcon2_name, net=net, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=mcon2_name, ref_name=cell2_name, ref_pin=True,
                prim=li, net=net,
            )
            placer.center_y(
                name=mcon2_name, ref_name=mcon1_name, prim=li, net=net,
            )

            placer.connect(
                name1=mcon1_name, name2=mcon2_name, prim=m1, net=net,
            )

        # lg_rightvdden
        net = nets.lg_rightvdden
        wire1_name = f"mcon_{net.name}_psd"
        lg_rightvddend_wire_name = wire2_name = f"mcon_{net.name}_nsd"
        corner_name = f"m1_{net.name}_corner"

        placer.wire(
            wire_name=wire1_name, net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=wire1_name, ref_name=lg_ptrans12sd_name, prim=li, net=net,
        )
        placer.align_top(
            name=wire1_name, ref_name=lg_ptrans12sd_name, prim=li, net=net,
        )

        placer.wire(
            wire_name=wire2_name, net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=wire2_name, ref_name=lg_ntrans1sd2_name, prim=li, net=net,
        )
        placer.align_bottom(
            name=wire2_name, ref_name=lg_ntrans1sd2_name, prim=li, net=net,
        )

        placer.wire(
            wire_name=corner_name, net=net, wire=m1,
            ref_width=wire1_name, ref_height=wire2_name,
        )
        placer.center_x(
            name=corner_name, ref_name=wire1_name, prim=m1, net=net,
        )
        placer.center_y(
            name=corner_name, ref_name=wire2_name, prim=m1, net=net,
        )
        placer.connect(
            name1=corner_name, name2=wire1_name, prim=m1, net=net,
        )
        placer.connect(
            name1=corner_name, name2=wire2_name, prim=m1, net=net,
        )

        # lg_leftvdden
        net = nets.lg_leftvdden
        wire1_name = f"mcon_{net.name}_psd"
        lg_leftvdden_wire_name = wire2_name = f"mcon_{net.name}_nsd"
        corner_name = f"m1_{net.name}_corner"

        placer.wire(
            wire_name=wire1_name, net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=wire1_name, ref_name=lg_ptrans34sd_name, prim=li, net=net,
        )
        placer.align_top(
            name=wire1_name, ref_name=lg_ptrans34sd_name, prim=li, net=net,
        )

        placer.wire(
            wire_name=wire2_name, net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=wire2_name, ref_name=lg_ntrans6sd1_name, prim=li, net=net,
        )
        placer.align_bottom(
            name=wire2_name, ref_name=lg_ntrans6sd1_name, prim=li, net=net,
        )

        placer.wire(
            wire_name=corner_name, net=net, wire=m1,
            ref_width=wire1_name, ref_height=wire2_name,
        )
        placer.center_x(
            name=corner_name, ref_name=wire1_name, prim=m1, net=net,
        )
        placer.center_y(
            name=corner_name, ref_name=wire2_name, prim=m1, net=net,
        )
        placer.connect(
            name1=corner_name, name2=wire1_name, prim=m1, net=net,
        )
        placer.connect(
            name1=corner_name, name2=wire2_name, prim=m1, net=net,
        )

        # cmp_set & cmp_rst
        net1 = nets.cmp_set
        net2 = nets.cmp_rst

        wire11_name = f"mcon_{net1.name}_psd"
        wire12_name = f"mcon_{net1.name}_nsd"
        wire13_name = f"mcon_{net1.name}_pad"
        wire21_name = f"mcon_{net2.name}_psd"
        wire22_name = f"mcon_{net2.name}_nsd"
        wire23_name = f"mcon_{net2.name}_pad"

        placer.wire(
            wire_name=wire11_name, net=net1, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )

        placer.center_x(
            name=wire11_name, ref_name=lg_ptrans2sd1_name, prim=li, net=net1,
        )
        placer.align_top(
            name=wire11_name, ref_name=lg_ptrans2sd1_name, prim=li, net=net1,
        )

        placer.wire(
            wire_name=wire12_name, net=net1, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=wire12_name, ref_name=lg_ntrans23sd_name, prim=li, net=net1,
        )
        placer.align_bottom(
            name=wire12_name, ref_name=lg_ntrans23sd_name, prim=li, net=net1,
        )

        placer.wire(
            wire_name=wire21_name, net=net2, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=wire21_name, ref_name=lg_ptrans3sd2_name, prim=li, net=net2,
        )
        placer.align_top(
            name=wire21_name, ref_name=lg_ptrans3sd2_name, prim=li, net=net2,
        )

        placer.wire(
            wire_name=wire22_name, net=net2, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=wire22_name, ref_name=lg_ntrans45sd_name, prim=li, net=net2,
        )
        placer.align_bottom(
            name=wire22_name, ref_name=lg_ntrans45sd_name, prim=li, net=net2,
        )

        placer.wire(
            wire_name=wire13_name, net=net1, wire=mcon, rows=2,
            bottom_enclosure="wide", top_enclosure="tall",
        )
        placer.place_to_the_left(name=wire13_name, ref_names=(
            wire21_name, wire22_name, lg_leftvdden_wire_name,
        ))
        placer.align_top(
            name=wire13_name, ref_name=lg_pad5_name, prim=li, net=net1,
        )

        placer.wire(
            wire_name=wire23_name, net=net2, wire=mcon, rows=2,
            bottom_enclosure="wide", top_enclosure="tall",
        )
        placer.place_to_the_right(name=wire23_name, ref_names=(
            wire11_name, wire12_name, lg_rightvddend_wire_name,
        ))
        placer.align_bottom(
            name=wire23_name, ref_name=lg_pad2_name, prim=li, net=net2,
        )

        placer.connect(
            name1=lg_pad5_name, name2=wire13_name, prim=li, net=net1,
        )
        placer.connect(
            name1=lg_pad2_name, name2=wire23_name, prim=li, net=net2,
        )

        placer.connect(
            name1=wire11_name, name2=wire12_name, prim=m1, net=net1,
        )
        placer.connect(
            name1=wire21_name, name2=wire22_name, prim=m1, net=net2,
        )

        wire14_name = None
        wire24_name = None
        for n in range(bits):
            cell1_name = f"seq_nand2_nsetbit[{n}]"
            cell2_name = f"seq_nand2_nrstbit[{n}]"
            wire14_name = f"mcon__{net1.name}__{cell1_name}"
            wire24_name = f"mcon__{net2.name}__{cell2_name}"

            placer.wire(
                wire_name=wire14_name, net=net1, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=wire14_name, ref_name=cell1_name, prim=li, net=net1,
            )
            placer.place_below(
                name=wire14_name, ref_names=(wire11_name, wire21_name),
            )

            placer.wire(
                wire_name=wire24_name, net=net2, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=wire24_name, ref_name=cell2_name, prim=li, net=net2,
            )
            placer.place_above(
                name=wire24_name, ref_names=(wire12_name, wire22_name),
            )
        assert wire14_name is not None
        assert wire24_name is not None

        wire15_name = f"m1_{net1.name}_corner"
        placer.wire(
            wire_name=wire15_name, net=net1, wire=m1,
            ref_width=wire13_name, ref_height=wire14_name,
        )
        placer.center_x(name=wire15_name, ref_name=wire13_name, prim=m1)
        placer.center_y(name=wire15_name, ref_name=wire14_name, prim=m1)

        placer.connect(
            name1=wire13_name, name2=wire15_name, prim=m1, net=net1,
        )
        placer.connect(
            name1=wire14_name, name2=wire15_name, prim=m1, net=net1,
        )

        wire16_name = f"m1_{net1.name}_corner2"
        placer.wire(
            wire_name=wire16_name, net=net1, wire=m1,
            ref_width=wire11_name, ref_height=wire14_name,
        )
        placer.center_x(name=wire16_name, ref_name=wire11_name, prim=m1)
        placer.center_y(name=wire16_name, ref_name=wire14_name, prim=m1)

        placer.connect(
            name1=wire11_name, name2=wire16_name, prim=m1, net=net1,
        )

        wire25_name = f"m1_{net2.name}_corner"
        placer.wire(
            wire_name=wire25_name, net=net2, wire=m1,
            ref_width=wire23_name, ref_height=wire24_name,
        )
        placer.center_x(name=wire25_name, ref_name=wire23_name, prim=m1)
        placer.center_y(name=wire25_name, ref_name=wire24_name, prim=m1)

        placer.connect(
            name1=wire23_name, name2=wire25_name, prim=m1, net=net2,
        )

        wire26_name = f"m1_{net2.name}_corner2"
        placer.wire(
            wire_name=wire26_name, net=net2, wire=m1,
            ref_width=wire22_name, ref_height=wire24_name,
        )
        placer.center_x(name=wire26_name, ref_name=wire22_name, prim=m1)
        placer.center_y(name=wire26_name, ref_name=wire24_name, prim=m1)

        placer.connect(
            name1=wire22_name, name2=wire26_name, prim=m1, net=net2,
        )
        placer.connect(
            name1=wire24_name, name2=wire26_name, prim=m1, net=net2
        )

        # amp_buf[np]
        # Reuse wire names above
        cell1_name = "amp_inv1"
        cell2_name = "amp_inv2"
        placer.place_to_the_left(
            name=cell1_name,
            ref_names=(lg_ptrans4sd1_name, lg_ntrans6sd1_name, wire23_name),
            ignore_masks=nwell.mask
        )
        placer.place_to_the_left(
            name=cell2_name, ref_names=cell1_name, boundary_only=True,
        )

        for cell_name in (cell1_name, cell2_name):
            placer.place_above(
                name=cell_name, ref_names=left_cell, boundary_only=True,
            )

        net = nets.amp_bufp
        placer.connect(
            name1=lg_pad6_name, name2=cell1_name, prim=li, net=net,
        )

        net = nets.amp_bufn
        mcon1_name = f"mcon_{net.name}_{lg_pad2_name}"
        via1_name = f"via_{net.name}_{lg_pad2_name}"
        ampbufn_mcon_name = mcon2_name = f"mcon_{net.name}_{cell2_name}"
        ampbufn_via_name = via2_name = f"via_{net.name}_{cell2_name}"

        placer.wire(
            wire_name=mcon1_name, net=net, wire=mcon, columns=2,
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.place_to_the_right(
            name=mcon1_name, ref_names=f"mcon_lg_rightvdden_psd",
        )
        placer.center_y(
            name=mcon1_name, ref_name=lg_pad1_name, prim=li, net=net,
        )
        placer.wire(
            wire_name=via1_name, net=net, wire=via, columns=2,
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.align_left(
            name=via1_name, ref_name=mcon1_name, prim=m1, net=net,
        )
        placer.align_top(
            name=via1_name, ref_name=mcon1_name, prim=m1, net=net,
        )

        placer.wire(
            wire_name=mcon2_name, net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.align_left(
            name=mcon2_name, ref_name=cell2_name, ref_pin=True,
            prim=li, net=net,
        )
        placer.center_y(
            name=mcon2_name, ref_name=mcon1_name, prim=m1, net=net,
        )
        placer.wire(
            wire_name=via2_name, net=net, wire=via, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.align_left(
            name=via2_name, ref_name=mcon2_name, prim=m1, net=net,
        )
        placer.center_y(
            name=via2_name, ref_name=via1_name, prim=m2, net=net,
        )

        placer.connect(
            name1=via1_name, name2=via2_name, prim=m2, net=net,
        )

        # amp_out[np]
        net1 = nets.amp_outn
        net2 = nets.amp_outp
        net3 = nets.amp_vdden
        net4 = nets.dac_caps_common
        net5 = nets.clk_n

        amp_ptrans1_name = "amp_cmp1"
        amp_ptrans2_name = "amp_cmp2"
        amp_ptrans3_name = "amp_en"
        amp_ntrans1_name = "amp_unl1"
        amp_ntrans2_name = "amp_unl2"
        amp_ntrans3_name = "amp_unlen"

        amp_ptrans1sd2_name = f"licon__{net1.name}__psd"
        amp_ptrans12sd_name = f"licon__{net3.name}__psd"
        amp_ptrans2sd1_name = f"licon__{net2.name}__psd"
        amp_ptrans3sd2_name = f"licon__{net3.name}__psd2"
        amp_ptrans3sd1_name = f"licon_vdd_psd"
        amp_ntrans1sd2_name = f"licon__{net1.name}__nsd"
        amp_ntrans12sd_name = f"licon_vss_nsd"
        amp_ntrans2sd1_name = f"licon__{net2.name}__nsd"
        amp_ntrans3sd2_name = f"licon__{net3.name}__nsd"
        amp_ntrans3sd1_name = f"licon_vss_nsd2"

        amp_ppad1_name = f"licon__{net4.name}__{amp_ptrans1_name}"
        amp_ppad2_name = f"licon__vss__{amp_ptrans2_name}"
        amp_pad3_name = f"licon__{net5.name}__pad"

        for wire_name, net in (
            (amp_ptrans1sd2_name, net1),
            (amp_ptrans12sd_name, net3),
            (amp_ptrans2sd1_name, net2),
        ):
            placer.wire(
                wire_name=wire_name, net=net, well_net=nets.vdd, wire=licon,
                bottom=difftap, bottom_implant=psdm, bottom_well=nwell,
                bottom_height=self.pmos_amppair_args["w"],
                bottom_enclosure="tall", top_enclosure="tall",
            )
        for wire_name, net in (
            (amp_ptrans3sd2_name, net3),
            (amp_ptrans3sd1_name, nets.vdd),
        ):
            placer.wire(
                wire_name=wire_name, net=net, well_net=nets.vdd, wire=licon,
                bottom=difftap, bottom_implant=psdm, bottom_well=nwell,
                bottom_height=self.pmos_nom_args["w"],
                bottom_enclosure="tall", top_enclosure="tall",
            )
        for wire_name, net in (
            (amp_ntrans1sd2_name, net1),
            (amp_ntrans12sd_name, nets.vss),
            (amp_ntrans2sd1_name, net2),
            (amp_ntrans3sd2_name, net3),
            (amp_ntrans3sd1_name, nets.vss),
        ):
            placer.wire(
                wire_name=wire_name, net=net, wire=licon,
                bottom=difftap, bottom_implant=nsdm,
                bottom_height=self.nmos_nom_args["w"],
                bottom_enclosure="tall", top_enclosure="tall",
            )

        placer.place_to_the_left(
            name=amp_ptrans1sd2_name, ref_names="amp_inv2",
            ignore_masks=nwell.mask,
        )
        prev_name = amp_ptrans1sd2_name
        for wire_name in (
            amp_ptrans1_name, amp_ptrans12sd_name,
            amp_ptrans2_name, amp_ptrans2sd1_name,
        ):
            placer.place_to_the_left(
                name=wire_name, ref_names=prev_name,
                ignore_masks=(nwell.mask, difftap.mask),
            )
            prev_name = wire_name
        placer.place_to_the_left(
            name=amp_ptrans3sd2_name, ref_names=prev_name,
            ignore_masks=nwell.mask,
        )
        prev_name = amp_ptrans3sd2_name
        for wire_name in (
            amp_ptrans3_name, amp_ptrans3sd1_name,
        ):
            placer.place_to_the_left(
                name=wire_name, ref_names=prev_name,
                ignore_masks=(nwell.mask, difftap.mask),
            )
            prev_name = wire_name

        for wire_name in (
            amp_ptrans1sd2_name, amp_ptrans1_name,
            amp_ptrans12sd_name, amp_ptrans2_name,
            amp_ptrans2sd1_name,
            amp_ptrans3sd2_name, amp_ptrans3_name,
            amp_ptrans3sd1_name,
        ):
            placer.align_top(
                name=wire_name, ref_name="amp_inv2", prim=nwell,
            )

        for wire_name, ref_name, net in (
            (amp_ppad1_name, amp_ptrans1_name, net4),
            (amp_ppad2_name, amp_ptrans2_name, nets.vss),
        ):
            placer.wire(
                wire_name=wire_name, net=net, wire=licon,
                bottom=poly, ref_bottom_width=ref_name,
            )
            placer.center_x(
                name=wire_name, ref_name=ref_name, prim=poly, net=net,
            )
            placer.place_above(
                name=wire_name, ref_names=ref_name,
                ignore_masks=poly.mask,
            )

        placer.wire(
            wire_name=amp_pad3_name, net=net5, wire=licon, bottom=poly,
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.align_left(
            name=amp_pad3_name, ref_name=amp_ptrans3_name, prim=poly, net=net5,
        )
        placer.place_above(
            name=amp_pad3_name, ref_names=(amp_ppad1_name, amp_ppad2_name),
        )

        placer.align_right(
            name=amp_ntrans3_name, ref_name=amp_ptrans3_name, prim=poly, net=net5,
        )
        placer.place_above(
            name=amp_ntrans3_name, ref_names=(amp_ptrans3_name, amp_pad3_name),
            ignore_masks=poly.mask,
        )

        placer.place_to_the_left(
            name=amp_ntrans3sd1_name, ref_names=amp_ntrans3_name,
            ignore_masks=difftap.mask,
        )
        placer.place_to_the_right(
            name=amp_ntrans3sd2_name, ref_names=amp_ntrans3_name,
            ignore_masks=difftap.mask,
        )

        placer.center_x(
            name=amp_ntrans12sd_name, ref_name=amp_ptrans12sd_name, prim=difftap,
        )
        prev_name = amp_ntrans12sd_name
        for wire_name in (amp_ntrans2_name, amp_ntrans2sd1_name):
            placer.place_to_the_left(
                name=wire_name, ref_names=prev_name, ignore_masks=difftap.mask,
            )
            prev_name = wire_name
        prev_name = amp_ntrans12sd_name
        for wire_name in (amp_ntrans1_name, amp_ntrans1sd2_name):
            placer.place_to_the_right(
                name=wire_name, ref_names=prev_name, ignore_masks=difftap.mask,
            )
            prev_name = wire_name

        for wire_name in (
            amp_ntrans3sd1_name, amp_ntrans3sd2_name,
            amp_ntrans2sd1_name, amp_ntrans2_name,
            amp_ntrans12sd_name, amp_ntrans1_name,
            amp_ntrans1sd2_name,
        ):
            placer.align_bottom(
                name=wire_name, ref_name=amp_ntrans3_name, prim=difftap,
            )

        placer.connect(
            name1=amp_ptrans3_name, name2=amp_ntrans3_name, prim=poly, net=net5,
        )
        placer.connect(
            name1=amp_pad3_name, name2=amp_ntrans1_name, prim=poly, net=net5,
        )
        placer.connect(
            name1=amp_pad3_name, name2=amp_ntrans2_name, prim=poly, net=net5,
        )

        conn1_name = f"li_{net1.name}_conn1"
        conn2_name = f"li_{net1.name}_conn2"
        via1_name = f"mcon_{net1.name}_amp1"
        via2_name = f"mcon_{net1.name}_amp2"

        for conn_name in (conn1_name, conn2_name):
            placer.wire(
                wire_name=conn_name, net=net1, wire=li,
                height=2*li.min_width, width=li.min_width,
            )
            placer.place_to_the_right(
                name=conn_name, ref_names=amp_ppad1_name,
            )
        placer.align_top(
            name=conn1_name, ref_name=amp_ptrans1sd2_name, prim=li, net=net1,
        )
        placer.align_bottom(
            name=conn2_name, ref_name=amp_ntrans1sd2_name, prim=li, net=net1,
        )

        placer.connect(
            name1=conn1_name, name2=conn2_name, prim=li, net=net1,
        )
        placer.connect(
            name1=conn2_name, name2=amp_ntrans1sd2_name, prim=li, net=net1,
        )

        placer.wire(
            wire_name=via1_name, net=net1, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.wire(
            wire_name=via2_name, net=net1, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )

        placer.align_left(
            name=via1_name, ref_name=conn1_name, prim=li, net=net1,
        )
        placer.center_x(
            name=via2_name, ref_name="amp_inv1", ref_pin=True, prim=li, net=net1,
        )

        for via_name in (via1_name, via2_name):
            placer.place_below(
                name=via_name, ref_names=(ampbufn_mcon_name, ampbufn_via_name),
            )

        placer.connect(
            name1=via1_name, name2=via2_name, prim=m1, net=net1,
        )

        conn1_name = f"li_{net2.name}_conn1"
        conn2_name = f"li_{net2.name}_conn2"
        via1_name = f"mcon_{net2.name}_amp1"
        via2_name = f"mcon_{net2.name}_amp2"

        for conn_name in (conn1_name, conn2_name):
            placer.wire(
                wire_name=conn_name, net=net2, wire=li,
                height=2*li.min_width, width=li.min_width,
            )
            placer.place_to_the_left(
                name=conn_name, ref_names=amp_ppad2_name,
            )
        placer.align_top(
            name=conn1_name, ref_name=amp_ptrans2sd1_name, prim=li, net=net2,
        )
        placer.align_bottom(
            name=conn2_name, ref_name=amp_ntrans2sd1_name, prim=li, net=net2,
        )

        placer.connect(
            name1=conn1_name, name2=conn2_name, prim=li, net=net2,
        )
        placer.connect(
            name1=conn2_name, name2=amp_ntrans2sd1_name, prim=li, net=net2,
        )

        placer.wire(
            wire_name=via1_name, net=net2, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.wire(
            wire_name=via2_name, net=net2, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )

        placer.align_left(
            name=via1_name, ref_name=conn1_name, prim=li, net=net2,
        )
        placer.center_x(
            name=via2_name, ref_name="amp_inv2", ref_pin=True, prim=li, net=net2,
        )

        for via_name in (via1_name, via2_name):
            placer.place_above(
                name=via_name, ref_names=(ampbufn_mcon_name, ampbufn_via_name),
            )

        placer.connect(
            name1=via1_name, name2=via2_name, prim=m1, net=net2,
        )

        # amp_vdden (net3)
        mcon1_name = f"mcon__{net3.name}__{amp_ntrans3sd2_name}"
        mcon2_name = f"mcon__{net3.name}__{amp_ptrans3sd2_name}"
        mcon3_name = f"mcon__{net3.name}__{amp_ptrans12sd_name}"

        for licon_name in (mcon1_name, mcon2_name, mcon3_name):
            placer.wire(
                wire_name=licon_name, net=net3, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="tall",
            )

        placer.align_left(
            name=mcon1_name, ref_name=amp_ntrans3sd2_name, prim=li, net=net3,
        )
        placer.align_bottom(
            name=mcon1_name, ref_name=amp_ntrans3sd2_name, prim=li, net=net3,
        )

        placer.align_left(
            name=mcon2_name, ref_name=amp_ptrans3sd2_name, prim=li, net=net3,
        )
        placer.align_top(
            name=mcon2_name, ref_name=amp_ptrans3sd2_name, prim=li, net=net3,
        )

        placer.center_x(
            name=mcon3_name, ref_name=amp_ptrans12sd_name, prim=li, net=net3,
        )
        placer.align_top(
            name=mcon3_name, ref_name=amp_ptrans12sd_name, prim=li, net=net3,
        )

        placer.connect(
            name1=mcon1_name, name2=mcon2_name, prim=m1, net=net3,
        )
        placer.connect(
            name1=mcon2_name, name2=mcon3_name, prim=m1, net=net3,
        )

        placer.fill(
            names=(amp_ptrans3sd1_name, lg_pad5_name, "seq_nand2_nsetbit[0]"), prim=psdm,
        )
        placer.fill(
            names=(amp_ntrans3sd1_name, "seq_nand2_nsetbit[0]"), prim=nsdm,
        )

        # clk_n second time (net5)
        # keep previous mcon names for placement
        mcon4_name = f"mcon__{net5.name}__{amp_pad3_name}"
        cell5_name = "clk_inv"
        clkn_clkinv_mcon_name = mcon5_name = f"mcon__{net5.name}__{cell2_name}"
        conn_name = f"m1_{net5.name}_conn"

        placer.wire(
            wire_name=mcon4_name, net=net5, wire=mcon, columns=2,
            bottom_enclosure="wide", top_enclosure="tall",
        )
        placer.place_to_the_left(
            name=mcon4_name, ref_names=(mcon1_name, mcon1_name),
        )
        placer.center_y(
            name=mcon4_name, ref_name=amp_pad3_name, prim=li, net=net5,
        )

        placer.wire(
            wire_name=mcon5_name, net=net5, wire=mcon, rows=2,
            bottom_enclosure="wide", top_enclosure="tall",
        )
        placer.center_x(
            name=mcon5_name, ref_name=cell5_name, ref_pin=True, prim=li, net=net5,
        )
        # Placement will be done whe doing start net

        placer.wire(
            wire_name=conn_name, net=net5, wire=m1,
            ref_width=mcon4_name, ref_height=mcon5_name,
        )
        placer.center_x(
            name=conn_name, ref_name=mcon4_name, prim=m1, net=net5,
        )
        placer.center_y(
            name=conn_name, ref_name=mcon5_name, prim=m1, net=net5,
        )

        placer.connect(
            name1=conn_name, name2=mcon4_name, prim=m1, net=net5,
        )
        placer.connect(
            name1=conn_name, name2=mcon5_name, prim=m1, net=net5,
        )

        # q[n]
        wire3_name = None
        wire4_name = None
        for n in range(qs):
            net_name = f"q[{n}]" if n < (qs - 1) else "end"
            qff_name = f"seq_qff[{n}]"
            net = nets[net_name]

            wire1_name = f"mcon_{net_name}_{qff_name}"
            placer.wire(
                wire_name=wire1_name, net=net, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.align_left(
                name=wire1_name, ref_name=qff_name, ref_pin=True, prim=li, net=net,
            )
            placer.align_top(
                name=wire1_name, ref_name=qff_name, ref_pin=True, prim=li, net=net,
            )

            if n < (qs - 1):
                cell_name = f"seq_nor2_nsetbit[{n}]"
                wire2_name = f"mcon_{net_name}_{cell_name}"
                placer.wire(
                    wire_name=wire2_name, net=net, wire=mcon, rows=2,
                    bottom_enclosure="tall", top_enclosure="wide",
                )
                placer.align_left(
                    name=wire2_name, ref_name=cell_name, ref_pin=True,
                    prim=li, net=net,
                )
                placer.align_bottom(
                    name=wire2_name, ref_name=cell_name, ref_pin=True,
                    prim=li, net=net,
                )

                pad_name = f"m1pad_{net_name}_{cell_name}"
                placer.wire(
                    wire_name=pad_name, net=net, wire=m1,
                    ref_width=wire2_name, ref_height=wire1_name,
                )
                placer.center_x(name=pad_name, ref_name=wire2_name, prim=m1)
                placer.center_y(name=pad_name, ref_name=wire1_name, prim=m1)

                placer.connect(name1=pad_name, name2=wire1_name, prim=m1, net=net)
                placer.connect(name1=pad_name, name2=wire2_name, prim=m1, net=net)

            if n > 0:
                prevnet_name = f"q[{n - 1}]"
                prevcell_name = f"seq_nor2_nsetbit[{n - 1}]"
                prevwire2_name = f"mcon_{prevnet_name}_{prevcell_name}"

                cell_name = f"seq_nand2_nrstbit[{n - 1}]"
                wire3_name = f"mcon_{net_name}_{cell_name}"
                placer.wire(
                    wire_name=wire3_name, net=net, wire=mcon, rows=2,
                    bottom_enclosure="tall", top_enclosure="wide",
                )
                placer.align_left(
                    name=wire3_name, ref_name=cell_name, ref_pin=True,
                    prim=li, net=net,
                )
                placer.place_above(
                    name=wire3_name, ref_names=prevwire2_name, ignore_masks=li.mask,
                )

                pad_name = f"m1pad_{net_name}_{cell_name}"
                placer.wire(
                    wire_name=pad_name, net=net, wire=m1,
                    ref_width=wire3_name, ref_height=wire1_name,
                )
                placer.center_x(name=pad_name, ref_name=wire3_name, prim=m1)
                placer.center_y(name=pad_name, ref_name=wire1_name, prim=m1)

                placer.connect(name1=pad_name, name2=wire1_name, prim=m1, net=net)
                placer.connect(name1=pad_name, name2=wire3_name, prim=m1, net=net)

                cell_name = f"seq_nand2_nsetbit[{n - 1}]"
                wire4_name = f"mcon_{net_name}_{cell_name}"
                placer.wire(
                    wire_name=wire4_name, net=net, wire=mcon, rows=2,
                    bottom_enclosure="tall", top_enclosure="wide",
                )
                placer.align_left(
                    name=wire4_name, ref_name=cell_name, ref_pin=True,
                    prim=li, net=net,
                )
                placer.place_above(
                    name=wire4_name, ref_names=prevwire2_name, ignore_masks=li.mask,
                )

                placer.connect(
                    name1=wire3_name, name2=wire4_name, prim=m1, net=net,
                )
        assert wire3_name is not None
        assert wire4_name is not None

        # start
        net = nets.start
        wire5_name = None
        for n in range(bits):
            cell_name = f"seq_nor2_nrstbit[{n}]"
            wire5_name = f"mcon__{net.name}__{cell_name}"

            placer.wire(
                wire_name=wire5_name, net=net, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=wire5_name, ref_name=cell_name, prim=li, net=net,
            )
            placer.place_above(
                name=wire5_name, ref_names=(wire3_name, wire4_name),
            )
        assert wire5_name is not None

        cell_name = "seq_capt"
        wire6_name = f"mcon__{net.name}__{cell_name}"

        placer.wire(
            wire_name=wire6_name, net=net, wire=mcon, rows=2,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.center_x(
            name=wire6_name, ref_name=cell_name, prim=li, net=net,
        )
        placer.align_top(
            name=wire6_name, ref_name=cell_name, prim=li, net=net,
        )

        # Remaining placement for clk_n net
        placer.place_below(
            name=clkn_clkinv_mcon_name, ref_names=wire6_name,
        )

        corner_name = f"m1_{net.name}_corner"

        placer.wire(
            wire_name=corner_name, net=net, wire=m1,
            ref_width=wire6_name, ref_height=wire5_name,
        )
        placer.center_x(
            name=corner_name, ref_name=wire6_name, prim=m1, net=net,
        )
        placer.center_y(
            name=corner_name, ref_name=wire5_name, prim=m1, net=net,
        )

        placer.connect(
            name1=corner_name, name2=wire6_name, prim=m1, net=net,
        )
        placer.connect(
            name1=corner_name, name2=wire5_name, prim=m1, net=net,
        )

        # bit[n]
        for bit in range(bits):
            net = nets[f"bit[{bit}]"]
            cell1_name = f"seq_latch_bit[{bit}]"
            cell2_name = f"invswitch[{bit}]"
            mcon1_name = f"mcon__{net.name}__{cell1_name}"
            mcon2_name = f"mcon__{net.name}__{cell2_name}"

            placer.wire(
                wire_name=mcon1_name, net=net, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=mcon1_name, ref_name=cell1_name, ref_pin=True,
                prim=li, net=net,
            )
            placer.center_y(
                name=mcon1_name, ref_name=cell1_name, ref_pin=True,
                prim=li, net=net,
            )

            placer.wire(
                wire_name=mcon2_name, net=net, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=mcon2_name, ref_name=cell2_name, ref_pin=True,
                prim=li, net=net,
            )
            placer.center_y(
                name=mcon2_name, ref_name=cell2_name, ref_pin=True,
                prim=li, net=net,
            )

            placer.connect(
                name1=mcon1_name, name2=mcon2_name, prim=m1, net=net,
            )

        # bit_n[n]
        cap_bit_vias = []
        for bit in range(bits):
            net = nets[f"dac_cap_bit[{bit}]"]
            cell_name = f"invswitch[{bit}]"
            mcon_name = f"mcon__{net.name}__{cell_name}"
            via_name = f"via__{net.name}__{cell_name}"

            placer.wire(
                wire_name=mcon_name, net=net, wire=mcon, rows=2,
                bottom_enclosure="tall", top_enclosure="wide",
            )
            placer.center_x(
                name=mcon_name, ref_name=cell_name, ref_pin=True,
                prim=li, net=net,
            )
            placer.center_y(
                name=mcon_name, ref_name=cell_name, ref_pin=True,
                prim=li, net=net,
            )

            placer.wire(
                wire_name=via_name, net=net, wire=via, rows=2,
                bottom_enclosure="wide", top_enclosure="tall",
            )
            placer.center_x(
                name=via_name, ref_name=mcon_name, prim=m1, net=net,
            )
            placer.align_bottom(
                name=via_name, ref_name=mcon_name, prim=m1, net=net,
            )

            cap_bit_vias.append(via_name)
        assert len(cap_bit_vias) == bits, "Internal error"

        # vdd
        net = nets.vdd
        wire_name = "m1_vdd_left"
        nand2_name = "seq_nand2_nsetbit[0]"

        placer.wire(
            wire_name=wire_name, net=net, wire=li,
            ref_height=nand2_name, ref_height_pin=True,
        )
        placer.align_left(
            name=wire_name, ref_name=left_cell, prim=li, net=net,
        )
        placer.align_bottom(
            name=wire_name, ref_name=nand2_name, ref_pin=True,
            prim=li, net=net,
        )
        placer.connect(
            name1=wire_name, name2=nand2_name, prim=li, net=net,
        )

        for ref_name in (
            lg_ptrans1sd2_name, lg_ptrans4sd1_name,
            amp_ptrans3sd1_name,
        ):
            wire_name = f"m1_vdd_{ref_name}"

            placer.wire(
                wire_name=wire_name, net=net, wire=li,
                ref_height=nand2_name, ref_height_pin=True,
            )
            placer.center_x(
                name=wire_name, ref_name=ref_name, prim=li, net=net,
            )
            placer.align_top(
                name=wire_name, ref_name=nand2_name, ref_pin=True, prim=li, net=net,
            )
            placer.connect(
                name1=wire_name, name2=ref_name, prim=li, net=net,
            )

        # vss
        net = nets.vss

        wire_name = "m1_vss_left"

        placer.wire(
            wire_name=wire_name, net=net, wire=li,
            ref_height="seq_nand2_nsetbit[0]", ref_height_pin=True,
        )
        placer.align_left(
            name=wire_name, ref_name=left_cell, prim=li, net=net,
        )
        placer.align_top(
            name=wire_name, ref_name="seq_nand2_nsetbit[0]", ref_pin=True,
            prim=li, net=net,
        )
        placer.connect(
            name1=wire_name, name2="seq_nand2_nsetbit[0]", prim=li, net=net,
        )

        for ref_name in (
            lg_ntrans12sd_name, lg_ntrans34sd_name, lg_ntrans56sd_name,
            amp_ntrans12sd_name, amp_ntrans3sd1_name,
        ):
            wire_name = f"m1_vss_{ref_name}"

            placer.wire(
                wire_name=wire_name, net=net, wire=li,
                ref_height=nand2_name, ref_height_pin=True,
            )
            placer.center_x(
                name=wire_name, ref_name=ref_name, prim=li, net=net,
            )
            placer.align_top(
                name=wire_name, ref_name=nand2_name, ref_pin=True, prim=li, net=net,
            )
            placer.connect(
                name1=wire_name, name2=ref_name, prim=li, net=net,
            )
        # Special alignment for vss connect to pmos
        ref_name=amp_ppad2_name
        wire_name = f"m1_vss_{ref_name}"

        placer.wire(
            wire_name=wire_name, net=net, wire=li,
            width=2*li.min_width, height=li.min_width
        )
        placer.align_right(
            name=wire_name, ref_name=amp_ppad2_name, prim=li, net=net,
        )
        placer.center_y(
            name=wire_name, ref_name=amp_pad3_name, prim=li,
        )
        placer.connect(
            name1=wire_name, name2=amp_ntrans12sd_name, prim=li, net=net,
        )
        placer.connect(
            name1=wire_name, name2=amp_ppad2_name, prim=li, net=net,
        )

        if not placer.execute():
            print("Not all placement instructions have completed")

        # Now connect the cap_bit m2 lines based on their relative placement
        right_conns = []
        left_conns = []
        for bit in range(bits):
            net = nets[f"dac_cap_bit[{bit}]"]

            via1_name = cap_bit_vias[bit]
            via2_name = cap_bit_via2s[bit]

            info1 = placer.info_lookup[via1_name]
            info2 = placer.info_lookup[via2_name]

            bb1 = info1.bb(mask=m2.mask, net=net, placed=True)
            bb2 = info2.bb(mask=m2.mask, net=net, placed=True)
            assert bb1 is not None
            assert bb2 is not None

            conn_name = f"m2_bit_cap_conn[{bit}]"
            placer.wire(
                wire_name=conn_name, net=net, wire=m2,
                width=3*m2.min_width, height=2*m2.min_width,
            )

            if bb1.right < bb2.left:
                # Connect right
                placer.align_right(
                    name=conn_name, ref_name=via2_name, prim=m2, net=net,
                )
                right_conns.append(conn_name)
            else:
                # Connect left
                placer.align_left(
                    name=conn_name, ref_name=via2_name, prim=m2, net=net,
                )
                left_conns.append(conn_name)

            placer.connect(
                name1=conn_name, name2=via1_name, prim=m2, net=net,
            )
            placer.connect(
                name1=conn_name, name2=via2_name, prim=m2, net=net,
            )

        prev_conn = cap_bit_via2s[0]
        for bit, conn_name in enumerate((*right_conns, *reversed(left_conns))):
            placer.place_below(name=conn_name, ref_names=prev_conn)
            prev_conn = conn_name

        if not placer.execute():
            print("Not all placement instructions of second set have completed")
