#!/usr/bin/env python3
import argparse, time, sys, re, tempfile
from pathlib import Path
from roboflow import Roboflow
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

############################
# 1 ─ CLI & CONFIG
############################
def parse_args():
    ap = argparse.ArgumentParser(description="LC-slice pipeline")
    ap.add_argument("--in",  "-i", required=True, help="Folder of raw .tif stacks")
    ap.add_argument("--out", "-o", required=True, help="Destination folder")
    ap.add_argument("--conf", default=0.9, type=float, help="Min confidence")
    ap.add_argument("--watch", action="store_true",
                    help="Watch input folder & process new stacks automatically")
    return ap.parse_args()

# Roboflow init once
rf = Roboflow(api_key="")
model = rf.workspace("your-workspace").project("lc-stacker").version("2").model

############################
# 2 ─ Core processing fn
############################
def process_stack(tiff_path: Path, out_dir: Path, conf_th: float = 0.9):
    try:
        print(f"→ Processing {tiff_path.name}")
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # 2a. Split to JPEG
            slices = []
            with Image.open(tiff_path) as im:
                for i in range(im.n_frames):
                    im.seek(i)
                    p = tmp / f"{tiff_path.stem}_{i:04d}.jpg"
                    im.convert("RGB").save(p, "JPEG", quality=95)
                    slices.append((i, p))
            # 2b. Classify & keep LC
            keep = []
            for idx, jpeg in slices:
                pred = model.predict(str(jpeg)).json()["predictions"][0]
                if pred.get("top", "").lower().strip().replace(" ", "").replace("_", "-") == "lc" \
                   and pred["confidence"] >= conf_th:
                    keep.append((idx, Image.open(jpeg)))
            if not keep:
                print("   – No LC slices; skipping")
                return
            keep.sort(key=lambda x: x[0])
            imgs = [im.convert("L") for _, im in keep]
            out_dir.mkdir(exist_ok=True, parents=True)
            out_path = out_dir / f"{tiff_path.stem}_LC_only.tif"
            imgs[0].save(out_path, save_all=True, append_images=imgs[1:])
            print(f"   ✔ Saved {len(imgs)} slices → {out_path}")
    except Exception as e:
        print(f"   ✖ Error on {tiff_path.name}: {e}")

############################
# 3 ─ Optional folder-watch
############################
class StackHandler(FileSystemEventHandler):
    def __init__(self, out_dir, conf): self.out_dir, self.conf = out_dir, conf
    def on_created(self, ev):
        p = Path(ev.src_path)
        if p.suffix.lower() == ".tif":
            time.sleep(1)  # let file finish writing
            process_stack(p, self.out_dir, self.conf)

def main():
    args = parse_args()
    in_dir, out_dir = Path(args.__dict__["in"]), Path(args.out)
    for tif in in_dir.glob("*.tif"):
        process_stack(tif, out_dir, args.conf)
    if args.watch:
        obs = Observer()
        obs.schedule(StackHandler(out_dir, args.conf), str(in_dir))
        obs.start()
        print("⌛ Watching for new .tif stacks – press Ctrl+C to stop")
        try:  # keep alive
            while True: time.sleep(2)
        except KeyboardInterrupt:
            obs.stop()
        obs.join()

if __name__ == "__main__":
    main()
