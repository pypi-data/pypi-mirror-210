import logging
from pathlib import Path

import numpy as np
from matplotlib.path import Path as mpl_path
from matplotlib.markers import MarkerStyle
from matplotlib import transforms
import matplotlib.pyplot as plt

from .decay_scheme_classes import DecaySchema


class DecaySchemeDrawer:
    bracket_offset = 0.04
    QEC_text_offset = 0.2
    below_text_offset = 0.07
    above_text_offset = 0.
    mec2 = 0.51099895000
    energy_format_string = "2.3f"

    def __init__(self):
        data_dir = Path(__file__).parent / "data"
        arrowhead_vertices = np.loadtxt(data_dir / 'arrowhead_vertices.dat')
        arrowhead_vertices[:, 0] = arrowhead_vertices[:, 0] - np.min(arrowhead_vertices[:, 0])
        arrowhead_vertices[:, 1] = arrowhead_vertices[:, 1] - np.mean(arrowhead_vertices[:, 1]) - 0.05
        arrowhead_codes = np.loadtxt(data_dir / 'arrowhead_codes.dat')
        self.arrowhead = mpl_path(arrowhead_vertices, arrowhead_codes)

    class UnsizedMarker(MarkerStyle):
        def _set_custom_marker(self, path):
            self._transform = transforms.IdentityTransform()
            self._path = path

    def draw_arrow(self, ax, x1, y1, x2, y2, *, color, ls):
        ax.plot([x1, x2], [y1, y2], color=color, lw=0.5, ls=ls)

        r1 = np.array([x1, y1])
        r2 = np.array([x2, y2])
        r = r2 - r1
        n = r / np.linalg.norm(r)
        leftt, rightt = ax.get_xlim()
        bottomm, topp = ax.get_ylim()
        a = (topp - bottomm)/(rightt - leftt)
        b = 2
        n[0] *= a/b
        angle = np.arctan2(n[1], n[0]) + np.deg2rad(180.)

        tr = transforms.Affine2D().rotate(angle)
        m = self.UnsizedMarker(self.arrowhead.transformed(tr))
        ax.scatter(x2, y2, marker=m, s=0.3, color=color)

    def calculate_arrow_offsets(self, x1, y1, x2, y2):
        # index offset
        if x1 < x2:
            x1 += 1
        else:
            x2 += 1

        # arrowhead offset
        dx = 0.02
        dy = 0.12 * abs(y1 - y2)
        if x1 < x2:
            x2 -= dx
        else:
            x2 += dx
        if y1 < y2:
            y2 -= dy
        else:
            y2 += dy

        return x1, y1, x2, y2

    def draw_decay_scheme(self, 
                            decay_scheme: DecaySchema, *,
                            ax: plt.Axes,
                            hor_padding=0.3,
                          ) -> plt.Axes:
        found_index_zero = any([nuclide.index == 0 for nuclide in decay_scheme.nuclides])  # Check if any nuclide has index 0
        if not found_index_zero:
            logging.warning("Some drawing features relies on the left-most nuclide having index zero, '0'.")

        total_nuclide_padding = sum([n.horizontal_padding for n in decay_scheme.nuclides])

        columns = decay_scheme.num_nuclides
        total_width = columns + total_nuclide_padding + columns*hor_padding

        padding = 0.
        for nuclide in decay_scheme.nuclides:
            x1 = (nuclide.index + padding) / total_width
            x2 = (nuclide.index + 1 + padding) / total_width
            for level in nuclide.levels:
                energy_format_string = level.energy_format_string if level.energy_format_string else self.energy_format_string
                ax.axhline(level.energy+level.energy_y_adjust, x1, x2, ls=level.ls, lw=level.lw, color=level.color, )
                if level.broad:
                    upper = level.energy + level.width
                    lower = level.energy - level.width
                    left = x1 * (total_width - columns * hor_padding)
                    right = x2 * (total_width - columns * hor_padding)
                    ax.fill([left, left, right, right], [lower, upper, upper, lower], color='silver', lw=0.)
                if not level.hide_energy_spin_parity:
                    e_string = f"{level.energy:{energy_format_string}}" if level.energy != 0. else "0.0"
                    s_p_string = f"${level.spin}^{level.parity.value}$"
                    if not level.broad and not level.many:
                        if not level.energy_spin_parity_below:
                            E_text = ax.text( x1*(total_width - columns*hor_padding) + level.energy_x_adjust,
                                             level.energy + self.above_text_offset + level.energy_y_adjust,
                                             e_string, ha='left', va='bottom', transform=ax.transData)
                            ax.text(x2*(total_width - columns*hor_padding) + level.spin_parity_x_adjust,
                                    level.energy + self.above_text_offset + level.spin_parity_y_adjust,
                                    s_p_string, ha='right', va='bottom', transform=ax.transData)
                        else:
                            raise NotImplementedError
                    elif level.broad:
                        upper_e_string = f"{level.energy:{energy_format_string}}"
                        E_text = ax.text(x1*(total_width - columns*hor_padding) + level.energy_x_adjust,
                                         level.energy + level.width + self.above_text_offset + level.energy_y_adjust + level.upper_energy_y_adjust,
                                         upper_e_string, ha='left', va='bottom')
                        ax.text(x2*(total_width - columns*hor_padding) + level.spin_parity_x_adjust,
                                     level.energy + level.width + self.above_text_offset + level.spin_parity_y_adjust + level.upper_spin_parity_y_adjust,
                                s_p_string, ha='right', va='bottom')
                    elif level.many:
                        raise NotImplementedError
                if level.draw_QEC_level_below:
                    raise NotImplementedError
                if level.draw_reference_line:
                    raise NotImplementedError
                if level.text_below:
                    below_text = ax.text( 0.5*(x1+x2)*(total_width - columns*hor_padding) + level.text_below_x_adjust,
                                          level.energy - 0.5*self.below_text_offset + level.text_below_y_adjust, level.text_below, va='top', ha='center')
                if level.text_above:
                    raise NotImplementedError
            padding += hor_padding
        for decay in decay_scheme.decays:
            # this part should be simple, but matplotlib's standard arrows are ugly because their heads are drawn relative to data coordinates; "fancyarrowpatches" do not have this problem, but the variety of head shapes is limitied... so we draw the arrows ourselves
            # may the user ImportanceOfBeingErnest be prosperous and succesful and have many beautiful children! https://stackoverflow.com/questions/53227057/size-distortion-when-rotating-custom-path-marker-in-matplotlib
            pn = decay.parent_nuclide
            pl = decay.parent_level
            dn = decay.daughter_nuclide
            dl = decay.daughter_level

            start_x = (1+ pn.index*(1 + hor_padding)) / total_width * (total_width - columns * hor_padding)
            start_y = pl.energy

            end_x = ( dn.index*(1+hor_padding)) / total_width * (total_width - columns * hor_padding)
            end_y = dl.energy
            self.draw_arrow(ax, start_x, start_y, end_x, end_y, color=decay.color, ls=decay.ls)

        for farrow in decay_scheme.freearrows:
            self.draw_arrow(ax, farrow.startx, farrow.starty, farrow.endx, farrow.endy, color=farrow.color, ls=farrow.ls)
        for ftext in decay_scheme.freetexts:
            ax.text(ftext.x, ftext.y, ftext.text, va=ftext.va, ha=ftext.ha, rotation=ftext.rotation, color=ftext.color)

        ax.axis("off")
        return ax
