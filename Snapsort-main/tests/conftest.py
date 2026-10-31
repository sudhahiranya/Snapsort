import os
import shutil
from datetime import date

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

import pytest

from scripts.make_mock_data import generate
from snapsort import db
from snapsort.config import Settings


@pytest.fixture
def settings(tmp_path):
    s = Settings(root=tmp_path.resolve())
    s.ensure_dirs()
    return s


@pytest.fixture
def conn(settings):
    c = db.connect(settings.db_path)
    yield c
    c.close()


@pytest.fixture(scope="session")
def mock_dir(tmp_path_factory):
    root = tmp_path_factory.mktemp("gen").resolve() / "mock"
    generate(root, today=date.today())
    return root
