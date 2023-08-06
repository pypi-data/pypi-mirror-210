# SPDX-License-Identifier: GPL-2.0-or-later OR AGPL-3.0-or-later OR CERN-OHL-S-2.0+
"""This contains layout generation support classes. Planning is to upstream this
code to PDKMaster after making it more generic. After that this module should
be able to be removed.
So there is no backward compatibility guarantee for code in this module.
"""
import abc
from itertools import product
from typing import (
    List, Tuple, Dict,
    Iterable, Generator,
    Type, Optional, Union,
    overload, cast,
)

from pdkmaster.typing import MultiT, cast_MultiT
from pdkmaster.technology import (
    geometry as _geo, mask as _msk, primitive as _prm, technology_ as _tch,
)
from pdkmaster.design import circuit as _ckt, layout as _lay


__all__ = ["Sky130Layouter"]


class _Constraint(abc.ABC):
    def __init__(self, *, infos: Tuple["Sky130Layouter._PlaceInfo", ...]) -> None:
        self.infos = infos

    @abc.abstractmethod
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        ...


class _RefConstraint(_Constraint):
    def __init__(self, *,
        info: "Sky130Layouter._PlaceInfo", ref_infos: Tuple["Sky130Layouter._PlaceInfo", ...],
    ) -> None:
        assert len(ref_infos) > 0
        super().__init__(infos=(info, *ref_infos))
        self.infos: Tuple["Sky130Layouter._PlaceInfo", "Sky130Layouter._PlaceInfo"]

    @property
    def info(self) -> "Sky130Layouter._PlaceInfo":
        return self.infos[0]
    @property
    def ref_infos(self) -> Tuple["Sky130Layouter._PlaceInfo", ...]:
        return self.infos[1:]


class _PlaceConstraint(_RefConstraint):
    def __init__(self, *,
        info: "Sky130Layouter._PlaceInfo", ref_infos: Tuple["Sky130Layouter._PlaceInfo", ...],
        ignore_masks: MultiT[_msk.DesignMask]=tuple(), extra_space: float=0.0,
        use_boundary: Optional[bool]=None, boundary_only: bool,
    ) -> None:
        if boundary_only:
            if use_boundary is None:
                use_boundary = True
            elif not use_boundary:
                raise ValueError(
                    "use_boundary can't be 'False' if boundary_only is 'True'"
                )
        super().__init__(info=info, ref_infos=ref_infos)
        self.ignore_masks: Tuple[_msk.DesignMask, ...] = cast_MultiT(ignore_masks)
        self.extra_space = extra_space
        self.use_boundary = use_boundary
        self.boundary_only = boundary_only

    def _get_bbs(self, *,
        placer: "Sky130Layouter", ref_info: "Sky130Layouter._PlaceInfo",
    ) -> Generator[Tuple[_geo.Rect, _geo.Rect, float], None, None]:
        info = self.info

        tech = placer.layouter.tech

        # Handle layout boundary.
        if self.use_boundary is None:
            # If use_boundary is None take into account boundary if one of the
            # two objects has a boundary.
            # If the other layout does not have a boundary the layout bounding box will be
            # used.
            bdry = info.layout.boundary
            ref_bdry = ref_info.layout.boundary
            if (bdry is not None) and (ref_bdry is None):
                ref_bdry = ref_info.bb()
            if (bdry is None) and (ref_bdry is not None):
                bdry = info.bb()
        elif self.use_boundary:
            # If use_boundary is True always layout boundary box is used if the layout
            # has no boundary
            bdry = info.layout.boundary
            if bdry is None:
                bdry = info.bb()
            ref_bdry = ref_info.layout.boundary
            if ref_bdry is None:
                ref_bdry = ref_info.bb()
        else:
            assert not self.use_boundary
            bdry = None
            ref_bdry = None
        if (bdry is not None) and (ref_bdry is not None):
            assert isinstance(bdry, _geo.Rect)
            assert isinstance(ref_bdry, _geo.Rect)
            yield (bdry, ref_bdry, self.extra_space)
        if self.boundary_only:
            return

        # All minimum space rules for the _Conductor types.
        # Non-conductor primitives are assumed that the minimum space can be filled
        # up.
        for prim in tech.primitives.__iter_type__((
            _prm.WidthSpaceConductorT, _prm.Via,
        )):
            # print(f"prim: {prim}, align: {self}")
            if prim.mask in self.ignore_masks:
                # print("Ignored")
                continue
            rect = info.bb(mask=prim.mask)
            ref_rect = ref_info.bb(mask=prim.mask)
            if (rect is not None) and (ref_rect is not None):
                # print(f"Yield {(rect, ref_rect, prim.min_space)}")
                yield (rect, ref_rect, prim.min_space + self.extra_space)

        # Handle min_substrate_enclosure of WaferWire; it's implemented as minimum
        # space to the wells.
        for prim in tech.primitives.__iter_type__(_prm.WaferWire):
            if prim.mask in self.ignore_masks:
                continue
            prim_bb = info.bb(mask=prim.mask)
            prim_ref_bb = ref_info.bb(mask=prim.mask)
            if (prim_bb is None) and (prim_ref_bb is None):
                continue
            if prim.min_substrate_enclosure is not None:
                space = prim.min_substrate_enclosure.max() + self.extra_space
                for well in prim.well:
                    if well.mask in self.ignore_masks:
                        continue
                    if prim_ref_bb is not None:
                        well_bb = info.bb(mask=well.mask)
                        if well_bb is not None:
                            yield (well_bb, prim_ref_bb, space)
                    if prim_bb is not None:
                        well_ref_bb = ref_info.bb(mask=well.mask)
                        if well_ref_bb is not None:
                            yield (prim_bb, well_ref_bb, space)

        # Handle MOSFET contact gate spacing
        if (
            isinstance(info, Sky130Layouter._PlaceInstInfo)
            and isinstance(info.inst, _ckt._PrimitiveInstance)
            and isinstance(info.inst.prim, _prm.MOSFET)
            and (info.inst.prim.computed.contact is not None)
        ):
            mosfet = info.inst.prim
            active = mosfet.gate.active
            poly = mosfet.gate.poly
            space = mosfet.computed.min_contactgate_space + self.extra_space
            if (
                isinstance(ref_info, Sky130Layouter._PlaceWireInfo)
                and isinstance(ref_info.wire, _prm.Via)
                and ("bottom" in ref_info.wire_params)
            ):
                bottom = ref_info.wire_params["bottom"]
                via = ref_info.wire
                ref_bb = ref_info.bb(mask=via.mask)
                if bottom == active:
                    bb = info.bb(mask=poly.mask)
                elif bottom == poly:
                    bb = info.bb(mask=active.mask)
                else:
                    bb = None
                if (bb is not None) and (ref_bb is not None):
                    yield (bb, ref_bb, space)
        elif (
            isinstance(ref_info, Sky130Layouter._PlaceInstInfo)
            and isinstance(ref_info.inst, _ckt._PrimitiveInstance)
            and isinstance(ref_info.inst.prim, _prm.MOSFET)
            and (ref_info.inst.prim.computed.contact is not None)
        ):
            mosfet = ref_info.inst.prim
            active = mosfet.gate.active
            poly = mosfet.gate.poly
            space = mosfet.computed.min_contactgate_space + self.extra_space
            if (
                isinstance(info, Sky130Layouter._PlaceWireInfo)
                and isinstance(info.wire, _prm.Via)
                and ("bottom" in info.wire_params)
            ):
                bottom = info.wire_params["bottom"]
                via = info.wire
                bb = info.bb(mask=via.mask)
                if bottom == active:
                    ref_bb = ref_info.bb(mask=poly.mask)
                elif bottom == poly:
                    ref_bb = ref_info.bb(mask=active.mask)
                else:
                    ref_bb = None
                if (bb is not None) and (ref_bb is not None):
                    yield (bb, ref_bb, space)

        # Handle extra spacing rules
        # TODO: Handle derived masks like active.in_(implant)
        for prim in tech.primitives.__iter_type__(_prm.Spacing):
            space = prim.min_space + self.extra_space
            prims1 = cast(
                Iterable[_prm.ConductorT],
                filter(lambda p: isinstance(p, _prm.ConductorT), prim.primitives1),
            )
            if prim.primitives2 is not None:
                prims2 = cast(
                    Iterable[_prm.ConductorT],
                    filter(lambda p: isinstance(p, _prm.ConductorT), prim.primitives2),
                )
                for prim1, prim2 in product(prims1, prims2):
                    if (
                        (prim1.mask in self.ignore_masks)
                        or (prim2.mask in self.ignore_masks)
                    ):
                        continue
                    bb1 = info.bb(mask=prim1.mask)
                    ref_bb1 = ref_info.bb(mask=prim1.mask)

                    bb2 = info.bb(mask=prim2.mask)
                    ref_bb2 = ref_info.bb(mask=prim2.mask)

                    if (bb1 is not None) and (ref_bb2 is not None):
                        yield (bb1, ref_bb2, space)
                    if (bb2 is not None) and (ref_bb1 is not None):
                        yield (bb2, ref_bb1, space)

    def __str__(self) -> str:
        strs = tuple(f"'{ref_info.name}'" for ref_info in self.ref_infos)
        to = f"instances ({','.join(strs)})"
        return f"{self.__class__.__name__} instance '{self.info.name}' to {to}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}"
            f"(inst_name={self.info}, ref_infos={self.ref_infos!r})"
        )


class PlaceLeft(_PlaceConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        if info.x is not None:
            raise ValueError(
                f"Second x placement with '{self}'"
            )
        if any(ref_info.x is None for ref_info in self.ref_infos):
            return False
        xs = []
        for ref_info in self.ref_infos:
            for rect, ref_rect, space in self._get_bbs(placer=placer, ref_info=ref_info):
                xs.append(
                    cast(float, ref_info.x) + ref_rect.left - rect.right
                    - space,
                )
        if len(xs) == 0:
            raise ValueError(
                f"No constraint found for '{self}'"
            )
        info.x = min(xs)
        return True


class PlaceBelow(_PlaceConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        if info.y is not None:
            raise ValueError(
                f"Second y alignment with '{self}'"
            )
        if any(ref_info.y is None for ref_info in self.ref_infos):
            return False
        ys = []
        for ref_info in self.ref_infos:
            for rect, ref_rect, space in self._get_bbs(placer=placer, ref_info=ref_info):
                ys.append(
                    cast(float, ref_info.y) + ref_rect.bottom - rect.top
                    - space,
                )
        if len(ys) == 0:
            raise ValueError(
                f"No constraint found for '{self}'"
            )
        info.y = min(ys)
        return True


class PlaceRight(_PlaceConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        if info.x is not None:
            raise ValueError(
                f"Second x placement with '{self}'"
            )
        if any(ref_info.x is None for ref_info in self.ref_infos):
            return False
        xs = []
        for ref_info in self.ref_infos:
            for rect, ref_rect, space in self._get_bbs(placer=placer, ref_info=ref_info):
                xs.append(
                    cast(float, ref_info.x) + ref_rect.right - rect.left
                    + space,
                )
        if len(xs) == 0:
            raise ValueError(
                f"No constraint found for '{self}'"
            )
        info.x = max(xs)
        return True


class PlaceAbove(_PlaceConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        if info.y is not None:
            raise ValueError(
                f"Second y alignment with '{self}'"
            )
        if any(ref_info.y is None for ref_info in self.ref_infos):
            return False
        ys = []
        for ref_info in self.ref_infos:
            for rect, ref_rect, space in self._get_bbs(placer=placer, ref_info=ref_info):
                ys.append(
                    cast(float, ref_info.y) + ref_rect.top - rect.bottom
                    + space,
                )
        if len(ys) == 0:
            raise ValueError(
                f"No constraint found for '{self}'"
            )
        info.y = max(ys)
        return True


class _AlignConstraint(_RefConstraint):
    @overload
    def __init__(self, *,
        info: "Sky130Layouter._PlaceInfo", ref_info: "Sky130Layouter._PlaceInfo",
        ref_pin: bool, prim: None, net: None,
    ) -> None:
        ...
    @overload
    def __init__(self, *,
        info: "Sky130Layouter._PlaceInfo", ref_info: "Sky130Layouter._PlaceInfo",
        ref_pin: bool, prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet],
    ) -> None:
        ...
    def __init__(self, *,
        info: "Sky130Layouter._PlaceInfo", ref_info: "Sky130Layouter._PlaceInfo",
        ref_pin: bool, prim: Optional[_prm.DesignMaskPrimitiveT],
        net: Optional[_ckt._CircuitNet],
    ) -> None:
        super().__init__(info=info, ref_infos=(ref_info,))
        self.ref_pin = ref_pin
        self.prim = prim
        self.net = net

    @property
    def ref_info(self) -> "Sky130Layouter._PlaceInfo":
        return self.ref_infos[0]

    def get_bbs(self, *, placer: "Sky130Layouter") -> Tuple[_geo.Rect, _geo.Rect]:
        info = self.info
        ref_info = self.ref_info

        if self.prim is None:
            bb = info.layout.boundary
            if bb is None:
                bb = info.bb()
            other_bb = ref_info.layout.boundary
            if other_bb is None:
                other_bb = ref_info.bb()
            assert isinstance(bb, _geo.Rect)
            assert isinstance(other_bb, _geo.Rect)
        else:
            mask = self.prim.mask
            bb = info.bb(mask=mask, net=self.net)
            if bb is None:
                raise ValueError(
                    f"Can't align '{self.info}'; it has no layout on mask '{mask}'"
                )
            if not self.ref_pin:
                other_bb = ref_info.bb(mask=mask, net=self.net)
            else:
                pin = cast(_prm.PinAttrPrimitiveT, self.prim).pin
                assert pin is not None
                other_bb = ref_info.bb(mask=pin.mask, net=self.net, depth=1)
            if other_bb is None:
                raise ValueError(
                    f"Can't align '{self.info}';"
                    f" '{ref_info.name}' has no layout on mask '{mask}'"
                )

        return (bb, other_bb)


class AlignCenterX(_AlignConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        ref_info = self.ref_info

        if ref_info.x is None:
            return False

        bb, other_bb = self.get_bbs(placer=placer)
        info.x = ref_info.x + other_bb.center.x - bb.center.x
        return True


class AlignCenterY(_AlignConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        ref_info = self.ref_info

        if ref_info.y is None:
            return False

        bb, other_bb = self.get_bbs(placer=placer)
        info.y = ref_info.y + other_bb.center.y - bb.center.y
        return True


class AlignLeft(_AlignConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        ref_info = self.ref_info

        if ref_info.x is None:
            return False

        bb, other_bb = self.get_bbs(placer=placer)
        info.x = ref_info.x + other_bb.left - bb.left
        return True


class AlignRight(_AlignConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        ref_info = self.ref_info

        if ref_info.x is None:
            return False

        bb, other_bb = self.get_bbs(placer=placer)
        info.x = ref_info.x + other_bb.right - bb.right
        return True


class AlignBottom(_AlignConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        ref_info = self.ref_info

        if ref_info.y is None:
            return False

        bb, other_bb = self.get_bbs(placer=placer)
        info.y = ref_info.y + other_bb.bottom - bb.bottom
        return True


class AlignTop(_AlignConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        ref_info = self.ref_info

        if ref_info.y is None:
            return False

        bb, other_bb = self.get_bbs(placer=placer)
        info.y = ref_info.y + other_bb.top - bb.top
        return True


class _AlignAbsConstraint(_Constraint):
    def __init__(self, *,
        info: "Sky130Layouter._PlaceInfo", ref_value: float,
        prim: Optional[_prm.DesignMaskPrimitiveT],
        net: Optional[_ckt._CircuitNet],
    ) -> None:
        super().__init__(infos=(info,))
        self.ref_value = ref_value
        self.prim = prim
        self.net = net

    @property
    def info(self) -> "Sky130Layouter._PlaceInfo":
        return self.infos[0]

    def get_bb(self) -> _geo.Rect:
        info = self.info

        if self.prim is None:
            bb = info.layout.boundary
            if bb is None:
                bb = info.bb()
            assert isinstance(bb, _geo.Rect)
        else:
            mask = self.prim.mask
            bb = info.bb(mask=mask, net=self.net)
            if bb is None:
                raise ValueError(
                    f"Can't align '{self.info}'; it has no layout on mask '{mask}'"
                )

        return bb


class AlignCenterXAbs(_AlignAbsConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        bb = self.get_bb()

        info.x = self.ref_value - bb.center.x
        return True


class AlignCenterYAbs(_AlignAbsConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        bb = self.get_bb()

        info.y = self.ref_value - bb.center.y
        return True


class AlignLeftAbs(_AlignAbsConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        bb = self.get_bb()

        info.x = self.ref_value - bb.left
        return True


class AlignRightAbs(_AlignAbsConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        bb = self.get_bb()

        info.x = self.ref_value - bb.right
        return True


class AlignBottomAbs(_AlignAbsConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        bb = self.get_bb()

        info.y = self.ref_value - bb.bottom
        return True


class AlignTopAbs(_AlignAbsConstraint):
    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        bb = self.get_bb()

        info.y = self.ref_value - bb.top
        return True


class Fill(_Constraint):
    def __init__(self, *,
        infos: Tuple["Sky130Layouter._PlaceInfo", ...], prim: _prm.DesignMaskPrimitiveT,
        net: Optional[_ckt._CircuitNet]=None,
    ) -> None:
        super().__init__(infos=infos)
        self.prim = prim
        self.net = net

    def apply(self, *, placer: "Sky130Layouter") -> bool:
        rects: List[_geo.Rect] = []
        for info in self.infos:
            if not info.placed:
                return False
            rect = info.bb(mask=self.prim.mask, net=self.net)
            if rect is not None:
                dxy = _geo.Point(x=cast(float, info.x), y=cast(float, info.y))
                rects.append(rect + dxy)
        if len(rects) == 0:
            raise ValueError(
                f"No shapes found for fill for prim '{self.prim.name}'\n"
                f"\treferences '({','.join(info.name for info in self.infos)})'"
            )
        ms = _geo.MultiShape(shapes=rects)
        shape = _geo.Rect.from_rect(rect=ms.bounds)
        placer.layouter.layout.add_shape(
            layer=self.prim, net=self.net, shape=shape,
        )
        return True


class Connect(_Constraint):
    def __init__(self, *,
        info1: "Sky130Layouter._PlaceInfo", info2: "Sky130Layouter._PlaceInfo",
        prim: _prm.WidthSpaceConductorT, net: _ckt._CircuitNet,
    ) -> None:
        super().__init__(infos=(info1, info2))
        self.prim = prim
        self.net = net

    @property
    def info1(self) -> "Sky130Layouter._PlaceInfo":
        return self.infos[0]
    @property
    def info2(self) -> "Sky130Layouter._PlaceInfo":
        return self.infos[1]

    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info1 = self.info1
        info2 = self.info2
        mask = self.prim.mask
        min_width = self.prim.min_width
        if (not info1.placed) or (not info2.placed):
            return False
        bb1 = info1.bb(mask=mask, net=self.net)
        if bb1 is None:
            s_net = "" if self.net is None else f" on net '{self.net}'"
            raise ValueError(
                f"No layout found for '{self.prim}'{s_net} for '{info1.name}'"
            )
        bb2 = info2.bb(mask=mask, net=self.net)
        if bb2 is None:
            s_net = "" if self.net is None else f" and net '{self.net}'"
            raise ValueError(
                f"No layout found for '{self.prim}'{s_net} for '{info2.name}'"
            )
        dxy1 = _geo.Point(x=cast(float, info1.x), y=cast(float, info1.y))
        bb1 += dxy1
        dxy2 = _geo.Point(x=cast(float, info2.x), y=cast(float, info2.y))
        bb2 += dxy2

        is_tall1 = bb1.height > bb1.width
        is_tall2 = bb2.height > bb2.width

        # Swap if bb2 is left of bb1
        if bb1.left > bb2.right:
            bb1, bb2 = bb2, bb1
            is_tall1, is_tall2 = is_tall2, is_tall1

        if bb2.left > bb1.right:
            if bb1.top < bb2.bottom:
                if is_tall1:
                    # Go up first
                    if is_tall2:
                        # Go right at middle height
                        y = placer.tech.on_grid(0.5*(bb1.top + bb2.bottom))
                        if (bb2.bottom - bb1.top) > (min_width + _geo.epsilon):
                            shape = _geo.MultiPath(
                                _geo.Start(
                                    point=_geo.Point(x=bb1.center.x, y=bb1.top),
                                    width=bb1.width,
                                ),
                                _geo.GoUp(y - bb1.top),
                                _geo.SetWidth(min_width),
                                _geo.GoRight(bb2.center.x - bb1.center.x),
                                _geo.SetWidth(bb2.width),
                                _geo.GoUp(bb2.center.y - y),
                            )
                        else:
                            shape = _geo.Rect(
                                left=bb1.left,
                                bottom=placer.tech.on_grid(
                                    y - 0.5*min_width, rounding="floor",
                                ),
                                right=bb2.right,
                                top=placer.tech.on_grid(
                                    y - 0.5*min_width, rounding="ceiling",
                                ),
                            )
                    else:
                        # Go right at top
                        shape = _geo.MultiPath(
                            _geo.Start(
                                point=_geo.Point(x=bb1.center.x, y=bb1.top),
                                width=bb1.width,
                            ),
                            _geo.GoUp(bb2.center.y - bb1.top),
                            _geo.SetWidth(bb2.height),
                            _geo.GoRight(bb2.left - bb1.center.x),
                        )
                else:
                    # Go right first
                    if is_tall2:
                        # Go up on the right
                        shape = _geo.MultiPath(
                            _geo.Start(
                                point=_geo.Point(x=bb1.right, y=bb1.center.y),
                                width=bb1.height,
                            ),
                            _geo.GoRight(bb2.center.x - bb1.right),
                            _geo.SetWidth(bb2.width),
                            _geo.GoUp(bb2.bottom - bb1.center.y)
                        )
                    else:
                        # Go up in the middle
                        x = 0.5*(bb2.left + bb1.right)
                        if (bb2.left - bb1.right) > (min_width + _geo.epsilon):
                            shape = _geo.MultiPath(
                                _geo.Start(
                                    point=_geo.Point(x=bb1.right, y=bb1.center.y),
                                    width=bb1.height,
                                ),
                                _geo.GoRight(x - bb1.right),
                                _geo.SetWidth(min_width),
                                _geo.GoUp(bb2.center.y - bb1.center.y),
                                _geo.SetWidth(bb2.height),
                                _geo.GoRight(bb2.left - x),
                            )
                        else:
                            shape = _geo.Rect(
                                left=placer.tech.on_grid(x - 0.5*min_width, rounding="floor"),
                                bottom=bb1.bottom,
                                right=placer.tech.on_grid(x + 0.5*min_width, rounding="ceiling"),
                                top=bb2.top,
                            )
            elif bb2.top < bb1.bottom:
                if is_tall1:
                    # Go down first
                    if is_tall2:
                        # Go right at middle height
                        y = placer.tech.on_grid(0.5*(bb2.top + bb1.bottom))
                        if (bb1.bottom - bb2.top) > (min_width + _geo.epsilon):
                            shape = _geo.MultiPath(
                                _geo.Start(
                                    point=_geo.Point(x=bb1.center.x, y=bb1.bottom),
                                    width=bb1.width,
                                ),
                                _geo.GoDown(bb1.bottom - y),
                                _geo.SetWidth(min_width),
                                _geo.GoRight(bb2.center.x - bb1.center.x),
                                _geo.SetWidth(bb2.width),
                                _geo.GoDown(y - bb2.center.y),
                            )
                        else:
                            shape = _geo.Rect(
                                left=bb1.left,
                                bottom=placer.tech.on_grid(
                                    y - 0.5*min_width, rounding="floor",
                                ),
                                right=bb2.right,
                                top=placer.tech.on_grid(
                                    y + 0.5*min_width, rounding="ceiling",
                                ),
                            )
                    else:
                        # Go right at bottom
                        shape = _geo.MultiPath(
                            _geo.Start(
                                point=_geo.Point(x=bb1.center.x, y=bb1.bottom),
                                width=bb1.width,
                            ),
                            _geo.GoDown(bb1.bottom - bb2.center.y),
                            _geo.SetWidth(bb2.height),
                            _geo.GoRight(bb2.left - bb1.center.x),
                        )
                else: # not is_tall1
                    # Go right first
                    if is_tall2:
                        # Go down on the right
                        shape = _geo.MultiPath(
                            _geo.Start(
                                point=_geo.Point(x=bb1.right, y=bb1.center.y),
                                width=bb1.height,
                            ),
                            _geo.GoRight(bb2.center.x - bb1.right),
                            _geo.SetWidth(bb2.width),
                            _geo.GoDown(bb1.center.y - bb2.top)
                        )
                    else:
                        # Go up in the middle
                        x = 0.5*(bb2.left + bb1.right)
                        if (bb2.left - bb1.right) > (min_width + _geo.epsilon):
                            shape = _geo.MultiPath(
                                _geo.Start(
                                    point=_geo.Point(x=bb1.right, y=bb1.center.y),
                                    width=bb1.height,
                                ),
                                _geo.GoRight(x - bb1.right),
                                _geo.SetWidth(min_width),
                                _geo.GoUp(bb2.center.y - bb1.center.y),
                                _geo.SetWidth(bb2.height),
                                _geo.GoRight(bb2.left - x),
                            )
                        else:
                            shape = _geo.Rect(
                                left=placer.tech.on_grid(x - 0.5*min_width, rounding="floor"),
                                bottom=bb1.bottom,
                                right=placer.tech.on_grid(x + 0.5*min_width, rounding="ceiling"),
                                top=bb2.top,
                            )
            else:
                left = bb1.right
                right = bb2.left
                bottom = max(bb1.bottom, bb2.bottom)
                top = min(bb1.top, bb2.top)
                if (top - bottom) < (min_width + _geo.epsilon):
                    y = 0.5*(bottom + top)
                    bottom = placer.tech.on_grid(y - 0.5*min_width, rounding="floor")
                    top = placer.tech.on_grid(y + 0.5*min_width, rounding="ceiling")
                shape = _geo.Rect(left=left, bottom=bottom, right=right, top=top)
        elif bb1.left > bb2.right:
            raise RuntimeError("Internal error")
        else:
            left = max(bb1.left, bb2.left)
            right = min(bb1.right, bb2.right)
            if (right - left) > (min_width - _geo.epsilon):
                dy = 0.0
            else:
                x = 0.5*(left + right)
                left = placer.tech.on_grid(x - 0.5*min_width, rounding="floor")
                right = placer.tech.on_grid(x + 0.5*min_width, rounding="ceiling")
                dy = min_width
            if bb1.bottom > bb2.top:
                top = bb1.bottom + dy
                bottom = bb2.top - dy
            elif bb2.bottom > bb1.top:
                top = bb2.bottom + dy
                bottom = bb1.top - dy
            else:
                # Already overlaps
                # TODO: Fix possible minimum width rule violation
                return True
            shape = _geo.Rect(left=left, bottom=bottom, right=right, top=top)
        placer.layouter.add_wire(net=self.net, wire=self.prim, shape=shape)
        return True


class Extend(_Constraint):
    def __init__(self, *,
        info: "Sky130Layouter._PlaceInfo", ref_info: "Sky130Layouter._PlaceInfo",
        prim: _prm.DesignMaskPrimitiveT,
    ) -> None:
        super().__init__(infos=(info, ref_info))
        self.infos: Tuple["Sky130Layouter._PlaceInfo", "Sky130Layouter._PlaceInfo"]
        self.prim = prim

    @property
    def info(self) -> "Sky130Layouter._PlaceInfo":
        return self.infos[0]
    @property
    def ref_info(self) -> "Sky130Layouter._PlaceInfo":
        return self.infos[1]

    def apply(self, *, placer: "Sky130Layouter") -> bool:
        info = self.info
        ref_info = self.ref_info
        mask = self.prim.mask

        if (not info.placed) or (not ref_info.placed):
            return False

        bb = info.bb(mask=mask, placed=True)
        ref_bb = ref_info.bb(mask=mask, placed=True)
        assert (bb is not None) and (ref_bb is not None)

        if (
            (bb.bottom < ref_bb.top)
            and (bb.top > ref_bb.bottom)
        ):
            # Horizontal extension
            if bb.right < ref_bb.left:
                shape = _geo.Rect.from_rect(rect=bb, right=ref_bb.left)
            elif bb.left > ref_bb.right:
                shape = _geo.Rect.from_rect(rect=bb, left=ref_bb.right)
            else:
                # overlaps already
                return True
        elif (
            (bb.left < ref_bb.right)
            and (bb.right > ref_bb.left)
        ):
            # Vertical extension
            if bb.bottom > ref_bb.top:
                shape = _geo.Rect.from_rect(rect=bb, bottom=ref_bb.top)
            elif bb.top < ref_bb.bottom:
                shape = _geo.Rect.from_rect(rect=bb, top=ref_bb.bottom)
            else:
                # overlaps already
                return True
        else:
            raise ValueError(
                "No vertical or horizontal overlapping bounding boxes for"
                f" extending '{info.name}' to '{ref_info}' on '{self.prim.name}'"
            )

        placer.layouter.layout.add_shape(layer=self.prim, net=None, shape=shape)
        return True


class Sky130Layouter:
    """Helper class to place cells relative from each other.
    This is currently tested on bandgap but purpose is to have it more generally
    usable and upstream (modified) version to PDKMaster.
    """
    Object = Union[_ckt._Instance, _prm.ConductorT]

    class _PlaceInfo(abc.ABC):
        def __init__(self, *,
            name: str, obj: "Sky130Layouter.Object", placer: "Sky130Layouter", layout: _lay.LayoutT,
        ) -> None:
            self.name = name
            self.obj = obj
            self.placer = placer
            self.layout = layout
            self.placed_layout: Optional[_lay.LayoutT] = None

            self._x: Optional[float] = None
            self._y: Optional[float] = None
            self._bb: Dict[
                Tuple[str, Optional[_msk.DesignMask], Optional[_ckt._CircuitNet]],
                Optional[_geo.Rect],
            ] = {}

        @property
        def x(self) -> Optional[float]:
            return self._x
        @x.setter
        def x(self, v: float):
            if self._x is not None:
                raise TypeError("x value may only be set once")
            else:
                self._x = v
            if self._y is not None:
                self.place()

        @property
        def y(self) -> Optional[float]:
            return self._y
        @y.setter
        def y(self, v: float):
            if self._y is not None:
                raise TypeError("y value may only be set once")
            else:
                self._y = v
            if self._x is not None:
                self.place()

        @property
        def center(self) -> Optional[_geo.Point]:
            if (self._x is None) or (self._y is None):
                return None
            else:
                return _geo.Point(x=self._x, y=self._y)

        @property
        def placed(self) -> bool:
            return self.placed_layout is not None

        @overload
        def bb(self, *,
            mask: None=None, net: None=None, depth: None=None,
            placed: bool=False,
        ) -> _geo.Rect:
            ...
        @overload
        def bb(self, *,
            mask: _msk.DesignMask, net: Optional[_ckt._CircuitNet]=None,
            depth: Optional[int]=None, placed: bool=False,
        ) -> Optional[_geo.Rect]:
            ...
        def bb(self, *,
            mask: Optional[_msk.DesignMask]=None, net: Optional[_ckt._CircuitNet]=None,
            depth: Optional[int]=None, placed: bool=False,
        ) -> Optional[_geo.Rect]:
            if placed and not (self.placed):
                raise ValueError(
                    f"Asking for placed bounding box on non-placed info '{self.name}'"
                )

            try:
                rect = self._bb[(self.name, mask, net)]
            except KeyError:
                try:
                    rect = self.layout.bounds(mask=mask, net=net, depth=depth)
                except:
                    rect = None
                self._bb[(self.name, mask, net)] = rect
            if rect is None:
                return None
            elif not placed:
                return rect
            else: # placed & rect is not None
                o = self.center
                assert o is not None
                return rect + o

        def place(self):
            assert (self._x is not None) and (self._y is not None)
            self.placed_layout = self.placer.layouter.place(
                self.layout, x=self._x, y=self._y,
            )

        def __str__(self) -> str:
            return f"{self.__class__.__name__}['{self.name}']"

    class _PlaceInstInfo(_PlaceInfo):
        def __init__(self, *,
            placer: "Sky130Layouter", inst: _ckt._Instance, rotation: _geo.Rotation,
        ) -> None:
            self.rotation = rotation
            layout = placer.layouter.inst_layout(inst=inst, rotation=rotation)
            super().__init__(name=inst.name, obj=inst, placer=placer, layout=layout)
            self.obj: _ckt._Instance

        @property
        def inst(self) -> _ckt._Instance:
            return self.obj

    class _PlaceWireInfo(_PlaceInfo):
        def __init__(self, *,
            wire_name: str, placer: "Sky130Layouter",
            net: _ckt._CircuitNet, wire: _prm.ConductorT,
            ref_width: Optional[str], ref_width_pin: bool=False,
            ref_bottom_width: Optional[str], ref_bottom_width_pin: bool=False,
            ref_top_width: Optional[str], ref_top_width_pin: bool=False,
            ref_height: Optional[str], ref_height_pin: bool=False,
            ref_bottom_height: Optional[str], ref_bottom_height_pin: bool=False,
            ref_top_height: Optional[str], ref_top_height_pin: bool=False,
            **wire_params,
        ) -> None:
            if ref_width is not None:
                if "width" in wire_params:
                    raise ValueError(f"both ref_width and width specified")
                try:
                    info = placer.info_lookup[ref_width]
                except KeyError:
                    raise ValueError(f"ref_width '{ref_width}' not found")
                if not ref_width_pin:
                    bb = info.bb(mask=wire.mask, net=net)
                else:
                    assert wire.pin is not None
                    bb = info.bb(mask=wire.pin.mask, net=net)
                if bb is None:
                    raise ValueError(
                        f"No layout for ref_width '{ref_width}', wire '{wire.name}'"
                        f" and net {net.name}",
                    )
                wire_params["width"] = bb.width
            if ref_bottom_width is not None:
                if "bottom_width" in wire_params:
                    raise ValueError(
                        f"both ref_bottom_width and bottom_width specified",
                    )
                try:
                    bottom = wire_params["bottom"]
                except KeyError:
                    assert hasattr(wire, "bottom")
                    bottom = wire.bottom[0]
                try:
                    info = placer.info_lookup[ref_bottom_width]
                except KeyError:
                    raise ValueError(f"ref_bottom_width '{ref_bottom_width}' not found")
                if not ref_bottom_width_pin:
                    bb = info.bb(mask=bottom.mask, net=net)
                else:
                    assert bottom.pin is not None
                    bb = info.bb(mask=bottom.pin.mask, net=net)
                if bb is None:
                    raise ValueError(
                        f"No layout for ref_bottom_width '{ref_bottom_width}',"
                        f" bottom '{bottom.name}' and net {net.name}",
                    )
                wire_params["bottom_width"] = bb.width
            if ref_top_width is not None:
                if "top_width" in wire_params:
                    raise ValueError(
                        f"both ref_top_width and top_width specified",
                    )
                try:
                    top = wire_params["top"]
                except KeyError:
                    assert hasattr(wire, "top")
                    top = wire.top[0]
                try:
                    info = placer.info_lookup[ref_top_width]
                except KeyError:
                    raise ValueError(f"ref_top_width '{ref_top_width}' not found")
                if not ref_top_width_pin:
                    bb = info.bb(mask=top.mask, net=net)
                else:
                    assert top.pin is not None
                    bb = info.bb(mask=top.pin.mask, net=net)
                if bb is None:
                    raise ValueError(
                        f"No layout for ref_top_width '{ref_top_width}',"
                        f" top '{top.name}' and net {net.name}",
                    )
                wire_params["top_width"] = bb.width
            if ref_height is not None:
                if "height" in wire_params:
                    raise ValueError(f"both ref_height and height specified")
                try:
                    info = placer.info_lookup[ref_height]
                except KeyError:
                    raise ValueError(f"ref_height '{ref_height}' not found")
                if not ref_height_pin:
                    bb = info.bb(mask=wire.mask, net=net)
                else:
                    assert wire.pin is not None
                    bb = info.bb(mask=wire.pin.mask, net=net)
                if bb is None:
                    raise ValueError(
                        f"No layout for ref_height '{ref_height}', wire '{wire.name}'"
                        f" and net {net.name}",
                    )
                wire_params["height"] = bb.height
            if ref_bottom_height is not None:
                if "bottom_height" in wire_params:
                    raise ValueError(
                        f"both ref_bottom_height and bottom_height specified",
                    )
                try:
                    bottom = wire_params["bottom"]
                except KeyError:
                    assert hasattr(wire, "bottom")
                    bottom = wire.bottom[0]
                try:
                    info = placer.info_lookup[ref_bottom_height]
                except KeyError:
                    raise ValueError(f"ref_bottom_height '{ref_bottom_height}' not found")
                if not ref_bottom_height_pin:
                    bb = info.bb(mask=bottom.mask, net=net)
                else:
                    assert bottom.pin is not None
                    bb = info.bb(mask=bottom.pin.mask, net=net)
                if bb is None:
                    raise ValueError(
                        f"No layout for ref_bottom_height '{ref_bottom_height}',"
                        f" bottom '{bottom.name}' and net {net.name}",
                    )
                wire_params["bottom_height"] = bb.height
            if ref_top_height is not None:
                if "top_height" in wire_params:
                    raise ValueError(
                        f"both ref_top_height and top_height specified",
                    )
                try:
                    top = wire_params["top"]
                except KeyError:
                    assert hasattr(wire, "top")
                    top = wire.top[0]
                try:
                    info = placer.info_lookup[ref_top_height]
                except KeyError:
                    raise ValueError(f"ref_top_height '{ref_top_height}' not found")
                if not ref_top_height_pin:
                    bb = info.bb(mask=top.mask, net=net)
                else:
                    assert top.pin is not None
                    bb = info.bb(mask=top.pin.mask, net=net)
                if bb is None:
                    raise ValueError(
                        f"No layout for ref_top_height '{ref_top_height}',"
                        f" top '{top.name}' and net {net.name}",
                    )
                wire_params["top_height"] = bb.height
            layout = placer.layouter.wire_layout(net=net, wire=wire, **wire_params)

            super().__init__(
                name=wire_name, obj=wire, placer=placer, layout=layout,
            )
            self.net = net
            self.obj: _prm.ConductorT
            self.wire_params = wire_params

        @property
        def wire_name(self) -> str:
            return self.name
        @property
        def wire(self) -> _prm.ConductorT:
            return self.obj

    def __init__(self, *,
        layouter: _lay.CircuitLayouterT, rotations: Dict[str, _geo.Rotation]={},
    ) -> None:
        self._ckt = ckt = layouter.circuit
        self._insts = insts = ckt.instances
        self.layouter = layouter
        self.rotations = rotations
        self.constraint_stack: List[_Constraint] = []

        self.info_lookup: Dict[str, Sky130Layouter._PlaceInfo] = {
            inst.name: Sky130Layouter._PlaceInstInfo(
                placer=self, inst=inst,
                rotation=rotations.get(inst.name, _geo.Rotation.R0),
            )
            for inst in insts
        }

    @property
    def tech(self) -> _tch.Technology:
        return self.layouter.tech

    def wire(self, *,
        wire_name: str, net: _ckt._CircuitNet, wire: _prm.ConductorT,
        ref_width: Optional[str]=None, ref_bottom_width: Optional[str]=None,
        ref_top_width: Optional[str]=None,
        ref_height: Optional[str]=None, ref_bottom_height: Optional[str]=None,
        ref_top_height: Optional[str]=None,
        **wire_params,
    ):
        if wire_name in self.info_lookup:
            info = self.info_lookup[wire_name]
            if isinstance(info, Sky130Layouter._PlaceInstInfo):
                raise ValueError(
                    f"wire_name '{wire_name}' conflicts with instance of same name"
                )
            elif isinstance(info, Sky130Layouter._PlaceWireInfo):
                raise ValueError(
                    f"There is already a wire with name {wire_name}"
                )
            else:
                raise NotImplementedError(f"Unhandled _PlaceInfo type '{type(info)}'")
        self.info_lookup[wire_name] = Sky130Layouter._PlaceWireInfo(
            wire_name=wire_name, placer=self, net=net, wire=wire,
            ref_width=ref_width, ref_bottom_width=ref_bottom_width,
            ref_top_width=ref_top_width,
            ref_height=ref_height, ref_bottom_height=ref_bottom_height,
            ref_top_height=ref_top_height,
            **wire_params,
        )

    def place_at_left(self, *, name: str):
        try:
            info = self.info_lookup[name]
        except KeyError:
            raise ValueError(f"Unknown reference '{name}'")
        bb = info.bb()
        info.x = -bb.left

    def place_at_bottom(self, *, name: str):
        try:
            info = self.info_lookup[name]
        except KeyError:
            raise ValueError(f"Unknown reference '{name}'")
        bb = info.bb()
        info.y = -bb.bottom

    def _place(self, *,
        cls: Type[_PlaceConstraint],
        name: str, ref_names: Tuple[str, ...],
        ignore_masks: MultiT[_msk.DesignMask]=tuple(),
        use_boundary: Optional[bool], boundary_only: bool,
        extra_space: float=0.0,
    ):
        info = self.info_lookup[name]
        ref_infos = []
        for ref_name in ref_names:
            try:
                ref_infos.append(self.info_lookup[ref_name])
            except KeyError:
                raise ValueError(f"Unknown reference '{ref_name}'")

        self.constraint_stack.append(cls(
            info=info, ref_infos=tuple(ref_infos), ignore_masks=ignore_masks,
            use_boundary=use_boundary, boundary_only=boundary_only,
            extra_space=extra_space,
        ))

    def place_to_the_right(self, *,
        name: str, ref_names: MultiT[str], ignore_masks: MultiT[_msk.DesignMask]=tuple(),
        use_boundary: Optional[bool]=None, boundary_only: bool=False,
        extra_space: float=0.0,
    ):
        self._place(
            cls=PlaceRight, name=name, ref_names=cast_MultiT(ref_names),
            ignore_masks=ignore_masks, use_boundary=use_boundary,
            boundary_only=boundary_only, extra_space=extra_space,
        )

    def place_below(self, *,
        name: str, ref_names: MultiT[str], ignore_masks: MultiT[_msk.DesignMask]=tuple(),
        use_boundary: Optional[bool]=None, boundary_only: bool=False,
        extra_space: float=0.0,
    ):
        self._place(
            cls=PlaceBelow, name=name, ref_names=cast_MultiT(ref_names),
            ignore_masks=ignore_masks, use_boundary=use_boundary,
            boundary_only=boundary_only, extra_space=extra_space,
        )

    def place_to_the_left(self, *,
        name: str, ref_names: MultiT[str], ignore_masks: MultiT[_msk.DesignMask]=tuple(),
        use_boundary: Optional[bool]=None, boundary_only: bool=False,
        extra_space: float=0.0,
    ):
        self._place(
            cls=PlaceLeft, name=name, ref_names=cast_MultiT(ref_names),
            ignore_masks=ignore_masks, use_boundary=use_boundary,
            boundary_only=boundary_only, extra_space=extra_space,
        )

    def place_above(self, *,
        name: str, ref_names: MultiT[str], ignore_masks: MultiT[_msk.DesignMask]=tuple(),
        use_boundary: Optional[bool]=None, boundary_only: bool=False,
        extra_space: float=0.0,
    ):
        self._place(
            cls=PlaceAbove, name=name, ref_names=cast_MultiT(ref_names),
            ignore_masks=ignore_masks, use_boundary=use_boundary,
            boundary_only=boundary_only, extra_space=extra_space,
        )

    @overload
    def _align(self, *,
        cls: Type[_AlignConstraint],
        name: str, ref_name: str, ref_pin: bool,
        prim: None, net: None=None,
    ) -> None:
        ...
    @overload
    def _align(self, *,
        cls: Type[_AlignConstraint],
        name: str, ref_name: str, ref_pin: bool,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ) -> None:
        ...
    def _align(self, *,
        cls: Type[_AlignConstraint],
        name: str, ref_name: str, ref_pin: bool,
        prim, net: Optional[_ckt._CircuitNet]=None,
    ) -> None:
        info = self.info_lookup[name]
        ref_info = self.info_lookup[ref_name]

        self.constraint_stack.append(cls(
            info=info, ref_info=ref_info, ref_pin=ref_pin, prim=prim, net=net,
        ))

    def _alignabs(self, *,
        cls: Type[_AlignAbsConstraint],
        name: str, ref_value: float,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        info = self.info_lookup[name]

        self.constraint_stack.append(cls(
            info=info, ref_value=ref_value, prim=prim, net=net,
        ))

    @overload
    def center_x(self, *,
        name: str,
        ref_name: str, ref_pin: bool=False,
        ref_value: None=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    @overload
    def center_x(self, *,
        name: str,
        ref_name: None=None, ref_pin: bool=False,
        ref_value: float,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    def center_x(self, *,
        name: str,
        ref_name: Optional[str]=None, ref_pin: bool=False,
        ref_value: Optional[float]=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        if ref_name is not None:
            self._align(
                cls=AlignCenterX, name=name, ref_name=ref_name, ref_pin=ref_pin,
                prim=prim, net=net,
            )
        else:
            assert ref_value is not None
            self._alignabs(
                cls=AlignCenterXAbs, name=name, ref_value=ref_value, prim=prim, net=net,
            )

    @overload
    def center_y(self, *,
        name: str,
        ref_name: str, ref_pin: bool=False,
        ref_value: None=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    @overload
    def center_y(self, *,
        name: str,
        ref_name: None=None, ref_pin: bool=False,
        ref_value: float,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    def center_y(self, *,
        name: str,
        ref_name: Optional[str]=None, ref_pin: bool=False,
        ref_value: Optional[float]=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        if ref_name is not None:
            self._align(
                cls=AlignCenterY, name=name, ref_name=ref_name, ref_pin=ref_pin,
                prim=prim, net=net,
            )
        else:
            assert ref_value is not None
            self._alignabs(
                cls=AlignCenterYAbs, name=name, ref_value=ref_value, prim=prim, net=net,
            )

    @overload
    def align_left(self, *,
        name: str,
        ref_name: str, ref_pin: bool=False,
        ref_value: None=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    @overload
    def align_left(self, *,
        name: str,
        ref_name: None=None, ref_pin: bool=False,
        ref_value: float,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    def align_left(self, *,
        name: str,
        ref_name: Optional[str]=None, ref_pin: bool=False,
        ref_value: Optional[float]=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        if ref_name is not None:
            self._align(
                cls=AlignLeft, name=name, ref_name=ref_name, ref_pin=ref_pin,
                prim=prim, net=net,
            )
        else:
            assert ref_value is not None
            self._alignabs(
                cls=AlignLeftAbs, name=name, ref_value=ref_value, prim=prim, net=net,
            )

    @overload
    def align_bottom(self, *,
        name: str,
        ref_name: str, ref_pin: bool=False,
        ref_value: None=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    @overload
    def align_bottom(self, *,
        name: str,
        ref_name: None=None, ref_pin: bool=False,
        ref_value: float,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    def align_bottom(self, *,
        name: str,
        ref_name: Optional[str]=None, ref_pin: bool=False,
        ref_value: Optional[float]=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        if ref_name is not None:
            self._align(
                cls=AlignBottom, name=name, ref_name=ref_name, ref_pin=ref_pin,
                prim=prim, net=net,
            )
        else:
            assert ref_value is not None
            self._alignabs(
                cls=AlignBottomAbs, name=name, ref_value=ref_value,
                prim=prim, net=net,
            )

    @overload
    def align_right(self, *,
        name: str,
        ref_name: str, ref_pin: bool=False,
        ref_value: None=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    @overload
    def align_right(self, *,
        name: str,
        ref_name: None=None, ref_pin: bool=False,
        ref_value: float,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    def align_right(self, *,
        name: str,
        ref_name: Optional[str]=None, ref_pin: bool=False,
        ref_value: Optional[float]=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        if ref_name is not None:
            self._align(
                cls=AlignRight, name=name, ref_name=ref_name, ref_pin=ref_pin,
                prim=prim, net=net,
            )
        else:
            assert ref_value is not None
            self._alignabs(
                cls=AlignRightAbs, name=name, ref_value=ref_value, prim=prim, net=net,
            )

    @overload
    def align_top(self, *,
        name: str,
        ref_name: str, ref_pin: bool=False,
        ref_value: None=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    @overload
    def align_top(self, *,
        name: str,
        ref_name: None=None, ref_pin: bool=False,
        ref_value: float,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        ... # pragma: no cover
    def align_top(self, *,
        name: str,
        ref_name: Optional[str]=None, ref_pin: bool=False,
        ref_value: Optional[float]=None,
        prim: _prm.DesignMaskPrimitiveT, net: Optional[_ckt._CircuitNet]=None,
    ):
        if ref_name is not None:
            self._align(
                cls=AlignTop, name=name, ref_name=ref_name, ref_pin=ref_pin,
                prim=prim, net=net,
            )
        else:
            assert ref_value is not None
            self._alignabs(
                cls=AlignTopAbs, name=name, ref_value=ref_value,
                prim=prim, net=net,
            )

    def fill(self, *,
        names: Iterable[str], prim: _prm.DesignMaskPrimitiveT,
        net: Optional[_ckt._CircuitNet]=None,
    ):
        infos = tuple(
            self.info_lookup[name]
            for name in names
        )
        self.constraint_stack.append(Fill(
            infos=infos, prim=prim, net=net,
        ))

    def extend(self, *,
        name: str, ref_name: str, prim: _prm.DesignMaskPrimitiveT,
    ):
        info = self.info_lookup[name]
        ref_info = self.info_lookup[ref_name]
        self.constraint_stack.append(Extend(
            info=info, ref_info=ref_info, prim=prim,
        ))

    def connect(self, *,
        name1: str, name2: str,
        prim: _prm.WidthSpaceConductorT, net: _ckt._CircuitNet,
    ):
        try:
            info1 = self.info_lookup[name1]
        except KeyError:
            raise ValueError(f"'{name1}' not found")
        try:
            info2 = self.info_lookup[name2]
        except KeyError:
            raise ValueError(f"'{name2}' not found")

        self.constraint_stack.append(Connect(
            info1=info1, info2=info2, prim=prim, net=net,
        ))

    def execute(self) -> bool:
        updated = True
        while updated and (len(self.constraint_stack) > 0):
            updated = False
            new_stack = []
            for align in self.constraint_stack:
                if align.apply(placer=self):
                    updated = True
                else:
                    new_stack.append(align)
            self.constraint_stack = new_stack

        return len(self.constraint_stack) == 0

