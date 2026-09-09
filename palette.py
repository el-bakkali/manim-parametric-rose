"""Sample the dominant colours of a reference frame to match its palette."""

import sys

import numpy as np
from PIL import Image


def main(path: str) -> None:
    image = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32)
    flat = image.reshape(-1, 3)
    luma = flat @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)

    bands = {
        "background (darkest 40%)": luma <= np.percentile(luma, 40),
        "midtone glow (70-92%)": (luma > np.percentile(luma, 70)) & (luma <= np.percentile(luma, 92)),
        "highlight (top 2%)": luma >= np.percentile(luma, 98),
    }
    for name, mask in bands.items():
        mean = flat[mask].mean(axis=0)
        normalized = mean / max(mean.max(), 1e-6)
        print(f"{name:26s} rgb=({mean[0]:5.1f},{mean[1]:5.1f},{mean[2]:5.1f})  "
              f"normalized=({normalized[0]:.3f}, {normalized[1]:.3f}, {normalized[2]:.3f})")

    bright = flat[luma >= np.percentile(luma, 85)]
    hue_ratio = bright[:, 0] / np.maximum(bright[:, 2], 1e-6)
    print(f"\nbright pixels R/B ratio: mean={hue_ratio.mean():.3f} median={np.median(hue_ratio):.3f}")
    print(f"bright pixels G/B ratio: mean={(bright[:,1]/np.maximum(bright[:,2],1e-6)).mean():.3f}")
    print(f"overall mean rgb: {flat.mean(axis=0).round(1)}")


if __name__ == "__main__":
    main(sys.argv[1])
