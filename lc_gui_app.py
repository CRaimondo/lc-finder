#!/usr/bin/env python3
"""
LC-Finder – drag-and-drop GUI
Save in the same directory as lc_pipeline.py
"""

# ── Standard-library imports ─────────────────────────────────────────────
from pathlib import Path
import tempfile
import traceback
import sys
import re

# ── Third-party imports ──────────────────────────────────────────────────
import PySimpleGUI as sg            # pip install PySimpleGUI
from PIL import Image               # pip install pillow
from roboflow import Roboflow       # pip install roboflow

# ── Roboflow init (same creds as pipeline) ───────────────
from roboflow import Roboflow
RF_API_KEY   = "lq5fV0GkEKF4NWmvbI2n"
RF_WORKSPACE = "your-workspace"    # ← update if needed
RF_PROJECT   = "lc-stacker"
RF_VERSION   = "2"

rf    = Roboflow(api_key=RF_API_KEY)
model = rf.workspace(RF_WORKSPACE).project(RF_PROJECT).version(RF_VERSION).model

# ── Core function: split → classify → reassemble ─────────
def process_stack(tiff_path: Path, out_dir: Path, conf_th: float = 0.9):
    print(f"\n▶ {tiff_path.name}")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # 1 ▸ TIFF → JPEG slices
            slices = []
            with Image.open(tiff_path) as im:
                for i in range(getattr(im, "n_frames", 1)):
                    im.seek(i)
                    jpg = tmpdir / f"{tiff_path.stem}_{i:04d}.jpg"
                    im.convert("RGB").save(jpg, "JPEG", quality=95)
                    slices.append((i, jpg))

            # 2 ▸ Classify, keep LC≥threshold
            keep = []
            for idx, jpg in slices:
                res = model.predict(str(jpg)).json()
                if not res["predictions"]:
                    continue
                p = res["predictions"][0]
                if p["top"].strip().lower().replace(" ", "").replace("_", "-") == "lc" \
                   and float(p["confidence"]) >= conf_th:
                    keep.append((idx, Image.open(jpg)))

            if not keep:
                print("   – No LC slices found.")
                return

            keep.sort(key=lambda x: x[0])
            imgs = [im.convert("L") for _, im in keep]

            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"{tiff_path.stem}_LC_only.tif"
            imgs[0].save(out_path, save_all=True, append_images=imgs[1:])
            print(f"   ✔ Saved {len(imgs)} slices → {out_path}")
    except Exception:
        print("   ✖ Error:")
        traceback.print_exc(file=sys.stdout)

# ── GUI definition ───────────────────────────────────────
sg.theme("SystemDefault")

default_in  = str(Path.home() / "Desktop/ACORN/lc-finder/inputs")
default_out = str(Path.home() / "Desktop/ACORN/lc-finder/reassembled_outputs")

layout = [
    [sg.Text("Input folder (raw .tif stacks):"),
     sg.Input(default_in, key="-IN-"),  sg.FolderBrowse()],

    [sg.Text("Output folder:"),
     sg.Input(default_out, key="-OUT-"), sg.FolderBrowse()],

    [sg.Text("Min LC confidence:"), sg.Input("0.90", size=(6,1), key="-CONF-")],
    [sg.Button("Run"), sg.Button("Exit")],
    [sg.Output(size=(100,25), key="-LOG-")]
]

window = sg.Window("LC Stack Processor", layout, finalize=True)

# ── Event loop ───────────────────────────────────────────
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "Exit"):
        break

    if event == "Run":
        in_dir  = Path(values["-IN-"]).expanduser()
        out_dir = Path(values["-OUT-"]).expanduser()
        try:
            conf   = float(values["-CONF-"])
        except ValueError:
            print("Invalid confidence value; using 0.90.")
            conf = 0.90

        if not in_dir.exists():
            print(f"✖ Input folder not found: {in_dir}")
            continue

        tiffs = list(in_dir.glob("*.tif")) + list(in_dir.glob("*.tiff"))
        if not tiffs:
            print(f"✖ No .tif/.tiff files in {in_dir}")
            continue

        print(f"\nProcessing {len(tiffs)} stack(s)…")
        for tif in tiffs:
            process_stack(tif, out_dir, conf)
        print("\n✓ Done.\n")

window.close()