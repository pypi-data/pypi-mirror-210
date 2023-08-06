from __future__ import annotations

import enum
import functools
from typing import List, Iterable, Literal, Optional
import bisect
import dataclasses


class DecaySchema:
    def __init__(self):
        self.nuclides: List[Nuclide] = []
        self.current_nuclide: int = 0
        self.num_nuclides: int = 0
        self.decays: List[Decay] = []
        # self.decays_to_coordinates = []
        self.freetexts = []
        self.freearrows = []
    
    def add_nuclide(self, nuclide: Nuclide):
        bisect.insort(self.nuclides, nuclide)
        self.num_nuclides += 1
    
    def __iter__(self) -> List[Nuclide]:
        return self.nuclides
    
    def __str__(self) -> str:
        result = "------ Decay schema ------\n"
        for nuclide in self.nuclides:
            result += str(nuclide) + "\n"
        return result

    def __repr__(self) -> str:
        return f"<DecaySchema({self.nuclides})>"
    
    def add_decay(self, decay: Decay):
        self.decays.append(decay)

    def add_freetext(self, freetext: FreeText):
        self.freetexts.append(freetext)

    def add_freearrow(self, freearrow: FreeArrow):
        self.freearrows.append(freearrow)


@functools.total_ordering
@dataclasses.dataclass(init=True, repr=True, kw_only=True, eq=True)
class Nuclide:
    index: int
    name: str
    horizontal_padding: float = 0

    def __post_init__(self):
        if self.index < 0:
            raise ValueError(f"Nuclide index must be positive. Was {self.index}.")
        self.levels: List[Level] = []
        self.num_levels: int = 0
    
    def add_level(self, level: Level):
        bisect.insort(self.levels, level)
        self.num_levels += 1
    
    def __lt__(self, other: Nuclide):
        return self.index < other.index


class Parity(enum.Enum):
    """Represents the two parity options available."""
    UP = "+"
    DOWN = "-"


@functools.total_ordering
@dataclasses.dataclass(init=True, kw_only=True, eq=True)
class Level:
    energy: float
    spin: str
    parity: Parity
    ls: str = '-'
    lw: float = 1.
    color: str = 'k'
    text_above: Optional[str] = None
    text_below: Optional[str] = None
    energy_format_string: Optional[str] = None
    draw_QEC_level_below: bool = False
    draw_reference_line: bool = False
    hide_energy_spin_parity: bool = False
    energy_spin_parity_below: bool = False
    broad: bool = False
    many: bool = False
    width: float = 0
    upper_energy: float = 0.
    upper_spin: Optional[str] = None
    upper_parity: Optional[Parity] = None
    energy_x_adjust: float = 0.
    energy_y_adjust: float = 0.
    spin_parity_x_adjust: float = 0.
    spin_parity_y_adjust: float = 0.
    text_above_x_adjust: float = 0.
    text_above_y_adjust: float = 0.
    text_below_x_adjust: float = 0.
    text_below_y_adjust: float = 0.
    QEC_x_adjust: float = 0.
    QEC_y_adjust: float = 0.
    upper_energy_x_adjust: float = 0.
    upper_energy_y_adjust: float = 0.
    upper_spin_parity_x_adjust: float = 0.
    upper_spin_parity_y_adjust: float = 0.

    def __lt__(self, other: Level):
        return self.energy < other.energy
    
    def __repr__(self) -> str:
        f = "1.1f" if self.energy_format_string is None else self.energy_format_string
        return f"<Level(E={self.energy:{f}}, J={self.spin}, pi={self.parity})>"


@dataclasses.dataclass(init=True, kw_only=True, eq=True)
class Decay:
    parent_nuclide: Nuclide
    parent_level: Level
    daughter_nuclide: Nuclide
    daughter_level: Level
    color: str = "k"
    ls: str = "-"
#
#
# class decay_to_coordinate:
#     def __init__(self, parent_nuclide, parent_level, x, y, color='k'):
#         self.parent_nuclide = parent_nuclide
#         self.parent_level = parent_level
#         self.x = x
#         self.y = y
#         self.color = color
#


@dataclasses.dataclass(init=True, kw_only=True, eq=True)
class FreeText:
    text: str
    x: float
    y: float
    va: str = "center"
    ha: str = "center"
    rotation: float = 0
    color: str = "k"


@dataclasses.dataclass(init=True, kw_only=True, eq=True)
class FreeArrow:
    startx: float
    starty: float
    endx: float
    endy: float
    color: str = "k"
    ls: str = "-"
