import argparse
import json
import os
from multiprocessing import Pool

import neurokit2 as nk
import numpy as np
import pandas as pd
from biosppy.quality import quality_ecg
from biosppy.signals.ecg import ecg
from scipy.signal import butter, filtfilt
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from config import logger, DEFAULT_INPUT, DEFAULT_OUTPUT, DEFAULT_SAMPLING_RATE, DEFAULT_VERBOSE


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


def calculate_snr(signal: np.ndarray, sampling_rate: int = 130) -> float:
    """Custom SNR metric for ECG signal."""
    b, a = butter(4, [0.5, 40], btype="band", fs=sampling_rate)
    filtered = filtfilt(b, a, signal)
    noise = signal - filtered

    power_signal = np.mean(filtered**2)
    power_noise = np.mean(noise**2)

    return 10 * np.log10(power_signal / power_noise)


def evaluate_signal(signal: pd.Series, sampling_rate: int = 130) -> dict[str, dict[str, float | str | None]]:
    """Evaluates signal quality using multiple methods from NeuroKit and BioSPPy libraries."""
    results = {"NeuroKit": {}, "BioSPPy": {}, "SNR": {}}

    neurokit_cleaned = clean_signal_neurokit(signal, sampling_rate)
    neurokit_methods = ["zhao2018", "averageQRS", "templatematch"]

    biosppy_cleaned = clean_signal_biosppy(signal, sampling_rate)
    biosppy_methods = ['Level3', 'pSQI', 'kSQI', 'fSQI']

    for method in neurokit_methods:
        results["NeuroKit"][method] = calculate_quality(neurokit_cleaned, sampling_rate, method)

    biosppy_results = quality_ecg(segment=biosppy_cleaned, methods=biosppy_methods, sampling_rate=sampling_rate, verbose=False)
    for i, method in enumerate(biosppy_methods):
        results["BioSPPy"][method] = biosppy_results[i]

    results["SNR"]["CustomSNR"] = calculate_snr(signal, sampling_rate)

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


def save_metrics(output_path: str, metrics: dict):
    """Saves the metrics to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=4)


def unpack_and_process(args):
    return process_and_save(*args)


def process_and_save(session_path: str, person_hash: str, session: str, output_dir: str):
    logger.debug(f"Processing session: {session} for person: {person_hash}")
    metrics = process_session(session_path)
    if metrics:
        output_path = os.path.join(output_dir, person_hash, session, "metrics.json")
        save_metrics(output_path, metrics)


def main():
    parser = argparse.ArgumentParser(description="ECG Signal Quality Evaluation Tool")
    parser.add_argument("--input", default=DEFAULT_INPUT, help=f"Path to dataset directory or single ECG.csv file (default: {DEFAULT_INPUT})")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Path to output directory or output JSON file (default: {DEFAULT_OUTPUT})")
    parser.add_argument("--sampling-rate", type=int, default=DEFAULT_SAMPLING_RATE, help=f"Sampling rate of ECG (default: {DEFAULT_SAMPLING_RATE})")
    parser.add_argument("--verbose", action="store_true", default=DEFAULT_VERBOSE, help="Enable debug logging")

    args = parser.parse_args()

    # Ustawienie poziomu logów
    if args.verbose:
        logger.setLevel("DEBUG")

    # Tryb pojedynczego pliku
    if os.path.isfile(args.input):
        signal = load_ecg_file(args.input)
        if signal is None:
            logger.error("Invalid ECG file provided.")
            return
        metrics = {"ecg_signal_quality": evaluate_signal(signal, sampling_rate=args.sampling_rate)}
        save_metrics(args.output, metrics)
        logger.info(f"Saved metrics to {args.output}")
        return

    # Tryb datasetu
    tasks = []
    for iteration in os.listdir(args.input):
        iteration_path = os.path.join(args.input, iteration)
        if not os.path.isdir(iteration_path):
            continue

        for person_hash in os.listdir(iteration_path):
            person_path = os.path.join(iteration_path, person_hash)
            if not os.path.isdir(person_path):
                continue

            for session in os.listdir(person_path):
                session_path = os.path.join(person_path, session)
                output_path = os.path.join(args.output, iteration)
                tasks.append((session_path, person_hash, session, output_path))

    with Pool(processes=os.cpu_count()) as pool, logging_redirect_tqdm():
        with tqdm(total=len(tasks), desc="Processing tasks", dynamic_ncols=True) as pbar:
            for _ in pool.imap_unordered(unpack_and_process, tasks):
                pbar.update(1)
if __name__ == "__main__":
    main()
