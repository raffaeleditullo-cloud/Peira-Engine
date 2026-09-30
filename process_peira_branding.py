import base64
from PIL import Image
import numpy as np
import pathlib

logos_dir = pathlib.Path(r"c:\Users\stree\Desktop\Peira-Engine\logos")
logos_dir.mkdir(parents=True, exist_ok=True)

img_p = pathlib.Path(r"C:\Users\stree\.gemini\antigravity\brain\a70d1552-e1ca-4aaa-a384-61ec646d76b3\peira_symbol_core_1790756132490.jpg")
img = Image.open(img_p).convert("RGB")
arr = np.array(img, dtype=np.float32)

r = arr[:, :, 0]
g = arr[:, :, 1]
b = arr[:, :, 2]

# Pitch black background extraction
brightness = np.maximum(r, np.maximum(g, b))
threshold = 12.0
max_val = np.percentile(brightness[brightness > 30], 98)
alpha = np.clip((brightness - threshold) / (max_val - threshold) * 255.0, 0, 255).astype(np.uint8)

# Zero out dark background
alpha[brightness <= threshold] = 0

rgba = np.zeros((1024, 1024, 4), dtype=np.uint8)
rgba[:, :, 0] = np.clip(r * 1.12, 0, 255).astype(np.uint8)
rgba[:, :, 1] = np.clip(g * 1.12, 0, 255).astype(np.uint8)
rgba[:, :, 2] = np.clip(b * 1.12, 0, 255).astype(np.uint8)
rgba[:, :, 3] = alpha

master = Image.fromarray(rgba, "RGBA")
master.save(logos_dir / "peira_core_1024.png")
master.resize((512, 512), Image.Resampling.LANCZOS).save(logos_dir / "peira_core.png")
master.resize((512, 512), Image.Resampling.LANCZOS).save(pathlib.Path(r"c:\Users\stree\Desktop\Peira-Engine\logo.png"))

# Create scalable SVG wrapper
with open(logos_dir / "peira_core.png", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("ascii")

svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <image href="data:image/png;base64,{b64}" width="512" height="512" />
</svg>"""

(logos_dir / "peira_core.svg").write_text(svg_content, encoding="utf-8")
(pathlib.Path(r"c:\Users\stree\Desktop\Peira-Engine\logo.svg")).write_text(svg_content, encoding="utf-8")

print("Peira transparent branding created successfully!")
