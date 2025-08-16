import os
import json
import pandas as pd
import numpy as np
import neurokit2 as nk

from src.config import QUALITY_MAPPING, DATASET_DIR, logger


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


def clean_signal(signal: pd.Series, sampling_rate: int = 1000) -> np.ndarray:
    """Cleans the ECG signal."""
    return np.array(nk.ecg_clean(signal, sampling_rate=sampling_rate))


def calculate_quality(signal: np.ndarray, sampling_rate: int, method: str) -> float | None:
    """Calculates the quality of the signal using the given method."""
    try:
        labels = nk.ecg_quality(signal, sampling_rate=sampling_rate, method=method)
        if isinstance(labels[0], (int, float, np.floating)):
            return float(np.mean(labels))
        numeric = [QUALITY_MAPPING.get(q, 0) for q in labels]
        return float(np.mean(numeric))
    except Exception as e:
        logger.error(f"{method}: {e}")
        return None


def evaluate_signal(signal: pd.Series, sampling_rate: int = 1000) -> dict:
    """Evaluates signal quality using multiple methods."""
    cleaned = clean_signal(signal, sampling_rate)
    methods = ["zhao2018", "averageQRS", "templatematch"]
    results = {}
    for method in methods:
        results[method] = calculate_quality(cleaned, sampling_rate, method)
    return results


def process_session(session_path: str) -> dict:
    """Processes a single session (sample)."""
    ecg_file = os.path.join(session_path, "ECG.csv")
    if not os.path.isdir(session_path):
        return {}

    ecg_signal = load_ecg_file(ecg_file)
    if ecg_signal is None or len(ecg_signal) < 2000:
        return {}

    return {"ecg_signal_quality": evaluate_signal(ecg_signal)}


def save_metrics(session_path: str, metrics: dict):
    """Saves the metrics to a JSON file inside a session directory."""
    output_path = os.path.join(session_path, "metrics.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=4)


# def main():
#     for iteration in os.listdir(DATASET_DIR):
#         iteration_path = os.path.join(DATASET_DIR, iteration)
#         if not os.path.isdir(iteration_path):
#             continue
#
#         for person_hash in os.listdir(iteration_path):
#             person_path = os.path.join(iteration_path, person_hash)
#             if not os.path.isdir(person_path):
#                 continue
#
#             for session in os.listdir(person_path):
#                 logger.debug(f"Processing session: {session} for person: {person_hash}")
#                 session_path = os.path.join(person_path, session)
#                 metrics = process_session(session_path)
#                 save_metrics(session_path, metrics)

from concurrent.futures import ThreadPoolExecutor, as_completed

def main(max_workers: int = 16):
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
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
                    futures.append(
                        executor.submit(process_and_save, session_path, person_hash, session)
                    )

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Error in worker: {e}")


def process_and_save(session_path: str, person_hash: str, session: str):
    logger.debug(f"Processing session: {session} for person: {person_hash}")
    metrics = process_session(session_path)
    save_metrics(session_path, metrics)



if __name__ == "__main__":
    main()
