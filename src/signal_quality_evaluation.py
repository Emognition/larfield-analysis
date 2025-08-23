import json
import os
import neurokit2 as nk
import numpy as np
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from src.config import DATASET_DIR, logger
from biosppy.signals.ecg import ecg
from biosppy.quality import quality_ecg


def load_ecg_file(filepath: str) -> pd.Series | None:
    """Loads the ECG.csv file and returns the 'ecg' column or None if invalid."""
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return None
    try:
        df = pd.read_csv(filepath, sep="\t")
    except pd.errors.EmptyDataError:
        return None
    if df.empty or "ecg" not in df.columns:
        return None
    return df["ecg"]


def clean_signal_neurokit(signal: pd.Series, sampling_rate: int) -> np.ndarray:
    """Cleans the ECG signal using NeuroKit's built in method."""
    return np.array(nk.ecg_clean(signal, sampling_rate=sampling_rate))


def clean_signal_biosppy(signal: pd.Series, sampling_rate: int) -> np.ndarray:
    """Cleans the ECG signal using BioSPPy's built in method."""
    _, cleaned_signal, *_ = ecg(signal=signal.to_numpy(), sampling_rate=sampling_rate, show=False)
    return cleaned_signal


def calculate_quality(signal: np.ndarray, sampling_rate: int, method: str) -> float | str | None:
    """Calculates the quality of the signal using the given method."""
    try:
        labels = nk.ecg_quality(signal, sampling_rate=sampling_rate, method=method)
        if isinstance(labels[0], (int, float, np.floating)):
            return float(np.mean(labels))
        return labels
    except Exception as e:
        logger.error(f"{method}: {e}")
        return None


def evaluate_signal(signal: pd.Series, sampling_rate: int = 130) -> dict[str, dict[str, float | str | None]]:
    """Evaluates signal quality using multiple methods from NeuroKit and BioSPPy libraries."""
    results = {"NeuroKit": {}, "BioSPPy": {}}

    neurokit_cleaned = clean_signal_neurokit(signal, sampling_rate)
    neurokit_methods = ["zhao2018", "averageQRS", "templatematch"]

    biosppy_cleaned = clean_signal_biosppy(signal, sampling_rate)
    biosppy_methods = ['Level3', 'pSQI', 'kSQI', 'fSQI']

    for method in neurokit_methods:
        results["NeuroKit"][method] = calculate_quality(neurokit_cleaned, sampling_rate, method)

    biosppy_results = quality_ecg(segment=biosppy_cleaned, methods=biosppy_methods, sampling_rate=sampling_rate, verbose=False)
    for i, method in enumerate(biosppy_methods):
        results["BioSPPy"][method] = biosppy_results[i]

    return results


def process_session(session_path: str) -> dict:
    """Processes a single session (sample)."""
    ecg_file = os.path.join(session_path, "ECG.csv")
    if not os.path.isdir(session_path):
        logger.warning(f"Session path does not exist or is not a directory: {session_path}")
        return {}

    ecg_signal = load_ecg_file(ecg_file)
    if ecg_signal is None or len(ecg_signal) < 600:
        logger.warning(f"Invalid ECG signal in {ecg_file}. Skipping session.")
        return {}

    return {"ecg_signal_quality": evaluate_signal(ecg_signal)}


def save_metrics(session_path: str, metrics: dict):
    """Saves the metrics to a JSON file inside a session directory."""
    output_path = os.path.join(session_path, "metrics.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=4)


def unpack_and_process(args):
    """Rozpakowuje argumenty i wywołuje funkcję process_and_save."""
    return process_and_save(*args)


def main():
    tasks = []
    for iteration in os.listdir(DATASET_DIR):
        iteration_path = os.path.join(DATASET_DIR, iteration)
        if not os.path.isdir(iteration_path):
            continue

        for person_hash in os.listdir(iteration_path):
            person_path = os.path.join(iteration_path, person_hash)
            if not os.path.isdir(person_path):
                continue

            for session in os.listdir(person_path):
                session_path = os.path.join(person_path, session)
                tasks.append((session_path, person_hash, session))

    with Pool(processes=os.cpu_count()) as pool, logging_redirect_tqdm():
        with tqdm(total=len(tasks), desc="Processing tasks", dynamic_ncols=True) as pbar:
            for _ in pool.imap_unordered(unpack_and_process, tasks):
                pbar.update(1)


def process_and_save(session_path: str, person_hash: str, session: str):
    logger.debug(f"Processing session: {session} for person: {person_hash}")
    metrics = process_session(session_path)
    save_metrics(session_path, metrics)


if __name__ == "__main__":
    main()
