#!/usr/bin/env python3
"""
rename_images.py
-----------------
Matches your local car photos to the EXACT filenames DASH's index.html expects
(assets/cars/<slug>.webp), copies/renames them into place, converts to .webp
if Pillow is installed, and prints a report of anything it couldn't match
automatically so you can fix those by hand.

HOW TO USE
1. Put this file anywhere on your PC (e.g. the root of your project folder,
   next to index.html).
2. Edit SOURCE_DIR below to point at the folder that currently holds your
   car images (wherever they live on your PC right now).
3. (Optional but recommended) install Pillow so non-webp images get
   converted automatically:
       pip install pillow
4. Run it:
       python rename_images.py
5. It creates/fills:  <project_root>/assets/cars/<slug>.webp
6. Review the "COULD NOT MATCH" list it prints at the end — rename those
   source files yourself (or drop new ones into assets/cars manually)
   using the exact slug shown.
"""

import os
import re
import shutil
import difflib

# ---- 1. EDIT THIS: folder that currently holds your car photos ----
SOURCE_DIR = r"C:\Users\YourName\Desktop\car-images"          # <-- change this to your real folder

# ---- 2. Where the site expects them (relative to this script) ----
OUTPUT_DIR = r"./assets/cars"            # matches src="assets/cars/<id>.webp" in index.html

# ---- 3. Model list pulled directly from index.html's DATA object ----
MODELS = [
    "Alto K10", "WagonR", "Swift", "Baleno", "Dzire", "Brezza", "Grand Vitara", "Fronx",
    "Grand i10 Nios", "i20", "Venue", "Creta", "Verna", "Alcazar", "Exter",
    "Tiago", "Tigor", "Punch", "Altroz", "Nexon", "Harrier", "Safari", "Curvv",
    "Bolero", "XUV 3XO", "Scorpio Classic", "Scorpio-N", "XUV700", "Thar", "Thar Roxx",
    "Sonet", "Seltos", "Carens", "Carnival", "EV6", "Syros",
    "Glanza", "Taisor", "Urban Cruiser Hyryder", "Innova Hycross", "Fortuner", "Camry",
    "Amaze", "City", "City e:HEV", "Elevate",
    "Astor", "Hector", "Gloster", "Comet EV", "ZS EV", "Windsor EV",
    "Kushaq", "Slavia", "Kodiaq", "Superb",
    "Virtus", "Taigun", "Tiguan",
]

# Manual overrides — must match MODEL_IMAGE_IDS in index.html exactly
MODEL_IMAGE_IDS = {
    "WagonR": "wagonr",
    "City e:HEV": "city-hybrid",
}

def slugify(name):
    if name in MODEL_IMAGE_IDS:
        return MODEL_IMAGE_IDS[name]
    s = name.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

def normalize_for_matching(s):
    """loose normalization so 'Grand-Vitara_photo.jpg' can match 'Grand Vitara'"""
    s = os.path.splitext(s)[0]
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '', s)
    return s

def main():
    expected = {model: slugify(model) for model in MODELS}

    if not os.path.isdir(SOURCE_DIR):
        print(f"SOURCE_DIR '{SOURCE_DIR}' does not exist. Edit the SOURCE_DIR "
              f"variable at the top of this script and try again.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    source_files = [f for f in os.listdir(SOURCE_DIR)
                     if os.path.isfile(os.path.join(SOURCE_DIR, f))]
    source_norm = {normalize_for_matching(f): f for f in source_files}

    try:
        from PIL import Image
        have_pillow = True
    except ImportError:
        have_pillow = False
        print("Pillow not installed — files will be copied with their original "
              "extension instead of converted to .webp. Run 'pip install pillow' "
              "for automatic conversion.\n")

    matched, unmatched = [], []

    for model, slug in expected.items():
        model_norm = normalize_for_matching(model)
        # try exact normalized match first
        src_name = source_norm.get(model_norm)
        # else fuzzy match against all source files
        if not src_name:
            close = difflib.get_close_matches(model_norm, source_norm.keys(), n=1, cutoff=0.72)
            src_name = source_norm.get(close[0]) if close else None

        if src_name:
            src_path = os.path.join(SOURCE_DIR, src_name)
            dst_path = os.path.join(OUTPUT_DIR, slug + ".webp")
            if have_pillow:
                try:
                    img = Image.open(src_path).convert("RGB")
                    img.save(dst_path, "webp")
                except Exception as e:
                    print(f"  ! Failed converting {src_name}: {e}")
                    shutil.copy2(src_path, os.path.join(OUTPUT_DIR, slug + os.path.splitext(src_name)[1]))
            else:
                shutil.copy2(src_path, os.path.join(OUTPUT_DIR, slug + os.path.splitext(src_name)[1]))
            matched.append((model, src_name, slug))
        else:
            unmatched.append((model, slug))

    print("MATCHED:")
    for model, src_name, slug in matched:
        print(f"  {src_name}  ->  assets/cars/{slug}.webp   ({model})")

    print("\nCOULD NOT MATCH (add these manually):")
    for model, slug in unmatched:
        print(f"  {model}  ->  needs file: assets/cars/{slug}.webp")

    print(f"\nDone. {len(matched)} matched, {len(unmatched)} need manual attention.")

if __name__ == "__main__":
    main()
