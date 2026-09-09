"""A 1080x1920 still: the rendered scene as background, the maths typeset over it.

Expects docs/poster-src.png (a still of EnchantedRose); poster.ps1 renders that first.
"""

from pathlib import Path

from manim import DOWN, UP, ImageMobject, MathTex, Scene, Text, VGroup, config
from PIL import Image, ImageDraw, ImageFilter

WIDTH, HEIGHT = 1080, 1920
SOURCE = Path(__file__).with_name("docs") / "poster-src.png"
BACKGROUND = Path(__file__).with_name("docs") / "poster-bg.png"

INK = "#FFE8EF"
ACCENT = "#FF6E96"

BLOCKS = [
    ("Petals lie flatter further out", [r"\varphi(v) = \tfrac{\pi}{2}\,e^{-v/8\pi}"]),
    ("Folding v ruffles every edge", [r"X \sim \left(v \bmod 2\pi\right)^{2}"]),
]

# Drop the cloche into the lower half so the maths sits over empty space.
SUBJECT_DROP = 500


def compose_background(source: Path, target: Path) -> None:
    render = Image.open(source).convert("RGBA").resize((WIDTH, HEIGHT), Image.LANCZOS)

    # The top of the render is flat background, so stretching it fills the gap invisibly.
    frame = Image.new("RGBA", (WIDTH, HEIGHT))
    frame.paste(render.crop((0, 0, WIDTH, 4)).resize((WIDTH, SUBJECT_DROP)), (0, 0))
    frame.paste(render.crop((0, 0, WIDTH, HEIGHT - SUBJECT_DROP)), (0, SUBJECT_DROP))

    mask = Image.new("L", (WIDTH, HEIGHT), 0)
    draw = ImageDraw.Draw(mask)
    fade_end = 1080
    for y in range(fade_end):
        draw.line([(0, y), (WIDTH, y)], fill=int(110 * min((fade_end - y) / 240, 1.0)))
    mask = mask.filter(ImageFilter.GaussianBlur(50))

    scrim = Image.new("RGBA", (WIDTH, HEIGHT), (8, 2, 6, 255))
    scrim.putalpha(mask)
    frame.alpha_composite(scrim)

    target.parent.mkdir(parents=True, exist_ok=True)
    frame.convert("RGB").save(target)


class Poster(Scene):
    def construct(self):
        if not SOURCE.exists():
            raise FileNotFoundError(f"{SOURCE} missing - run poster.ps1, which renders it first.")
        compose_background(SOURCE, BACKGROUND)

        backdrop = ImageMobject(str(BACKGROUND))
        backdrop.height = config.frame_height
        self.add(backdrop)

        title = Text("A rose made of equations", font_size=31, color=INK, weight="BOLD")
        subtitle = Text("no mesh, no textures  ·  Manim", font_size=19,
                        color=ACCENT, slant="ITALIC")
        heading = VGroup(title, subtitle).arrange(DOWN, buff=0.16)
        heading.scale_to_fit_width(config.frame_width * 0.84)
        heading.to_edge(UP, buff=0.85)

        widest = config.frame_width * 0.88
        blocks = VGroup()
        for caption, equations in BLOCKS:
            lines = VGroup(*[MathTex(e, font_size=30, color=INK) for e in equations])
            lines.arrange(DOWN, buff=0.14)
            if lines.width > widest:
                lines.scale_to_fit_width(widest)
            blocks.add(VGroup(Text(caption, font_size=17, color=ACCENT), lines).arrange(DOWN, buff=0.16))
        blocks.arrange(DOWN, buff=0.34)
        blocks.next_to(heading, DOWN, buff=0.42)

        self.add(heading, blocks)

        def band(mobject) -> str:
            top = (config.frame_height / 2 - mobject.get_top()[1]) / config.frame_height * HEIGHT
            bottom = (config.frame_height / 2 - mobject.get_bottom()[1]) / config.frame_height * HEIGHT
            return f"y {top:6.0f} -> {bottom:6.0f} px"

        print(f"heading  {band(heading)}")
        print(f"blocks   {band(blocks)}   width {blocks.width:.2f} / {config.frame_width:.2f}")
        print(f"text margins: 190 -> {HEIGHT - 330} px")
