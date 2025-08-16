import shutil
import warnings
from pathlib import Path
from zipfile import ZipFile



def unzip_archive(f_path: str|Path, target_dir: str|Path) -> None:
    """
    Unzip file.

    Args:
        f_path (str|Path): File to unzip.
        target_dir (str|Path): Directory to unzip into.
    """
    f_path = Path(f_path)
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(f_path) as zip_f:
        zip_f.extractall(target_dir)


def remove_dir(dir_path: str, remove_nonempty: bool = False) -> None:
    """
    Remove directory.
    """
    assert dir_path.exists(), "Directory does not exist."
    if remove_nonempty:
        shutil.rmtree(dir_path)
        return
    try:
        for _, _, files in dir_path.walk(top_down=False):
            assert not files
        shutil.rmtree(dir_path)
    except:
        warnings.warn("Directory not empty after moving files. Terminating removal.")
    return


def extract_uid_from_filepath(f_path: Path) -> str | None:
    """Extract the UID from the file path."""
    if f_path.suffix == ".json" and "assessments" in str(f_path):
        return f_path.parents[2].stem
    elif f_path.suffix == ".zip" and "zip_participants_merged" in str(f_path):
        return f_path.parent.stem
    return None


def extract_iteration_from_filepath(f_path: Path) -> str:
    """Extract the iteration from the file path."""
    if f_path.suffix == ".json" and "assessments" in str(f_path):
        return f_path.parents[4].stem
    return f_path.parents[2].stem