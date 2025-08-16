import pandas as pd
import datetime
import logging
import sys
from src.dataset_operations.helpers import unzip_archive, remove_dir, extract_uid_from_filepath, extract_iteration_from_filepath
from pathlib import Path
from tqdm import tqdm
from multiprocessing import Pool
from typing import Iterable


# set global variables
# project directory
PROJECT_DIR = Path(r"C:\Users\jansz\PycharmProjects\LarField_analysis")
# data directory
DATA_DIR = Path(r"C:\Users\jansz\PycharmProjects\LarField_analysis\data\larfield_zipped")
# tmp directory - where intermediate files are stored
TMP_DIR = PROJECT_DIR / "data" / "larfield"
# iterations to process
ITERATIONS = [
    f"iteration_0{i}" for i in range(1, 7+1)
]
# list of expected files
EXPECTED_FILES = ("ECG.csv", "HR.csv") # ecg and hr only
# name of the logger
LOGGER_NAME = "dataRead"
# logging directory
LOG_DIR = "log"

# set tmp and save directories
tmp_path = TMP_DIR
SAVE_DIR = PROJECT_DIR / "processed_data"

log_dir_path = PROJECT_DIR / LOG_DIR
log_dir_path.mkdir(parents=True, exist_ok=True)

# set start time
START_TIME = datetime.datetime.now().isoformat(sep="T", timespec="seconds").replace(":", "-")
# create loggers for each iteration
iterations_loggers = list()
for iteration in ITERATIONS:
    # configure logging
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    filename=PROJECT_DIR / f"{LOG_DIR}/{LOGGER_NAME}_{iteration}_{START_TIME}.log",
                    filemode="a",
                    encoding='utf-8'
                    )
    # create console handler but do not add it as handler
    # I don't know why, but without it I could not suppress logging stderr to the console
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    # get logger
    logger = logging.getLogger(f'{LOGGER_NAME}_{iteration}')
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    logger.handlers = []  # Clear existing handlers
    # create file handler
    fh = logging.FileHandler(
        PROJECT_DIR / f"{LOG_DIR}/{LOGGER_NAME}_{iteration}_{START_TIME}.log",
        mode='a',
        encoding='utf-8'
        )
    # format messages
    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
        )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # save logger
    iterations_loggers.append((iteration, logger))


def iter_expected_files(path: Path) -> Iterable[tuple[Path, bool]]:
    """
    Iterate over expected files. Helps to validate that all expected files are present, as opposed to iterating over the entire directory.
    """
    for f_name in EXPECTED_FILES:
        yield path / f_name, (path / f_name).exists()


def read_csv_to_dataframe(file_path: Path) -> pd.DataFrame:
    """
    Reads a CSV file and returns a DataFrame.
    """
    try:
        # read the CSV file
        df = pd.read_csv(file_path, sep="\t", low_memory=False)
        # convert ts - faster than using a formatter
        df["ts"] = pd.to_datetime(df["ts"], format="%Y-%m-%dT%H:%M:%S:%f", errors='raise')
    except pd.errors.EmptyDataError as e:
        logging.error(f"Empty file {file_path}: {e}")
        return pd.DataFrame()  # Return an empty DataFrame for empty files
    # convert columns to numeric (ts is already in datetime type)
    for col in df.select_dtypes(include=['object']):
        # convert to numeric. coerce errors (replace incorrect values with nan)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        # save na indices
        na_series = df.isna().any(axis=1)
        # if NA values at the end, simply drop them
        if na_series.any() and all(len(df) - 2 <= df[na_series].index):
            df.dropna(inplace=True, axis=0, how='any')
        # else throw error - does not happen, but just to be safe
        else:
            raise ValueError(f"NA at unexpected position in file: {file_path}.")
    return df


def process_iteration(iteration_str: str, logger: logging.Logger) -> None:
    """Process a single iteration of data files, unpacking while removing 'zip_participants_merged' from tmp path."""

    print(f"Processing iteration: {iteration_str} in directory {DATA_DIR / iteration_str}")

    for f_path in tqdm(
        (DATA_DIR / iteration_str).glob("**/POLAR*.zip"),
        desc="Processing files for " + iteration_str,
        file=sys.stdout
    ):
        print(f"Processing file: {f_path}")
        rel_f_path = f_path.relative_to(DATA_DIR)
        uid = extract_uid_from_filepath(f_path)
        iteration = extract_iteration_from_filepath(f_path)

        # --- build target path in tmp, without "zip_participants_merged"
        parts = list(rel_f_path.parts)
        if "zip_participants_merged" in parts:
            parts.remove("zip_participants_merged")

        # drop last part (the zip filename), keep only directory structure
        target_dir = tmp_path.joinpath(*parts[:-1])
        target_dir.mkdir(parents=True, exist_ok=True)

        # final extracted folder (zip filename without extension)
        extracted_dir = target_dir / f_path.stem

        # --- unzip only if not already extracted
        if extracted_dir.exists() and any(extracted_dir.iterdir()):
            logger.debug(f"Skipping {f_path}, already extracted to {extracted_dir}")
        else:
            unzip_archive(f_path, target_dir)
            logger.info(f"Unzipped {f_path} to {target_dir}")
            print(f"Unzipped {f_path} to {target_dir}")

        # # --- iterate over expected files in unpacked folder
        # for f, exists in iter_expected_files(target_dir / f_path.stem):
        #     if not exists:
        #         logger.warning(f"Expected file not found: {f}")
        #         continue
        #
        #     if f.name == "metadata.json":
        #         continue  # Skip metadata.json for now
        #
        #     try:
        #         df = read_csv_to_dataframe(f)
        #     except Exception as e:
        #         logger.error(f"Unhandled error reading {f.name} in {rel_f_path}: {e}")
        #         continue
        #
        #     if df.empty:
        #         continue
        #     else:
        #         # <- place your dataframe processing logic here
        #         pass

            # Example save (keeping per-iteration and uid structure)
            # out_path = SAVE_DIR / iteration / uid / f_path.stem
            # out_path.mkdir(parents=True, exist_ok=True)
            # df.to_csv(out_path / f.name, sep="\t", index=False)

        # optionally clean up extracted folder afterwards
        # remove_dir(target_dir / f_path.stem, remove_nonempty=True)



if __name__ == "__main__":
    print("Processing start.")
    with Pool(processes=len(iterations_loggers)) as pool:
        pool.starmap(process_iteration, iterations_loggers)
    print("Processing completed.")