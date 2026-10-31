"""SnapSort: an offline Gemma 4 agent that organises personal documents on this laptop."""
import os
import shutil

# Ensure Tesseract OCR is found on Windows if installed in common directories
if not shutil.which("tesseract"):
    for cand in (
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR"),
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
    ):
        if os.path.isdir(cand) and cand not in os.environ.get("PATH", ""):
            os.environ["PATH"] = cand + os.pathsep + os.environ.get("PATH", "")
            break
