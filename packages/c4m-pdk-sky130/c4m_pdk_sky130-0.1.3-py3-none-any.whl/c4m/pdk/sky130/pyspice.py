# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
from pathlib import Path

from pdkmaster.io.spice import SpicePrimsParamSpec, PySpiceFactory

from .pdkmaster import tech as _tech

__all__ = ["prims_spiceparams", "pyspicefab", "pyspice_factory"]


pyspicefab = pyspice_factory = None
_file = Path(__file__)
_libfile = _file.parent.joinpath("models", "C4M.Sky130_all_lib.spice")
_prims = _tech.primitives
prims_spiceparams = SpicePrimsParamSpec()
for dev_name, params in (
    # sheet resistances are estimated from the model
    ("ndiff_res", dict(sheetres=120.0, model="sky130_fd_pr__res_generic_nd")),
    ("pdiff_res", dict(sheetres=197.0, model="sky130_fd_pr__res_generic_pd")),
    ("poly_res", dict(sheetres=48.2, model="sky130_fd_pr__res_generic_po")),
    ("MIM_m3_capm", dict(model="sky130_fd_pr__cap_mim_m3_1")),
    ("MIM_m4_cap2m", dict(model="sky130_fd_pr__cap_mim_m3_2")),
    ("ndiode", {}),
    ("pdiode", {}),
    ("nfet_01v8", dict(model="sky130_fd_pr__nfet_01v8__model")),
    ("nfet_01v8_sc", dict(model="sky130_fd_pr__nfet_01v8__model")),
    ("pfet_01v8", dict(model="sky130_fd_pr__pfet_01v8__model")),
    ("nfet_01v8_lvt", dict(model="sky130_fd_pr__nfet_01v8_lvt__model")),
    ("pfet_01v8_lvt", dict(model="sky130_fd_pr__pfet_01v8_lvt__model")),
    ("pfet_01v8_hvt", dict(model="sky130_fd_pr__pfet_01v8_hvt__model")),
    ("nfet_g5v0d10v5", dict(model="sky130_fd_pr__nfet_g5v0d10v5__model")),
    ("pfet_g5v0d10v5", dict(model="sky130_fd_pr__pfet_g5v0d10v5__model")),
    ("npn_05v5_w1u00l1u00", dict(model="sky130_fd_pr__npn_05v5_W1p00L1p00")),
    ("npn_05v5_w1u00l2u00", dict(model="sky130_fd_pr__npn_05v5_W1p00L2p00")),
    ("pnp_05v5_w0u68l0u68", dict(model="sky130_fd_pr__pnp_05v5_W0p68L0p68")),
    ("pnp_05v5_w3u40l3u40", dict(model="sky130_fd_pr__pnp_05v5_W3p40L3p40")),
):
    prims_spiceparams.add_device_params(prim=_prims[dev_name], **params)
pyspicefab = pyspice_factory = PySpiceFactory(
    libfile=str(_libfile),
    corners=(
        "logic_tt", "logic_sf", "logic_ff", "logic_ss", "logic_fs",
        "io_tt", "io_sf", "io_ff", "io_ss", "io_fs",
        "diode_tt", "diode_sf", "diode_ff", "diode_ss", "diode_fs",
        "pnp_t", "pnp_f", "pnp_s",
        "npn_t", "npn_f", "npn_s",
        "rc_tt", "rc_ll", "rc_hh", "rc_lh", "rc_hl",
    ),
    conflicts={
        "logic_tt": ("logic_sf", "logic_ff", "logic_ss", "logic_fs"),
        "logic_sf": ("logic_tt", "logic_ff", "logic_ss", "logic_fs"),
        "logic_ff": ("logic_tt", "logic_sf", "logic_ss", "logic_fs"),
        "logic_ss": ("logic_tt", "logic_sf", "logic_ff", "logic_fs"),
        "logic_fs": ("logic_tt", "logic_sf", "logic_ff", "logic_ss"),
        "io_tt": ("io_sf", "io_ff", "io_ss", "io_fs"),
        "io_sf": ("io_tt", "io_ff", "io_ss", "io_fs"),
        "io_ff": ("io_tt", "io_sf", "io_ss", "io_fs"),
        "io_ss": ("io_tt", "io_sf", "io_ff", "io_fs"),
        "io_fs": ("io_tt", "io_sf", "io_ff", "io_ss"),
        "diode_tt": ("diode_sf", "diode_ff", "diode_ss", "diode_fs"),
        "diode_sf": ("diode_tt", "diode_ff", "diode_ss", "diode_fs"),
        "diode_ff": ("diode_tt", "diode_sf", "diode_ss", "diode_fs"),
        "diode_ss": ("diode_tt", "diode_sf", "diode_ff", "diode_fs"),
        "diode_fs": ("diode_tt", "diode_sf", "diode_ff", "diode_ss"),
        "npn_t": ("npn_f", "npn_s"),
        "npn_f": ("npn_t", "npn_s"),
        "npn_s": ("npn_t", "npn_f"),
        "pnp_t": ("pnp_f", "pnp_s"),
        "pnp_f": ("pnp_t", "pnp_s"),
        "pnp_s": ("pnp_t", "pnp_f"),
        "rc_tt": ("rc_lh", "rc_hh", "rc_ll", "rc_hl"),
        "rc_lh": ("rc_tt", "rc_hh", "rc_ll", "rc_hl"),
        "rc_hh": ("rc_tt", "rc_lh", "rc_ll", "rc_hl"),
        "rc_ll": ("rc_tt", "rc_lh", "rc_hh", "rc_hl"),
        "rc_hl": ("rc_tt", "rc_lh", "rc_hh", "rc_ll"),
    },
    prims_params=prims_spiceparams,
)
