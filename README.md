## Dataset Structure

The dataset consists of two main parts: raw, unpacked data (larfield) and the original compressed files (larfield_zipped).

```
data/
├── larfield/
│   ├── iteration_01/
│   │   └── [person_hash]/
│   │       ├── POLAR_B2E7B722_v1_2023-06-26T10-07-00-664/
│   │       │   ├── ACC.csv
│   │       │   ├── ECG.csv
│   │       │   ├── HR.csv
│   │       │   ├── metadata.json
│   │       │   └── metrics.json
│   │       ├── POLAR_XXXXXXX_v1_2023-07-01T14-32-00-123/
│   │       │   ├── ACC.csv
│   │       │   ├── ECG.csv
│   │       │   ├── HR.csv
│   │       │   ├── metadata.json
│   │       │   └── metrics.json
│   │       └── ...
│   ├── iteration_02/
│   │   └── [person_hash]/
│   │       ├── POLAR_B2E7B722_v1_2023-06-26T10-07-00-664/
│   │       │   ├── ACC.csv
│   │       │   ├── ECG.csv
│   │       │   ├── HR.csv
│   │       │   ├── metadata.json
│   │       │   └── metrics.json
│   │       ├── POLAR_YYYYYYY_v1_2023-07-15T09-11-45-987/
│   │       │   ├── ACC.csv
│   │       │   ├── ECG.csv
│   │       │   ├── HR.csv
│   │       │   ├── metadata.json
│   │       │   └── metrics.json
│   │       └── ...
│   └── ...
└── larfield_zipped/
    ├── iteration_01/
    │   └── zip_participants_merged/
    │       └── [person_hash]/
    │           ├── POLAR_B2E7B722_v1_2023-06-26T10-07-00-664.zip
    │           ├── POLAR_XXXXXXX_v1_2023-07-01T14-32-00-123.zip
    │           └── ...
    ├── iteration_02/
    │   └── zip_participants_merged/
    │       └── [person_hash]/
    │           ├── POLAR_B2E7B722_v1_2023-06-26T10-07-00-664.zip
    │           ├── POLAR_YYYYYYY_v1_2023-07-15T09-11-45-987.zip
    │           └── ...
    └── ...
```
   
### `metrics.json`

Each `metrics.json` file is stored in the root folder of a participant (`[person_hash]`) and contains quality metrics for each recorded `POLAR_...` session.  
Example:

```json
{
    "ecg_signal_quality": {
        "NeuroKit": {
            "zhao2018": "Barely acceptable",
            "averageQRS": 0.9896970940918103,
            "templatematch": 0.9734324880490363
        },
        "BioSPPy": {
            "Level3": 1.0,
            "pSQI": 0.1423680605148544,
            "kSQI": 29.26033779633734,
            "fSQI": 0.5010238875453531
        },
        "SNR": {
            "CustomSNR": 10.069691606156182
        }
    }
}
```

`metrics.json` — aggregated quality metrics for each session.

# How to use:

signal_processing_python module can be built by following the instructions at https://github.com/Emognition/signal-processing-python

1. Place the **LarField** dataset in the `data/` folder and name it `larfield_zipped`
2. Unzip the dataset into the `larfield/` folder by running: `python src/dataset_operations/unzip.py`
3. Enter the ./src directory: `cd ./src`
4. Evaluate the ECG signal quality using the following script: `python signal_quality_evaluation.py`
