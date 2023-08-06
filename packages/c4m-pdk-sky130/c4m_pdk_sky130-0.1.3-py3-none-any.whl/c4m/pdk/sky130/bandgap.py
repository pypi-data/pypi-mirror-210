# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
"""This is preliminary bandgap code. Target it to make the code more generic and
spin it off in separate repo.
"""
from typing import Tuple, Dict, Iterable, Any, Optional, cast
from textwrap import dedent
from matplotlib import pyplot as _plt
import numpy as _np

from PySpice.Unit import u_Degree  # type: ignore

from pdkmaster.technology import (
    geometry as _geo, primitive as _prm, technology_ as _tch
)
from pdkmaster.design import (
    circuit as _ckt, layout as _lay, cell as _cell, library as _lbry,
)
from pdkmaster.io.spice.typing import CornerSpec

from c4m.pdk import sky130
from c4m.pdk.sky130 import _layout as _sky130lay, _simulation as _sim
_prims = sky130.tech.primitives

__all__ = [
    "BandgapBranch1", "BandgapBranch2", "Bandgap", "BandgapCell",
]


def _reldiff(f1: float, f2: float):
    return abs(f1/f2 - 1)


class BandgapBranch1:
    """This represents the first branch of the bandgap structure;
    e.g. a pmos, a nmos and the bipolar.
    """
    def __init__(self, *,
        nmos: _prm.MOSFET, nmos_l: float, nmos_w: float, nmos_mult: int=1,
        pmos: _prm.MOSFET, pmos_l: float, pmos_w: float, pmos_mult: int=1,
        pnp: _prm.Bipolar, pnp_mult: int=1,
    ):
        assert nmos_mult >= 1
        assert pmos_mult >= 1
        assert pnp_mult >= 1

        self.nmos = nmos
        self.nmos_l = nmos_l
        self.nmos_w = nmos_w
        self.nmos_mult = nmos_mult

        self.pmos = pmos
        self.pmos_l = pmos_l
        self.pmos_w = pmos_w
        self.pmos_mult = pmos_mult

        self.pnp = pnp
        self.pnp_mult = pnp_mult

        self.ckt = ckt = sky130.cktfab.new_circuit(name="bgbranch1")

        ns = tuple(
            ckt.instantiate(nmos, name=f"n[{n}]", l=nmos_l, w=nmos_w)
            for n in range(nmos_mult)
        )

        ps = tuple(
            ckt.instantiate(pmos, name=f"p[{n}]", l=pmos_l, w=pmos_w)
            for n in range(pmos_mult)
        )

        pnps = tuple(
            ckt.instantiate(pnp, name=f"pnp[{n}]")
            for n in range(pnp_mult)
        )

        ckt.new_net(name="vdd", external=True, childports=(
            *(p.ports.sourcedrain1 for p in ps),
            *(p.ports.bulk for p in ps),
        ))
        ckt.new_net(name="vss", external=True, childports=(
            *(n.ports.bulk for n in ns),
            *(pnp.ports.base for pnp in pnps),
            *(pnp.ports.collector for pnp in pnps),
        ))

        ckt.new_net(name="p_gate", external=True, childports=(
            *(p.ports.gate for p in ps),
        ))
        ckt.new_net(name="n_gate", external=True, childports=(
            *(n.ports.sourcedrain1 for n in ns),
            *(n.ports.gate for n in ns),
            *(p.ports.sourcedrain2 for p in ps),
        ))
        ckt.new_net(name="vq", external=True, childports=(
            *(n.ports.sourcedrain2 for n in ns),
            *(pnp.ports.emitter for pnp in pnps),
        ))

    def I_Vq(self, *,
        Vdd: float, Vgs_n: float, Vgs_p: float,
        corner: CornerSpec, temp: u_Degree=u_Degree(25), debug: bool=False,
        **simopts: float,
    ) -> Tuple[float, float]:
        tb = sky130.pyspicefab.new_pyspicecircuit(
            corner=corner, top=self.ckt, title="I_Vq tb",
        )

        tb.V("gnd", "vss", tb.gnd, 0.0)
        tb.V("vdd", "vdd", tb.gnd, Vdd)
        tb.V("p_gate", "vdd", "p_gate", Vgs_p)
        tb.V("n_gate", "n_gate", "vq", Vgs_n)

        self.last_sim = sim = tb.simulator(temperature=temp)
        if simopts:
            sim.options(**simopts)
        if debug:
            print("Circuit:")
            print(str(sim))
            print("\nSimulating...")
        self.last_op = op = sim.operating_point()
        Ivdd = float(-op.Vvdd)
        Vq = float(op.vq)
        if debug:
            Vn = float(op.n_gate)
            Vp = float(op.p_gate)
            print(f"Done, (I={Ivdd}, Vq={Vq}, Vn_gate={Vn}, Vp_gate={Vp})")

        return Ivdd, Vq


class BandgapBranch2:
    """This represents the first branch of the bandgap structure;
    e.g. a pmos, a nmos and the bipolar.
    """
    def __init__(self, *,
        nmos: _prm.MOSFET, nmos_l: float, nmos_w: float, nmos_mult: int=1,
        pmos: _prm.MOSFET, pmos_l: float, pmos_w: float, pmos_mult: int=1,
        pnp: _prm.Bipolar, pnp_mult: int=1, pnp_ratio: int,
        resistor: _prm.Resistor, r1_height: float,
    ):
        assert nmos_mult >= 1
        assert pmos_mult >= 1
        assert pnp_mult >= 1

        self.nmos = nmos
        self.nmos_l = nmos_l
        self.nmos_w = nmos_w
        self.nmos_mult = nmos_mult

        self.pmos = pmos
        self.pmos_l = pmos_l
        self.pmos_w = pmos_w
        self.pmos_mult = pmos_mult

        self.pnp = pnp
        self.pnp_mult = pnp_mult

        self.resistor = resistor
        self.r1_height = r1_height

        self.ckt = ckt = sky130.cktfab.new_circuit(name="bgbranch2")

        ns = tuple(
            ckt.instantiate(nmos, name=f"n[{n}]", l=nmos_l, w=nmos_w)
            for n in range(nmos_mult)
        )

        ps = tuple(
            ckt.instantiate(pmos, name=f"p[{n}]", l=pmos_l, w=pmos_w)
            for n in range(pmos_mult)
        )

        pnps = tuple(
            ckt.instantiate(pnp, name=f"pnp[{n}]")
            for n in range(pnp_mult*pnp_ratio)
        )

        res = ckt.instantiate(resistor, name=f"res", height=r1_height)

        ckt.new_net(name="vdd", external=True, childports=(
            *(p.ports.sourcedrain1 for p in ps),
            *(p.ports.bulk for p in ps),
        ))
        ckt.new_net(name="vss", external=True, childports=(
            *(n.ports.bulk for n in ns),
            *(pnp.ports.base for pnp in pnps),
            *(pnp.ports.collector for pnp in pnps),
        ))

        ckt.new_net(name="p_gate", external=True, childports=(
            *(p.ports.gate for p in ps),
        ))
        ckt.new_net(name="n_gate", external=True, childports=(
            *(n.ports.sourcedrain1 for n in ns),
            *(n.ports.gate for n in ns),
            *(p.ports.sourcedrain2 for p in ps),
        ))
        ckt.new_net(name="vqr", external=True, childports=(
            *(n.ports.sourcedrain2 for n in ns),
            res.ports.port1,
        ))
        ckt.new_net(name="vq", external=True, childports=(
            res.ports.port2,
            *(pnp.ports.emitter for pnp in pnps),
        ))

    def I_Vq_Vqr(self, *,
        Vdd: float, Vgs_n: float, Vgs_p: float,
        corner: CornerSpec, temp: u_Degree=u_Degree(25), debug: bool=False,
        **simopts: float,
    ) -> Tuple[float, float, float]:
        tb = sky130.pyspicefab.new_pyspicecircuit(
            corner=corner, top=self.ckt, title="I_Vq tb",
        )

        tb.V("gnd", "vss", tb.gnd, 0.0)
        tb.V("vdd", "vdd", tb.gnd, Vdd)
        tb.V("p_gate", "vdd", "p_gate", Vgs_p)
        tb.V("n_gate", "n_gate", "vqr", Vgs_n)

        self.last_sim = sim = tb.simulator(temperature=temp)
        if simopts:
            sim.options(**simopts)
        if debug:
            print("Circuit:")
            print(str(sim))
            print("\nSimulating...")
        self.last_op = op = sim.operating_point()
        Ivdd = float(-op.Vvdd)
        Vq = float(op.vq)
        Vqr = float(op.vqr)
        if debug:
            Vn = float(op.n_gate)
            Vp = float(op.p_gate)
            print(f"Done, (I={Ivdd}, Vq={Vq}, Vqr={Vqr}, Vn_gate={Vn}, Vp_gate={Vp})")

        return Ivdd, Vq, Vqr


class Bandgap:
    class AreaSpec:
        """This class can be overloaded to have custom area computation
        """
        def __init__(self, *,
            trans_dl: float, trans_dw: float,
            r_pitch: float,
            pnp_area: float,
        ):
            self.trans_dl = trans_dl
            self.trans_dw = trans_dw
            self.r_pitch = r_pitch
            self.pnp_area = pnp_area

        def trans_area(self, *, l: float, w: float) -> float:
            return (l + self.trans_dl)*(w + self.trans_dw)

        def r_area(self, *, height: float) -> float:
            return self.r_pitch*height

    def __init__(self, *,
        nmos: _prm.MOSFET, nmos_l: float, nmos_w: float, nmos_mult: int=1,
        pmos: _prm.MOSFET, pmos_l: float, pmos_w: float, pmos_mult: int=1,
        resistor: _prm.Resistor, r1_height: float, r2_height: float,
        pnp: _prm.Bipolar, pnp_mult:int=1, pnp_ratio: int,
    ):
        assert nmos_mult >= 1
        assert pmos_mult >= 1
        assert pnp_mult >= 1

        self.nmos = nmos
        self.nmos_l = nmos_l
        self.nmos_w = nmos_w
        self.nmos_mult = nmos_mult

        self.pmos = pmos
        self.pmos_l = pmos_l
        self.pmos_w = pmos_w
        self.pmos_mult = pmos_mult

        self.resistor = resistor
        self.r1_height = r1_height
        self.r2_height = r2_height

        self.pnp = pnp
        self.pnp_mult = pnp_mult
        self.pnp_ratio = pnp_ratio

        self.ckt = ckt = sky130.cktfab.new_circuit(name="bandgap")

        n1s = tuple(
            ckt.instantiate(nmos, name=f"n1[{n}]", l=nmos_l, w=nmos_w)
            for n in range(nmos_mult)
        )
        n2s = tuple(
            ckt.instantiate(nmos, name=f"n2[{n}]", l=nmos_l, w=nmos_w)
            for n in range(nmos_mult)
        )
        ns = (*n1s, *n2s)

        p1s = tuple(
            ckt.instantiate(pmos, name=f"p1[{n}]", l=pmos_l, w=pmos_w)
            for n in range(pmos_mult)
        )
        p2s = tuple(
            ckt.instantiate(pmos, name=f"p2[{n}]", l=pmos_l, w=pmos_w)
            for n in range(pmos_mult)
        )
        p3s = tuple(
            ckt.instantiate(pmos, name=f"p3[{n}]", l=pmos_l, w=pmos_w)
            for n in range(pmos_mult)
        )
        ps = (*p1s, *p2s, *p3s)

        r1 = ckt.instantiate(resistor, name="r1", height=r1_height)
        r2 = ckt.instantiate(resistor, name="r2bot", height=r2_height)

        pnp1s = tuple(
            ckt.instantiate(pnp, name=f"pnp1[{n}]")
            for n in range(pnp_mult)
        )
        pnp2s = tuple(
            ckt.instantiate(pnp, name=f"pnp2[{n}]")
            for n in range(pnp_mult*pnp_ratio)
        )
        pnp3s = tuple(
            ckt.instantiate(pnp, name=f"pnp3[{n}]")
            for n in range(pnp_mult*pnp_ratio)
        )
        pnps = (*pnp1s, *pnp2s, *pnp3s)

        ckt.new_net(name="vdd", external=True, childports=(
            *(p.ports.sourcedrain1 for p in ps),
            *(p.ports.bulk for p in ps),
        ))
        ckt.new_net(name="vss", external=True, childports=(
            *(n.ports.bulk for n in ns),
            *(pnp.ports.base for pnp in pnps),
            *(pnp.ports.collector for pnp in pnps),
        ))
        ckt.new_net(name="vref", external=True, childports=(
            *(p3.ports.sourcedrain2 for p3 in p3s), r2.ports.port2,
        ))

        ckt.new_net(name="p_gate", external=False, childports=(
            *(p.ports.gate for p in ps),
            *(p2.ports.sourcedrain2 for p2 in p2s),
            *(n2.ports.sourcedrain1 for n2 in n2s),
        ))
        ckt.new_net(name="n_gate", external=False, childports=(
            *(n.ports.gate for n in ns),
            *(p1.ports.sourcedrain2 for p1 in p1s),
            *(n1.ports.sourcedrain1 for n1 in n1s),
        ))
        ckt.new_net(name="vq1", external=False, childports=(
            *(n1.ports.sourcedrain2 for n1 in n1s),
            *(pnp1.ports.emitter for pnp1 in pnp1s),
        ))
        ckt.new_net(name="vq2r1", external=False, childports=(
            *(n2.ports.sourcedrain2 for n2 in n2s), r1.ports.port1,
        ))
        ckt.new_net(name="vq2", external=False, childports=(
            r1.ports.port2, *(pnp2.ports.emitter for pnp2 in pnp2s),
        ))
        ckt.new_net(name="vq3", external=False, childports=(
            r2.ports.port1,
            *(pnp3.ports.emitter for pnp3 in pnp3s),
        ))

    def derive(self, *,
        nmos_l: Optional[float]=None, nmos_w: Optional[float]=None,
        nmos_mult: Optional[int]=None,
        pmos_l: Optional[float]=None, pmos_w: Optional[float]=None,
        pmos_mult: Optional[int]=None,
        r1_height: Optional[float]=None, r2_height: Optional[float]=None,
        pnp_mult: Optional[int]=None, pnp_ratio: Optional[int]=None,
    ) -> "Bandgap":
        """Create bandgap from current bandgap with selected parameters changed.
        """
        nmos = self.nmos
        if nmos_l is None:
            nmos_l = self.nmos_l
        if nmos_w is None:
            nmos_w = self.nmos_w
        if nmos_mult is None:
            nmos_mult = self.nmos_mult

        pmos = self.pmos
        if pmos_l is None:
            pmos_l = self.pmos_l
        if pmos_w is None:
            pmos_w = self.pmos_w
        if pmos_mult is None:
            pmos_mult = self.pmos_mult

        resistor = self.resistor
        if r1_height is None:
            r1_height = self.r1_height
        if r2_height is None:
            r2_height = self.r2_height

        pnp = self.pnp
        if pnp_mult is None:
            pnp_mult = self.pnp_mult
        if pnp_ratio is None:
            pnp_ratio = self.pnp_ratio

        return self.__class__(
            nmos=nmos, nmos_l=nmos_l, nmos_w=nmos_w, nmos_mult=nmos_mult,
            pmos=pmos, pmos_l=pmos_l, pmos_w=pmos_w, pmos_mult=pmos_mult,
            resistor=resistor, r1_height=r1_height, r2_height=r2_height,
            pnp=pnp, pnp_mult=pnp_mult, pnp_ratio=pnp_ratio,
        )

    def A(self, *, device: str, spec: AreaSpec):
        devices = (
            "trans", "ntrans", "ptrans", "r", "r1", "r2", "pnp", "pnp1", "pnp2", "pnp3",
            "all",
        )
        if device not in devices:
            raise ValueError(f"device not one of\n  {devices}")

        if device == "trans":
            return self.A(device="ntrans", spec=spec) + self.A(device="ptrans", spec=spec)
        elif device == "ntrans":
            return self.nmos_mult*spec.trans_area(l=self.nmos_l, w=self.nmos_w)
        elif device == "ptrans":
            return self.pmos_mult*spec.trans_area(l=self.pmos_l, w=self.pmos_w)
        elif device == "r":
            return self.A(device="r1", spec=spec) + self.A(device="r2", spec=spec)
        elif device == "r1":
            return spec.r_area(height=self.r1_height)
        elif device == "r2":
            return spec.r_area(height=self.r2_height)
        elif device == "pnp":
            return sum(self.A(device=dev, spec=spec) for dev in ("pnp1", "pnp2", "pnp3"))
        elif device == "pnp1":
            return self.pnp_mult*spec.pnp_area
        elif device in ("pnp2", "pnp3"):
            return self.pnp_mult*self.pnp_ratio*spec.pnp_area
        elif device == "all":
            return sum(self.A(device=dev, spec=spec) for dev in ("trans", "r", "pnp"))
        else:
            raise RuntimeError("Internal error: unhandled device specification")

    def operating_point(self, *,
        vdd: float, corner: CornerSpec, temp=u_Degree(25),
        **simopts: float,
    ):
        self.last_tb = tb = sky130.pyspicefab.new_pyspicecircuit(
            corner=corner, top=self.ckt, title="bandgap test",
        )
        tb.V("supply", "vdd", "vss", vdd)
        tb.C("out", "vref", "vss", 1e-12)
        tb.V("gnd", "vss", tb.gnd, 0.0)
        sckt = tb._subcircuits["bandgap"]
        sckt.element("Mp1[0]").drain.add_current_probe(sckt)
        sckt.element("Mp2[0]").drain.add_current_probe(sckt)
        sckt.element("Mp3[0]").drain.add_current_probe(sckt)

        self.last_sim = sim = tb.simulator(temperature=temp)
        if simopts:
            sim.options(**simopts)
        return BandgapSimResult(
            bandgap=self, res=sim.operating_point(),
        )

    def tempsweep(self, *,
        vdd: float, corner: CornerSpec, sweep=slice(-20, 81, 20),
        **simopts: float,
    ):
        self.last_tb = tb = sky130.pyspicefab.new_pyspicecircuit(
            corner=corner, top=self.ckt, title="bandgap test",
        )
        tb.V("supply", "vdd", "vss", vdd)
        tb.C("out", "vref", "vss", 1e-12)
        tb.V("gnd", "vss", tb.gnd, 0.0)
        sckt = tb._subcircuits["bandgap"]
        sckt.element("Mp1[0]").drain.add_current_probe(sckt)
        sckt.element("Mp2[0]").drain.add_current_probe(sckt)
        sckt.element("Mp3[0]").drain.add_current_probe(sckt)

        self.last_sim = sim = tb.simulator(temperature=u_Degree(25))
        if simopts:
            sim.options(**simopts)
        return BandgapTempSweepResult(
            bandgap=self, res=sim.dc(temp=sweep),
        )

    def tempsweep_corners(self, *,
        vdd: float, corners: Iterable[CornerSpec],
        sweep: slice=slice(-20, 81, 20),
        **simopts: float,
    ) -> "BandgapTempSweepCornersResult":
        results = {
            corner: self.tempsweep(vdd=vdd, corner=corner, sweep=sweep, **simopts)
            for corner in corners
        }

        return BandgapTempSweepCornersResult(results=results)

    def tempsweep_vdds(self, *,
        vdds: Iterable[float], corner: CornerSpec,
        sweep: slice=slice(-20, 81, 20),
        **simopts: float,
    ) -> "BandgapTempSweepVddsResult":
        results = {
            vdd: self.tempsweep(vdd=vdd, corner=corner, sweep=sweep, **simopts)
            for vdd in vdds
        }

        return BandgapTempSweepVddsResult(results=results)

    def optimize_r2_height(self, *,
        vdd: float, corner: CornerSpec,
        temp: slice=slice(-20, 81, 20), vref_reldiff: float=0.001,
        debug: bool=False,
        **simopts: float,
    ) -> "Bandgap":
        """Optimize r2_height of a bandgap

        Return the bandgap with same dimensions as the current one but with
        the optimized r2_height value.
        """
        if debug:
            print("Computing first temperature sweep")
        bg = self
        res = self.tempsweep(vdd=vdd, corner=corner, sweep=temp, **simopts)
        vref = _np.array(res.V_node(node="vref"))
        vref_mint = vref[0]
        vref_maxt = vref[-1]
        reldiff = _reldiff(vref_mint, vref_maxt)

        if debug:
            print(
                f"0: r2_height={bg.r2_height:.3f}, reldiff={reldiff:.5f}, "
                f"vref_mint={vref_mint:.3f}, vref_maxt={vref_maxt:.3f}",
            )
        if reldiff < vref_reldiff:
            if debug:
                print("Already within spec")
            return self
        else:
            run = 1
            while True:
                reldiff_prev = reldiff

                vref_delta = vref_maxt - vref_mint
                Ibr3 = res.I(branch=3)
                Ibr3_mint = Ibr3[0]
                Ibr3_maxt = Ibr3[-1]
                Ibr3_delta = Ibr3_maxt - Ibr3_mint

                R_delta = -vref_delta/Ibr3_delta
                R_avg = _np.mean((vref_mint/Ibr3_mint, vref_maxt/Ibr3_maxt))

                bg2 = bg.derive(r2_height=bg.r2_height*(R_avg + R_delta)/R_avg)
                res = bg2.tempsweep(vdd=vdd, corner=corner, sweep=temp, **simopts)
                vref = _np.array(res.V_node(node="vref"))
                vref_mint = vref[0]
                vref_maxt = vref[-1]
                reldiff = _reldiff(vref_mint, vref_maxt)

                if debug:
                    print(
                        f"{run}: r2_height={bg2.r2_height:.3f}, reldiff={reldiff:.5f}, "
                        f"vref_mint={vref_mint:.3f}, vref_maxt={vref_maxt:.3f}",
                    )
                if reldiff > reldiff_prev:
                    print("WARNING: r2_height optimization not converging; bayling out")
                    return bg
                bg = bg2
                if reldiff < vref_reldiff:
                    if debug:
                        print("Convergence criteria met")
                    return bg

                run += 1

    @staticmethod
    def compute_minpower(*,
        nmos: _prm.MOSFET, nmos_l_min: float, nmos_l_max: float, nmos_w: float,
        nmos_mult: int=1, nmos_Vgs_min: Optional[float],
        pmos: _prm.MOSFET, pmos_l_min: float, pmos_l_max: float, pmos_w: float,
        pmos_mult: int=1, pmos_Vgs_min: Optional[float],
        pnp: _prm.Bipolar, pnp_mult: int=1, pnp_ratio: int=2,
        resistor: _prm.Resistor,
        vdd_min: float, vdd_max: float,
        corner: CornerSpec, temp_min: float, temp_max: float,
        debug: bool=False,
        **simopts: float,
    ) -> "Bandgap":
        """Minimum Vgs for nmos and pmos can be specified to be sure to be above
        threshold.
        """
        # Support functions
        def comp_Vgs_Vds(*, Vpnp1: float, Vref: float):
            Vgs_n = Vgs_p = Vds_n = Vds_p = (vdd_min - Vpnp1)/2
            if (nmos_Vgs_min is not None) and (Vgs_n < nmos_Vgs_min):
                Vgs_n = nmos_Vgs_min
            if (pmos_Vgs_min is not None) and (Vgs_p < pmos_Vgs_min):
                Vgs_p = pmos_Vgs_min

            return Vgs_n, Vds_n, Vgs_p, Vds_p

        def comp_I_min(*, Vgs_n: float, Vds_n: float, Vgs_p: float, Vds_p: float):
            In_min = _sim.SimMOS(
                mos=nmos, l=nmos_l_max, w=nmos_w,
            ).Ids(
                Vgs=Vgs_n, Vds=Vds_n, corner=corner, temp=temp,
                **simopts,
            )*nmos_mult
            Ip_min = abs(_sim.SimMOS(
                mos=pmos, l=pmos_l_max, w=pmos_w,
            ).Ids(
                Vgs=-Vgs_p, Vds=-Vds_p, corner=corner, temp=temp,
                **simopts,
            ))*pmos_mult

            return In_min, Ip_min

        def assure_Vgs_p(*,
            bg: Bandgap, bgop: BandgapSimResult,
        ) -> Tuple[Bandgap, BandgapSimResult]:
            pmos_l = bg.pmos_l
            assert pmos_Vgs_min is not None
            Vgs_p = float(bgop.V_trans(trans="p2", nodes="gs"))
            if Vgs_p < 0.999*pmos_Vgs_min:
                if debug:
                    print(f"Vgs_p too low ({Vgs_p} < {pmos_Vgs_min})")
                    print(f"Increasing l of pmos to try to increase it's Vgs")
                step = (pmos_l_max - pmos_l_min)/20
                while pmos_l < 0.99*pmos_l_max:
                    pmos_l2 = min(pmos_l + step, pmos_l_max)
                    bg2 = bg.derive(pmos_l=pmos_l2)
                    bgop2 = bg2.operating_point(
                        vdd=vdd_min, corner=corner, temp=temp, **simopts,
                    )
                    Vgs_p2 = float(bgop2.V_trans(trans="p2", nodes="gs"))
                    if Vgs_p2 > pmos_Vgs_min:
                        return bg2, bgop2
                    if Vgs_p2 < 0.999*Vgs_p:
                        print("WARNING: Vgs_p does not increase, bailing out")
                        return bg, bgop
                    pmos_l = pmos_l2
                    Vgs_p = Vgs_p2
                    bg = bg2
                    bgop = bgop2
                    if debug:
                        print(f"pmos_l={pmos_l}, Vgs_p={Vgs_p}")
                print("WARNING: max pmos l reached when incresing Vgs_p")
            return bg, bgop

        def assure_Vgs_n(*, bg: Bandgap, bgop) -> Tuple[Bandgap, Any]:
            Vgs_n = float(bgop.V_trans(trans="n1", nodes="gs"))
            assert nmos_Vgs_min is not None
            if Vgs_n < 0.999*nmos_Vgs_min:
                print("WARNING: not implemented Vgs_n min optimization")
            return bg, bgop

        # Do computation in the middle of the temperature range
        temp = (temp_min + temp_max)/2
        if debug:
            print(f"Using temperature {temp:.1f}")

        # First estimation of Vgs and Vds
        # Assume 0.6V over the pnp;
        # divide Vgs evenly over nmos and pmos but obey minimum Vgs
        Vpnp1 = 0.6
        Vref = 1.2
        Vgs_n, Vds_n, Vgs_p, Vds_p = comp_Vgs_Vds(Vpnp1=Vpnp1, Vref=Vref)
        if debug:
            print(
                "First Vgs/Vds estimates:\n"
                f"   Vgs_n={Vgs_n}, Vds_n={Vds_n}, Vgs_p={Vgs_p}, Vds_p={Vds_p}"
            )

        # Determine the first current target
        # Take lowest current with maximum l of nmos and pmos
        if debug:
            print(f"Computing first target current estimate...")
        In_min, Ip_min = comp_I_min(Vgs_n=Vgs_n, Vds_n=Vds_n, Vgs_p=Vgs_p, Vds_p=Vds_p)
        if debug:
            print(f"In_min={In_min}, Ip_min={Ip_min}")
        Itgt = min(In_min, Ip_min)

        # Voltage of pnp for the given current
        if debug:
            print("Computing voltage of bipolar for target current")
        Vpnp1 = _sim.SimPNP(pnp=pnp).Vec_diode(Iec=Itgt, corner=corner, temp=temp, **simopts)
        if debug:
            print(f"Vpnp1={Vpnp1}")
        Vgs_n, Vds_n, Vgs_p, Vds_p = comp_Vgs_Vds(Vpnp1=Vpnp1, Vref=Vref)
        if debug:
            print(
                "New Vgs/Vds estimates:\n"
                f"   Vgs_n={Vgs_n}, Vds_n={Vds_n}, Vgs_p={Vgs_p}, Vds_p={Vds_p}"
            )
        if debug:
            print(f"Computing new target current estimate...")
        In_min, Ip_min = comp_I_min(Vgs_n=Vgs_n, Vds_n=Vds_n, Vgs_p=Vgs_p, Vds_p=Vds_p)
        if debug:
            print(f"In_min={In_min}, Ip_min={Ip_min}")

        # Computing transistor dimensions for target current and estimated voltages
        if debug:
            print("Computing transistor l")
        # Use biggest current of two as target current,
        # Compute l for the other transistor
        if Ip_min < In_min:
            Itgt = In_min
            nmos_l = nmos_l_max
            # Compute pmos_l
            try:
                pmos_l = _sim.SimMOS.l_for_Ids(
                    mos=pmos, l_min=pmos_l_min, l_max=pmos_l_max, w=pmos_w,
                    Vgs=Vgs_p, Vds=Vds_p, Ids=Itgt/pmos_mult,
                    corner=corner, temp=temp,
                    **simopts,
                )
            except ValueError:
                print("WARNING: pmos too weak, taking minimum l")
                pmos_l = pmos_l_min
        else:
            Itgt = Ip_min
            pmos_l = pmos_l_max
            # Compute pmos_l
            try:
                nmos_l = _sim.SimMOS.l_for_Ids(
                    mos=nmos, l_min=nmos_l_min, l_max=nmos_l_max, w=nmos_w,
                    Vgs=Vgs_p, Vds=Vds_p, Ids=Itgt/nmos_mult,
                    corner=corner, temp=temp,
                    **simopts,
                )
            except ValueError:
                print("WARNING: nmos too weak, taking minimum l")
                nmos_l = nmos_l_min
        if debug:
            print(f"nmos_l={nmos_l}, nmos_w={nmos_w}, pmos_l={pmos_l}, pmos_w={pmos_w}")

        if debug:
            print("Updating bipolar voltage...")
        br1 = BandgapBranch1(
            nmos=nmos, nmos_l=nmos_l, nmos_w=nmos_w, nmos_mult=nmos_mult,
            pmos=pmos, pmos_l=pmos_l, pmos_w=pmos_w, pmos_mult=pmos_mult,
            pnp=pnp, pnp_mult=pnp_mult,
        )
        Ibr1, Vpnp1 = br1.I_Vq(
            Vdd=vdd_min, Vgs_n=Vgs_n, Vgs_p=Vgs_p,
            corner=corner, temp=temp,
            **simopts,
        )
        Vpnp2 = _sim.SimPNP(pnp=pnp).Vec_diode(
            Iec=Ibr1/(pnp_mult*pnp_ratio), corner=corner, temp=temp,
            **simopts,
        )
        if pmos_Vgs_min is None:
            pmos_Vgs_min = (vdd_min - Vpnp1)/2
        if nmos_Vgs_min is None:
            nmos_Vgs_min = (vdd_min - Vpnp1)/2

        if debug:
            print(f"Ibr1={Ibr1}, Vpnp1={Vpnp1:.3f}, Vpnp2={Vpnp2:.3f}")

        assert Vpnp2 < Vpnp1
        if debug:
            print("Computing r1_height...")
        R1 = (Vpnp1 - Vpnp2)/Itgt
        r1_height = _sim.SimR.height_for_R(
            resistor=resistor, start_height=10.0, R=R1, corner=corner, temp=temp,
            **simopts,
        )
        if debug:
            print("Computing r2_height...")
        assert Vpnp2 < Vref
        R2 = (Vref - Vpnp2)/Itgt
        r2_height = _sim.SimR.height_for_R(
            resistor=resistor, start_height=10.0, R=R2, corner=corner, temp=temp,
            **simopts,
        )
        if debug:
            print(f"r1_height={r1_height:.2f}, r2_height={r2_height:.2f}")

        if debug:
            print("Updating parameters")
        bg = Bandgap(
            nmos=nmos, nmos_l=nmos_l, nmos_w=nmos_w, nmos_mult=nmos_mult,
            pmos=pmos, pmos_l=pmos_l, pmos_w=pmos_w, pmos_mult=pmos_mult,
            pnp=pnp, pnp_mult=pnp_mult, pnp_ratio=pnp_ratio,
            resistor=resistor, r1_height=r1_height, r2_height=r2_height,
        )
        bgop = bg.operating_point(vdd=vdd_min, corner=corner, temp=temp, **simopts)

        bg, bgop = assure_Vgs_p(bg=bg, bgop=bgop)
        bg, bgop = assure_Vgs_n(bg=bg, bgop=bgop)

        if debug:
            Vgs_n = float(bgop.V_trans(trans="n1", nodes="gs"))
            Vgs_p = float(bgop.V_trans(trans="p2", nodes="gs"))
            Vpnp1 = float(bgop.V_node(node="vq1"))
            Vpnp2 = float(bgop.V_node(node="vq2"))
            Ibr1 = float(bgop.I(1))
            Ibr2 = float(bgop.I(2))
            Ibr3 = float(bgop.I(3))
            Vgs_n = float(bgop.V_trans(trans="n1", nodes="gs"))
            Vds_p1 = float(bgop.V_trans(trans="p1", nodes="ds"))
            Vds_n2 = float(bgop.V_trans(trans="n2", nodes="ds"))
            print(
                f"Vpnp1={Vpnp1:.3f}, Vpnp2={Vpnp2:.3f}"
                f"\nIbr1={Ibr1:5.3g}, rIbr2={Ibr2/Ibr1}, rIbr3={Ibr3/Ibr1}"
                f"\nVgs_n={Vgs_n:.3f}, Vgs_p={Vgs_p:.3f}, Vds_p1={Vds_p1:.3f}, Vds_n2={Vds_n2:.3f}"
            )

        temp_delta = temp_max - temp_min
        temp_step = temp_delta/5

        if debug:
            print("Optimizing r2 height")
        return bg.optimize_r2_height(
            vdd=0.5*(vdd_min + vdd_max), corner=corner,
            temp=slice(temp_min, temp_max+0.1*temp_step, temp_step),
            debug=debug, **simopts,
        )

    def convert2cell(self, *,
        cell_name: str,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        pnp_cell: _cell.Cell,
    ) -> "BandgapCell":
        r1_height = tech.on_grid(self.r1_height)
        r2_height = tech.on_grid(self.r2_height)

        return BandgapCell(
            name=cell_name, tech=tech, cktfab=cktfab, layoutfab=layoutfab,
            nmos=self.nmos, nmos_l=self.nmos_l, nmos_w=self.nmos_w, nmos_mult=self.nmos_mult,
            pmos=self.pmos, pmos_l=self.pmos_l, pmos_w=self.pmos_w, pmos_mult=self.pmos_mult,
            resistor=self.resistor, r1_height=r1_height, r2_height=r2_height,
            pnp=pnp_cell, pnp_mult=self.pnp_mult, pnp_ratio=self.pnp_ratio,
        )

    @property
    def param_str(self):
        return dedent(f"""
            Bandgap:
            - nmos: {self.nmos}
            - nmos_l: {self.nmos_l}
            - nmos_w: {self.nmos_w}
            - nmos_mult: {self.nmos_mult}
            - pmos: {self.pmos}
            - pmos_l: {self.pmos_l}
            - pmos_w: {self.pmos_w}
            - pmos_mult: {self.pmos_mult}
            - pnp: {self.pnp}
            - pnp_mult: {self.pnp_mult}
            - pnp_ratio: {self.pnp_ratio}
            - resistor: {self.resistor}
            - r1_height: {self.r1_height}
            - r2_height: {self.r2_height}
        """[1:])


class BandgapSimResult:
    def __init__(self, *, bandgap: Bandgap, res):
        self.bandgap = bandgap
        self.res = res

    def V_node(self, *, node: str):
        """Return voltage at a node in the bandgap circuit"""
        assert node in (
            "n_gate", "p_gate", "vq1", "vq2", "vq2r1", "vq3", "vref",
        )
        if node != "vref":
            node = f"xtop.{node}"
        return self.res.nodes[node]

    def V_trans(self, *, trans: str, nodes: str):
        """Returns absolute voltage over nodes of a transistor"""
        if nodes == "sd":
            nodes = "ds"
        if nodes == "sg":
            nodes = "gs"
        assert nodes in ("ds", "gs")
        assert trans in ("n1", "p1", "n2", "p2", "p3")

        dc = self.res

        if (trans == "n1"): # Vgs = Vds for n1
            return dc.nodes["xtop.n_gate"] - dc.nodes["xtop.vq1"]
        elif (
            (trans == "p2")
            or ((nodes == "gs") and (trans == "p1"))
        ):
            return dc.vdd - dc.nodes["xtop.p_gate"]
        elif ((nodes == "ds") and (trans == "p1")):
            return dc.vdd - dc.nodes["xtop.n_gate"]
        elif ((nodes == "ds") and (trans == "n2")):
            return dc.nodes["xtop.p_gate"] - dc.nodes["xtop.vq2r1"]
        elif ((nodes == "gs") and (trans == "n2")):
            return dc.nodes["xtop.n_gate"] - dc.nodes["xtop.vq2r1"]
        elif ((nodes == "ds") and (trans == "p3")):
            return dc.vdd - dc.vref
        else:
            raise RuntimeError("Internal error: unhandled transistor voltage")

    def V_pnp(self, *, branch: int):
        assert branch in (1, 2, 3)
        return self.res.nodes[f"xtop.vq{branch}"]

    def I(self, branch: int):
        """Return current a branch"""
        assert branch in (1, 2, 3)
        bg = self.bandgap
        return self.res.branches[f"v.xtop.vmp{branch}[0]_drain"]*bg.pmos_mult


class BandgapTempSweepResult(BandgapSimResult):
    def __init__(self, *, bandgap: Bandgap, res):
        super().__init__(bandgap=bandgap, res=res)

        self._temp: Optional[_np.ndarray] = None
        self._temp_range: Optional[Tuple[float, float]] = None
    @property
    def sweep(self):
        return self.res.sweep
    @property
    def temp(self) -> _np.ndarray:
        if self._temp is None:
            self._temp = _np.array(self.sweep)
        return self._temp
    @property
    def temp_range(self) -> Tuple[float, float]:
        if self._temp_range is None:
            temp = self.temp
            self._temp_range = (temp[0], temp[-1])
        return self._temp_range

    def plot_internals(self):
        """Plot the internals of the temperature sweep.
        This will generate 2x2 subplots.
        """
        temp = self.temp
        temp_range = self.temp_range

        # Vref
        ax = _plt.subplot(2, 2, 1)
        vref = _np.array(self.V_node(node="vref"))
        vref_avg = _np.mean(vref)
        _plt.plot(self.temp, vref)
        _plt.plot(self.temp_range, (0.99*vref_avg, 0.99*vref_avg), 'k--', label="-1%")
        _plt.plot(self.temp_range, (1.01*vref_avg, 1.01*vref_avg), 'k--', label='+1%')
        ax.set(xlim=self.temp_range)
        _plt.title("Vref")
        _plt.xlabel("temp [℃]")
        _plt.ylabel("V [V]")
        _plt.grid(True)

        # Currents
        ax = _plt.subplot(2, 2, 2)
        for i in range(3):
            branch = i + 1
            cur = _np.array(self.I(branch))
            _plt.plot(self.temp, cur, label=f"branch {branch}")
        axis = _plt.axis()
        ax.set(xlim=self.temp_range, ylim=(0.0, axis[3]))
        _plt.title("Branch currents")
        _plt.xlabel("temp [℃]")
        _plt.ylabel("I [A]")
        _plt.grid(True)
        _plt.legend()

        # Nodes
        ax = _plt.subplot(2, 2, 3)
        for node in (
            "n_gate", "p_gate",
            "vq1", "vq2", "vq2r1", "vq3", "vref",
        ):
            v = _np.array(self.V_node(node=node))
            _plt.plot(self.temp, v, label=node)
        axis = _plt.axis()
        ax.set(xlim=self.temp_range, ylim=(0.0, axis[3]))
        _plt.title("Node voltages")
        _plt.xlabel("temp [℃]")
        _plt.ylabel("V [V]")
        _plt.grid(True)
        _plt.legend()

        # V transistor
        ax = _plt.subplot(2, 2, 4)
        for curve, label in (
            (self.V_trans(nodes="sd", trans="p1"), "Vsd,p1"),
            (self.V_trans(nodes="sd", trans="n1"), "Vgs,n1=Vsd,n1"),
            (self.V_trans(nodes="sd", trans="p2"), "Vgs,p1=Vgs,p2=Vgs,p3=Vsd,p2"),
            (self.V_trans(nodes="sd", trans="n2"), "Vsd,n2"),
            (self.V_trans(nodes="gs", trans="n2"), "Vgs,n2"),
            (self.V_trans(nodes="sd", trans="p3"), "Vsd,p3"),
        ):
            _plt.plot(self.temp, curve, label=label)
        axis = _plt.axis()
        ax.set(xlim=self.temp_range, ylim=(0.0, axis[3]))
        _plt.title("Transistor biases")
        _plt.xlabel("temp [℃]")
        _plt.ylabel("V [V]")
        _plt.grid(True)
        _plt.legend()

    def plot_voltages(self, subplots=False):
        dc = self.res

        if not subplots:
            nodes = ("xtop.p_gate", "xtop.n_gate", "xtop.vq1", "xtop.vq2", "vref")
            for node in nodes:
                _plt.plot(dc.sweep, dc.nodes[node])
            _plt.legend(nodes)
            _plt.grid(True)
        else:
            nodes2 = (
                ("xtop.p_gate", "xtop.n_gate"),
                ("xtop.vq1", "xtop.vq2r1", "xtop.vq3"),
                ("vref",),
            )
            for i, nodes in enumerate(nodes2):
                _plt.subplot(2, 2, i + 1)
                for node in nodes:
                    _plt.plot(dc.sweep, dc.nodes[node], label=node)
                if i == 2:
                    vref_avg = _np.mean(_np.array(dc.nodes["vref"]))
                    left = float(dc.sweep[0])
                    right = float(dc.sweep[-1])
                _plt.legend()
                _plt.grid(True)
            _plt.subplot(2, 2, 4)
            for curve, label in (
                (self.V_trans(nodes="sd", trans="p1"), "Vsd,p1"),
                (self.V_trans(nodes="sd", trans="n1"), "Vgs,n1=Vsd,n1"),
                (self.V_trans(nodes="sd", trans="p2"), "Vgs,p1=Vgs,p2=Vgs,p3=Vsd,p2"),
                (self.V_trans(nodes="sd", trans="n2"), "Vsd,n2"),
                (self.V_trans(nodes="gs", trans="n2"), "Vgs,n2"),
                (self.V_trans(nodes="sd", trans="p3"), "Vsd,p3"),
            ):
                _plt.plot(dc.sweep, curve, label=label)
            _plt.legend()

    def plot_currents(self, subplots=False):
        dc = self.res

        for i in range(3):
            branch = i + 1
            cur = self.I(branch)
            label = f"i{branch}"
            if subplots:
                _plt.subplot(2, 2, i)
                _plt.title(label)
                _plt.grid(True)
                _plt.plot(dc.sweep, cur)
            else:
                _plt.plot(dc.sweep, cur, label=label)
        if not subplots:
            _plt.legend()
            _plt.grid(True)
            ax = _plt.gca()
            axis = ax.axis()
            ax.axis((axis[0], axis[1], 0.0, axis[3]))

    def __repr__(self) -> str:
        return ""


class BandgapTempSweepCornersResult:
    def __init__(self, *, results: Dict[CornerSpec, BandgapTempSweepResult]):
        self.results = results

    def plot_Vref(self):
        vref_avgs = []
        temp_range = None
        for corner, res in self.results.items():
            if temp_range is None:
                temp_range = res.temp_range
            label = corner if isinstance(corner, str) else "/".join(corner)
            vref = res.V_node(node="vref")
            vref_avgs.append(_np.mean(vref))
            _plt.plot(res.temp, vref, label=label)
        assert temp_range is not None
        vref_avg = _np.mean(vref_avgs)
        _plt.plot(temp_range, (0.99*vref_avg, 0.99*vref_avg), 'k--', label="-1%")
        _plt.plot(temp_range, (1.01*vref_avg, 1.01*vref_avg), 'k--', label='+1%')
        _plt.gca().set(xlim=temp_range)
        _plt.title("Vref through corners")
        _plt.xlabel("temp [℃]")
        _plt.ylabel("Vref [V]")
        _plt.grid(True)
        _plt.legend()


class BandgapTempSweepVddsResult:
    def __init__(self, *, results: Dict[float, BandgapTempSweepResult]):
        self.results = results

    def plot_Vref(self):
        vref_avgs = []
        temp_range = None
        for vdd, res in self.results.items():
            if temp_range is None:
                temp_range = res.temp_range
            label = f"Vdd={vdd}"
            vref = res.V_node(node="vref")
            vref_avgs.append(_np.mean(vref))
            _plt.plot(res.temp, vref, label=label)
        assert temp_range is not None
        vref_avg = _np.mean(vref_avgs)
        _plt.plot(temp_range, (0.99*vref_avg, 0.99*vref_avg), 'k--', label="-1%")
        _plt.plot(temp_range, (1.01*vref_avg, 1.01*vref_avg), 'k--', label='+1%')
        _plt.gca().set(xlim=temp_range)
        _plt.title("Vref Vdd sensitivity")
        _plt.xlabel("temp [℃]")
        _plt.ylabel("Vref [V]")
        _plt.grid(True)
        _plt.legend()


class BandgapCell(_cell.OnDemandCell):
    def __init__(self, *,
        name: str,
        tech: _tch.Technology, cktfab: _ckt.CircuitFactory, layoutfab: _lay.LayoutFactory,
        nmos: _prm.MOSFET, nmos_l: float, nmos_w: float, nmos_mult: int=1,
        pmos: _prm.MOSFET, pmos_l: float, pmos_w: float, pmos_mult: int=1,
        resistor: _prm.Resistor,
        r1_height: float, r1_legheight_max: Optional[float]=None,
        r2_height: float, r2_legheight_max: Optional[float]=None,
        pnp: _cell.Cell, pnp_mult:int=1, pnp_ratio: int,
    ):
        super().__init__(name=name, tech=tech, cktfab=cktfab, layoutfab=layoutfab)
        assert nmos_mult >= 1
        assert pmos_mult >= 1
        assert pnp_mult >= 1

        assert nmos.well is None
        assert pmos.well is not None

        self.nmos = nmos
        self.nmos_l = nmos_l
        self.nmos_w = nmos_w
        self.nmos_mult = nmos_mult

        self.pmos = pmos
        self.pmos_l = pmos_l
        self.pmos_w = pmos_w
        self.pmos_mult = pmos_mult

        if r1_legheight_max is None:
            r1_legheight_max = nmos_w
        r1_mult = round((r1_height + _geo.epsilon)//r1_legheight_max) + 1
        r1_legheight = tech.on_grid(r1_height/r1_mult)
        if r2_legheight_max is None:
            r2_legheight_max = nmos_w + pmos_w
        r2_mult = round((r2_height + _geo.epsilon)//r2_legheight_max) + 1
        r2_legheight = tech.on_grid(r2_height/r2_mult)

        self.resistor = resistor
        self.r1_height = r1_height
        self.r1_legheight_max = r1_legheight_max
        self.r1_mult = r1_mult
        self.r1_legheight = r1_legheight
        self.r2_height = r2_height
        self.r2_legheight_max = r2_legheight_max
        self.r2_mult = r2_mult
        self.r2_legheight = r2_legheight

        self.pnp = pnp
        self.pnp_mult = pnp_mult
        self.pnp_ratio = pnp_ratio

    def _create_circuit(self):
        nmos = self.nmos
        nmos_l = self.nmos_l
        nmos_w = self.nmos_w
        nmos_mult = self.nmos_mult

        pmos = self.pmos
        pmos_l = self.pmos_l
        pmos_w = self.pmos_w
        pmos_mult = self.pmos_mult

        resistor = self.resistor
        r1_legheight = self.r1_legheight
        r1_mult = self.r1_mult
        r2_legheight = self.r2_legheight
        r2_mult = self.r2_mult

        pnp = self.pnp
        pnp_mult = self.pnp_mult
        pnp_ratio = self.pnp_ratio

        ckt = self.new_circuit()

        n1s = tuple(
            ckt.instantiate(nmos, name=f"n1[{n}]", l=nmos_l, w=nmos_w)
            for n in range(nmos_mult)
        )
        n2s = tuple(
            ckt.instantiate(nmos, name=f"n2[{n}]", l=nmos_l, w=nmos_w)
            for n in range(nmos_mult)
        )
        ns = (*n1s, *n2s)

        p1s = tuple(
            ckt.instantiate(pmos, name=f"p1[{n}]", l=pmos_l, w=pmos_w)
            for n in range(pmos_mult)
        )
        p2s = tuple(
            ckt.instantiate(pmos, name=f"p2[{n}]", l=pmos_l, w=pmos_w)
            for n in range(pmos_mult)
        )
        p3s = tuple(
            ckt.instantiate(pmos, name=f"p3[{n}]", l=pmos_l, w=pmos_w)
            for n in range(pmos_mult)
        )
        ps = (*p1s, *p2s, *p3s)

        r1s = tuple(
            ckt.instantiate(resistor, name=f"r1[{n}]", height=r1_legheight)
            for n in range(r1_mult)
        )
        r2s = tuple(
            ckt.instantiate(resistor, name=f"r2[{n}]", height=r2_legheight)
            for n in range(r2_mult)
        )

        pnp1s = tuple(
            ckt.instantiate(pnp, name=f"pnp1[{n}]")
            for n in range(pnp_mult)
        )
        pnp2s = tuple(
            ckt.instantiate(pnp, name=f"pnp2[{n}]")
            for n in range(pnp_mult*pnp_ratio)
        )
        pnp3s = tuple(
            ckt.instantiate(pnp, name=f"pnp3[{n}]")
            for n in range(pnp_mult*pnp_ratio)
        )
        pnps = (*pnp1s, *pnp2s, *pnp3s)

        ckt.new_net(name="vdd", external=True, childports=(
            *(p.ports.sourcedrain2 for p in ps),
            *(p.ports.bulk for p in ps),
        ))
        ckt.new_net(name="vss", external=True, childports=(
            *(n.ports.bulk for n in ns),
            *(pnp.ports.base for pnp in pnps),
            *(pnp.ports.collector for pnp in pnps),
        ))
        ckt.new_net(name="vref", external=True, childports=(
            *(p3.ports.sourcedrain1 for p3 in p3s), r2s[0].ports.port1,
        ))

        ckt.new_net(name="p_gate", external=False, childports=(
            *(p.ports.gate for p in ps),
            *(p2.ports.sourcedrain1 for p2 in p2s),
            *(n2.ports.sourcedrain1 for n2 in n2s),
        ))
        ckt.new_net(name="n_gate", external=False, childports=(
            *(n.ports.gate for n in ns),
            *(p1.ports.sourcedrain1 for p1 in p1s),
            *(n1.ports.sourcedrain1 for n1 in n1s),
        ))
        ckt.new_net(name="vq1", external=False, childports=(
            *(n1.ports.sourcedrain2 for n1 in n1s),
            *(pnp1.ports.emitter for pnp1 in pnp1s),
        ))

        ckt.new_net(name="vq2r1", external=False, childports=(
            *(n2.ports.sourcedrain2 for n2 in n2s), r1s[0].ports.port1,
        ))
        for n in range(r1_mult - 1):
            ckt.new_net(name=f"r1conn[{n}]", external=False, childports=(
                r1s[n].ports.port2, r1s[n + 1].ports.port1,
            ))
        ckt.new_net(name="vq2", external=False, childports=(
            r1s[-1].ports.port2, *(pnp2.ports.emitter for pnp2 in pnp2s),
        ))

        for n in range(r2_mult - 1):
            ckt.new_net(name=f"r2conn[{n}]", external=False, childports=(
                r2s[n].ports.port2, r2s[n + 1].ports.port1,
            ))
        ckt.new_net(name="vq3", external=False, childports=(
            r2s[-1].ports.port2,
            *(pnp3.ports.emitter for pnp3 in pnp3s),
        ))

    def _create_layout(self):
        nmos_mult = self.nmos_mult
        pmos_mult = self.pmos_mult
        pnp_mult = self.pnp_mult
        pnp_ratio = self.pnp_ratio
        r1_mult = self.r1_mult
        r2_mult = self.r2_mult

        if nmos_mult > 1:
            raise NotImplementedError("BandgapCell layout for nmos_mult > 1")
        if pmos_mult > 1:
            raise NotImplementedError("BandgapCell layout for pmos_mult > 1")
        if pnp_mult > 1:
            raise NotImplementedError("BandgapCell layout for pnp_mult > 1")
        if pnp_ratio != 2:
            raise NotImplementedError("BandgapCell layout for pnp_mult != 2")

        difftap = cast(_prm.WaferWire, _prims.difftap)
        nsdm = cast(_prm.Implant, _prims.nsdm)
        psdm = cast(_prm.Implant, _prims.psdm)
        nwell = self.pmos.well
        assert nwell is not None
        pwell = self.nmos.well
        assert pwell is None
        oxide = self.nmos.gate.oxide
        assert self.pmos.gate.oxide == oxide
        poly = cast(_prm.GateWire, _prims.poly)
        licon = cast(_prm.Via, _prims.licon)
        li = cast(_prm.MetalWire, _prims.li)
        mcon = cast(_prm.Via, _prims.mcon)
        m1 = cast(_prm.MetalWire, _prims.m1)
        assert m1.pin is not None

        ckt = self.circuit
        nets = ckt.nets
        layouter = self.new_circuitlayouter()
        # Mirror the odd resistor around X axis
        rotations = {
            "p3[0]": _geo.Rotation.MY,
            **{
                f"r1[{n}]": _geo.Rotation.MX
                for n in range(0, r1_mult, 2)
            },
            **{
                f"r2[{n}]": _geo.Rotation.MX
                for n in range(0, r2_mult, 2)
            },
        }
        placer = _sky130lay.Sky130Layouter(layouter=layouter, rotations=rotations)

        # Put extra space for difftap in hvi minimum space
        # TODO: this needs to be handled inside Sky130Layouter
        sd_extra_space = 0.0 if oxide is None else 0.03

        # Short collector and base on the pnps
        shape = _geo.Ring(
            outer_bound=_geo.Rect.from_size(width=6.44, height=6.44),
            ring_width=1.175,
        )
        for name in (
            "pnp1[0]", "pnp2[0]", "pnp2[1]", "pnp3[0]", "pnp3[1]"
        ):
            info = placer.info_lookup[name]
            info.layout.add_shape(layer=li, net=nets.vss, shape=shape)

        # Transistor contacts
        placer.wire(
            wire_name="n1[0]_pad", net=nets.n_gate, wire=licon, rows=2,
            bottom=poly, bottom_width=self.nmos_l,
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.wire(
            wire_name="n1[0]_sd1", net=nets.n_gate, wire=licon, columns=2,
            bottom=difftap, bottom_implant=nsdm, bottom_oxide=oxide,
            bottom_height=self.nmos_w,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.wire(
            wire_name="n1[0]_sd2", net=nets.vq1, wire=licon, columns=2,
            bottom=difftap, bottom_implant=nsdm, bottom_oxide=oxide,
            bottom_height=self.nmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )

        placer.wire(
            wire_name="n2[0]_pad", net=nets.n_gate, wire=licon, rows=2,
            bottom=poly, bottom_width=self.nmos_l,
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.wire(
            wire_name="n2[0]_sd1", net=nets.p_gate, wire=licon, columns=2,
            bottom=difftap, bottom_implant=nsdm, bottom_oxide=oxide,
            bottom_height=self.nmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.wire(
            wire_name="n2[0]_sd2", net=nets.vq2r1, wire=licon, columns=2,
            bottom=difftap, bottom_implant=nsdm, bottom_oxide=oxide,
            bottom_height=self.nmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )

        placer.wire(
            wire_name="p1[0]_pad", net=nets.p_gate, wire=licon, rows=2,
            bottom=poly, bottom_width=(self.pmos_l - li.min_space),
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.wire(
            wire_name="p1[0]_sd1", net=nets.n_gate, wire=licon, columns=2,
            bottom=difftap, bottom_implant=psdm, bottom_oxide=oxide,
            bottom_well=nwell, well_net=nets.vdd,
            bottom_height=self.pmos_w,
            bottom_enclosure="tall", top_enclosure="tall",
        )
        placer.wire(
            wire_name="p1[0]_sd2", net=nets.vdd, wire=licon, columns=2,
            bottom=difftap, bottom_implant=psdm, bottom_oxide=oxide,
            bottom_well=nwell, well_net=nets.vdd,
            bottom_height=self.pmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.wire(
            wire_name="vddtap1", net=nets.vdd, wire=licon, columns=2,
            bottom=difftap, bottom_implant=nsdm, bottom_oxide=oxide,
            bottom_well=nwell, well_net=nets.vdd,
            bottom_height=self.pmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )

        placer.wire(
            wire_name="p2[0]_pad", net=nets.p_gate, wire=licon, rows=2,
            bottom=poly, bottom_width=self.pmos_l,
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.wire(
            wire_name="p2[0]_sd1", net=nets.p_gate, wire=licon, columns=2,
            bottom=difftap, bottom_implant=psdm, bottom_oxide=oxide,
            bottom_well=nwell, well_net=nets.vdd,
            bottom_height=self.pmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.wire(
            wire_name="p2[0]_sd2", net=nets.vdd, wire=licon, columns=2,
            bottom=difftap, bottom_implant=psdm, bottom_oxide=oxide,
            bottom_well=nwell, well_net=nets.vdd,
            bottom_height=self.pmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.wire(
            wire_name="vddtap2", net=nets.vdd, wire=licon, columns=2,
            bottom=difftap, bottom_implant=nsdm, bottom_oxide=oxide,
            bottom_well=nwell, well_net=nets.vdd,
            bottom_height=self.pmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )

        placer.wire(
            wire_name="p3[0]_pad", net=nets.p_gate, wire=licon, rows=2,
            bottom=poly, bottom_width=self.pmos_l,
            bottom_enclosure="wide", top_enclosure="wide",
        )
        placer.wire(
            wire_name="p3[0]_sd1", net=nets.vdd, wire=licon, columns=2,
            bottom=difftap, bottom_implant=psdm, bottom_oxide=oxide,
            bottom_well=nwell, well_net=nets.vdd,
            bottom_height=self.pmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )
        placer.wire(
            wire_name="p3[0]_sd2", net=nets.vref, wire=licon, columns=2,
            bottom=difftap, bottom_implant=psdm, bottom_oxide=oxide,
            bottom_well=nwell, well_net=nets.vdd,
            bottom_height=self.pmos_w,
            bottom_enclosure="tall", top_enclosure="wide",
        )

        # Add psdm on pmos pad
        # TODO: should be able to be done by adding bottom implamt layer to the
        # wire
        for pad_name in ("p1[0]_pad", "p2[0]_pad", "p3[0]_pad"):
            info = placer.info_lookup[pad_name]
            bb = info.bb(mask=poly.mask)
            assert bb is not None
            info.layout.add_shape(layer=psdm, net=None, shape=bb)

        # n1[0] placement
        placer.place_at_left(name="n1[0]_sd1")
        placer.place_to_the_right(
                name="n1[0]", ref_names="n1[0]_sd1",
                ignore_masks=difftap.mask,
        )
        placer.place_to_the_right(
            name="n1[0]_sd2", ref_names="n1[0]",
            ignore_masks=difftap.mask,
        )
        placer.place_at_bottom(name="n1[0]")
        placer.place_above(
            name="n1[0]_pad", ref_names="n1[0]",
            ignore_masks=poly.mask,
        )
        placer.center_y(
            name="n1[0]_sd1", ref_name="n1[0]", prim=difftap,
        )
        placer.center_y(
            name="n1[0]_sd2", ref_name="n1[0]", prim=difftap,
        )
        placer.center_x(
            name="n1[0]_pad", ref_name="n1[0]", prim=poly,
        )

        placer.connect(
            name1="n1[0]_pad", name2="n1[0]", prim=poly, net=nets.n_gate,
        )

        # n2[0] placement
        placer.place_to_the_right(
            name="n2[0]_sd1", ref_names=("n1[0]_sd2", "vddtap1"),
            extra_space=sd_extra_space,
        )
        placer.place_to_the_right(
            name="n2[0]", ref_names="n2[0]_sd1",
            ignore_masks=difftap.mask,
        )
        placer.place_to_the_right(
            name="n2[0]_sd2", ref_names="n2[0]",
            ignore_masks=difftap.mask,
        )
        placer.place_at_bottom(name="n2[0]")
        placer.place_above(
            name="n2[0]_pad", ref_names="n2[0]",
            ignore_masks=poly.mask,
        )
        placer.center_y(
            name="n2[0]_sd1", ref_name="n2[0]", prim=difftap,
        )
        placer.center_y(
            name="n2[0]_sd2", ref_name="n2[0]", prim=difftap,
        )
        placer.center_x(
            name="n2[0]_pad", ref_name="n2[0]", prim=poly,
        )

        placer.connect(
            name1="n2[0]_pad", name2="n2[0]", prim=poly, net=nets.n_gate,
        )

        # p1[0] placement
        placer.align_left(name="p1[0]_sd1", ref_name="n1[0]_sd1", prim=li)
        placer.place_to_the_right(
            name="p1[0]", ref_names="p1[0]_sd1",
            ignore_masks=(difftap.mask, nwell.mask),
        )
        placer.place_to_the_right(
            name="p1[0]_sd2", ref_names="p1[0]",
            ignore_masks=(difftap.mask, nwell.mask),
        )
        placer.place_to_the_right(
            name="vddtap1", ref_names="p1[0]_sd2", extra_space=sd_extra_space,
            ignore_masks=(nwell.mask, li.mask),
        )
        placer.place_above(name="p1[0]_pad", ref_names="n1[0]_pad")
        placer.place_above(
            name="p1[0]", ref_names="p1[0]_pad",
            ignore_masks=poly.mask,
        )
        placer.center_y(
            name="p1[0]_sd1", ref_name="p1[0]", prim=difftap,
        )
        placer.center_y(
            name="p1[0]_sd2", ref_name="p1[0]", prim=difftap,
        )
        placer.center_y(
            name="vddtap1", ref_name="p1[0]", prim=difftap,
        )
        placer.align_right(
            name="p1[0]_pad", ref_name="p1[0]", prim=poly,
        )

        placer.connect(
            name1="p1[0]_pad", name2="p1[0]", prim=poly, net=nets.p_gate,
        )
        placer.connect(name1="p1[0]_sd2", name2="vddtap1", prim=li, net=nets.vdd)

        # p2[0] placement
        placer.align_left(name="p2[0]_sd1", ref_name="n2[0]_sd1", prim=li)
        placer.place_to_the_right(
            name="p2[0]", ref_names="p2[0]_sd1",
            ignore_masks=(difftap.mask, nwell.mask),
        )
        placer.place_to_the_right(
            name="p2[0]_sd2", ref_names="p2[0]",
            ignore_masks=(difftap.mask, nwell.mask),
        )
        placer.place_to_the_right(
            name="vddtap2", ref_names="p2[0]_sd2", extra_space=sd_extra_space,
            ignore_masks=(nwell.mask, li.mask),
        )
        placer.place_above(name="p2[0]_pad", ref_names="n2[0]_pad")
        placer.place_above(
            name="p2[0]", ref_names="p2[0]_pad",
            ignore_masks=poly.mask,
        )
        placer.center_y(
            name="p2[0]_sd1", ref_name="p2[0]", prim=difftap,
        )
        placer.center_y(
            name="p2[0]_sd2", ref_name="p2[0]", prim=difftap,
        )
        placer.center_y(
            name="vddtap2", ref_name="p2[0]", prim=difftap,
        )
        placer.center_x(
            name="p2[0]_pad", ref_name="p2[0]", prim=poly,
        )

        placer.connect(
            name1="p2[0]_pad", name2="p2[0]", prim=poly, net=nets.p_gate,
        )
        placer.connect(name1="p2[0]_sd2", name2="vddtap2", prim=li, net=nets.vdd)

        # p3[0] placement
        placer.place_to_the_right(
            name="p3[0]_sd1", ref_names="vddtap2", extra_space=sd_extra_space,
            ignore_masks=(nwell.mask),
        )
        placer.place_to_the_right(
            name="p3[0]", ref_names="p3[0]_sd1",
            ignore_masks=(difftap.mask, nwell.mask),
        )
        placer.place_to_the_right(
            name="p3[0]_sd2", ref_names="p3[0]",
            ignore_masks=(difftap.mask, nwell.mask),
        )
        placer.place_above(name="p3[0]_pad", ref_names="n2[0]_pad")
        placer.place_above(
            name="p3[0]", ref_names="p3[0]_pad",
            ignore_masks=poly.mask,
        )
        placer.center_y(
            name="p3[0]_sd1", ref_name="p3[0]", prim=difftap,
        )
        placer.center_y(
            name="p3[0]_sd2", ref_name="p3[0]", prim=difftap,
        )
        placer.center_x(
            name="p3[0]_pad", ref_name="p3[0]", prim=poly,
        )

        placer.connect(
            name1="p3[0]_pad", name2="p3[0]", prim=poly, net=nets.p_gate,
        )
        placer.connect(name1="vddtap2", name2="p3[0]_sd1", prim=li, net=nets.vdd)

        # n_gate
        net = nets.n_gate
        placer.connect(
            name1="n1[0]_pad", name2="n2[0]_pad", prim=li, net=net,
        )
        placer.connect(
            name1="n1[0]_sd1", name2="n1[0]_pad", prim=li, net=net,
        )
        placer.connect(
            name1="n1[0]_sd1", name2="p1[0]_sd1", prim=li, net=net,
        )

        # p_gate
        net = nets.p_gate

        info = placer.info_lookup["n2[0]_sd1"]
        bb = info.bb(mask=li.mask)
        assert bb is not None
        li_width = bb.width

        placer.connect(
            name1="p1[0]_pad", name2="p2[0]_pad", prim=li, net=net,
        )
        placer.connect(
            name1="p2[0]_pad", name2="p3[0]_pad", prim=li, net=net,
        )

        placer.wire(
            wire_name="n2[0]_pgate", net=net, wire=mcon,
            rows=4, bottom_width=li_width,
        )
        placer.center_x(
            name="n2[0]_pgate", ref_name="n2[0]_sd1", prim=li,
        )
        placer.align_top(
            name="n2[0]_pgate", ref_name="n2[0]_sd1", prim=li,
        )
        placer.wire(
            wire_name="p2[0]_pgate", net=net, wire=mcon,
            rows=4, bottom_width=li_width,
        )
        placer.center_x(
            name="p2[0]_pgate", ref_name="p2[0]_sd1", prim=li,
        )
        placer.align_bottom(
            name="p2[0]_pgate", ref_name="p2[0]_pad", prim=li,
        )
        placer.connect(
            name1="p2[0]_pgate", name2="p2[0]_sd1", prim=li, net=net,
        )
        placer.connect(
            name1="n2[0]_pgate", name2="p2[0]_pgate", prim=m1, net=net,
        )

        # r1s
        for n in range(r1_mult):
            placer.place_at_bottom(name=f"r1[{n}]")
            if n == 0:
                placer.place_to_the_right(
                    name=f"r1[{n}]", ref_names="n2[0]",
                    use_boundary=True, extra_space=0.5,
                )
            else:
                placer.place_to_the_right(
                    name=f"r1[{n}]", ref_names=f"r1[{n - 1}]",
                )

        # r1conn
        for n in range(r1_mult - 1):
            placer.connect(
                name1=f"r1[{n}]", name2=f"r1[{n + 1}]", prim=li, net=nets[f"r1conn[{n}]"],
            )

        # pnps
        for name in ("pnp1[0]", "pnp2[0]", "pnp2[1]", "pnp3[0]", "pnp3[1]"):
            placer.place_to_the_right(
                name=name, ref_names=f"r1[{r1_mult - 1}]", extra_space=0.5,
            )
        placer.place_at_bottom(name="pnp3[0]")
        placer.place_above(name="pnp2[0]", ref_names="pnp3[0]")
        placer.place_above(name="pnp1[0]", ref_names="pnp2[0]")
        placer.place_above(name="pnp2[1]", ref_names="pnp1[0]")
        placer.place_above(name="pnp3[1]", ref_names="pnp2[1]")

        placer.connect(name1="pnp3[0]", name2="pnp2[0]", prim=li, net=nets.vss)
        placer.connect(name1="pnp2[0]", name2="pnp1[0]", prim=li, net=nets.vss)
        placer.connect(name1="pnp1[0]", name2="pnp2[1]", prim=li, net=nets.vss)
        placer.connect(name1="pnp2[1]", name2="pnp3[1]", prim=li, net=nets.vss)

        # vss tap
        net = nets.vss

        info = placer.info_lookup["pnp3[1]"]
        bb = info.bb(mask=li.mask, net=net)
        assert bb is not None
        li_width = bb.width

        placer.wire(
            wire_name="vsstap", net=net, wire=licon,
            rows=5, top_width=li_width,
            bottom=difftap, bottom_implant=psdm,
        )

        placer.center_x(
            name="vsstap", ref_name="pnp3[1]", prim=li, net=net,
        )
        placer.place_above(name="vsstap", ref_names="pnp3[1]")
        placer.connect(name1="vsstap", name2="pnp3[1]", prim=li, net=net)

        placer.wire(
            wire_name="vss_m1pin", net=net, wire=mcon,
            rows=5, top_width=li_width,
        )
        placer.center_x(
            name="vss_m1pin", ref_name="vsstap", prim=li, net=net,
        )
        placer.align_bottom(
            name="vss_m1pin", ref_name="vsstap", prim=li, net=net,
        )

        placer.extend(
            name="vsstap", ref_name="pnp3[1]", prim=psdm,
        )

        # r2s
        for n in range(r2_mult):
            placer.place_at_bottom(name=f"r2[{n}]")
            placer.place_to_the_right(
                name=f"r2[{n}]",
                ref_names=(f"r2[{n - 1}]" if n > 0 else (
                    "pnp1[0]", "p3[0]_sd2"
                )),
                use_boundary=True,
            )

        # r2conn
        for n in range(r2_mult - 1):
            placer.connect(
                name1=f"r2[{n}]", name2=f"r2[{n + 1}]", prim=li, net=nets[f"r2conn[{n}]"],
            )

        # vq1
        net = nets.vq1
        placer.wire(wire_name="n[0]_vq1", net=net, wire=mcon, rows=4)
        placer.align_right(
            name="n[0]_vq1", ref_name="n1[0]_sd2", prim=li,
        )
        placer.center_y(
            name="n[0]_vq1", ref_name="pnp1[0]", prim=m1, net=net,
        )
        placer.connect(name1="n[0]_vq1", name2="pnp1[0]", prim=m1, net=net)

        # vq2
        net = nets.vq2

        info = placer.info_lookup["pnp2[0]"]
        bb = info.bb(mask=m1.mask, net=net)
        assert bb is not None
        m1_height = bb.height

        placer.wire(
            wire_name="pnp2[0]_vq2r1", net=net, wire=mcon,
            columns=2, top_height=m1_height,
        )
        placer.wire(
            wire_name="pnp2[1]_vq2r1", net=net, wire=mcon,
            columns=2, top_height=m1_height,
        )

        r1_name = f"r1[{r1_mult - 1}]"
        placer.align_left(
            name="pnp2[0]_vq2r1", ref_name=r1_name, prim=li, net=net,
        )
        placer.center_y(
            name="pnp2[0]_vq2r1", ref_name="pnp2[0]", prim=m1, net=net,
        )
        placer.align_left(
            name="pnp2[1]_vq2r1", ref_name=r1_name, prim=li, net=net,
        )
        placer.center_y(
            name="pnp2[1]_vq2r1", ref_name=f"pnp2[1]", prim=m1, net=net,
        )

        placer.connect(
            name1=r1_name, name2="pnp2[0]_vq2r1", prim=li, net=net,
        )
        placer.connect(
            name1=r1_name, name2="pnp2[1]_vq2r1", prim=li, net=net,
        )
        placer.connect(
            name1="pnp2[0]", name2="pnp2[0]_vq2r1", prim=m1, net=net,
        )
        placer.connect(
            name1="pnp2[1]", name2="pnp2[1]_vq2r1", prim=m1, net=net,
        )

        # vq2r1
        net = nets.vq2r1
        placer.connect(
            name1="n2[0]_sd2", name2="r1[0]", prim=li, net=net,
        )

        # vq3
        net = nets.vq3

        placer.wire(
            wire_name="r2_vq3", net=net, wire=mcon, rows=4,
        )
        placer.wire(
            wire_name="pnp3[0]_vq3", net=net, wire=m1, height=m1_height,
        )
        placer.wire(
            wire_name="pnp3[1]_vq3", net=net, wire=m1, height=m1_height,
        )

        placer.align_left(
            name="r2_vq3", ref_name=f"r2[{r2_mult - 1}]", prim=li, net=net,
        )
        # Vertical alignment dependent if contact is at bottom or top
        # e.g. if r2_mult is odd or even.
        if (r2_mult%2) == 1:
            placer.align_bottom(
                name="r2_vq3", ref_name=f"r2[{r2_mult - 1}]", prim=li, net=net,
            )
        else:
            placer.align_top(
                name="r2_vq3", ref_name=f"r2[{r2_mult - 1}]", prim=li, net=net,
            )
        placer.align_left(
            name="pnp3[0]_vq3", ref_name="r2_vq3", prim=m1,
        )
        placer.center_y(
            name="pnp3[0]_vq3", ref_name="pnp3[0]", prim=m1, net=net,
        )
        placer.align_left(
            name="pnp3[1]_vq3", ref_name="r2_vq3", prim=m1,
        )
        placer.center_y(
            name="pnp3[1]_vq3", ref_name="pnp3[1]", prim=m1, net=net,
        )

        placer.connect(
            name1="pnp3[0]_vq3", name2="pnp3[0]", prim=m1, net=net,
        )
        placer.connect(
            name1="pnp3[0]_vq3", name2="r2_vq3", prim=m1, net=net,
        )
        placer.connect(
            name1="pnp3[1]_vq3", name2="pnp3[1]", prim=m1, net=net,
        )
        placer.connect(
            name1="pnp3[1]_vq3", name2="r2_vq3", prim=m1, net=net,
        )

        # vref
        net = nets.vref
        placer.connect(
            name1="p3[0]_sd2", name2="r2[0]", prim=li, net=net,
        )

        placer.wire(
            wire_name="vref_m1pin", net=net, wire=mcon, rows=8, columns=8,
        )

        if self.nmos_l > self.pmos_l:
            placer.align_left(
                name="vref_m1pin", ref_name="p3[0]_sd2", prim=li, net=net,
            )
        else:
            placer.align_right(
                name="vref_m1pin", ref_name="r2[0]", prim=li, net=net,
            )
        placer.align_top(
            name="vref_m1pin", ref_name="r2[0]", prim=li, net=net,
        )

        # vdd conn
        net = nets.vdd
        placer.wire(
            wire_name="p1[0]_mconvdd", net=net, wire=mcon, rows=4, columns=2,
        )
        placer.wire(
            wire_name="p23[0]_mconvdd", net=net, wire=mcon, rows=4, columns=2,
        )

        placer.align_right(
            name="p1[0]_mconvdd", ref_name="vddtap1", prim=li,
        )
        placer.align_top(
            name="p1[0]_mconvdd", ref_name="vddtap1", prim=li,
        )
        placer.align_left(
            name="p23[0]_mconvdd", ref_name="p2[0]_sd2", prim=li,
        )
        placer.align_top(
            name="p23[0]_mconvdd", ref_name="vddtap2", prim=li,
        )

        placer.connect(
            name1="p1[0]_mconvdd", name2="p23[0]_mconvdd", prim=m1, net=net,
        )

        # Fill minimum space
        if oxide is not None:
            placer.fill(
                names=(
                    "n1[0]", "n1[0]_pad", "n1[0]_sd1", "n1[0]_sd2",
                    "n2[0]", "n2[0]_pad", "n2[0]_sd1", "n2[0]_sd2",
                    "p1[0]", "p1[0]_pad", "p1[0]_sd1", "p1[0]_sd2",
                    "p2[0]", "p2[0]_pad", "p2[0]_sd1", "p2[0]_sd2",
                ),
                prim=oxide,
            )
            placer.fill(
                names=(
                    "p1[0]", "p1[0]_pad", "p1[0]_sd1", "p1[0]_sd2",
                    "p2[0]", "p2[0]_pad", "p2[0]_sd1", "p2[0]_sd2",
                    "p3[0]", "p3[0]_pad", "p3[0]_sd1", "p3[0]_sd2",
                ),
                prim=oxide,
            )
        placer.fill(
            names=(
                "n1[0]", "n1[0]_pad", "n1[0]_sd1", "n1[0]_sd2",
                "n2[0]", "n2[0]_pad", "n2[0]_sd1", "n2[0]_sd2",
            ),
            prim=nsdm,
        )
        placer.fill(
            names=(
                "p1[0]", "p1[0]_pad", "p1[0]_sd1", "p1[0]_sd2",
            ),
            prim=psdm,
        )
        placer.fill(
            names=(
                "p2[0]", "p2[0]_pad", "p2[0]_sd1", "p2[0]_sd2",
            ),
            prim=psdm,
        )
        placer.fill(
            names=(
                "p3[0]", "p3[0]_pad", "p3[0]_sd1", "p3[0]_sd2",
            ),
            prim=psdm,
        )
        placer.fill(
            names=(
                "p1[0]", "p1[0]_pad", "p1[0]_sd1", "p1[0]_sd2", "vddtap1",
                "p2[0]", "p2[0]_pad", "p2[0]_sd1", "p2[0]_sd2", "vddtap2",
                "p3[0]", "p3[0]_pad", "p3[0]_sd1", "p3[0]_sd2",
            ),
            prim=nwell, net=nets.vdd,
        )

        if not placer.execute():
            print("Not all aligns have completed")

        # Manually draw the pin layers
        layout = layouter.layout
        for net in (nets.vdd, nets.vss, nets.vref):
            bb = layout.bounds(mask=m1.mask, net=net)
            layouter.add_wire(net=net, wire=m1, pin=m1.pin, shape=bb)

