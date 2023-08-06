from pathlib import Path
import course_search

# Project Directories
PACKAGE_ROOT = Path(course_search.__file__).resolve().parent
ROOT = PACKAGE_ROOT.parent
CONFIG_FILE_PATH = PACKAGE_ROOT / "params.yaml"
DATASET_DIR = PACKAGE_ROOT / "index"
PICKLE_FILE_PATH = PACKAGE_ROOT / "index/ssg_courses_full_indexed.csv"


def find_config_file() -> Path:
    """Locate the configuration file."""
    if CONFIG_FILE_PATH.is_file():
        return CONFIG_FILE_PATH
    raise Exception(f"Config not found at {CONFIG_FILE_PATH!r}")