#!/usr/bin/env python3
"""
setup.py  —  FCHV_assist Offline Setup
=============================================
Run this once to install all dependencies and pre-download
the Whisper model so the app works fully offline afterwards.

  python setup.py
"""

import os
import shutil
import subprocess
import sys

# Make emojis print correctly on Windows consoles
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Always work from the folder this script lives in
os.chdir(os.path.dirname(os.path.abspath(__file__)))

SEP = "=" * 55
WHISPER_MODEL = "medium"   # must match WHISPER_MODEL in app_offline.py


def run(cmd, label):
    """Run a command given as a LIST, so paths with spaces work fine."""
    print(f"\n  Installing {label}...")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"  ⚠️  Warning: '{label}' may have failed. Check above.")
        return False
    print(f"  ✅  {label} installed.")
    return True


print(SEP)
print("  FCHV_assist — Offline Setup")
print(SEP)

# 1. Python packages
print("\n📦  Installing Python packages...")
packages = [
    ("flask",               "Flask web server"),
    ("openai-whisper",      "Whisper offline STT"),
    ("numpy",               "Audio processing"),
    ("ffmpeg-python",       "Audio conversion"),
    ("scikit-learn==1.7.2", "SVM classifier (version matches svm_model.pkl)"),
    ("requests",            "HTTP client"),
    ("gTTS",                "Text-to-speech (online)"),
    ("groq",                "Groq API client (optional)"),
]
failed = []
for pkg, label in packages:
    if not run([sys.executable, "-m", "pip", "install", pkg], label):
        failed.append(pkg)

if failed:
    print("\n  ⚠️  These packages failed to install:")
    for p in failed:
        print(f"      {p}")
    print("  Fix the errors above, then run setup.py again.")

# 2. Pre-download Whisper model
print(f"\n🤖  Pre-downloading Whisper '{WHISPER_MODEL}' model (~1.4GB)...")
print("    This only happens once. Future runs are fully offline.")
try:
    import whisper
    model = whisper.load_model(WHISPER_MODEL)
    print(f"  ✅  Whisper '{WHISPER_MODEL}' model ready.")
    del model
except Exception as e:
    print(f"  ❌  Failed to load Whisper model: {e}")
    print("      Make sure you have internet for this one-time download,")
    print("      and that the package install above succeeded.")
    sys.exit(1)

# 3. Check required files
print("\n📁  Checking required files...")
required = [
    "svm_model.pkl",
    "normalization_map.json",
    "normalized_stopwords.json",
    "normalized_suffixes.json",
    os.path.join("templates", "index.html"),
]
missing = [f for f in required if not os.path.exists(f)]
if missing:
    print("  ❌  Missing files:")
    for m in missing:
        print(f"      {m}")
    print("\n  Place all model files in the same folder as app_offline.py")
    sys.exit(1)
else:
    for f in required:
        print(f"  ✅  {f}")

# 4. Check that the SVM model actually loads
print("\n🧠  Checking SVM model loads...")
try:
    import pickle
    with open("svm_model.pkl", "rb") as fh:
        pickle.load(fh)
    print("  ✅  svm_model.pkl loads correctly.")
except Exception as e:
    print(f"  ❌  Could not load svm_model.pkl: {e}")
    print("      Try: python -m pip install scikit-learn==1.7.2")
    sys.exit(1)

# 5. Check ffmpeg
print("\n🎬  Checking ffmpeg...")
ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    try:
        result = subprocess.run([ffmpeg_path, "-version"],
                                capture_output=True, text=True)
        version = result.stdout.split("\n")[0]
        print(f"  ✅  {version[:50]}")
    except Exception:
        print(f"  ✅  ffmpeg found at {ffmpeg_path}")
else:
    print("  ⚠️  ffmpeg not found! Whisper needs it.")
    print("      Win:   winget install ffmpeg   (then restart the terminal)")
    print("             or https://ffmpeg.org/download.html")
    print("      Mac:   brew install ffmpeg")
    print("      Linux: sudo apt install ffmpeg")

print()
print(SEP)
print("  ✅  Setup complete!")
print()
print("  Run the app:")
print("    python app_offline.py")
print()
print("  Then open:  http://localhost:5000")
print(SEP)