import numpy as np

try:
    import spectra
    from colormath.density import auto_density
    from colormath.color_objects import LabColor as LabColor
    from colormath.color_diff import delta_e_cie1994
except ImportError:
    msg = (
        "Generating plotly.py figure templates from bootstrap theme files requires\n"
        "the optional spectra and tinycss2 packages, which can be installed using pip...\n"
        "    $ pip install spectra tinycss2\n"
        "or conda...\n"
        "    $ conda install -c conda-forge spectra tinycss2"
    )
    raise ValueError(msg)


white = spectra.lab(100, 0, 0)
black = spectra.lab(0, 0, 0)


def to_colormath(spectra_color):
    lab_values = spectra.html(spectra_color.hexcode).to("lab").values
    return LabColor(*lab_values)


def color_distance(clr1, clr2):
    return delta_e_cie1994(to_colormath(clr1), to_colormath(clr2))


# Distance matric
def color_distance_matrix(colors):
    return np.array(
        [
            [color_distance(c1, c2) for i, c1 in enumerate(colors)]
            for j, c2 in enumerate(colors)
        ],
        dtype="float32",
    )


def get_darkened_colors(colors, darkening_list):
    return [c.darken(d) for c, d in zip(colors, darkening_list)]


def best_darkening(c1, c2, c1_step=(1, 1), c2_step=(1, 1)):
    d = color_distance(c1, c2)
    d1 = color_distance(c1.darken(c1_step[1]), c2)
    dm1 = color_distance(c1.darken(c1_step[0]), c2)
    d2 = color_distance(c1, c2.darken(c2_step[1]))
    dm2 = color_distance(c1, c2.darken(c2_step[0]))

    # Return step with sign that increases distance most
    # Return 0 if either step lower distance
    return sorted(
        [
            (d, (0, 0)),
            (d1, (c1_step[1], 0)),
            (dm1, (c1_step[0], 0)),
            (d2, (0, c2_step[1])),
            (dm2, (0, c2_step[0])),
        ]
    )[-1]


def separate_colorway(html_colors):

    try:
        raw_colors = [
            spectra.rgb(*[c / 255 for c in to_rgb_tuple(clr)]) for clr in html_colors
        ]
    except ValueError:
        # Unable to parse colors as hex or rgb, return as-is
        return html_colors

    test_colors = [white] + raw_colors + [black]

    darkenings = list(np.zeros(len(test_colors)))
    threshold = 36

    max_shift = 16
    max_step = 16
    max_iterations = 4
    max_step_factor = 0.9

    iterations = 0
    distances = np.ones((len(html_colors) + 2, len(html_colors) + 2)) * np.nan

    while iterations < max_iterations:
        for i in range(len(test_colors) - 1):
            c1 = test_colors[i].darken(darkenings[i])
            for j in range(i + 1, len(test_colors)):
                c2 = test_colors[j].darken(darkenings[j])
                distance = color_distance(c1, c2)
                distances[i, j] = distance

                # When comparing to black and white,
                # skip if at least threshold units away
                if distance > threshold:
                    continue

                # Compute max step based on how close colors are
                this_step = max_step * ((100 - distance) / 100) ** 2

                # Clamp max steps based on how close we are to max shift allowances
                c1_step_up = max(0, min(this_step, max_shift - darkenings[i]))
                c2_step_up = max(0, min(this_step, max_shift - darkenings[j]))
                c1_step_down = min(0, max(-this_step, -darkenings[i] - max_shift))
                c2_step_down = min(0, max(-this_step, -darkenings[j] - max_shift))

                # Compute best way to lighten or darken ONE of the colors (not both)
                distance, (delta1, delta2) = best_darkening(
                    c1,
                    c2,
                    c1_step=(c1_step_down, c1_step_up),
                    c2_step=(c2_step_down, c2_step_up),
                )
                distances[i, j] = distance

                darkenings[i] += delta1
                darkenings[j] += delta2

        iterations += 1
        max_step *= max_step_factor

    result = [clr.hexcode for clr in get_darkened_colors(test_colors, darkenings)[1:-1]]

    return result


def hex_to_rgb(clr):
    clr = clr.lstrip("#")
    if len(clr) == 3:
        clr = "".join(c[0] * 2 for c in clr)
    return tuple(int(clr[i : i + 2], 16) for i in (0, 2, 4))


def to_rgb_tuple(color):
    from plotly.colors import unlabel_rgb

    if isinstance(color, tuple):
        pass
    elif color.startswith("#"):
        color = hex_to_rgb(color)
    else:
        color = unlabel_rgb(color)

    return tuple(int(c) for c in color)


def make_grid_color(bg_color, font_color, weight=0.1):
    bg_color = to_rgb_tuple(bg_color)
    font_color = to_rgb_tuple(font_color)

    s_bg_color = spectra.rgb(*[c / 255 for c in bg_color])
    s_font_color = spectra.rgb(*[c / 255 for c in font_color])
    return s_bg_color.blend(s_font_color, weight).hexcode


def maybe_blend(base_color, overlay_color):
    """
    Try to blend semi transparent overlay color on opaque
    base color. Return None if not successful
    """
    import re

    try:
        bc = spectra.html(base_color).to("rgb")
    except ValueError:
        return None

    try:
        # If overlay color is hex code or named color, it's
        # opaque, return as is
        return spectra.html(overlay_color).hexcode
    except ValueError:
        # Otherwise, it might be rgba
        pass

    rgba_match = re.match(r"rgba\(([^,]+),([^,]+),([^,]+),([^,]+)\)", overlay_color)
    if rgba_match is None:
        return None

    r, g, b, a = [float(n) for n in rgba_match.groups()]
    overlay_rgb = spectra.rgb(r / 255, g / 255, b / 255)
    blended = overlay_rgb.blend(bc, 1 - a)
    return blended.hexcode
