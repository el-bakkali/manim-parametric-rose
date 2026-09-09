"""The Nylander rose under a glass cloche.

Everything shares one Manim camera, so the glass sorts correctly in front of the bloom.
"""

import os

import numpy as np
from manim import (
    DEGREES, PI, Dot, Surface, ThreeDAxes, ThreeDScene, VGroup,
)

BACKGROUND = "#15040C"
RAMP = [("#40021A", -0.40), ("#B00838", 0.05), ("#E01046", 0.45), ("#F4416A", 1.00)]

TURNS = 11.0
V_START = -2.0 * PI

ROSE_SCALE = 1.12
ROSE_Z = 0.15
DOME_R = 2.05
DOME_H = 1.95
BASE_Z = -2.05


def nylander(u: float, v: float) -> np.ndarray:
    """u in [0, 1] runs along a petal, v spirals outward through the bloom."""
    phi = (PI / 2) * np.exp(-v / (8 * PI))
    # The squared term folds v back on itself, which is what ruffles each petal edge.
    x = 1 - 0.5 * ((5 / 4) * (1 - np.mod(3.6 * v, 2 * PI) / PI) ** 2 - 0.25) ** 2
    y = 1.9565284531299512 * u**2 * (1.2765 * u - 1) ** 2 * np.sin(phi)
    r = x * (u * np.sin(phi) + y * np.cos(phi))
    return np.array([r * np.cos(v), r * np.sin(v), x * (u * np.cos(phi) - y * np.sin(phi))])


def cloche(u: float, v: float) -> np.ndarray:
    """u sweeps around, v runs up the profile: straight wall, then a domed cap."""
    if v < 0.58:
        radius, height = DOME_R, (v / 0.58) * DOME_H
    else:
        t = (v - 0.58) / 0.42 * (PI / 2)
        radius, height = DOME_R * np.cos(t), DOME_H + DOME_R * np.sin(t)
    return np.array([radius * np.cos(u), radius * np.sin(u), BASE_Z + height])


def fallen_petal(u: float, v: float) -> np.ndarray:
    width = 0.55 * np.sin(PI * u) ** 0.6
    across = v * width
    return np.array([across, u, 0.30 * across * across - 0.18 * u * u])


def tube(radius: float, z0: float, z1: float):
    def f(u: float, v: float) -> np.ndarray:
        return np.array([radius * np.cos(u), radius * np.sin(u), z0 + v * (z1 - z0)])
    return f


def disc(radius: float, z: float):
    def f(u: float, v: float) -> np.ndarray:
        return np.array([v * radius * np.cos(u), v * radius * np.sin(u), z])
    return f


def ball(radius: float, centre: tuple[float, float, float]):
    def f(u: float, v: float) -> np.ndarray:
        return np.array([centre[0] + radius * np.sin(v) * np.cos(u),
                         centre[1] + radius * np.sin(v) * np.sin(u),
                         centre[2] + radius * np.cos(v)])
    return f


class EnchantedRose(ThreeDScene):
    def construct(self):
        from manim import config

        self.camera.background_color = BACKGROUND

        axes = ThreeDAxes(
            x_range=[-1.2, 1.2, 1], y_range=[-1.2, 1.2, 1], z_range=[-0.5, 1.2, 1],
            x_length=5, y_length=5, z_length=3.5,
        )

        rose = Surface(
            nylander,
            u_range=[0.0, 1.0],
            v_range=[V_START, TURNS * PI],
            resolution=(int(os.environ.get("ROSE_U", "16")), int(os.environ.get("ROSE_V", "220"))),
            fill_opacity=1.0,
            checkerboard_colors=False,
            stroke_width=0.35,
            stroke_color="#FF6E96",
            stroke_opacity=0.35,
        )
        rose.set_fill_by_value(axes=axes, colorscale=RAMP, axis=2)
        rose.scale(ROSE_SCALE).move_to([0.0, 0.0, ROSE_Z])

        stem = Surface(tube(0.055, BASE_Z + 0.02, BASE_Z + 1.75),
                       u_range=[0.0, 2 * PI], v_range=[0.0, 1.0], resolution=(10, 6),
                       fill_color="#2E5A22", fill_opacity=1.0, checkerboard_colors=False,
                       stroke_width=0)

        base_side = Surface(tube(2.30, BASE_Z - 0.30, BASE_Z), u_range=[0.0, 2 * PI],
                            v_range=[0.0, 1.0], resolution=(72, 3),
                            fill_color="#2A1712", fill_opacity=1.0,
                            checkerboard_colors=False, stroke_width=0)
        base_top = Surface(disc(2.30, BASE_Z), u_range=[0.0, 2 * PI], v_range=[0.0, 1.0],
                           resolution=(72, 5), fill_color="#5E2E28", fill_opacity=1.0,
                           checkerboard_colors=False, stroke_width=0)
        base = VGroup(base_side, base_top)

        petals = VGroup()
        for i, (px, py, ang) in enumerate([(0.85, 0.35, 0.6), (-0.75, 0.55, 2.4),
                                           (0.20, -0.95, 4.1), (-0.95, -0.45, 5.2)]):
            petal = Surface(fallen_petal, u_range=[0.10, 0.90], v_range=[-1.0, 1.0],
                            resolution=(8, 8), fill_opacity=1.0, checkerboard_colors=False,
                            stroke_width=0)
            petal.set_fill("#C00A3C" if i % 2 else "#E4144E", opacity=1.0)
            petal.scale(0.55).rotate(ang, axis=np.array([0.0, 0.0, 1.0]))
            petal.move_to([px, py, BASE_Z + 0.04])
            petals.add(petal)

        glass = Surface(
            cloche, u_range=[0.0, 2 * PI], v_range=[0.0, 1.0],
            resolution=(52, 26),
            fill_color="#CFE9FF", fill_opacity=0.085,
            checkerboard_colors=False,
            stroke_width=0,
        )
        knob = Surface(ball(0.13, (0.0, 0.0, BASE_Z + DOME_H + DOME_R + 0.10)),
                       u_range=[0.0, 2 * PI], v_range=[0.0, PI], resolution=(14, 8),
                       fill_color="#CFE8FF", fill_opacity=0.30,
                       checkerboard_colors=False, stroke_width=0)

        sparks = VGroup()
        for i in range(24):
            seed = np.random.RandomState(i)
            a = seed.uniform(0, 2 * PI)
            r = seed.uniform(0.35, 1.55)
            z = seed.uniform(-1.40, 1.05)
            sparks.add(Dot(point=[r * np.cos(a), r * np.sin(a), z],
                           radius=seed.uniform(0.018, 0.042),
                           color="#FFE2EC", fill_opacity=seed.uniform(0.45, 1.0)))

        self.set_camera_orientation(phi=68 * DEGREES, theta=40 * DEGREES)
        self.add(base, stem, petals, rose, sparks, glass, knob)

        if config.write_to_movie:
            self.begin_ambient_camera_rotation(rate=0.14)
            self.wait(float(os.environ.get("ROSE_DURATION", "10")))
            self.stop_ambient_camera_rotation()

