"""Paul Nylander's parametric rose, plotted as a Manim surface.

Two parameters sweep the whole bloom: u across a petal, v spiralling outward.
"""

import os

import numpy as np
from manim import (
    DEGREES, PI, Surface, ThreeDAxes, ThreeDScene, config,
)

# Each turn of v lays down another layer of petals.
TURNS = 14.0
V_START = -2.0 * PI

BACKGROUND = "#05010A"
RAMP = [("#40021A", -0.40), ("#B00838", 0.05), ("#F51E52", 0.45), ("#FF5C2E", 1.00)]


def nylander(u: float, v: float) -> np.ndarray:
    """u in [0, 1] runs along a petal, v spirals outward through the bloom."""
    phi = (PI / 2) * np.exp(-v / (8 * PI))
    # The squared term folds v back on itself, which is what ruffles each petal edge.
    x = 1 - 0.5 * ((5 / 4) * (1 - np.mod(3.6 * v, 2 * PI) / PI) ** 2 - 0.25) ** 2
    y = 1.9565284531299512 * u**2 * (1.2765 * u - 1) ** 2 * np.sin(phi)
    r = x * (u * np.sin(phi) + y * np.cos(phi))
    return np.array([r * np.cos(v), r * np.sin(v), x * (u * np.cos(phi) - y * np.sin(phi))])


class NylanderRose(ThreeDScene):
    def construct(self):
        self.camera.background_color = BACKGROUND
        spin = float(os.environ.get("ROSE_SPIN", "0"))

        axes = ThreeDAxes(
            x_range=[-1.2, 1.2, 1], y_range=[-1.2, 1.2, 1], z_range=[-0.5, 1.2, 1],
            x_length=5, y_length=5, z_length=3.5,
        )

        rose = Surface(
            nylander,
            u_range=[0.0, 1.0],
            v_range=[V_START, TURNS * PI],
            resolution=(int(os.environ.get("ROSE_U", "20")), int(os.environ.get("ROSE_V", "300"))),
            fill_opacity=1.0,
            checkerboard_colors=False,
            stroke_width=0.7,
            stroke_color="#FFB3C8",
            stroke_opacity=0.65,
        )
        rose.set_fill_by_value(axes=axes, colorscale=RAMP, axis=2)
        rose.scale(2.75).move_to([0.0, 0.0, 0.0])

        self.set_camera_orientation(phi=64 * DEGREES, theta=(40 + spin) * DEGREES)
        self.add(rose)

        if config.write_to_movie:
            self.begin_ambient_camera_rotation(rate=0.16)
            self.wait(float(os.environ.get("ROSE_DURATION", "12")))
            self.stop_ambient_camera_rotation()
